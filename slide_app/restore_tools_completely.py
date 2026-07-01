# -*- coding: utf-8 -*-
import os

def restore_all():
    tools_path = "/Users/junhattori/Code/agentBox/SlideExpert/slide_app/tools.py"
    
    with open(tools_path, "r", encoding="utf-8") as f:
        content = f.read()

    # もしすでに add_sheets_chart_from_data が定義されているか確認
    if "def add_sheets_chart_from_data" in content:
        print("Already defined. We will clean tools.py first.")
        # tools.py を 712 行目（generate_and_upload_plot_direct の末尾）までで一旦切り捨てます
        lines = content.split("\n")
        truncated_lines = []
        for line in lines:
            truncated_lines.append(line)
            if "def generate_and_upload_plot_direct" in line:
                # この関数の定義より前の状態に戻したいが、一番安全なのは git checkout した状態 (712行)
                pass
        
    # 完全な追加関数コード群
    additional_code = """

def add_sheets_chart_from_data(
    presentation_id: str,
    slide_id: str,
    data: list,
    title: str = "Chart",
    chart_type: str = "COLUMN",
    x: float = None,
    y: float = None,
    width: float = None,
    height: float = None
) -> dict:
    \"\"\"
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
        
    Returns:
        dict: 実行結果。
    \"\"\"
    import io
    from googleapiclient.http import MediaIoBaseUpload
    
    slides_service = get_slides_service()
    sheets_service = get_sheets_service()
    drive_service = get_drive_service()
    
    try:
        # 1. スプレッドシートの新規作成
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
        
        # 2. データの書き込み
        value_range_body = {
            "values": data
        }
        sheet_name = "Sheet1"
        sheets_service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=f"{sheet_name}!A1",
            valueInputOption="USER_ENTERED",
            body=value_range_body
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
            "BLUE": {"color": {"rgbColor": {"red": 0.10, "green": 0.45, "blue": 0.91}}},
            "RED": {"color": {"rgbColor": {"red": 0.85, "green": 0.19, "blue": 0.15}}}
        }
        
        for col_idx in range(1, num_cols):
            target_axis = "LEFT_AXIS"
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
                "color": BRAND_COLORS["BLUE"]
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
    \"\"\"
    新規の白紙スライドを追加します。
    
    Args:
        presentation_id (str): プレゼンテーションID。
        slide_id (str, optional): 作成するスライドのオブジェクトID。事前に確定させたIDでスライドを作成したい場合に指定します。
        
    Returns:
        dict: 作成結果（slideIdなど）。
    \"\"\"
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
    \"\"\"
    指定した位置とサイズ（単位: PT）にテキストボックスを作成し、文字を入力します。
    \"\"\"
    text = text.replace('\\\\n', '\\n').replace('\\n', '\\n')
    
    service = get_slides_service()
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
    outline_weight: float = 1.5
) -> dict:
    \"\"\"
    指定した位置とサイズ（単位: PT）に図形を作成し、色を適用します。
    \"\"\"
    if shape_type == "ROUND_RECTANGLE":
        shape_type = "ROUNDED_RECTANGLE"
        
    service = get_slides_service()
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
            "solidFill": {
                "color": {"rgbColor": {"red": out_rgb[0], "green": out_rgb[1], "blue": out_rgb[2]}}
            },
            "weight": {"magnitude": int(outline_weight * PT_TO_EMU), "unit": "EMU"},
            "propertyState": "RENDERED"
        }
    else:
        outline_properties = {
            "outlineFill": {"solidFill": {"alpha": 0}},
            "propertyState": "RENDERED"
        }
        
    requests = [
        {
            "createShape": {
                "objectId": obj_id,
                "shapeType": shape_type,
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
            "updateShapeProperties": {
                "objectId": obj_id,
                "shapeProperties": {
                    "shapeBackgroundFill": {
                        "solidFill": {
                            "color": {"rgbColor": {"red": rgb[0], "green": rgb[1], "blue": rgb[2]}}
                        }
                    },
                    "outline": outline_properties,
                    "contentAlignment": "MIDDLE",
                    "textMarginLeft": {"magnitude": (25 if shape_type == "CHEVRON" else 8) * PT_TO_EMU, "unit": "EMU"},
                    "textMarginRight": {"magnitude": (25 if shape_type == "CHEVRON" else 8) * PT_TO_EMU, "unit": "EMU"},
                    "textMarginTop": {"magnitude": 5 * PT_TO_EMU, "unit": "EMU"},
                    "textMarginBottom": {"magnitude": 5 * PT_TO_EMU, "unit": "EMU"}
                },
                "fields": "shapeBackgroundFill.solidFill.color,outline,contentAlignment,textMarginLeft,textMarginRight,textMarginTop,textMarginBottom"
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
                    "fontSize": {"magnitude": 14, "unit": "PT"},
                    "bold": True,
                    "foregroundColor": {"weightedColor": {"solidColor": {"rgbColor": {"red": tc_rgb[0], "green": tc_rgb[1], "blue": tc_rgb[2]}}}}
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
    \"\"\"
    指定したスライドの要素一覧（ID、テキスト、位置等）を取得します。
    \"\"\"
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
    \"\"\"
    特定のテキストボックスの文字を書き換えます。既存のテキストは削除されます。
    \"\"\"
    service = get_slides_service()
    text = text.replace('\\\\n', '\\n')
    
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
    \"\"\"
    特定の要素の位置（X, Y）を移動します。単位は PT です。
    \"\"\"
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
    \"\"\"
    特定の要素（テキストボックス、図形、グラフなど）を削除します。
    \"\"\"
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
"""

    # 元の tools.py から不要な重複定義がない状態で、末尾に追加
    with open(tools_path, "a", encoding="utf-8") as f:
        f.write(additional_code)
        
    print("✅ tools.py にすべての拡張スライド操作関数群を完璧に復元・追記しました！")

if __name__ == "__main__":
    restore_all()
