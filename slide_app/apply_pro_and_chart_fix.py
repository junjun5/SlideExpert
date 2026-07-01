def patch_all():
    # 1. tools.py の Docstring 修正
    tools_path = "/Users/junhattori/Code/agentBox/SlideExpert/slide_app/tools.py"
    with open(tools_path, "r", encoding="utf-8") as f:
        tools_content = f.read()

    target_doc = """    Args:
        presentation_id (str): プレゼンテーションID。
        slide_id (str): 挿入するスライドのID。
        data (list): 書き込むデータ（二次元配列。1行目はヘッダー）。
        title (str): グラフのタイトル。
        chart_type (str): グラフの種類 ("BAR", "COLUMN", "LINE", "AREA", "SCATTER")。
        
    Returns:"""

    replacement_doc = """    Args:
        presentation_id (str): プレゼンテーションID。
        slide_id (str): 挿入するスライドのID。
        data (list): 書き込むデータ（二次元配列。1行目はヘッダー）。
        title (str): グラフのタイトル。
        chart_type (str): グラフの種類 ("BAR", "COLUMN", "LINE", "AREA", "SCATTER")。
        x (float, optional): グラフを配置するX座標 (pt)。デフォルトは SLIDE_WIDTH * 0.1。
        y (float, optional): グラフを配置するY座標 (pt)。デフォルトは SLIDE_HEIGHT * 0.2。
        width (float, optional): グラフの横幅 (pt)。デフォルトは SLIDE_WIDTH * 0.8。
        height (float, optional): グラフの高さ (pt)。デフォルトは SLIDE_HEIGHT * 0.6。
        
    Returns:"""

    if target_doc in tools_content:
        tools_content = tools_content.replace(target_doc, replacement_doc)
        with open(tools_path, "w", encoding="utf-8") as f:
            f.write(tools_content)
        print("✅ tools.py の add_sheets_chart_from_data の Docstring を完璧に修正しました！")
    else:
        print("❌ tools.py の Docstring 置換に失敗しました（ターゲットが見つかりません）。")

    # 2. agent.py のデフォルトモデルを gemini-1.5-pro に変更
    agent_path = "/Users/junhattori/Code/agentBox/SlideExpert/slide_app/agent.py"
    with open(agent_path, "r", encoding="utf-8") as f:
        agent_content = f.read()

    target_model = 'model=os.environ.get("AGENT_MODEL", "gemini-3-flash-preview"),'
    replacement_model = 'model=os.environ.get("AGENT_MODEL", "gemini-1.5-pro"),'

    if target_model in agent_content:
        agent_content = agent_content.replace(target_model, replacement_model)
        with open(agent_path, "w", encoding="utf-8") as f:
            f.write(agent_content)
        print("✅ agent.py のデフォルトモデルを gemini-1.5-pro (3.1 Pro) に変更しました！")
    else:
        # 代替パターン
        alternative_target = 'model=os.environ.get("AGENT_MODEL", "gemini-3-flash-preview")'
        alternative_replacement = 'model=os.environ.get("AGENT_MODEL", "gemini-1.5-pro")'
        if alternative_target in agent_content:
            agent_content = agent_content.replace(alternative_target, alternative_replacement)
            with open(agent_path, "w", encoding="utf-8") as f:
                f.write(agent_content)
            print("✅ agent.py のデフォルトモデルを gemini-1.5-pro (3.1 Pro) に変更しました！(Alt)")
        else:
            print("❌ agent.py のモデル指定置換に失敗しました。")

if __name__ == "__main__":
    patch_all()
