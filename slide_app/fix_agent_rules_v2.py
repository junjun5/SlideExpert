import re

def patch_agent():
    file_path = "/Users/junhattori/Code/agentBox/SlideExpert/slide_app/agent.py"
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    target = """3. **【最重要・超厳禁】自動調整・再描画時の枠線消失 ＆ 角丸破壊の禁止**:
    - スライドの描画完了後に、AIが図形の形状調整（再描画）を行う工程がある場合、**絶対に枠線の無い単純な四角形（RECTANGLE）で上書き描画をしてはなりません（厳禁）。**
    - 最初の描画時に大判カード（ROUNDED_RECTANGLE）へ赤枠（`#F28B82`）や青枠（`#8AB4F8`）などの美しい枠線（`outline_color_hex`, `outline_weight`）を指定した場合、再描画を行う際も、**必ず最初の形状（ROUNDED_RECTANGLE）と枠線カラー・太さを100%そのまま維持して**呼び出しを行ってください。
    - 枠線パラメータを省略したり、単純な `RECTANGLE` に退化させて上書きすることは【絶対厳禁】です。これを行うと、せっかく描画した枠線が完全に消滅してしまいます。"""

    replacement = """3. **【最重要・超厳禁】背景オブジェクトの二重描画・最終微調整ターンでの上書き重ね描きの完全永久禁止**:
    - スライド内の「背景オブジェクト」（大判角丸座布団カード、タイムラインの縦線や丸いノード、グラフやチャートの枠など、背後に敷くすべての図形オブジェクト）は、**スライド作成の最初（第1ターン・第1パス）のタイミングで1回だけ描画しなければならず、その後のどんな「最終調整」「微調整」「再描画」の工程であっても、同じ座標に対して再度 `add_custom_shape` などを呼び出して上書き描画・再作成することは【絶対厳禁】です。**
    - 後からの微調整ターンで背景オブジェクトを追加描画すると、Google Slides API の仕様上、それらが文字やテキストボックスの「前面」に配置されてしまい、文字や枠線が完全に塗りつぶされて見えなくなる重大なバグ（ビジュアル破壊）が発生します。
    - 最終調整のターンで呼び出してよいのは、**「テキストボックスの位置微調整（`add_custom_text_box`）」のみ**であり、背景の図形オブジェクトを重ね描きすることは、いかなる理由があっても絶対に許されません。最初の美しい枠線（`outline_color_hex`や`outline_weight`）を持ったカード群をそのまま維持・残存させてください。"""

    if target in content:
        new_content = content.replace(target, replacement)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print("✅ agent.py のルール3を完璧にアップグレードしました！")
    else:
        # インデントなどが少しずれている場合を考慮して、より柔軟にマッチング
        normalized_target = target.replace("\r\n", "\n").strip()
        normalized_content = content.replace("\r\n", "\n")
        # 一部のフレーズで部分置換を試みる
        if "【最重要・超厳禁】自動調整・再描画時の枠線消失" in normalized_content:
            # 単純にルール3の文字列ブロックを検出して置換
            pattern = r"3\.\s+\*\*【最重要・超厳禁】自動調整・再描画時の枠線消失.*?(?=4\.\s+\*\*ブランド固有固有名詞)"
            match = re.search(pattern, normalized_content, re.DOTALL)
            if match:
                new_content = normalized_content[:match.start()] + replacement + "\n" + normalized_content[match.end():]
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                print("✅ 正則表現マッチにより、agent.py のルール3を完璧にアップグレードしました！")
            else:
                print("❌ ルール3のパターンマッチに失敗しました。")
        else:
            print("❌ ターゲットテキストが見つかりませんでした。")

if __name__ == "__main__":
    patch_agent()
