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

---

## 🚀 ローカル環境での自律E2Eテストの実行方法

本番環境（Cloud Run）にデプロイする前に、ローカルから本物の Google Slides API に対してAIエージェントを完全自律起動させ、ゼロから構成案〜スライドの一括描画までを実行・検証できる統合テスト環境が用意されています。

### 1. 前提条件（Google API 認証の紐付け）
ローカル環境から本物の Google Presentation にアクセスするため、Google Cloud プロジェクトとの紐付けが必要です。
お手元のPCで Google Cloud SDK (`gcloud`) がセットアップされている場合、以下のコマンドを実行してローカルの認証鍵（Application Default Credentials: ADC）を有効化してください：
```bash
gcloud auth application-default login
```

### 2. テストの起動手順
SlideExpert のルートディレクトリ直下にある統合テストプログラムを実行します。

```bash
# 1. リポジトリのルートに移動
cd /Users/junhattori/Code/agentBox/SlideExpert

# 2. テストプログラムを稼働
python3 test_final_agent_behavior.py
```

### 3. テストの挙動と特徴（完全動的生成）
- このテストは、スライドのレイアウト座標や文字情報を事前に固定（ハードコーディング）して再現するものではありません。
- テストスクリプトはAIに対して**「サウナの入り方と、初心者がプロサウナーになるためのロードマップをガントチャートで説明して」**という**生のプロンプトをそのままチャットに入力しているだけ**です。
- スライド枚数、各スライドのアジェンダ、図形（CHEVRON等）の正確な計算座標（X, Y, W, H）の決定は、**すべてAIエージェント（Gemini Pro）がリアルタイムの思考によってその場で自律的に設計・構築**し、APIを発行しています。

---

## 🎨 文字切れ・はみ出しを防ぐ「自動レイアウト制御」仕様

特殊な図形（山形の `CHEVRON` など）の中にテキストを埋め込んだ際、しっぽの凹み部分や先端の尖った境界を文字が突き抜けてしまう「はみ出しバグ」を防ぐため、`tools.py` の `add_custom_shape` には以下の Slides API 最適化仕様が組み込まれています。

1. **しっぽの尖りを回避する「左右余白（Margin）の動的制御」**
   - 図形タイプが `CHEVRON` の場合、左右マージン（`textMarginLeft` / `textMarginRight`）が自動的に **`25pt`（通常図形の3倍以上）** に広げて設定されます。
   - これにより、文字は自動的にしっぽの境界を避けた中央の安全なフラット領域でのみ折り返され、綺麗に中央に収まります。
2. **長文でも絶対に突き抜けない「自動フォントサイズ縮小（Autofit）」の強制適用**
   - すべての描画図形に対し、Google Slides が誇る **`autofitType: TEXT_AUTOFIT`** 機能を有効化して作成します。
   - これにより、万が一図形に対して文字数が多すぎる場合であっても、文字ははみ出さず、自動的に一番読みやすいサイズまで縮小されてピタッと図形内に格納されます。
3. **物理的なテキストボックス重ね合わせの完全排除**
   - AIに対し、図形の上に別のテキストボックスを載せる重ね合わせ手法を禁止し、`add_custom_shape` 側の `text` 引数を通じて図形オブジェクト自体に直接テキストを書き込ませることで、オブジェクトグループのズレやはみ出しを根底からシャットアウトしています。
