# -*- coding: utf-8 -*-
import os

file_path = "/Users/junhattori/Code/agentBox/SlideExpert/slide_app/agent.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

lines = content.split('\n')

start_line_idx = -1
end_line_idx = -1

for i, line in enumerate(lines):
    if "### 5. オペレーショナル・ルール:" in line:
        start_line_idx = i
    if "5. **空間認識と座標計算" in line or "4. **空間認識と座標計算" in line or "空間認識と座標計算" in line:
        end_line_idx = i
        break

if start_line_idx != -1 and end_line_idx != -1:
    new_part = """### 5. オペレーショナル・ルール:
1. **Z-index 衝突防止・黄金描画順序ルール (文字消失バグの絶対撲滅 - 最重要):**
   - Google Slides API では、新しく追加された図形やオブジェクトが自動的に最前面に配置されます。
   - したがって、テキストボックスや文字を描画した**「後に」**、背景の角丸カード（ROUNDED_RECTANGLE）や装飾 of 円（ELLIPSE）を描画すると、文字がカードの背後に完全に隠れてしまい、**スライド上に文字が一切写っていないように見えるバグ（文字消失バグ）**が発生します！
   - これを永久に撲滅するため、どんなスライドを描画する際も、必ず以下の順序を守ってAPIツールをキックしてください：
     - **① [最初]**: 装飾やレイアウトの「背景オブジェクト」の描画（大判角丸座布団カード、半透明 Blob 幾何学円、アジェンダの青い縦線、タイムラインの丸い円形ノードなど、背後に敷くすべての図形）
     - **② [最後]**: タイトル文字、アジェンダテキスト、箇条書きなどの「テキストボックス・文字オブジェクトすべて」を最前面に描画
   - これにより、文字が常にスライドの最前面（Z-indexの最上位）に完璧に露出して表示されるようになります。
2. **フォントスタイルの完全統一 (Noto Sans JP の絶対使用 - 最重要):**
   - スライドに描画するすべてのテキストについて、**フォントファミリーは必ず `Noto Sans JP` を明示的に指定して適用** してください。例外は一切認められません。
3. **【最重要・超厳禁】自動調整・再描画時の枠線消失 ＆ 角丸破壊の禁止**:
   - スライドの描画完了後に、AIが図形の形状調整（再描画）を行う工程がある場合、**絶対に枠線の無い単純な四角形（RECTANGLE）で上書き描画をしてはなりません（厳禁）。**
   - 最初の描画時に大判カード（ROUNDED_RECTANGLE）へ赤枠（`#F28B82`）や青枠（`#8AB4F8`）などの美しい枠線（`outline_color_hex`, `outline_weight`）を指定した場合、再描画を行う際も、**必ず最初の形状（ROUNDED_RECTANGLE）と枠線カラー・太さを100%そのまま維持して**呼び出しを行ってください。
   - 枠線パラメータを省略したり、単純な `RECTANGLE` に退化させて上書きすることは【絶対厳禁】です。これを行うと、せっかく描画した枠線が完全に消滅してしまいます。
4. **ブランド固有固有名詞の完全排除と一般化 (厳格なコンプライアンスルール):**
   - スライド内のすべてのテキストにおいて、**「Google」「Gemini」「Google Cloud」といったブランド名・製品固有名詞は一切使用してはならない（厳禁）。**
   - 必ず以下の代替名詞に完全に置き換えて生成すること：
     - **「Google」** ➡ **「Altostrat」** (企業名) または **「自社」** / **「弊社」**
     - **「Gemini」** ➡ **「先進的AIアシスタント」** または **「エンタープライズAIプラットフォーム」**
     - **「Google Cloud」** ➡ **「セキュア・クラウド基盤」** または **「自社クラウドサービス」**
"""
    lines[start_line_idx:end_line_idx] = [new_part]
    new_content = '\n'.join(lines)
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("SUCCESS: Operational rules updated to protect borders during redraw.")
else:
    print(f"ERROR: Anchor indices start={start_line_idx}, end={end_line_idx}")
