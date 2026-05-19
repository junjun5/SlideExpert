import asyncio
import os
import sys
import json
from dotenv import load_dotenv

# 1. SlideExpert プロジェクトのルートディレクトリ
project_root = "/Users/junhattori/Code/agentBox/SlideExpert"
sys.path.append(project_root)

# 2. .env のロード
load_dotenv(os.path.join(project_root, "slide_app", ".env"))

# 3. ADK runner とエージェントのインポート
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from slide_app.agent import root_agent

async def run_behavior_test():
    print("🚀 【実機検証】AIエージェント『サウナの入り方』一括ツールコール出力テストを開始します...")
    
    session_service = InMemorySessionService()
    session = await session_service.create_session(user_id="test_user", app_name="slide_app")
    runner = Runner(agent=root_agent, session_service=session_service, app_name="slide_app")
    
    prompt = "サウナの入り方を説明するスライドを作って、初心者がプロのサウナーになるためのロードマップをガントチャートで説明するスライドも作って欲しい"
    
    print(f"💬 [TURN 1] プロンプト送信: '{prompt}'")
    
    # TURN 1: 構成案の受信
    async for event in runner.run_async(
        new_message=types.Content(role="user", parts=[types.Part.from_text(text=prompt)]),
        user_id="test_user",
        session_id=session.id
    ):
        if hasattr(event, "content") and event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    print(part.text, end="", flush=True)
                    
    print("\n\n✅ [TURN 1 完了] 構成案を受信しました。自動承認（Yes）を送信します...")
    
    captured_tool_calls = []
    
    # 最大3回、ツールコールが検出されるまでターンを継続します (最大合計4ターン)
    next_message = "Yes"
    next_message = "Yes"
    print(f"\n💬 [TURN 2] '{next_message}' を送信します...")
    
    async for event in runner.run_async(
        new_message=types.Content(role="user", parts=[types.Part.from_text(text=next_message)]),
        user_id="test_user",
        session_id=session.id
    ):
        # ツールコールのキャプチャ
        if hasattr(event, "content") and event.content and event.content.parts:
            for part in event.content.parts:
                if part.function_call:
                    fc = part.function_call
                    captured_tool_calls.append({
                        "name": fc.name,
                        "args": fc.args
                    })
                    print(f"🛠️ [TOOL CALL] {fc.name} called with args: {fc.args}")
                    
        # テキスト出力の表示
        if hasattr(event, "content") and event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    print(part.text, end="", flush=True)
 
    print("\n✅ [TURN 2 完了] 自律ツールコールチェーンの実行が完了しました。")
 
    print("\n\n--- 📊 【検証レポート：ツールコール解析結果】 ---")
    if not captured_tool_calls:
        print("❌ エージェントは一括ツールコールを呼び出しませんでした。")
        return
        
    print(f"合計ツールコール数: {len(captured_tool_calls)}")
    
    slide_creation_ids = []
    chart_slide_id = None
    shapes = []
    text_boxes = []
    batch_updates = []
    
    for call in captured_tool_calls:
        name = call["name"]
        args = call["args"]
        
        if name == "create_blank_slide":
            slide_id = args.get("slide_id")
            if slide_id:
                slide_creation_ids.append(slide_id)
                
        elif name == "add_sheets_chart_from_data":
            chart_slide_id = args.get("slide_id")
            
        elif name == "add_custom_shape":
            shapes.append(args)
            
        elif name == "add_custom_text_box":
            text_boxes.append(args)
            
        elif name == "execute_batch_update":
            batch_updates.append(args)
 
    print(f"1. 作成されたカスタムスライドID: {slide_creation_ids}")
    print(f"2. グラフの挿入先スライドID: {chart_slide_id}")
    
    # 表紙スライドの誤挿入チェック
    if chart_slide_id == "first_custom_slide_001":
        print("❌ [ERROR] 表紙スライド（1枚目）にグラフが挿入されています！ (バグ再発)")
    elif chart_slide_id in slide_creation_ids:
        print(f"✅ [SUCCESS] グラフは新規作成されたスライド '{chart_slide_id}' に正しくマッピングされています！")
    else:
        print(f"⚠️ [WARNING] グラフの挿入先 '{chart_slide_id}' がスライドIDリストに見当たりません。")
 
    # 2. 完璧なアサーション（一括並行個別ツールコールおよび batchUpdate の双方に対応）
    pentagon_found = False
    chevron_count = 0
    embedded_texts_found = []
    three_col_text_boxes = []
    
    # A. 個別ツールコールの履歴（shapes, text_boxes）からスキャン
    for s in shapes:
        st = s.get("shape_type")
        s_id = s.get("slide_id", "")
        
        if st == "CHEVRON" or "arrow" in s.get("elementId", "").lower():
            chevron_count += 1
            # 図形に直接埋め込まれたテキストがあるかチェック
            if s.get("text"):
                embedded_texts_found.append((s_id, s.get("text")))
                print(f"✅ [FOUND EMBEDDED TEXT ACTION] Shape text: '{s.get('text')}'")
        elif st == "PENTAGON":
            pentagon_found = True
            print("❌ [ERROR] PENTAGON が検出されました。CHEVRON に統一されている必要があります！")
            
    for tb in text_boxes:
        x = tb.get("x", 0)
        y = tb.get("y", 0)
        slide_id = tb.get("slide_id", "")
        text = tb.get("text", "")
        
        # サウナ手順スライド（slide_page_3 または slide_process）の箇条書きテキスト
        if ("page_3" in slide_id or "process" in slide_id) and (170 <= y <= 210):
            three_col_text_boxes.append((x, y, text))
            print(f"📝 [FOUND COL TEXTBOX] at X: {x}pt, Y: {y}pt -> {text.splitlines()[0] if text else ''}")

    # B. 従来の execute_batch_update が呼ばれた場合のバックアップ解析
    for bu in batch_updates:
        requests_str = bu.get("requests_json", "[]")
        try:
            clean_json_str = requests_str.strip()
            requests = json.loads(clean_json_str)
            
            for r in requests:
                if "createShape" in r:
                    cs = r["createShape"]
                    st = cs.get("shapeType")
                    obj_id = cs.get("objectId", "")
                    
                    if st == "CHEVRON" or "arrow" in obj_id.lower():
                        chevron_count += 1
                    elif st == "PENTAGON":
                        pentagon_found = True
                        
                    if st in ["TEXT_BOX", "RECTANGLE"] and ("desc" in obj_id.lower() or "step" in obj_id.lower() and "arrow" not in obj_id.lower()):
                        transform = cs.get("elementProperties", {}).get("transform", {})
                        x = transform.get("translateX", 0)
                        y = transform.get("translateY", 0)
                        if 170 <= y <= 210:
                            three_col_text_boxes.append((x, y, obj_id))

                if "insertText" in r:
                    it = r["insertText"]
                    obj_id = it.get("objectId", "")
                    text = it.get("text", "")
                    
                    if "arrow" in obj_id.lower():
                        embedded_texts_found.append((obj_id, text))
                        
        except Exception as e:
            print(f"⚠️ batchUpdateの解析中にエラーが発生しました: {e}")
  
    print(f"\n--- 🔔 【アサーション判定結果】 ---")
    
    # 判定1: PENTAGONの完全廃止とCHEVRONの統一
    if pentagon_found:
        print("❌ [FAIL] PENTAGON（五角形）がまだ残っています。")
    elif chevron_count >= 3:
        print(f"✅ [SUCCESS] 水平プロセスで形状が完璧に {chevron_count}個 の CHEVRON で統一されています！")
    else:
        print(f"❌ [FAIL] CHEVRON の描画数 ({chevron_count}個) が足りません。")

    # 判定2: テキストの直接埋め込み
    if len(embedded_texts_found) >= 3:
        print(f"✅ [SUCCESS] 矢印テキストが {len(embedded_texts_found)}個 の CHEVRON 図形オブジェクトの中に直接テキスト埋め込みされています！")
    else:
        print("❌ [FAIL] 図形内への直接テキスト埋め込みアクション数が足りません。")

    # 判定3: 箇条書き説明テキストボックスの 3列独立配置
    print(f"検出された3列分離テキストボックス数: {len(three_col_text_boxes)}")
    if len(three_col_text_boxes) >= 3:
        print("✅ [SUCCESS] 各ステップの詳細説明が、3列の独立したテキストボックスに美しく分離されて配置されています！")
    else:
        print("❌ [FAIL] 各ステップの詳細説明が3列に独立した個別テキストボックスとして作成されていません。")

    # === スライドの画像自動エクスポート処理 ===
    print("\n📸 生成されたスライドのPNG画像をローカルにダウンロード中...")
    from slide_app.tools import export_slide_to_png
    
    # プレゼンテーションIDの取得 (ツールコールから取得)
    pres_id = None
    for call in captured_tool_calls:
        if "presentation_id" in call["args"]:
            pres_id = call["args"]["presentation_id"]
            break
            
    if pres_id:
        # Google Slides API を使用して、プレゼンテーション内の実際のスライドIDリストを順番に取得
        from slide_app.tools import get_slides_service
        slides_service = get_slides_service()
        try:
            presentation = slides_service.presentations().get(presentationId=pres_id).execute()
            actual_slides = presentation.get("slides", [])
            actual_slide_ids = [s["objectId"] for s in actual_slides]
            print(f"🔍 プレゼンテーション内の実際のスライド順序: {actual_slide_ids}")
            
            # 古いスライド画像（PNG）を完全にクリーンアップ
            import glob
            old_images = glob.glob("/Users/junhattori/Code/agentBox/SlideExpert/slide_images/*.png")
            for old_img in old_images:
                try:
                    os.remove(old_img)
                except Exception:
                    pass
                    
            for idx, s_id in enumerate(actual_slide_ids, 1):
                out_path = f"/Users/junhattori/Code/agentBox/SlideExpert/slide_images/slide_{idx}.png"
                print(f" -> スライド {idx} をエクスポート中 (ID: {s_id})...")
                res = export_slide_to_png(presentation_id=pres_id, slide_id=s_id, output_png_path=out_path)
                if "error" in res:
                    print(f"    ⚠️ エクスポート失敗: {res['error']}")
                else:
                    print(f"    ✅ 保存成功: {out_path}")
        except Exception as e:
            print(f"⚠️ スライド一覧の取得中にエラーが発生しました: {e}")

    print("\n🎉 実機検証完了。ログおよびレポートをご確認ください。")

if __name__ == "__main__":
    asyncio.run(run_behavior_test())

