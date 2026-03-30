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
# Helper: Get Slides Service
# =============================================================================

def get_slides_service():
    """Returns an authorized Google Slides API service."""
    scopes = [
        "https://www.googleapis.com/auth/presentations",
        "https://www.googleapis.com/auth/drive"
    ]
    credentials, _ = google.auth.default(scopes=scopes)
    return build("slides", "v1", credentials=credentials)

def get_drive_service():
    """Returns an authorized Google Drive API service."""
    scopes = [
        "https://www.googleapis.com/auth/drive"
    ]
    credentials, _ = google.auth.default(scopes=scopes)
    return build("drive", "v3", credentials=credentials)

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
    slides_service = get_slides_service()
    drive_service = get_drive_service()
    
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

        file = drive_service.files().create(
            body=body,
            supportsAllDrives=True, # Required for Shared Drives
            fields="id"
        ).execute()
        
        presentation_id = file.get("id")
        
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
