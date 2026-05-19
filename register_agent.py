import sys
import json
import urllib.request
import urllib.error
import ssl

# macOS環境でのSSL証明書エラー回避
ssl._create_default_https_context = ssl._create_unverified_context

PROJECT_NUMBER = "989491130286"
PROJECT_ID = "agentspace-469000"
LOCATION = "global"
APP_ID = "workforceagentspace_1755760899124"  # 先ほど選択したアプリのID
AGENT_NAME = "SlideExpert"
AGENT_SHORT_NAME = "SlideExpert"
SUMMARY = "Googleブランドの美学に基づき、プロフェッショナルな日本ビジネススタイルのGoogle Slides資料を作成します。"
SERVICE_URL = "https://google-slide-agent-989491130286.us-east1.run.app"

# コマンドラインからトークンを受け取る
if len(sys.argv) < 2:
    print("Error: Access token required as argument.")
    sys.exit(1)
token = sys.argv[1]

endpoint = "discoveryengine.googleapis.com"
url = f"https://{endpoint}/v1alpha/projects/{PROJECT_NUMBER}/locations/{LOCATION}/collections/default_collection/engines/{APP_ID}/assistants/default_assistant/agents"

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
    "X-Goog-User-Project": PROJECT_ID,
}

data = {
    "name": AGENT_NAME,
    "displayName": f"{AGENT_SHORT_NAME} ({AGENT_NAME})",
    "description": SUMMARY,
    "a2aAgentDefinition": {
        "jsonAgentCard": json.dumps({
            "protocolVersion": "1.0",
            "name": AGENT_NAME,
            "description": SUMMARY,
            "url": f"{SERVICE_URL}/a2a/slide_app",
            "version": "1.0.0",
            "defaultInputModes": ["text/plain"],
            "defaultOutputModes": ["text/plain", "application/json"],
            "capabilities": {
                "streaming": True,
                "extensions": [
                    {
                        "uri": "https://a2ui.org/a2a-extension/a2ui/v0.8"
                    }
                ]
            },
            "preferredTransport": "JSONRPC",
            "skills": []
        })
    }
}

print(f"Registering {AGENT_NAME} directly to Discovery Engine API...")
req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers)
try:
    with urllib.request.urlopen(req) as response:
        resp_data = json.loads(response.read().decode("utf-8"))
        print("✅ Successfully registered agent!")
        print(json.dumps(resp_data, indent=2))
except urllib.error.HTTPError as e:
    print(f"Error registering agent: {e}", file=sys.stderr)
    print(e.read().decode("utf-8"), file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"Unexpected error: {e}", file=sys.stderr)
    sys.exit(1)
