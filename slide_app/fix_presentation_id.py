# -*- coding: utf-8 -*-
import os

file_path = "/Users/junhattori/Code/agentBox/SlideExpert/slide_app/agent.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

target = '    - **一括ツールコール時のスライドID完全追跡黄金律 (CRITICAL FOR MULTI-TOOL CALLS)**:'

replacement = """    - **一括ツールコール時のプレゼンテーションID ＆ スライドID完全追跡黄金律 (CRITICAL FOR MULTI-TOOL CALLS - MUST FOLLOW)**:
      - **【最重要】新規スライド生成時、作成した `create_google_presentation` の戻り値である `presentationId` を【一言一句違わず完全コピー】して、同じターン内の他のすべてのツールコールの `presentation_id` 引数に正確にバインドしてください。過去の履歴に存在する古いプレゼンテーションIDを混同して混入させることは【厳重に禁止】します。**"""

if target in content:
    content = content.replace(target, replacement)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("SUCCESS")
else:
    # 曖昧検索
    lines = content.split("\n")
    replaced = False
    for i, line in enumerate(lines):
        if "一括ツールコール時のスライドID完全追跡黄金律" in line:
            lines[i] = replacement
            replaced = True
            break
    if replaced:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print("SUCCESS_VIA_FALLBACK")
    else:
        print("FAILED")
