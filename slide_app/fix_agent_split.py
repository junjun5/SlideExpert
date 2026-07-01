# -*- coding: utf-8 -*-
import os

file_path = "/Users/junhattori/Code/agentBox/SlideExpert/slide_app/agent.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

lines = content.split('\n')

start_line_idx = -1
end_line_idx = -1

for i, line in enumerate(lines):
    if "3) **左右2カラム対比" in line:
        start_line_idx = i
    if "4) **統計数値・テーブル" in line:
        end_line_idx = i
        break

if start_line_idx != -1 and end_line_idx != -1:
    # 該当の範囲を新しいプロンプトに差し替える
    new_part = """       3) **左右2カラム対比 (Split 2-Column / 課題対比)**:
          - 初心者の課題と解決策など、左右に2つの大判カードを配するレイアウトです。
          - **【重要】スライドヘッダータイトル（大見出し）の絶対描画**:
            - 本スライドの左上には、必ずスライド全体のタイトル（見出しテキスト）として、**X = `40pt`, Y = `40pt`, 幅 = `640pt`, 高さ = `45pt`** のテキストボックスを `add_custom_text_box` で真っ先に作成してください（フォント: Noto Sans JP, 24px, Bold, 文字色: Charcoal `#202124`、例: 「現状の課題と科学的解決策」）。
          - **インサイドマージンの絶対義務化と重複描画の完全禁止 (最重要)**:
            - **【重複描画の厳重禁止】**: すでに `add_custom_shape` や `add_custom_text_box` などの個別ツールで描画した背景カードやテキストの上から、**後日やバッチアップデート（execute_batch_update）で、再度二重に四角形（RECTANGLE）やカードを上書きして重ね描きすることは【厳禁】です。** これを行うと、テキストが図形の裏側へZ-indexのせいで完全に隠れてしまいます。
            - **Z-index黄金順序の遵守**: 必ず、①背景カードの描画（add_custom_shape で ROUNDED_RECTANGLE 描画）、②ヘッダータイトルの描画、③カード内テキスト（タイトル・本文）の重ね描画、の順序を守って呼び出してください。
            - カードのフチに文字が張り付くのを防ぐため、必ず以下の **「20ptインサイドマージン物理方程式」** に沿って、カードより一回り小さいテキストボックスを上に配置してください。
            - **【重要】大判カードの枠線（Outline）の明示的指定**:
              - カードを描画する `add_custom_shape` を呼び出す際、**必ず新しく拡張された `outline_color_hex` 引数を指定して枠線を描画してください！**
              - **左側カードの座標 ＆ 枠線**: X_c = `40pt`, Y_c = `95pt`, 幅 = `300pt`, 高さ = `270pt` (塗り色: `fill_color_hex='#FCE8E6'`, 枠線色: `outline_color_hex='#F28B82'`, 枠線の太さ: `outline_weight=2.0`)。
              - **右側カードの座標 ＆ 枠線**: X_c = `380pt`, Y_c = `95pt`, 幅 = `300pt`, 高さ = `270pt` (塗り色: `fill_color_hex='#E8F0FE'`, 枠線色: `outline_color_hex='#8AB4F8'`, 枠線の太さ: `outline_weight=2.0`)。
            - **タイトルテキスト用ボックス (カードのヘッダー)**: カードの上端から20pt下げ、左右に20ptの余白を取るため、必ず **X = `X_c + 20pt` (左は60pt, 右は400pt), Y = `115pt`, 幅 = `260pt`, 高さ = `30pt`** に配置してください (Noto Sans JP 18px, Bold, 文字色: 左は赤 `#D93025`, 右は青 `#1A73E8`)。タイトル文字列は、添付画像通り、左側は「現状の課題：我慢のサウナ」、右側は「理想の姿：整いへの最適化」を必ず指定してください。
            - **本文詳細テキスト用ボックス**: タイトルから十分な間隔を空けるため、必ず **X = `X_c + 20pt` (左は60pt, 右は400pt), Y = `160pt`, 幅 = `260pt`, 高さ = `180pt`** に配置してください (Noto Sans JP 12px, Charcoal `#3C4043`, 各行の先頭に箇条書きバッジ `・` を付与)。
            - これにより、カードのフチから綺麗に 20pt 内側に引っ込んだ、プロ顔負けの美しいマージンデザインが 100% 完成します。
          - **グラフと角丸カードの左右対比ルール (データ分析時)**:
            - グラフ画像と解説角丸カードを左右に配する際、**絶対に要素同士が重なってはならない（厳禁）。** グラフの重要度に応じて、① `Visual Focus (6:4)` (グラフ幅360pt, パネル幅240pt, パネル左端X2=440pt), ② `Standard (5:5)` (各300pt, X2=380pt), ③ `Text Focus (4:6)` (グラフ240pt, パネル360pt, X2=320pt) から最適な横幅比率を自律選択し、必ず **`X2 = 40 + グラフ幅 + 40`** の物理方程式を用いて配置すること。また、Matplotlib グラフ画像を生成する際は、スライド上の描画アスペクト比 (`グラフ幅 / 270`) と一致するように必ず `figsize` を計算・指定し、画像の自動引き伸ばしによる衝突を100%防止すること。"""
            
    lines[start_line_idx:end_line_idx] = [new_part]
    
    new_content = '\n'.join(lines)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("SUCCESS: Patched agent.py using line index search.")
else:
    print(f"ERROR: Anchor indices start={start_line_idx}, end={end_line_idx}")
