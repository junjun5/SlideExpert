import re

def patch_agent():
    file_path = "/Users/junhattori/Code/agentBox/SlideExpert/slide_app/agent.py"
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 既存のブランド名排除ルールの直後に追記するターゲットを定義
    target = """4. **ブランド固有固有名詞の完全排除と一般化 (厳格なコンプライアンスルール):**
   - スライド内のすべてのテキストにおいて、**「Google」「Gemini」「Google Cloud」といったブランド名・製品固有名詞は一切使用してはならない（厳禁）。**
   - 必ず以下の代替名詞に完全に置き換えて生成すること：
     - **「Google」** ➡ **「Altostrat」** (企業名) または **「自社」** / **「弊社」**
     - **「Gemini」** ➡ **「先進的AIアシスタント」** または **「エンタープライズAIプラットフォーム」**
     - **「Google Cloud」** ➡ **「セキュア・クラウド基盤」** または **「自社クラウドサービス」**"""

    replacement = """4. **ブランド固有固有名詞の完全排除と一般化 (厳格なコンプライアンスルール):**
   - スライド内のすべてのテキストにおいて、**「Google」「Gemini」「Google Cloud」といったブランド名・製品固有名詞は一切使用してはならない（厳禁）。**
   - 必ず以下の代替名詞に完全に置き換えて生成すること：
     - **「Google」** ➡ **「Altostrat」** (企業名) または **「自社」** / **「弊社」**
     - **「Gemini」** ➡ **「先進的AIアシスタント」** または **「エンタープライズAIプラットフォーム」**
     - **「Google Cloud」** ➡ **「セキュア・クラウド基盤」** または **「自社クラウドサービス」**

5. **【超厳格】エラー絶対撲滅・一発必中・定数指定ルール (リプレイによるビジュアルダウングレード防止):**
   - スライドIDの指定に余計な文字列（例: `slide_page_5 Jungle` のようなミス）を1ミリも混入させないこと。
   - 角丸四角形を描画する際の `shape_type` は必ず **`ROUNDED_RECTANGLE`** を、円形を描画する際は必ず **`ELLIPSE`** を指定すること。`ROUND_RECT` や `CIRCLE` などの不正な省略形・名詞はAPIエラーになり、ADKの自動エラーリトライが走り、カードの枠線や背景色が剥ぎ取られて RECTANGLE にダウングレードされる最悪のバグを引き起こします。絶対に一発必中で正しい定数名を指定してください。

6. **【超厳格】グラフ挿入時の左右2カラム黄金レイアウトルール (グラフ被りバグの絶対撲滅):**
   - スプレッドシートからグラフを挿入する `add_sheets_chart_from_data` を呼び出す際は、**絶対に座標引数を省略してはなりません（厳禁）。**
   - グラフと右側説明文が衝突するのを物理的に防ぐため、必ず以下の「左右2カラム黄金比」の数値パラメータを明示的に渡して呼び出してください：
     - グラフ（左側カラム）: `x`=**`40`**, `y`=**`95`**, `width`=**`380`**, `height`=**`270`**
     - 説明カード（右側カラム）: `x`=**`440`**, `y`=**`95`**, `width`=**`240`**, `height`=**`270`**
     - 説明タイトル（右側テキスト）: `x`=**`460`**, `y`=**`115`**, `width`=**`200`**, `height`=**`30`**
     - 説明本文（右側テキスト）: `x`=**`460`**, `y`=**`150`**, `width`=**`200`**, `height`=**`200`**"""

    normalized_target = target.replace("\r\n", "\n").strip()
    normalized_content = content.replace("\r\n", "\n")

    if normalized_target in normalized_content:
        new_content = normalized_content.replace(normalized_target, replacement)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print("✅ agent.py のシステムプロンプトに、エラー絶滅 ＆ グラフ左右カラム黄金ルールを完璧に焼き付けました！")
    else:
        # より柔軟なパターンマッチで置換
        pattern = r"4\.\s+\*\*ブランド固有固有名詞の完全排除と一般化.*?(?=4\.\s+\*\*空間認識と座標計算)"
        match = re.search(pattern, normalized_content, re.DOTALL)
        if match:
            new_content = normalized_content[:match.start()] + replacement + "\n\n" + normalized_content[match.end():]
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            print("✅ 正則表現マッチにより、agent.py にエラー絶滅 ＆ グラフ左右カラム黄金ルールを焼き付けました！")
        else:
            print("❌ ルールの追記ターゲットの検出に失敗しました。")

if __name__ == "__main__":
    patch_agent()
