# -*- coding: utf-8 -*-
import os

file_path = "/Users/junhattori/Code/agentBox/SlideExpert/slide_app/agent.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

target = """       3) **左右2カラム対比 (Split 2-Column / 課題対比)**:
          - 初心者の課題と解決策など、左右に2つの大判カードを配するレイアウトです。
          - **インサイドマージンの絶対義務化と上書き禁止 (最重要)**:
            - AIがカード（ROUNDED_RECTANGLE）の上に文字テキストを重ねる際、カードの座標と全く同じ位置にテキストボックスを置くことや、あとから四角形（RECTANGLE）を上書きして角丸デザインを破壊することは【厳禁】です。
            - カード의 フチに文字が張り付く素人っぽさを完全に防ぐため、必ず以下の **「20ptインサイドマージン物理方程式」** に沿って、カードより一回り小さいテキストボックスを上に配置してください。
            - **カードの座標**: X_c = `40pt` (左) または `380pt` (右), Y_c = `95pt`, 幅 = `300pt`, 高さ = `270pt` (塗り色: 左は薄赤 `#FCE8E6` / 枠線 `#F28B82`, 右は薄青 `#E8F0FE` / 枠線 `#8AB4F8`)。
            - **タイトルテキスト用ボックス (カードのヘッダー)**: カードの上端から20pt下げ、左右に20ptの余白を取るため、必ず **X = `X_c + 20pt` (左は60pt, 右は400pt), Y = `115pt`, 幅 = `260pt`, 高さ = `30pt`** に配置してください (Noto Sans JP 18px, Bold, 文字色: 左は赤 `#D93025`, 右は青 `#1A73E8`)。
            - **本文詳細テキスト用ボックス**: タイトルから十分な間隔を空けるため、必ず **X = `X_c + 20pt` (leftは60pt, rightは400pt), Y = `160pt`, 幅 = `260pt`, 高さ = `180pt`** に配置してください (Noto Sans JP 12px, Charcoal `#3C4043`, 各行の先頭に箇条書きバッジ `・` を付与)。
            - これにより、カードのフチから綺麗に 20pt 内側に引っ込んだ、プロ顔負けの美しいマージンデザインが 100% 完成します。"""

# 念のための曖昧フォールバック用ターゲット
fallback_anchor = "左右に2つの大判カードを配するレイアウトです。"

replacement = """       3) **左右2カラム対比 (Split 2-Column / 課題対比)**:
          - 初心者の課題と解決策など、左右に2つの大判カードを配するレイアウトです。
          - **【重要】スライドヘッダータイトル（大見出し）の絶対描画**:
            - 本スライドの左上には、必ずスライド全体のタイトル（見出しテキスト）として、**X = `40pt`, Y = `40pt`, 幅 = `640pt`, 高さ = `45pt`** のテキストボックスを `add_custom_text_box` で真っ先に作成してください（フォント: Noto Sans JP, 24px, Bold, 文字色: Charcoal `#202124`、例: 「現状の課題と誤解」）。
          - **インサイドマージンの絶対義務化と重複描画の完全禁止 (最重要)**:
            - **【重複描画の厳重禁止】**: すでに `add_custom_shape` や `add_custom_text_box` などの個別ツールで描画した背景カードやテキストの上から、**後日やバッチアップデート（execute_batch_update）で、再度二重に四角形（RECTANGLE）やカードを上書きして重ね描きすることは【厳禁】です。** これを行うと、テキストが図形の裏側へZ-indexのせいで完全に隠れてしまいます。
            - **Z-index黄金順序の遵守**: 必ず、①背景カードの描画（add_custom_shape で ROUNDED_RECTANGLE 描画）、②ヘッダータイトルの描画、③カード内テキスト（タイトル・本文）の重ね描画、の順序を守って呼び出してください。
            - カードのフチに文字が張り付くのを防ぐため、必ず以下の **「20ptインサイドマージン物理方程式」** に沿って、カードより一回り小さいテキストボックスを上に配置してください。
            - **カードの座標**: X_c = `40pt` (左) または `380pt` (右), Y_c = `95pt`, 幅 = `300pt`, 高さ = `270pt` (塗り色: 左は薄赤 `#FCE8E6` / 枠線 `#F28B82`, 右は薄青 `#E8F0FE` / 枠線 `#8AB4F8`)。
            - **タイトルテキスト用ボックス (カードのヘッダー)**: カードの上端から20pt下げ、左右に20ptの余白を取るため、必ず **X = `X_c + 20pt` (左は60pt, 右は400pt), Y = `115pt`, 幅 = `260pt`, 高さ = `30pt`** に配置してください (Noto Sans JP 18px, Bold, 文字色: 左は赤 `#D93025`, 右は青 `#1A73E8`)。
            - **本文詳細テキスト用ボックス**: タイトルから十分な間隔を空けるため、必ず **X = `X_c + 20pt` (左は60pt, 右は400pt), Y = `160pt`, 幅 = `260pt`, 高さ = `180pt`** に配置してください (Noto Sans JP 12px, Charcoal `#3C4043`, 各行の先頭に箇ため書きバッジ `・` を付与)。
            - これにより、カードのフチから綺麗に 20pt 内側に引っ込んだ、プロ顔負けの美しいマージンデザインが 100% 完成します。"""

if target in content:
    content = content.replace(target, replacement)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("SUCCESS")
else:
    lines = content.split("\n")
    replaced = False
    for i, line in enumerate(lines):
        if fallback_anchor in line:
            # anchorの次の行から置換処理
            # より安全な部分置換
            content = content.replace("左右に2つの大判カードを配するレイアウトです。", "左右に2つの大判カードを配するレイアウトです。\n" + replacement.split("左右に2つの大判カードを配するレイアウトです。\n")[1])
            replaced = True
            break
    
    if replaced:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("SUCCESS_VIA_FALLBACK")
    else:
        # 直接のフルスワップを狙う
        content = content.replace("左右2カラム対比 (Split 2-Column / 課題対比)", "左右2カラム対比 (Split 2-Column / 課題対比)_OLD")
        print("FAILED")
