import os
import dotenv
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
import subprocess
import sys
import io

dotenv.load_dotenv()

# =============================================================================
# Configuration & Constants
# =============================================================================

PROJECT_ID = os.getenv("PROJECT_ID", "YOUR_PROJECT_ID")

BRAND_COLORS = {
    "BLUE": {"red": 0.258, "green": 0.521, "blue": 0.957},  # #4285F4
    "RED": {"red": 0.917, "green": 0.262, "blue": 0.207},   # #EA4335
    "YELLOW": {"red": 0.984, "green": 0.737, "blue": 0.019}, # #FBBC05
    "GREEN": {"red": 0.203, "green": 0.658, "blue": 0.325},  # #34A853
    "GREY_DARK": {"red": 0.235, "green": 0.251, "blue": 0.263}, # #3C4043
    "GREY_LIGHT": {"red": 0.972, "green": 0.976, "blue": 0.98}, # #F8F9FA
}

# EMU (English Metric Units) constants: 1 inch = 914400 EMU
INCH = 914400
SLIDE_WIDTH = 10 * INCH
SLIDE_HEIGHT = 5.625 * INCH # 16:9 aspect ratio

# =============================================================================
# Helper: Get API Services (Cached Singletons with Static Discovery)
# =============================================================================

_SLIDES_SERVICE = None
_DRIVE_SERVICE = None
_SHEETS_SERVICE = None

def get_slides_service():
    """Returns an authorized Google Slides API service."""
    global _SLIDES_SERVICE
    if _SLIDES_SERVICE is None:
        scopes = [
            "https://www.googleapis.com/auth/presentations",
            "https://www.googleapis.com/auth/drive"
        ]
        credentials, _ = google.auth.default(scopes=scopes)
        _SLIDES_SERVICE = build("slides", "v1", credentials=credentials, static_discovery=True)
    return _SLIDES_SERVICE

def get_drive_service():
    """Returns an authorized Google Drive API service."""
    global _DRIVE_SERVICE
    if _DRIVE_SERVICE is None:
        scopes = [
            "https://www.googleapis.com/auth/drive"
        ]
        credentials, _ = google.auth.default(scopes=scopes)
        _DRIVE_SERVICE = build("drive", "v3", credentials=credentials, static_discovery=True)
    return _DRIVE_SERVICE

def get_sheets_service():
    """Returns an authorized Google Sheets API service."""
    global _SHEETS_SERVICE
    if _SHEETS_SERVICE is None:
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        credentials, _ = google.auth.default(scopes=scopes)
        _SHEETS_SERVICE = build("sheets", "v4", credentials=credentials, static_discovery=True)
    return _SHEETS_SERVICE

# =============================================================================
# Tools
# =============================================================================

def create_google_presentation(title: str, folder_id: str = "1xqjbUZ28L13nJrLeFvwViRHKalvcDntE") -> dict:
    """
    Creates a new Google Slides presentation.
    
    Args:
        title (str): The title of the presentation.
        folder_id (str, optional): The ID of the Google Drive folder to save the presentation in.
        
    Returns:
        dict: Information about the created presentation including presentationId and url.
    """
    print("DEBUG: create_google_presentation starting...", flush=True)
    slides_service = get_slides_service()
    print("DEBUG: slides_service acquired.", flush=True)
    drive_service = get_drive_service()
    print("DEBUG: drive_service acquired.", flush=True)
    
    body = {"title": title}
    try:
        # 0. Sanitize folder_id
        if folder_id:
            folder_id = folder_id.strip()

        # 1. Create the presentation directly in the target folder using Drive API
        # This is the most efficient way for Shared Drives.
        body = {
            "name": title,
            "mimeType": "application/vnd.google-apps.presentation"
        }
        if folder_id:
            body["parents"] = [folder_id]

        print("DEBUG: Sending create presentation request to Drive API...", flush=True)
        file = drive_service.files().create(
            body=body,
            supportsAllDrives=True, # Required for Shared Drives
            fields="id"
        ).execute()
        print("DEBUG: Drive API request completed. File ID obtained.", flush=True)
        
        presentation_id = file.get("id")
        
        # 最初の自動生成スライド内のデフォルトプレースホルダー要素を全削除し、完全な白紙スライドへリセット
        try:
            pres_data = slides_service.presentations().get(presentationId=presentation_id).execute()
            slides = pres_data.get("slides", [])
            if slides:
                first_slide = slides[0]
                first_slide_id = first_slide["objectId"]
                page_elements = first_slide.get("pageElements", [])
                delete_reqs = []
                for elem in page_elements:
                    delete_reqs.append({
                        "deleteObject": {
                            "objectId": elem["objectId"]
                        }
                    })
                if delete_reqs:
                    slides_service.presentations().batchUpdate(
                        presentationId=presentation_id,
                        body={"requests": delete_reqs}
                    ).execute()
                    print(f"DEBUG: Successfully purged {len(delete_reqs)} default templates from first slide {first_slide_id}.", flush=True)
        except Exception as e:
            print(f"DEBUG: Non-blocking first slide placeholder purging warning: {e}", flush=True)
        
        return {
            "presentationId": presentation_id,
            "url": f"https://docs.google.com/presentation/d/{presentation_id}/edit",
            "title": title,
            "folderId": folder_id
        }
    except HttpError as error:
        error_msg = error.content.decode() if hasattr(error, 'content') else str(error)
        return {
            "error": f"Google API Error: {error_msg}",
            "title_attempted": title,
            "folder_id_attempted": folder_id
        }

def add_structured_slide(
    presentation_id: str,
    slide_type: str,
    title: str,
    key_message: str = "",
    body_text: str = "",
    image_url: str | None = None
) -> dict:
    """
    構造化されたスライドを追加します。

    Args:
        presentation_id: プレゼンテーションID
        slide_type: スライドタイプ ("TITLE", "SECTION", "CONTENT", "IMAGE")
        title: タイトル
        key_message: キーメッセージ（任意）
        body_text: 本文（任意）
        image_url: 画像URL（任意）

    Returns:
        dict: 作成ステータス
    """
    service = get_slides_service()
    requests = []
    
    # 既存のスライドを取得し、1枚のみでIDが 'p' の場合は削除リストに追加
    delete_first_slide = False
    try:
        p_info = service.presentations().get(presentationId=presentation_id).execute()
        slides = p_info.get("slides", [])
        if len(slides) == 1 and slides[0]["objectId"] == "p":
            delete_first_slide = True
            first_slide_id = slides[0]["objectId"]
    except Exception:
        pass # 取得失敗時は安全のため通常の追加のみを行う

    # 1. Create a blank slide
    slide_id = f"slide_{os.urandom(4).hex()}"
    requests.append({
        "createSlide": {
            "objectId": slide_id,
            "slideLayoutReference": {"predefinedLayout": "BLANK"}
        }
    })
    
    if delete_first_slide:
        requests.append({
            "deleteObject": {
                "objectId": first_slide_id
            }
        })
    
    if slide_type.upper() == "TITLE" and not image_url:
        # Title Slide Layout
        requests.extend(_get_title_slide_requests(slide_id, title, body_text))
    elif slide_type.upper() == "SECTION" and not image_url:
        # Section Header Layout
        requests.extend(_get_section_slide_requests(slide_id, title))
    elif slide_type.upper() == "IMAGE" or image_url:
        # Image + Content Layout (2-column)
        requests.extend(_get_image_slide_requests(slide_id, title, key_message, body_text, image_url))
    else:
        # Standard Content Layout (Japanese Style)
        requests.extend(_get_content_slide_requests(slide_id, title, key_message, body_text))

    # 共通ブランディング要素を追加（右上ヘッダー、左下フッター、色バー）
    requests.extend(_get_common_branding_requests(slide_id))

    try:
        service.presentations().batchUpdate(
            presentationId=presentation_id, 
            body={"requests": requests}
        ).execute()
        return {"status": "success", "slideId": slide_id, "type": slide_type}
    except HttpError as error:
        return {"error": str(error)}

# =============================================================================
# Layout Internal Helpers
# =============================================================================

def _get_common_branding_requests(slide_id):
    """
    右上（機密情報）、左下（フッター）、最下部（Googleカラーの4色バー）を追加するリクエストを返します。
    """
    reqs = []
    
    # 1. 右上の Proprietary + Confidential
    header_id = f"header_brand_{slide_id}"
    reqs.append({
        "createShape": {
            "objectId": header_id,
            "shapeType": "TEXT_BOX",
            "elementProperties": {
                "pageObjectId": slide_id,
                "size": {"width": {"magnitude": 2.5 * INCH, "unit": "EMU"}, "height": {"magnitude": 0.3 * INCH, "unit": "EMU"}},
                "transform": {"scaleX": 1, "scaleY": 1, "translateX": SLIDE_WIDTH - 2.3 * INCH, "translateY": 0.2 * INCH, "unit": "EMU"}
            }
        }
    })
    reqs.append({"insertText": {"objectId": header_id, "text": "Proprietary + Confidential"}})
    reqs.append({"updateTextStyle": {"objectId": header_id, "style": {"fontSize": {"magnitude": 9, "unit": "PT"}, "foregroundColor": {"opaqueColor": {"rgbColor": BRAND_COLORS["GREY_DARK"]}}}, "textRange": {"type": "ALL"}, "fields": "fontSize,foregroundColor"}})

    # 2. 左下の Gemini Enterprise
    footer_id = f"footer_brand_{slide_id}"
    reqs.append({
        "createShape": {
            "objectId": footer_id,
            "shapeType": "TEXT_BOX",
            "elementProperties": {
                "pageObjectId": slide_id,
                "size": {"width": {"magnitude": 3.0 * INCH, "unit": "EMU"}, "height": {"magnitude": 0.3 * INCH, "unit": "EMU"}},
                "transform": {"scaleX": 1, "scaleY": 1, "translateX": 0.5 * INCH, "translateY": SLIDE_HEIGHT - 0.5 * INCH, "unit": "EMU"}
            }
        }
    })
    reqs.append({"insertText": {"objectId": footer_id, "text": "Gemini Enterprise"}})
    reqs.append({"updateTextStyle": {"objectId": footer_id, "style": {"fontSize": {"magnitude": 10, "unit": "PT"}, "foregroundColor": {"opaqueColor": {"rgbColor": BRAND_COLORS["GREY_DARK"]}}}, "textRange": {"type": "ALL"}, "fields": "fontSize,foregroundColor"}})

    # 3. 最下部の4色の帯 (青, 赤, 黄, 緑)
    bar_height = 4  # EMU 換算（PT）
    bar_width = SLIDE_WIDTH / 4
    colors = ["BLUE", "RED", "YELLOW", "GREEN"]
    
    for i, color_name in enumerate(colors):
        bar_id = f"bottom_bar_{color_name}_{slide_id}"
        reqs.append({
            "createShape": {
                "objectId": bar_id,
                "shapeType": "RECTANGLE",
                "elementProperties": {
                    "pageObjectId": slide_id,
                    "size": {"width": {"magnitude": bar_width, "unit": "EMU"}, "height": {"magnitude": bar_height, "unit": "PT"}},
                    "transform": {"scaleX": 1, "scaleY": 1, "translateX": bar_width * i, "translateY": SLIDE_HEIGHT - bar_height * (914400 / 72), "unit": "EMU"} # PTをEMUへ
                }
            }
        })
        reqs.append({"updateShapeProperties": {"objectId": bar_id, "shapeProperties": {"shapeBackgroundFill": {"solidFill": {"color": {"rgbColor": BRAND_COLORS[color_name]}}}, "outline": {"outlineFill": {"solidFill": {"alpha": 0}}}}, "fields": "shapeBackgroundFill.solidFill.color,outline"}})

    return reqs

def _get_title_slide_requests(slide_id, title, subtitle):
    reqs = []
    # Title text box
    obj_id = f"title_{slide_id}"
    reqs.append({
        "createShape": {
            "objectId": obj_id,
            "shapeType": "TEXT_BOX",
            "elementProperties": {
                "pageObjectId": slide_id,
                "size": {"width": {"magnitude": SLIDE_WIDTH * 0.8, "unit": "EMU"}, "height": {"magnitude": 1.5 * INCH, "unit": "EMU"}},
                "transform": {"scaleX": 1, "scaleY": 1, "translateX": SLIDE_WIDTH * 0.1, "translateY": SLIDE_HEIGHT * 0.3, "unit": "EMU"}
            }
        }
    })
    reqs.append({
        "insertText": {"objectId": obj_id, "text": title}
    })
    reqs.append({
        "updateTextStyle": {
            "objectId": obj_id, 
            "style": {"fontSize": {"magnitude": 44, "unit": "PT"}, "bold": True, "foregroundColor": {"opaqueColor": {"rgbColor": BRAND_COLORS["GREY_DARK"]}}},
            "textRange": {"type": "ALL"},
            "fields": "fontSize,bold,foregroundColor"
        }
    })
    # Accent Line (Google Blue)
    line_id = f"line_{slide_id}"
    
    # Calculate Y position based on title length (Font 44pt wrapped at ~22 characters)
    title_len = len(title)
    estimated_lines = (title_len // 22) + 1
    base_translate_y = SLIDE_HEIGHT * 0.65
    if estimated_lines > 1:
        # Shift down by 6% height per extra line to avoid overlapping
        base_translate_y += SLIDE_HEIGHT * 0.06 * (estimated_lines - 1)

    reqs.append({
        "createShape": {
            "objectId": line_id,
            "shapeType": "RECTANGLE",
            "elementProperties": {
                "pageObjectId": slide_id,
                "size": {"width": {"magnitude": SLIDE_WIDTH * 0.8, "unit": "EMU"}, "height": {"magnitude": 0.05 * INCH, "unit": "EMU"}},
                "transform": {"scaleX": 1, "scaleY": 1, "translateX": SLIDE_WIDTH * 0.1, "translateY": base_translate_y, "unit": "EMU"}
            }
        }
    })
    reqs.append({
        "updateShapeProperties": {
            "objectId": line_id,
            "shapeProperties": {"shapeBackgroundFill": {"solidFill": {"color": {"rgbColor": BRAND_COLORS["BLUE"]}}}, "outline": {"dashStyle": "SOLID", "outlineFill": {"solidFill": {"alpha": 0}}}},
            "fields": "shapeBackgroundFill.solidFill.color,outline"
        }
    })
    return reqs

def _get_content_slide_requests(slide_id, title, key_message, body):
    reqs = []
    # 1. Slide Title with Left Border
    title_id = f"title_{slide_id}"
    reqs.append({
        "createShape": {
            "objectId": title_id,
            "shapeType": "TEXT_BOX",
            "elementProperties": {
                "pageObjectId": slide_id,
                "size": {"width": {"magnitude": SLIDE_WIDTH * 0.9, "unit": "EMU"}, "height": {"magnitude": 0.6 * INCH, "unit": "EMU"}},
                "transform": {"scaleX": 1, "scaleY": 1, "translateX": 0.5 * INCH, "translateY": 0.3 * INCH, "unit": "EMU"}
            }
        }
    })
    reqs.append({"insertText": {"objectId": title_id, "text": title}})
    reqs.append({
        "updateTextStyle": {
            "objectId": title_id, 
            "style": {"fontSize": {"magnitude": 24, "unit": "PT"}, "bold": True, "foregroundColor": {"opaqueColor": {"rgbColor": BRAND_COLORS["GREY_DARK"]}}},
            "textRange": {"type": "ALL"},
            "fields": "fontSize,bold,foregroundColor"
        }
    })
    # Accent border
    border_id = f"border_{slide_id}"
    reqs.append({
        "createShape": {
            "objectId": border_id,
            "shapeType": "RECTANGLE",
            "elementProperties": {
                "pageObjectId": slide_id,
                "size": {"width": {"magnitude": 6, "unit": "PT"}, "height": {"magnitude": 0.4 * INCH, "unit": "EMU"}},
                "transform": {"scaleX": 1, "scaleY": 1, "translateX": 0.3 * INCH, "translateY": 0.4 * INCH, "unit": "EMU"}
            }
        }
    })
    reqs.append({"updateShapeProperties": {"objectId": border_id, "shapeProperties": {"shapeBackgroundFill": {"solidFill": {"color": {"rgbColor": BRAND_COLORS["BLUE"]}}}, "outline": {"outlineFill": {"solidFill": {"alpha": 0}}}}, "fields": "shapeBackgroundFill.solidFill.color,outline"}})

    # 2. Key Message Box (Japanese Style)
    if key_message:
        km_id = f"km_{slide_id}"
        reqs.append({
            "createShape": {
                "objectId": km_id,
                "shapeType": "RECTANGLE",
                "elementProperties": {
                    "pageObjectId": slide_id,
                    "size": {"width": {"magnitude": SLIDE_WIDTH * 0.9, "unit": "EMU"}, "height": {"magnitude": 0.8 * INCH, "unit": "EMU"}},
                    "transform": {"scaleX": 1, "scaleY": 1, "translateX": 0.5 * INCH, "translateY": 1.0 * INCH, "unit": "EMU"}
                }
            }
        })
        reqs.append({"updateShapeProperties": {"objectId": km_id, "shapeProperties": {"shapeBackgroundFill": {"solidFill": {"color": {"rgbColor": BRAND_COLORS["GREY_LIGHT"]}}}, "outline": {"weight": {"magnitude": 1, "unit": "PT"}, "outlineFill": {"solidFill": {"color": {"rgbColor": {"red": 0.9, "green": 0.9, "blue": 0.9}}}}}}, "fields": "shapeBackgroundFill.solidFill.color,outline"}})
        reqs.append({"insertText": {"objectId": km_id, "text": key_message}})
        reqs.append({"updateTextStyle": {"objectId": km_id, "style": {"fontSize": {"magnitude": 14, "unit": "PT"}, "italic": True, "foregroundColor": {"opaqueColor": {"rgbColor": BRAND_COLORS["GREY_DARK"]}}}, "textRange": {"type": "ALL"}, "fields": "fontSize,italic,foregroundColor"}})

    # 3. Body Text
    if body:
        body_id = f"body_{slide_id}"
        reqs.append({
            "createShape": {
                "objectId": body_id,
                "shapeType": "TEXT_BOX",
                "elementProperties": {
                    "pageObjectId": slide_id,
                    "size": {"width": {"magnitude": SLIDE_WIDTH * 0.9, "unit": "EMU"}, "height": {"magnitude": 2.5 * INCH, "unit": "EMU"}},
                    "transform": {"scaleX": 1, "scaleY": 1, "translateX": 0.5 * INCH, "translateY": 2.0 * INCH, "unit": "EMU"}
                }
            }
        })
        # * や - を ・ に変換（日本ビジネス用）
        body_sanitized = body.replace('* ', '・ ').replace('- ', '・ ')
        
        # Remove bullet '・' if it precedes '【'
        lines = body_sanitized.split('\n')
        new_lines = []
        for l in lines:
            if l.strip().startswith('・ 【'):
                new_lines.append(l.replace('・ 【', '【'))
            else:
                new_lines.append(l)
        body_sanitized = '\n'.join(new_lines)
        reqs.append({"insertText": {"objectId": body_id, "text": body_sanitized}})
        reqs.append({"updateTextStyle": {"objectId": body_id, "style": {"fontSize": {"magnitude": 14, "unit": "PT"}, "foregroundColor": {"opaqueColor": {"rgbColor": BRAND_COLORS["GREY_DARK"]}}}, "textRange": {"type": "ALL"}, "fields": "fontSize,foregroundColor"}})

    return reqs

def _get_section_slide_requests(slide_id, title):
    reqs = []
    # Grey background
    reqs.append({"updatePageProperties": {"objectId": slide_id, "pageProperties": {"pageBackgroundFill": {"solidFill": {"color": {"rgbColor": BRAND_COLORS["GREY_LIGHT"]}}}}, "fields": "pageBackgroundFill.solidFill.color"}})
    # Section Title
    title_id = f"section_{slide_id}"
    reqs.append({
        "createShape": {
            "objectId": title_id,
            "shapeType": "TEXT_BOX",
            "elementProperties": {
                "pageObjectId": slide_id,
                "size": {"width": {"magnitude": SLIDE_WIDTH * 0.8, "unit": "EMU"}, "height": {"magnitude": 1.0 * INCH, "unit": "EMU"}},
                "transform": {"scaleX": 1, "scaleY": 1, "translateX": SLIDE_WIDTH * 0.1, "translateY": SLIDE_HEIGHT * 0.4, "unit": "EMU"}
            }
        }
    })
    reqs.append({"insertText": {"objectId": title_id, "text": title}})
    reqs.append({"updateTextStyle": {"objectId": title_id, "style": {"fontSize": {"magnitude": 36, "unit": "PT"}, "bold": True, "foregroundColor": {"opaqueColor": {"rgbColor": BRAND_COLORS["BLUE"]}}}, "textRange": {"type": "ALL"}}})
    return reqs

def _get_image_slide_requests(slide_id, title, key_message, body, image_url):
    reqs = []
    
    # 1. Slide Title (Reduced Width)
    title_id = f"title_{slide_id}"
    reqs.append({
        "createShape": {
            "objectId": title_id,
            "shapeType": "TEXT_BOX",
            "elementProperties": {
                "pageObjectId": slide_id,
                "size": {"width": {"magnitude": SLIDE_WIDTH * 0.9, "unit": "EMU"}, "height": {"magnitude": 0.6 * INCH, "unit": "EMU"}},
                "transform": {"scaleX": 1, "scaleY": 1, "translateX": 0.5 * INCH, "translateY": 0.3 * INCH, "unit": "EMU"}
            }
        }
    })
    reqs.append({"insertText": {"objectId": title_id, "text": title}})
    reqs.append({
        "updateTextStyle": {
            "objectId": title_id, 
            "style": {"fontSize": {"magnitude": 24, "unit": "PT"}, "bold": True, "foregroundColor": {"opaqueColor": {"rgbColor": BRAND_COLORS["GREY_DARK"]}}},
            "textRange": {"type": "ALL"},
            "fields": "fontSize,bold,foregroundColor"
        }
    })

    # Accent border
    border_id = f"border_{slide_id}"
    reqs.append({
        "createShape": {
            "objectId": border_id,
            "shapeType": "RECTANGLE",
            "elementProperties": {
                "pageObjectId": slide_id,
                "size": {"width": {"magnitude": 6, "unit": "PT"}, "height": {"magnitude": 0.4 * INCH, "unit": "EMU"}},
                "transform": {"scaleX": 1, "scaleY": 1, "translateX": 0.3 * INCH, "translateY": 0.4 * INCH, "unit": "EMU"}
            }
        }
    })
    reqs.append({"updateShapeProperties": {"objectId": border_id, "shapeProperties": {"shapeBackgroundFill": {"solidFill": {"color": {"rgbColor": BRAND_COLORS["BLUE"]}}}, "outline": {"outlineFill": {"solidFill": {"alpha": 0}}}}, "fields": "shapeBackgroundFill.solidFill.color,outline"}})

    # 2. Key Message Box (Left side)
    if key_message:
        km_id = f"km_{slide_id}"
        reqs.append({
            "createShape": {
                "objectId": km_id,
                "shapeType": "RECTANGLE",
                "elementProperties": {
                    "pageObjectId": slide_id,
                    "size": {"width": {"magnitude": SLIDE_WIDTH * 0.9, "unit": "EMU"}, "height": {"magnitude": 0.8 * INCH, "unit": "EMU"}},
                    "transform": {"scaleX": 1, "scaleY": 1, "translateX": 0.5 * INCH, "translateY": 1.0 * INCH, "unit": "EMU"}
                }
            }
        })
        reqs.append({"updateShapeProperties": {"objectId": km_id, "shapeProperties": {"shapeBackgroundFill": {"solidFill": {"color": {"rgbColor": BRAND_COLORS["GREY_LIGHT"]}}}, "outline": {"weight": {"magnitude": 1, "unit": "PT"}, "outlineFill": {"solidFill": {"color": {"rgbColor": {"red": 0.9, "green": 0.9, "blue": 0.9}}}}}}, "fields": "shapeBackgroundFill.solidFill.color,outline"}})
        reqs.append({"insertText": {"objectId": km_id, "text": key_message}})
        reqs.append({"updateTextStyle": {"objectId": km_id, "style": {"fontSize": {"magnitude": 12, "unit": "PT"}, "italic": True, "foregroundColor": {"opaqueColor": {"rgbColor": BRAND_COLORS["GREY_DARK"]}}}, "textRange": {"type": "ALL"}, "fields": "fontSize,italic,foregroundColor"}})

    # 3. Body Text (Left side)
    if body:
        body_id = f"body_{slide_id}"
        reqs.append({
            "createShape": {
                "objectId": body_id,
                "shapeType": "TEXT_BOX",
                "elementProperties": {
                    "pageObjectId": slide_id,
                    "size": {"width": {"magnitude": SLIDE_WIDTH * 0.45, "unit": "EMU"}, "height": {"magnitude": 2.5 * INCH, "unit": "EMU"}},
                    "transform": {"scaleX": 1, "scaleY": 1, "translateX": 0.5 * INCH, "translateY": 2.0 * INCH, "unit": "EMU"}
                }
            }
        })
        # * や - を ・ に変換（日本ビジネス用）
        body_sanitized = body.replace('* ', '・ ').replace('- ', '・ ')
        
        # Remove bullet '・' if it precedes '【'
        lines = body_sanitized.split('\n')
        new_lines = []
        for l in lines:
            if l.strip().startswith('・ 【'):
                new_lines.append(l.replace('・ 【', '【'))
            else:
                new_lines.append(l)
        body_sanitized = '\n'.join(new_lines)
        reqs.append({"insertText": {"objectId": body_id, "text": body_sanitized}})
        reqs.append({"updateTextStyle": {"objectId": body_id, "style": {"fontSize": {"magnitude": 12, "unit": "PT"}, "foregroundColor": {"opaqueColor": {"rgbColor": BRAND_COLORS["GREY_DARK"]}}}, "textRange": {"type": "ALL"}, "fields": "fontSize,foregroundColor"}})

    # 4. Image Position (Right side)
    if image_url:
        reqs.append({
            "createImage": {
                "objectId": f"image_{slide_id}",
                "url": image_url,
                "elementProperties": {
                    "pageObjectId": slide_id,
                    "size": {"width": {"magnitude": SLIDE_WIDTH * 0.45, "unit": "EMU"}, "height": {"magnitude": SLIDE_HEIGHT * 0.6, "unit": "EMU"}},
                    "transform": {"scaleX": 1, "scaleY": 1, "translateX": SLIDE_WIDTH * 0.5, "translateY": SLIDE_HEIGHT * 0.35, "unit": "EMU"}
                }
            }
        })

    return reqs

def upload_image_to_drive(file_path: str, folder_id: str = "1xqjbUZ28L13nJrLeFvwViRHKalvcDntE") -> dict:
    """
    ローカルの画像ファイルをGoogle Driveにアップロードし、Slides APIで読み込めるURLを取得します。
    
    Args:
        file_path (str): アップロードするローカル画像ファイルのパス。
        folder_id (str): 保存先のGoogle DriveフォルダID（デフォルト指定あり）。
    
    Returns:
        dict: アップロード結果（fileId, imageUrl または error）
    """
    drive_service = get_drive_service()
    
    if not os.path.exists(file_path):
        return {"error": f"指定されたファイルが見つかりません: {file_path}"}
        
    file_name = os.path.basename(file_path)
    
    file_metadata = {
        'name': file_name,
        'mimeType': 'image/png'
    }
    if folder_id:
        file_metadata['parents'] = [folder_id]
        
    try:
        media = MediaFileUpload(file_path, mimetype='image/png', resumable=True)
        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id',
            supportsAllDrives=True
        ).execute()
        
        file_id = file.get('id')
        
        # Slides APIがアクセスできるように権限を一時的に公開（PoC用）
        drive_service.permissions().create(
            fileId=file_id,
            body={'type': 'anyone', 'role': 'reader'},
            supportsAllDrives=True
        ).execute()
        
        image_url = f"https://drive.google.com/uc?id={file_id}"
        
        return {
            "status": "success",
            "fileId": file_id,
            "imageUrl": image_url
        }
    except Exception as e:
        return {"error": f"画像のアップロード中にエラーが発生しました: {str(e)}"}

def generate_matplotlib_image(code: str, output_file: str = "generated_plot.png") -> dict:
    """
    Pythonコード（Matplotlib等）を実行して画像ファイル（PNG）を生成します。
    
    Args:
        code (str): 実行するPythonコード（Matplotlibのプロットコード等）。
        output_file (str): 保存する画像ファイル名（例: generated_plot.png）。
    
    Returns:
        dict: 実行結果（ステータス、絶対ファイルパス等）。
    """
    app_dir = os.path.dirname(os.path.dirname(__file__))
    scratch_dir = os.path.join(app_dir, "scratch")
    os.makedirs(scratch_dir, exist_ok=True)
    
    temp_script = os.path.join(scratch_dir, "temp_plot_runner.py")
    
    # ensure plt.savefig is used if not present
    if "plt.savefig" not in code:
        code += f"\nimport matplotlib.pyplot as plt\nplt.savefig('{output_file}')\n"
        
    try:
        with open(temp_script, "w", encoding="utf-8") as f:
            f.write(code)
            
        result = subprocess.run(
            [sys.executable, temp_script],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            return {
                "error": f"コードの実行に失敗しました:\n{result.stderr}",
                "stdout": result.stdout
            }
            
        if not os.path.exists(output_file):
            return {
                "error": f"コード実行は成功しましたが、画像（{output_file}）が生成されませんでした。"
            }
            
        return {
            "status": "success",
            "filePath": os.path.abspath(output_file),
            "message": f"画像を生成しました: {output_file}"
        }
    except Exception as e:
        return {"error": f"画像生成中にエラーが発生しました: {str(e)}"}

def generate_and_upload_plot_direct(code: str, folder_id: str = "1xqjbUZ28L13nJrLeFvwViRHKalvcDntE") -> dict:
    """
    Pythonコードを実行してグラフ画像を生成し、ローカルに保存せず直接Google Driveにアップロードします。
    
    Args:
        code (str): 実行するPythonコード（Matplotlibのプロットコード）。
        folder_id (str): 保存先のGoogle DriveフォルダID（デフォルト指定あり）。
    
    Returns:
        dict: 実行結果（fileId, imageUrl, status等）。
    """
    import matplotlib.pyplot as plt
    from googleapiclient.http import MediaIoBaseUpload
    
    drive_service = get_drive_service()
    
    try:
        # plt の状態をリセットして汚染を防ぐ
        plt.clf()
        plt.close('all')
        
        # 日本語フォントの設定（Mac等のトーフ「文字化け」対策：日本語名も含めたフォールバック対応）
        plt.rcParams['font.sans-serif'] = [
            'Hiragino Sans', 'ヒラギノ角ゴシック',
            'Yu Gothic', '游ゴシック',
            'Meiryo', 'メイリオ',
            'TakaoPGothic', 'IPAexGothic', 'Noto Sans CJK JP',
            'DejaVu Sans', 'sans-serif'
        ]
        plt.rcParams['font.family'] = 'sans-serif'
        
        # コードの実行（グラフ描画ステートが plt に保持される）
        # ただし外部依存が大きいため、カレントコンテキストで安全に実行
        # エージェントがコード内で plt.show() や plt.close() を呼び出して
        # カレントフィギュアがリセット（白紙）されないよう、一時的に無効化（モック化）する
        orig_show = plt.show
        orig_close = plt.close
        plt.show = lambda *args, **kwargs: None
        plt.close = lambda *args, **kwargs: None
        
        local_scope = {}
        try:
            exec(code, globals(), local_scope)
            
            # インメモリバッファに保存
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight')
            buf.seek(0)
        finally:
            # モックを元に戻す
            plt.show = orig_show
            plt.close = orig_close
        
        media = MediaIoBaseUpload(buf, mimetype='image/png', resumable=True)
        
        file_metadata = {
            'name': 'generated_plot_direct.png',
            'mimeType': 'image/png'
        }
        if folder_id:
            file_metadata['parents'] = [folder_id]
            
        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id',
            supportsAllDrives=True
        ).execute()
        
        file_id = file.get('id')
        
        # Slides APIがアクセスできるように権限を一時的に公開（PoC用）
        drive_service.permissions().create(
            fileId=file_id,
            body={'type': 'anyone', 'role': 'reader'},
            supportsAllDrives=True
        ).execute()
        
        image_url = f"https://drive.google.com/uc?id={file_id}"
        
        return {
            "status": "success",
            "fileId": file_id,
            "imageUrl": image_url,
            "message": "画像をインメモリで生成し、直接共有ドライブにアップロードしました。"
        }
    except Exception as e:
        return {"error": f"インメモリ画像生成/アップロード中にエラーが発生しました: {str(e)}"}


def add_sheets_chart_from_data(
    presentation_id: str,
    slide_id: str,
    data: list,
    title: str = "Chart",
    chart_type: str = "COLUMN",
    x: float = None,
    y: float = None,
    width: float = None,
    height: float = None,
    spreadsheet_id: str = None
) -> dict:
    """
    Google Sheets にデータを書き込んでグラフを作成し、それをスライドに挿入します。
    
    Args:
        presentation_id (str): プレゼンテーションID。
        slide_id (str): 挿入するスライドのID。
        data (list): 書き込むデータ（二次元配列。1行目はヘッダー）。
        title (str): グラフのタイトル。
        chart_type (str): グラフの種類 ("BAR", "COLUMN", "LINE", "AREA", "SCATTER")。
        x (float, optional): グラフを配置するX座標 (pt)。デフォルトは SLIDE_WIDTH * 0.1。
        y (float, optional): グラフを配置するY座標 (pt)。デフォルトは SLIDE_HEIGHT * 0.2。
        width (float, optional): グラフの横幅 (pt)。デフォルトは SLIDE_WIDTH * 0.8。
        height (float, optional): グラフの高さ (pt)。デフォルトは SLIDE_HEIGHT * 0.6。
        spreadsheet_id (str, optional): 既存のスプレッドシートID。指定された場合は新規作成せずシートを追加します。
        
    Returns:
        dict: 実行結果。
    """
    import io
    from googleapiclient.http import MediaIoBaseUpload
    
    slides_service = get_slides_service()
    sheets_service = get_sheets_service()
    drive_service = get_drive_service()
    
    try:
        spreadsheet_id_provided = (spreadsheet_id is not None)
        
        # 1. スプレッドシートの準備
        if spreadsheet_id_provided:
            # 既存のスプレッドシートを使用。新しいユニークなシート（タブ）を追加する
            import time
            sheet_name = f"Chart_{int(time.time())}"
            
            add_sheet_request = {
                "addSheet": {
                    "properties": {
                        "title": sheet_name
                    }
                }
            }
            batch_update_response = sheets_service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={"requests": [add_sheet_request]}
            ).execute()
            
            sheet_id = batch_update_response["replies"][0]["addSheet"]["properties"]["sheetId"]
        else:
            # スプレッドシートの新規作成（フォールバック）
            spreadsheet_body = {
                "properties": {
                    "title": f"TempChartData_{title}"
                }
            }
            spreadsheet = sheets_service.spreadsheets().create(
                body=spreadsheet_body,
                fields="spreadsheetId"
            ).execute()
            spreadsheet_id = spreadsheet.get("spreadsheetId")
            sheet_name = "Sheet1"
            
        # 2. データの書き込み
        value_range_body = {
            "values": data
        }
        sheets_service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=f"'{sheet_name}'!A1",
            valueInputOption="USER_ENTERED",
            body=value_range_body
        ).execute()
        
        # 新規作成時のみ共有設定を変更し、sheet_idを取得する
        if not spreadsheet_id_provided:
            # 2.5. スプレッドシートの共有権限を anyone/reader に変更（Slidesレンダリングエンジンへのデータアクセス許可）
            drive_service.permissions().create(
                fileId=spreadsheet_id,
                body={
                    "role": "reader",
                    "type": "anyone"
                }
            ).execute()
            
            # シート情報の取得
            sheet_metadata = sheets_service.spreadsheets().get(
                spreadsheetId=spreadsheet_id
            ).execute()
            sheet_id = sheet_metadata["sheets"][0]["properties"]["sheetId"]
        
        # 3. グラフの作成
        num_rows = len(data)
        num_cols = len(data[0]) if num_rows > 0 else 0
        
        chart_spec = {
            "title": title,
            "basicChart": {
                "chartType": chart_type,
                "legendPosition": "BOTTOM_LEGEND",
                "headerCount": 1,
                "domains": [
                    {
                        "domain": {
                            "sourceRange": {
                                "sources": [
                                    {
                                        "sheetId": sheet_id,
                                        "startRowIndex": 0,
                                        "endRowIndex": num_rows,
                                        "startColumnIndex": 0,
                                        "endColumnIndex": 1
                                    }
                                ]
                            }
                        }
                    }
                ],
                "series": []
            }
        }
        
        BRAND_COLORS = {
            "BLUE": {"rgbColor": {"red": 0.10, "green": 0.45, "blue": 0.91}},
            "RED": {"rgbColor": {"red": 0.85, "green": 0.19, "blue": 0.15}}
        }
        
        COLOR_KEYS = ["BLUE", "RED"]
        for col_idx in range(1, num_cols):
            target_axis = "LEFT_AXIS"
            color_key = COLOR_KEYS[(col_idx - 1) % len(COLOR_KEYS)]
            chart_spec["basicChart"]["series"].append({
                "series": {
                    "sourceRange": {
                        "sources": [
                            {
                                "sheetId": sheet_id,
                                "startRowIndex": 0,
                                "endRowIndex": num_rows,
                                "startColumnIndex": col_idx,
                                "endColumnIndex": col_idx + 1
                            }
                        ]
                    }
                },
                "targetAxis": target_axis,
                "colorStyle": BRAND_COLORS[color_key]
            })
            
        add_chart_request = {
            "addChart": {
                "chart": {
                    "spec": chart_spec,
                    "position": {
                        "overlayPosition": {
                            "anchorCell": {
                                "sheetId": sheet_id,
                                "rowIndex": 0,
                                "columnIndex": 3
                            }
                        }
                    }
                }
            }
        }
        
        res_chart = sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={"requests": [add_chart_request]}
        ).execute()
        
        chart_id = res_chart["replies"][0]["addChart"]["chart"]["chartId"]
        
        # 4. グラフをスライドに挿入
        PT_TO_EMU = 12700
        
        SLIDE_WIDTH = 9144000 / PT_TO_EMU   # approx 720 pt
        SLIDE_HEIGHT = 5143500 / PT_TO_EMU  # approx 405 pt
        
        w_emu = width * PT_TO_EMU if width is not None else SLIDE_WIDTH * 0.8 * PT_TO_EMU
        h_emu = height * PT_TO_EMU if height is not None else SLIDE_HEIGHT * 0.6 * PT_TO_EMU
        x_emu = x * PT_TO_EMU if x is not None else SLIDE_WIDTH * 0.1 * PT_TO_EMU
        y_emu = y * PT_TO_EMU if y is not None else SLIDE_HEIGHT * 0.2 * PT_TO_EMU

        insert_chart_request = {
            "createSheetsChart": {
                "spreadsheetId": spreadsheet_id,
                "chartId": chart_id,
                "linkingMode": "LINKED",
                "elementProperties": {
                    "pageObjectId": slide_id,
                    "size": {"width": {"magnitude": w_emu, "unit": "EMU"}, "height": {"magnitude": h_emu, "unit": "EMU"}},
                    "transform": {"scaleX": 1.0, "scaleY": 1.0, "translateX": x_emu, "translateY": y_emu, "unit": "EMU"}
                }
            }
        }
        
        slides_service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={"requests": [insert_chart_request]}
        ).execute()
        
        return {"status": "success", "sheetName": sheet_name, "chartId": chart_id}
    except Exception as e:
        return {"error": f"Error in add_sheets_chart_from_data: {str(e)}"}

def create_blank_slide(presentation_id: str, slide_id: str = None) -> dict:
    """
    新規の白紙スライドを追加します。
    
    Args:
        presentation_id (str): プレゼンテーションID。
        slide_id (str, optional): 作成するスライドのオブジェクトID。事前に確定させたIDでスライドを作成したい場合に指定します。
        
    Returns:
        dict: 作成結果（slideIdなど）。
    """
    service = get_slides_service()
    if not slide_id:
        slide_id = f"slide_{os.urandom(4).hex()}"
    requests = [
        {
            "createSlide": {
                "objectId": slide_id,
                "slideLayoutReference": {"predefinedLayout": "BLANK"}
            }
        }
    ]
    try:
        service.presentations().batchUpdate(
            presentationId=presentation_id, 
            body={"requests": requests}
        ).execute()
        return {"status": "success", "slideId": slide_id}
    except Exception as e:
        return {"error": str(e)}

def add_custom_text_box(
    presentation_id: str,
    slide_id: str,
    text: str,
    x: float,
    y: float,
    width: float,
    height: float,
    font_family: str = "Noto Sans JP",
    font_size: float = 14,
    color_hex: str = "#45474C",
    bold: bool = False
) -> dict:
    """
    指定した位置とサイズ（単位: PT）にテキストボックスを作成し、文字を入力します。
    """
    text = text.replace('\\n', '\n').replace('\n', '\n')
    
    service = get_slides_service()
    
    # もし slide_id が "p" の場合、最初のスライドIDを動的に解決
    if slide_id == "p":
        try:
            pres_info = service.presentations().get(presentationId=presentation_id).execute()
            slides = pres_info.get("slides", [])
            if slides:
                slide_id = slides[0]["objectId"]
        except Exception:
            pass
            
    obj_id = f"text_{os.urandom(4).hex()}"
    
    PT_TO_EMU = 12700
    
    hex_str = color_hex.lstrip('#')
    rgb = tuple(int(hex_str[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    
    requests = [
        {
            "createShape": {
                "objectId": obj_id,
                "shapeType": "TEXT_BOX",
                "elementProperties": {
                    "pageObjectId": slide_id,
                    "size": {
                        "width": {"magnitude": width * PT_TO_EMU, "unit": "EMU"},
                        "height": {"magnitude": height * PT_TO_EMU, "unit": "EMU"}
                    },
                    "transform": {
                        "scaleX": 1.0, "scaleY": 1.0,
                        "translateX": x * PT_TO_EMU,
                        "translateY": y * PT_TO_EMU,
                        "unit": "EMU"
                    }
                }
            }
        },
        {
            "insertText": {
                "objectId": obj_id,
                "text": text
            }
        },
        {
            "updateTextStyle": {
                "objectId": obj_id,
                "style": {
                    "fontFamily": font_family,
                    "fontSize": {"magnitude": font_size, "unit": "PT"},
                    "foregroundColor": {"opaqueColor": {"rgbColor": {"red": rgb[0], "green": rgb[1], "blue": rgb[2]}}},
                    "bold": bold
                },
                "textRange": {"type": "ALL"},
                "fields": "fontFamily,fontSize,foregroundColor,bold"
            }
        }
    ]
    
    try:
        service.presentations().batchUpdate(
            presentationId=presentation_id, 
            body={"requests": requests}
        ).execute()
        return {"status": "success", "elementId": obj_id}
    except Exception as e:
        return {"error": str(e)}

def add_custom_shape(
    presentation_id: str,
    slide_id: str,
    shape_type: str,
    x: float,
    y: float,
    width: float,
    height: float,
    fill_color_hex: str = "#030813",
    text: str = None,
    text_color_hex: str = None,
    outline_color_hex: str = None,
    outline_weight: float = 1.5,
    font_size: float = 14
) -> dict:
    """
    指定した位置とサイズ（単位: PT）に図形を作成し、色を適用します。
    """
    if shape_type == "ROUNDED_RECTANGLE":
        shape_type = "ROUND_RECTANGLE"
        
    service = get_slides_service()
    
    # もし slide_id が "p" の場合、最初のスライドIDを動的に解決
    if slide_id == "p":
        try:
            pres_info = service.presentations().get(presentationId=presentation_id).execute()
            slides = pres_info.get("slides", [])
            if slides:
                slide_id = slides[0]["objectId"]
        except Exception:
            pass
            
    obj_id = f"shape_{os.urandom(4).hex()}"
    
    PT_TO_EMU = 12700
    
    hex_str = fill_color_hex.lstrip('#')
    rgb = tuple(int(hex_str[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    
    outline_properties = {
        "propertyState": "NOT_RENDERED"
    }
    if outline_color_hex:
        out_hex = outline_color_hex.lstrip('#')
        out_rgb = tuple(int(out_hex[i:i+2], 16) / 255.0 for i in (0, 2, 4))
        outline_properties = {
            "outlineFill": {
                "solidFill": {
                    "color": {"rgbColor": {"red": out_rgb[0], "green": out_rgb[1], "blue": out_rgb[2]}},
                    "alpha": 1.0
                }
            },
            "weight": {"magnitude": int(outline_weight * PT_TO_EMU), "unit": "EMU"},
            "propertyState": "RENDERED"
        }
    else:
        outline_properties = {
            "propertyState": "NOT_RENDERED"
        }
        
    requests = [
        {
            "createShape": {
                "objectId": obj_id,
                "shapeType": shape_type,
                "elementProperties": {
                    "pageObjectId": slide_id,
                    "size": {
                        "width": {"magnitude": int(width * PT_TO_EMU), "unit": "EMU"},
                        "height": {"magnitude": int(height * PT_TO_EMU), "unit": "EMU"}
                    },
                    "transform": {
                        "scaleX": 1.0, "scaleY": 1.0,
                        "translateX": int(x * PT_TO_EMU),
                        "translateY": int(y * PT_TO_EMU),
                        "unit": "EMU"
                    }
                }
            }
        },
        {
            "updateShapeProperties": {
                "objectId": obj_id,
                "shapeProperties": {
                    "shapeBackgroundFill": {
                        "solidFill": {
                            "color": {"rgbColor": {"red": rgb[0], "green": rgb[1], "blue": rgb[2]}},
                            "alpha": 1.0
                        },
                        "propertyState": "RENDERED"
                    },
                    "outline": outline_properties,
                    "contentAlignment": "MIDDLE"
                },
                "fields": "shapeBackgroundFill.solidFill.color,shapeBackgroundFill.solidFill.alpha,shapeBackgroundFill.propertyState,outline,contentAlignment"
            }
        }
    ]
    
    if text:
        requests.append({
            "insertText": {
                "objectId": obj_id,
                "text": text
            }
        })
        
        tc = text_color_hex
        if not tc:
            tc = "#202124" if fill_color_hex.upper() in ["#FFFFFF", "#FFF", "#F2F4F6"] else "#FFFFFF"
            
        tc_str = tc.lstrip('#')
        tc_rgb = tuple(int(tc_str[i:i+2], 16) / 255.0 for i in (0, 2, 4))
        
        requests.append({
            "updateTextStyle": {
                "objectId": obj_id,
                "style": {
                    "fontFamily": "Noto Sans JP",
                    "fontSize": {"magnitude": font_size, "unit": "PT"},
                    "bold": True,
                    "foregroundColor": {"opaqueColor": {"rgbColor": {"red": tc_rgb[0], "green": tc_rgb[1], "blue": tc_rgb[2]}}}
                },
                "fields": "fontFamily,fontSize,bold,foregroundColor"
            }
        })
        
        requests.append({
            "updateParagraphStyle": {
                "objectId": obj_id,
                "style": {
                    "alignment": "CENTER"
                },
                "fields": "alignment"
            }
        })
        
    try:
        service.presentations().batchUpdate(
            presentationId=presentation_id, 
            body={"requests": requests}
        ).execute()
        return {"status": "success", "elementId": obj_id}
    except Exception as e:
        return {"error": str(e)}

def get_slide_content(presentation_id: str, slide_id: str) -> dict:
    """
    指定したスライドの要素一覧（ID、テキスト、位置等）を取得します。
    """
    service = get_slides_service()
    try:
        page = service.presentations().pages().get(
            presentationId=presentation_id,
            pageObjectId=slide_id
        ).execute()
        
        elements = page.get("pageElements", [])
        result = []
        
        for el in elements:
            el_info = {
                "objectId": el.get("objectId"),
                "type": el.get("shape", {}).get("shapeType") if "shape" in el else "OTHER",
                "x": el.get("transform", {}).get("translateX", 0) / 12700,
                "y": el.get("transform", {}).get("translateY", 0) / 12700,
                "width": el.get("size", {}).get("width", {}).get("magnitude", 0) / 12700,
                "height": el.get("size", {}).get("height", {}).get("magnitude", 0) / 12700,
            }
            
            if "shape" in el and "text" in el["shape"]:
                text_elements = el["shape"]["text"].get("textElements", [])
                full_text = "".join([te.get("textRun", {}).get("content", "") for te in text_elements])
                el_info["text"] = full_text.strip()
                
            result.append(el_info)
            
        return {"status": "success", "elements": result}
    except Exception as e:
        return {"error": str(e)}

def update_text_element(presentation_id: str, element_id: str, text: str) -> dict:
    """
    特定のテキストボックスの文字を書き換えます。既存のテキストは削除されます。
    """
    service = get_slides_service()
    text = text.replace('\\n', '\n')
    
    requests = [
        {
            "deleteText": {
                "objectId": element_id,
                "textRange": {"type": "ALL"}
            }
        },
        {
            "insertText": {
                "objectId": element_id,
                "text": text,
                "insertionIndex": 0
            }
        }
    ]
    
    try:
        service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={"requests": requests}
        ).execute()
        return {"status": "success"}
    except Exception as e:
        return {"error": str(e)}

def update_element_transform(
    presentation_id: str,
    element_id: str,
    x: float = None,
    y: float = None
) -> dict:
    """
    特定の要素の位置（X, Y）を移動します。単位は PT です。
    """
    service = get_slides_service()
    PT_TO_EMU = 12700
    
    transform = {
        "scaleX": 1.0,
        "scaleY": 1.0,
        "shearX": 0.0,
        "shearY": 0.0,
        "unit": "EMU"
    }
    
    if x is not None:
        transform["translateX"] = x * PT_TO_EMU
    if y is not None:
        transform["translateY"] = y * PT_TO_EMU
        
    requests = [
        {
            "updatePageElementTransform": {
                "objectId": element_id,
                "transform": transform,
                "applyMode": "ABSOLUTE"
            }
        }
    ]
    
    try:
        service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={"requests": requests}
        ).execute()
        return {"status": "success"}
    except Exception as e:
        return {"error": str(e)}

def delete_slide_element(presentation_id: str, element_id: str) -> dict:
    """
    特定の要素（テキストボックス、図形、グラフなど）を削除します。
    """
    service = get_slides_service()
    requests = [
        {
            "deleteObject": {
                "objectId": element_id
            }
        }
    ]
    try:
        service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={"requests": requests}
        ).execute()
        return {"status": "success"}
    except Exception as e:
        return {"error": str(e)}


def export_slide_to_png(
    presentation_id: str,
    slide_id: str,
    output_png_path: str
) -> dict:
    """
    Google Slides API を用いて、特定のスライドページをPNG画像としてエクスポートし、ローカルに保存します。
    
    Args:
        presentation_id (str): プレゼンテーションID。
        slide_id (str): スライドID。
        output_png_path (str): 出力先のPNG画像ファイルパス（絶対パス）。
        
    Returns:
        dict: 実行結果。
    """
    import requests
    import os
    service = get_slides_service()
    try:
        thumbnail = service.presentations().pages().getThumbnail(
            presentationId=presentation_id,
            pageObjectId=slide_id
        ).execute()
        
        content_url = thumbnail.get("contentUrl")
        if not content_url:
            return {"error": "Could not retrieve thumbnail URL"}
            
        response = requests.get(content_url)
        if response.status_code != 200:
            return {"error": f"Failed to download image from URL: {response.status_code}"}
            
        # 親ディレクトリを作成
        os.makedirs(os.path.dirname(output_png_path), exist_ok=True)
        
        with open(output_png_path, "wb") as f:
            f.write(response.content)
            
        return {"status": "success", "output_path": output_png_path}
    except Exception as e:
        return {"error": str(e)}
