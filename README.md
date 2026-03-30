# Google Slide Agent (SlideExpert)

## 概要
SlideExpertは、Googleのブランド美学と日本特有のビジネススタイル（結論を先に述べるスタイル）に基づいた、プロフェッショナルなGoogleスライドを自動生成するAIエージェントです。ユーザーの指示プロセスをもとに、構成案の作成からスライドの自動生成、データ可視化（グラフの自動生成と挿入）までを一貫して行います。

Vertex AI Agent Engine (Reasoning Engine) 上にデプロイし、Gemini 3モデルと連携動作する堅牢な設計になっています。

## 主な特徴
- 🎨 **Google Branding**: Google公式のブランドカラー（Blue, Red, Yellow, Green）を基調とした洗練されたデザイン。
- 📊 **Matplotlib連携によるデータ可視化**: グラフ生成スクリプト内で動的に日本語フォント（Noto Sans CJK JP）をダウンロードし、「豆腐（文字化け）」を完全に防ぐセキュアな実装。
- 📄 **日本のビジネススタイル（キーメッセージ・ファースト）**: スライド上部の専用ボックスに「一番伝えたい結論」を配置し、視覚的に分かりやすい構造化スライドを生成。
- 🤖 **Vertex AI Agent Engine 完全互換**: わずかなコマンドでGoogle Cloud上に簡単にデプロイ・稼働させることが可能。

## インストールと環境構築

### 前提条件
- [uv](https://github.com/astral-sh/uv) (超高速なPythonパッケージマネージャ) 
- Google Cloud プロジェクトの作成と課金の有効化。
- Vertex AI API および Google Slides API / Google Drive API の有効化。

### 1. リポジトリのクローンとパッケージ構築
```bash
git clone <YOUR_GITHUB_REPO_URL>
cd google_slide_agent
uv sync
```

### 2. 環境変数とプロジェクトIDの設定
`.env.example` をコピーして `.env` を作成し、ご自身のGoogle CloudプロジェクトIDに書き換えてください。
```bash
cp slide_app/.env.example slide_app/.env
```
例 (`slide_app/.env`):
```text
GOOGLE_GENAI_USE_VERTEXAI=1
GOOGLE_CLOUD_PROJECT=your-custom-project-id
GOOGLE_CLOUD_LOCATION=global
```

※ソースコード内（`deploy.sh`, `Makefile`, `slide_app/agent.py` など）にある `YOUR_PROJECT_ID` というプレースホルダーも、エディタの一括置換機能を使ってご自身のプロジェクトIDに書き換えてください。

### 3. デプロイ
`deploy.sh` スクリプトを実行するだけで、依存関係の解決、パッケージングおよび Vertex AI Reasoning Engine へのデプロイが自動で行われます。

```bash
bash deploy.sh
```

デプロイ完了後、表示されるURLからGoogle Cloud Consoleの「Playground」にアクセスすることで、実際のブラウザ画面からエージェントと対話できます。

## エージェントの基本的な使い方
エージェントに対して自然言語で資料作成の指示を出します。以下のステップで進行します。

1. **構成の提案依頼**: 
   「第2四半期の売上報告スライドを5枚くらいで作ってください」と指示すると、エージェントはスライドを作成する前に、まず**構成案（アウトライン）を提案**します。
2. **フィードバック・生成開始**: 
   提案された構成に合意すると、エージェントが自律的にGoogle Slides APIを叩き、一枚ずつスライドを作成していきます。必要に応じてMatplotlibのコードを書き、Drive経由でグラフ画像を挿入します。
3. **完成とURL発行**: 
   すべての作業が完了すると、生成されたプレゼンテーションのURLがチャット上に返却されます。そのままアクセスして編集や共有が可能です。

## 構成ツール群
エージェントは裏側で以下の専用ツールを呼び出してスライドを構築しています。
- `create_google_presentation`: 新規プレゼンテーション枠の作成
- `add_structured_slide`: 構造化スライド（タイトル、中扉、コンテンツ）の追加
- `upload_image_to_drive`: ローカル画像のGoogle Driveアップロードと公開設定
- `generate_and_upload_plot_direct`: Matplotlibのスクリプト実行とグラフ内包データ転送
# SlideExpert
