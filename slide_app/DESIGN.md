---
name: Modern Business / Google Material Aesthetic
colors:
  surface-container-lowest: '#FFFFFF'
  surface-container-low: '#F8F9FA'
  surface-container: '#F1F3F4'
  on-surface-variant: '#3C4043'
  outline-variant: '#DADCE0'
  primary: '#1A73E8'
  secondary: '#202124'
typography:
  display-lg:
    fontFamily: Noto Sans JP
    fontSize: 36px
    fontWeight: '700'
    lineHeight: '1.2'
    letterSpacing: '0'
  headline-md:
    fontFamily: Noto Sans JP
    fontSize: 18px
    fontWeight: '600'
    lineHeight: '1.4'
    letterSpacing: '0'
  body-base:
    fontFamily: Noto Sans JP
    fontSize: 14px
    fontWeight: '400'
    lineHeight: '1.6'
    letterSpacing: '0'
  label-sm:
    fontFamily: Noto Sans JP
    fontSize: 10px
    fontWeight: '400'
    lineHeight: '1.2'
    letterSpacing: '0'
---

## Brand, Style & Security Policy
The style is strictly **Modern Business / Google Material Aesthetic**. It prioritizes clarity, professionalism, and elegant simplicity. The interface is characterized by a clean white background, soft gray or light blue informational cards, charcoal-colored highly legible text, and rounded grid structures. Heavy dark backgrounds, pitch black boxes, and high-contrast official official block structures are strictly forbidden.

### 🔒 ブランド固有ワードの完全排除ルール (No Brand-specific Words)
スライド内に表示・描画するすべてのテキスト（タイトル、本文、表紙、ヘッダー、フッター）において、**「Google」「Gemini」「Google Cloud」といった特定のブランド・サービス固有名詞は一切使用しないでください。**
代わりに、以下の一般名詞または自社名へと自動的に置き換えて作成してください：
- **「Google」** ➡ **「Altostrat」** (企業名) または **「自社」** / **「弊社」**
- **「Gemini」** ➡ **「先進的AIアシスタント」** または **「エンタープライズAIプラットフォーム」**
- **「Google Cloud」** ➡ **「セキュア・クラウド基盤」** または **「自社クラウドサービス」**

## Colors
The palette is a carefully curated, professional business tone with Google colors as clean accents:
- **Background Surfaces:** Pure White (#FFFFFF) for general backgrounds.
- **Informational Cards:** Light Soft Gray (#F8F9FA) or extremely Soft Blue (#E8F0FE) with a rounded subtle touch.
- **Text:** Elegant Charcoal Gray (#3C4043) for general body copy, and Pitch Charcoal (#202124) for headings to ensure modern visual comfort (do not use harsh #000000 pure black).
- **Accent (Blue):** Google Action Blue (#1A73E8) for title vertical lines, core highlights, and highlighted markers.
- **Border/Divider:** Elegant Muted Gray (#DADCE0) for card borders and dividers.

## Typography
The typography system uses **Noto Sans JP** as the default workhorse:
- Main headings use bold weight (#202124) with large comfortable spacing.
- Secondary annotations and tags use smaller sizes (10px - 12px) with gray styling (#5F6368).

## Layout & Spacing (Global Rules)
The slide size is strictly fixed:
- **Width:** 720pt
- **Height:** 405pt (16:9 aspect ratio)
All coordinates (X, Y) and sizes (W, H) must be precisely calculated to fit within this grid.
- **Center X:** 360pt
- **Center Y:** 202.5pt
- **Safe Margins:** Leave at least 24pt from edges.
- **Rounded Corners:** Cards and informational boxes should use rounded corners (typically 8pt to 12pt, equivalent to custom shape formatting) to give a modern, friendly, yet professional software aesthetic.

## Layout & Spacing (Cover Slide Specific)
The cover slide is clean, modern, and dynamically branded with Google Material 3 Aesthetics to ensure an extremely premium corporate software look:
- **Top-Right:** Date or Metadata in small, clean gray text (e.g., "2026/05/18 First Edition") at X = `500pt`, Y = `40pt`, Width = `180pt`, Height = `30pt`.
- **Top-Left:** Requesting Organisation/Brand in elegant font ("Altostrat株式会社") at X = `40pt`, Y = `40pt`, Width = `300pt`, Height = `30pt`.
- **Right-Bottom Space Decor (半透明トリプル幾何学Blob装飾 - ELLIPSE)**:
  - 右下隅に、最高級のIT企業感を演出するために、以下の2つの半透明な円を少し重ね合わせて配置（すべて線なし）：
    1. **装飾円 1 (大・淡いブルー)**: X = `520pt`, Y = `220pt`, 幅 = `240pt`, 高さ = `240pt` (塗り色: `#E8F0FE`, alpha = 0.4)
    2. **装飾円 2 (中・スカイブルー)**: X = `580pt`, Y = `160pt`, 幅 = `200pt`, 高さ = `200pt` (塗り色: `#D2E3FC`, alpha = 0.3)
- **Center Branded Title Area (アンダーレイ大判カード & タイトル直接埋め込み - CRITICAL COLLISION PREVENTION):**
  - 表紙全体のレイアウトの緩さ・スカスカ感を根絶するため、タイトルの背後に大判の上品なカードを敷き、そこにタイトルを直接埋め込みます。
  - **アンダーレイ大判カード (ROUNDED_RECTANGLE)**: X = `40pt`, Y = `120pt`, 幅 = `640pt`, 高さ = `180pt` (背景色: 極淡ブルー `#F8F9FA`, 枠線なし)。
  - **左垂直カラーアクセントライン (RECTANGLE)**: X = `40pt`, Y = `120pt`, 幅 = `6pt`, 高さ = `180pt` (塗り色: Google Action Blue `#1A73E8`)。
  - **タイトルテキストの埋め込み**:
    - タイトルテキストは、上に重ね合わせた別テキストボックスを描画することを【厳禁】とし、**必ずアンダーレイ大判カードの `text` 引数に直接タイトル文字列（例: `"サウナの極意：初心者からプロサウナーへの道"`) を指定して一発で埋め込んでください！**
    - 文字色は Pitch Charcoal `#202124`、フォントサイズは自動調整（Autofit）が有効になるため、タイトルが長文であっても改行されてカードの中心（CENTER/MIDDLE）に完璧な余白を保って収まります。
- **Bottom:** Clean footnotes or disclaimers starting with "※" in muted gray (10px) at X = `70pt`, Y = `320pt`, Width = `610pt`, Height = `50pt`.


## Components
- **Cards / Blocks (情報ブロック - CRITICAL MODERNIZE RULE):**
  - **NEVER use deep black or dark gray fills** for cards or information blocks. It looks heavy, harsh, and unpolished.
  - Instead, strictly use **Light Gray (#F8F9FA)** or **Soft Blue (#E8F0FE)** as the fill color.
  - Apply a thin, clean border of **Muted Gray (#DADCE0)** around cards.
  - Round the corners of all blocks (8pt to 12pt) to create a highly polished modern workspace look.
- **Tables (表):**
  - Clean borders with light gray header fills (#F1F3F4). Text inside is centered and comfortably padded.
- **Lists (箇条書き):**
  - Clean, readable bullet points using standard Gothic styling with proper line height (1.5x task spacing).

---

## Layout & Spacing (Timeline & Process Slide Specific)
* **🎯 最適な適用シーン (どういう時に使うか)**:
  - **アジェンダ（目次）、段階的なロードマップ、製品の歴史、業務プロセス、時系列の進捗、または「ステップ順の推移（時間的・段階的変化）」を説明・表現したい場合**。

### A) カラフル・タイムライン・アジェンダ (Premium Vertical Timeline)
* **用途**: 縦型の箇条書きを、時間の流れやアジェンダ項目として垂直軸で美しく見せたい時。
* **レイアウト構成**:
  - **左側 (Title & Left Blob Decoration)**:
    - **アジェンダタイトル ("Agenda")**: X = `60pt`, Y = `100pt`, 幅 = `200pt`, 高さ = `60pt` (Noto Sans JP 36px, Bold, Charcoal `#202124`)。
    - **左下のセキュア幾何学Blob装飾 (半透明トリプルELLIPSE重ね合わせ)**: 画像クローラー制約を回避しつつ美しいグラデーションBlobを再現するため、以下の3枚の半透明の楕円（ELLIPSE）を重ね合わせて構築してください（線なし）：
      1. **ベース楕円 (大・淡いブルー)**: X = `-80pt`, Y = `240pt`, 幅 = `260pt`, 高さ = `260pt` (色: `#E8F0FE`, alpha = 0.3)
      2. **ミドル楕円 (中・スカイブルー)**: X = `-40pt`, Y = `280pt`, 幅 = `180pt`, 高さ = `180pt` (色: `#D2E3FC`, alpha = 0.4)
      3. **トップ楕円 (小・ラベンダーグレー)**: X = `-10pt`, Y = `310pt`, 幅 = `120pt`, 高さ = `120pt` (色: `#E8EAED`, alpha = 0.5)
  - **中央 (青いタイムライン垂直線)**:
    - **垂直タイムライン線 (RECTANGLE)**: X = `320pt`, Y = `60pt`, 幅 = `2pt`, 高さ = `285pt` (塗り色: `#1A73E8`、線なし)。
  - **右側 (タイムラインノード ＆ テキストの動的等間隔配置 - 項目数 N に自動対応)**:
    - Y軸の開始位置 `90pt` から終了位置 `310pt` までの範囲（220pt）の中で、すべての項目を完璧に均等な等間隔（gap）で自動配置します。
    - **計算式**: `gap = 220 / (N - 1)` （※N = 1 の場合は Y = 200pt）
    - **各項目 i の座標**:
      - **円形ノード (ELLIPSE)**: X = `311pt`, 幅 = `20pt`, 高さ = `20pt`, Y = `90 + (i * gap)`。塗り色は上から順に Google 4カラー (`#1A73E8`, `#F9AB00`, `#EA4335`, `#34A853`) をループ適用（線なし）。
      - **項目テキストボックス (TEXTBOX)**: X = `345pt`, 幅 = `330pt`, 高さ = `30pt`, Y = `(90 + (i * gap)) - 2` (円形ノードと高さを視覚的に揃えるための補正値 -2pt)。フォント: Noto Sans JP 14px, Medium, Charcoal `#3C4043`。

### B) 水平ステップ矢印・ロードマップ (Horizontal Arrow Timeline)
* **用途**: 横方向のダイナミックなフェーズ推移、ロードマップ、プロセスの進行感をアピールしたい時。
* **レイアウト構成 (全フェーズ CHEVRON 統一 ＆ 図形内埋め込みテキスト仕様)**:
  - **形状の完全統一**: プロセスの連続性と美しい整列を保つため、第1〜第3まですべて背景図形には **`CHEVRON` (山形・矢印型)** を使用してください。
  - **図形内テキスト埋め込みの絶対ルール (Shape Embedded Text)**: 
    - 矢印の内部に別のテキストボックスを物理的に重ねることは【厳禁】です（文字切れ・ズレを防止するため）。
    - 必ず、作成した `CHEVRON` 図形の `objectId` に対して直接 `insertText` を使用してフェーズ名テキスト（例: `"STEP 1: サウナ"`, `"STEP 2: 水風呂"`, `"STEP 3: 外気浴"`) を流し込んでください。
    - 埋め込んだテキストに対して、上下中央揃え（`contentAlignment: "MIDDLE"`）と、左右中央揃え（`alignment: "CENTER"`）を指定してください。
  - **第1フェーズ (左端)**: 
    - **背景図形**: `CHEVRON` を使用。
    - 座標: X = `40pt`, Y = `110pt`, 幅 = `210pt`, 高さ = `60pt` (塗り色: 淡いブルー `#E8F0FE`, 枠線なし)。
    - **詳細説明テキストボックス**: **X = `40pt`, Y = `185pt`, 幅 = `200pt`, 高さ = `180pt`**。フォント: Noto Sans JP 10px, Charcoal `#3C4043`, 左寄せ, 行間 1.3x。
  - **第2フェーズ (中央)**: 
    - **背景図形**: `CHEVRON` を使用。
    - 座標: X = `250pt`, Y = `110pt`, 幅 = `210pt`, 高さ = `60pt` (塗り色: 中間ブルー `#D2E3FC`, 枠線なし)。
    - **詳細説明テキストボックス**: **X = `250pt`, Y = `185pt`, 幅 = `210pt`, 高さ = `180pt`**。フォント: Noto Sans JP 10px, Charcoal `#3C4043`, 左寄せ, 行间 1.3x。
  - **第3フェーズ (右端)**: 
    - **背景図形**: `CHEVRON` を使用。
    - 座標: X = `460pt`, Y = `110pt`, 幅 = `220pt`, 高さ = `60pt` (塗り色: Google Action Blue `#1A73E8`, 枠線なし)。
    - **詳細説明テキストボックス**: **X = `470pt`, Y = `185pt`, 幅 = `210pt`, 高さ = `180pt`**。フォント: Noto Sans JP 10px, Charcoal `#3C4043`, 左寄せ, 行間 1.3x。
  - **時間・時期ラベル (各矢印の上部)**: 各矢印の開始位置に合わせ、Y = `85pt` に Noto Sans JP 11px (Bold, 灰色 `#5F6368`, 左寄せ) で時期を配置。
  - **フェーズ名（埋め込みテキスト書式）**:
    - フォント: Noto Sans JP 14px (Bold)。
    - 文字色: 第1・第2フェーズは Charcoal `#202124`（淡色背景のため）、第3フェーズは White `#FFFFFF`（濃い青背景のため）。
    - 整列: 水平方向 `CENTER`、垂直方向 `MIDDLE`。

---

## Layout & Spacing (Horizontal Grid / Parallel Cards Slide Specific)
* **🎯 最適な適用シーン (どういう時に使うか)**:
  - **3つまたは4つの主要なメリット、並列する強み、同等レベルの主要ポリシー、SWOT、または「時間的な順序関係のない並列的な論点」を整理・分類したい場合**。

### A) 3列並列カード・グリッド (Triple Parallel Cards)
* **用途**: 単なる縦並びの箇条書きを、横方向のスマートなカード型グリッドに配置して格別のデザイン価値を与えたい時。
* **レイアウト構成 (横並び3つカード - ROUNDED_RECTANGLE)**:
  - スライドの有効幅 640pt を 3等分し、カード間に 20pt の快適な隙間を確保します。
  - **カード 1**: X = `40pt`, Y = `130pt`, 幅 = `200pt`, 高さ = `230pt` (背景色: `#FFFFFF`, 境界線: 黄色 `#F9AB00` 2pt)。
  - **カード 2**: X = `260pt`, Y = `130pt`, 幅 = `200pt`, 高さ = `230pt` (背景色: `#FFFFFF`, 境界線: 赤色 `#EA4335` 2pt)。
  - **カード 3**: X = `480pt`, Y = `130pt`, 幅 = `200pt`, 高さ = `230pt` (背景色: `#FFFFFF`, 境界線: 緑色 `#34A853` 2pt)。
  - **カード内のテキスト配置 (各カード共通)**:
    - **見出し**: Y = `155pt`, 幅 = `180pt`。Noto Sans JP 14px (Bold, 各カードの枠線と同一色、中央寄せ)。
    - **本文詳細**: Y = `190pt`, 幅 = `180pt`。Noto Sans JP 10px (Charcoal `#3C4043`, 左寄せ、行間 1.5x)。

### B) 4象限モダンタイルグリッド (Quad / Matrix Tile Grid)
* **用途**: 3並列では収まらない「4つの強み」「4つの推進フェーズ」「SWOT分析」「4大ターゲット」を、画面をフルに使って美しく均等マッピングしたい時。
* **レイアウト構成 (2x2 タイル配置 - ROUNDED_RECTANGLE)**:
  - スライド有効領域を田の字型に綺麗に4分割し、カード間に十分な隙間（横30pt, 縦20pt）を確保します。
  - **タイル 1 (左上)**: X = `40pt`, Y = `100pt`, 幅 = `305pt`, 高さ = `115pt` (背景色: 淡いブルー `#E8F0FE`, 境界線なし)。
  - **タイル 2 (右上)**: X = `375pt`, Y = `100pt`, 幅 = `305pt`, 高さ = `115pt` (背景色: 淡いグリーン `#E6F4EA`, 境界線なし)。
  - **タイル 3 (左下)**: X = `40pt`, Y = `235pt`, 幅 = `305pt`, 高さ = `115pt` (背景色: 淡いイエロー `#FEF7E0`, 境界線なし)。
  - **タイル 4 (右下)**: X = `375pt`, Y = `235pt`, 幅 = `305pt`, 高さ = `115pt` (背景色: 淡いレッド `#FCE8E6`, 境界線なし)。
  - **各タイル内のテキスト配置**:
    - **見出し**: Y = `(各タイルの Y座標) + 15pt`, 幅 = `285pt`。Noto Sans JP 14px (Bold, 暗い灰色 `#202124`, 左寄せ)。
    - **本文詳細**: Y = `(各タイルの Y座標) + 45pt`, 幅 = `285pt`。Noto Sans JP 10px (Charcoal `#3C4043`, 左寄せ、行間 1.4x)。

---

## Layout & Spacing (Split 2-Column Slide Specific)
* **🎯 最適な適用シーン (どういう時に使うか)**:
  - **「ビジュアル要素（Matplotlib等で出力したグラフ画像、イメージ図など）」と「その解説文」を対比させたい場合、または「現状課題と未来解決策」を対比してドラマチックに示したい場合**。

### 🚨 物理衝突防止 ＆ 動的カラム比率決定ルール (CRITICAL COLLISION PREVENTION):
スライド内にグラフ画像と解説パネルを配置する際、**絶対に要素同士が重なり合ってはなりません（厳禁）。**
グラフ画像の重要度や見やすさに応じて、AIは以下の **3つの横幅比率モード** から最適なものを自律的に選択し、座標（X, Y）を **数式に基いて厳密に計算** して配置してください。

- **比率モードの選択基準**:
  1. **`Visual Focus (6:4) - グラフ重視 [超推奨]`**: グラフのデータや推移（例: サウナ中の自律神経推移）を大きくはっきりと見せたい場合。
  2. **`Standard (5:5) - 対等バランス`**: グラフの形状と解説テキストの文章量が同等である場合。
  3. **`Text Focus (4:6) - 解説文章重視`**: グラフは単純な傾向値であり、右側の解説カードで詳細な箇条書きや考察をたっぷり展開したい場合。

- **各比率モードにおける絶対座標計算式（隙間 gap = 40pt）**:
  - **共通開始位置**: グラフ左端 `X1 = 40pt`, `Y = 95pt`, `高さ = 270pt`
  - **計算方程式**: **`X2（解説パネル左端） = X1 (40pt) + グラフ幅 (W1) + 隙間 (40pt)`** （※この数式により、重なりは数学的に 100% 発生しなくなります）

  | 比率モード | グラフ幅 (`W1`) | 解説パネル幅 (`W2`) | 解説パネル左端 (`X2`) |
  | :--- | :--- | :--- | :--- |
  | **Visual Focus (6:4)** | **`360pt`** | **`240pt`** | **`440pt`** (`= 40 + 360 + 40`) |
  | **Standard (5:5)** | **`300pt`** | **`300pt`** | **`380pt`** (`= 40 + 300 + 40`) |
  | **Text Focus (4:6)** | **`240pt`** | **`360pt`** | **`320pt`** (`= 40 + 240 + 40`) |

---

### A) グラフ ＆ 考察 左右分割 (Chart & Text Split)
* **用途**: グラフ画像等のビジュアル要素と解説パネルを左右に配して説得力を出す時。
* **レイアウト構成**:
  - AIは上記の **「物理衝突防止 ＆ 動的カラム比率決定ルール」** に基づき、選択したモードの `W1`, `W2`, `X2` 座標を用いて要素を配置すること。
  - **左側 (グラフ画像)**: X = `40pt`, Y = `95pt`, 幅 = `W1`, 高さ = `270pt`。
  - **右側 (解説・考察カード - ROUNDED_RECTANGLE)**: X = `X2`, Y = `95pt`, 幅 = `W2`, 高さ = `270pt` (背景色: 淡いブルー `#E8F0FE` または `#F8F9FA`, 枠線 `#DADCE0` 1pt)。
  - **Matplotlib figsize 調整ルール**:
    - AIが Python ツールで折れ線グラフ等のグラフ画像を生成する際は、スライド上の描画比率 (`W1 / 270`) と一致するアスペクト比を Matplotlib の `figsize` に必ず指定すること（例: Visual Focus モードなら `W1 = 360pt, H = 270pt` ➡ アスペクト比 `4:3`。Matplotlib 側では `figsize=(8, 6)` など）。これにより、画像の自動引き伸ばしによるはみ出し・重なりを完全に防止します。

### B) 課題 ➡ 解決策のドラマチック対比 (Problem & Solution Double Cards)
* **用途**: 提案の導入部で、深刻な課題（左）と推奨解決アプローチ（右）を強力に対比して示す時。
* **レイアウト構成 (2つの特大対比カード - ROUNDED_RECTANGLE)**:
  - グラフ画像と同様に、Standard (5:5) 比率を基準に、左右の重なりを完全防止して配置します。
  - **左側カード (課題/Problem)**: X = `40pt`, Y = `95pt`, 幅 = `300pt`, 高さ = `270pt` (背景色: ソフトグレー `#F8F9FA`, 境界線: 薄い赤 `#FAD2CF` 2pt)。
    - **カード見出し**: Y = `120pt`, 幅 = `260pt`。フォント: Noto Sans JP 18px (Bold, 赤 `#EA4335`, 左寄せ)。
    - **本文詳細**: Y = `165pt`, 幅 = `260pt`。フォント: Noto Sans JP 12px (Charcoal `#3C4043`, 左寄せ、行間 1.5x)。
  - **右側カード (解決策/Solution)**: X = `380pt`, Y = `95pt`, 幅 = `300pt`, 高さ = `270pt` (背景色: 淡いブルー `#E8F0FE`, 境界線: 青 `#1A73E8` 2pt)。
    - **カード見出し**: Y = `120pt`, 幅 = `260pt`。フォント: Noto Sans JP 18px (Bold, 青 `#1A73E8`, 左寄せ)。
    - **本文詳細**: Y = `165pt`, 幅 = `260pt`。フォント: Noto Sans JP 12px (Charcoal `#3C4043`, 左寄せ、行間 1.5x)。
  - **安全マージン**: 左右の間に必ず **40pt** の安全な隙間（X=340〜380の間）を物理的に確保すること。

---

## Layout & Spacing (Data Summary & Key Metrics Slide Specific)
* **🎯 最適な適用シーン (どういう時に使うか)**:
  - **数値データ、KPI、削減コスト、特定の価格プラン、主要統計、または「大枠のサマリー数値 ＋ 詳細な内訳データテーブル」を提示したい場合**。

### A) キーデータ・ダブルカード (Keynote Double Stats)
* **用途**: 重要なデータ、決定的な2つのKPI、または2つの対比数値のみを強力に強調したい時。
* **レイアウト構成**:
  - **左側 (説明・補足領域)**: X = `40pt`, Y = `100pt`, 幅 = `260pt`, 高さ = `260pt`。補足説明や関連図をスマートに配置。
  - **右側 (ダブル角丸カード領域 - ROUNDED_RECTANGLE)**:
    - **カード 1**: X = `330pt`, Y = `120pt`, 幅 = `165pt`, 高さ = `230pt` (背景色: ソフトグレー `#F8F9FA` または淡いブルー `#E8F0FE`、枠線なし)。
    - **カード 2**: X = `515pt`, Y = `120pt`, 幅 = `165pt`, 高さ = `230pt` (背景色: ソフトグレー `#F8F9FA`、枠線なし)。
    - **カード内のテキスト配置 (各カード内共通)**:
      - **上部説明テキスト**: Y = `140pt`, 幅 = `145pt`。Noto Sans JP 12px, 灰色 `#5F6368` (中央寄せ)。
      - **中央巨大数値 (最重要)**: Y = `180pt` 〜 `210pt` 付近に, Noto Sans JP **48px〜54px (Bold)** の特大フォントで数値のみを配置 (色: Google Action Blue `#1A73E8`、中央寄せ)。
      - **下部補足説明**: Y = `265pt`, 幅 = `145pt`。Noto Sans JP 10px, 暗い灰色 `#3C4043` (中央寄せ)。

### B) サマリーカード ＆ 詳細テーブルマトリクス (Metrics Summary & Detail Table)
* **用途**: 複数のトータル数値サマリーを見せつつ、下部にその詳細内訳テーブルを並べて1枚で説得したい時。
* **レイアウト構成**:
  - **上部サマリーカード (3つ並列 - ROUNDED_RECTANGLE)**:
    - **カード 1**: X = `40pt`, Y = `100pt`, 幅 = `200pt`, 高さ = `80pt` (背景色: `#F8F9FA`, 境界線なし)。巨大数値テキスト (青色 `#1A73E8` 24px Bold) を中央配置。
    - **カード 2**: X = `260pt`, Y = `100pt`, 幅 = `200pt`, 高さ = `80pt` (背景色: `#E8F0FE`, 境界線なし)。巨大数値テキスト (緑色 `#34A853` 24px Bold) を中央配置。
    - **カード 3**: X = `480pt`, Y = `100pt`, 幅 = `200pt`, 高さ = `80pt` (背景色: `#F8F9FA`, 境界線なし)。巨大数値テキスト (赤色 `#EA4335` 24px Bold) を中央配置。
  - **下部詳細テーブル (TABLE)**:
    - X = `40pt`, Y = `200pt`, 幅 = `640pt`, 高さ = `150pt`
    - Slides API の `createTable` を使用し、詳細な内訳データを表形式でクリーンに描画。見出し行背景は `#F1F3F4`。

---

## Layout & Spacing (Hierarchical Layer / Stack Slide Specific)
* **🎯 最適な適用シーン (どういう時に使うか)**:
  - **システム構成図、ロードマップの階層、プロダクトスタック、または「ステアリングコミッティやPMOを中心とする高度なプロジェクト・ガバナンス体制図」を美しく表現したい場合**。

### A) 丸角スタック階層アーキテクチャ (Layered Stack Architecture)
* **用途**: 箇条書きでは複雑になりがちな階層構造を、角丸ブロックの美しい積み重ねとして視覚的に整理する時。
* **レイアウト構成 (ROUNDED_RECTANGLE の階層配置)**:
  - **上段 (上位/応用レイヤー)**: X = `40pt`, Y = `100pt`, 幅 = `640pt`, 高さ = `80pt` (背景: 淡いブルー `#E8F0FE`、境界線: 青 `#1A73E8`、線幅 = 2pt)。
  - **中段 (中位/プラットフォーム層)**: X = `40pt`, Y = `190pt`, 幅 = `640pt`, 高さ = `100pt` (背景: 純白 `#FFFFFF`、境界線: 薄いグレー `#DADCE0`、線幅 = 1pt)。
  - **下段 (下位/共通基盤レイヤー)**: X = `40pt`, Y = `300pt`, 幅 = `640pt`, 高さ = `60pt` (背景: ソフトグレー `#F8F9FA`、境界線なし)。
  - **各段のテキストおよびコンポーネント配置**:
    - 各段の上部に Noto Sans JP 12px (Bold, Charcoal `#202124`) のテキストでレイヤー名（例: "Applications and solutions" 等）を中央寄せで配置。
    - レイヤー内部には、等間隔に並べた小さな角丸ホワイトボックスや、関連するアイコン・テキストを X 軸方向に均等配置してください。

### B) プレミアム・プロジェクト・ガバナンス体制図 (Governance & Hub Spoke Slide)
* **用途**: 「最高意思決定機関 (Steering Committee) ➡ 推進事務局 (PMO) ➡ 各協働ステークホルダー」というプロジェクト推進のガバナンス体制図を圧倒的なリッチさで描く時。
* **レイアウト構成 (3階層ガバナンスツリー - ROUNDED_RECTANGLE & CONNECTORS)**:
  - **最上段 (意思決定カード)**: X = `260pt`, Y = `75pt`, 幅 = `200pt`, 高さ = `60pt` (背景色: ソフトラベンダー `#F1F3F4`、境界線: 薄いグレー `#DADCE0` 1pt)。見出し: "STEERING COMMITTEE" (Noto Sans JP 12px, Bold, Charcoal `#202124`, 中央寄せ)。
  - **中段中央 (事務局PMOカード - ハブ)**: X = `240pt`, Y = `175pt`, 幅 = `240pt`, 高さ = `130pt` (背景色: 淡いブルー `#E8F0FE`、境界線: 青 `#1A73E8` 2pt)。
    - **ハブタイトル**: Y = `195pt`, 幅 = `220pt`。フォント: Noto Sans JP 14px (Bold, 暗い灰色 `#202124`, 中央寄せ)。
    - **ハブ内バッジ (角丸ホワイトボックス)**: 
      - バッジ 1 (Project Control): X = `260pt`, Y = `250pt`, 幅 = `95pt`, 高さ = `25pt` (背景: `#FFFFFF`、境界なし)。
      - バッジ 2 (Quality Assurance): X = `365pt`, Y = `250pt`, 幅 = `95pt`, 高さ = `25pt` (背景: `#FFFFFF`、境界なし)。
  - **下段左 (クライアント・ステークホルダーカード)**: X = `40pt`, Y = `175pt`, 幅 = `180pt`, 高さ = `130pt` (背景色: ソフトグレー `#F8F9FA`、境界線なし)。
    - タイトル: "CLIENT STAKEHOLDERS" (Noto Sans JP 12px Bold, 中央寄せ) を上部に配置。
    - 中に "Requirement gathering", "User Acceptance Testing" 等 of 役割を示すホワイトバッジを等間隔に配置。
  - **下段右 (戦略パートナーカード)**: X = `500pt`, Y = `175pt`, 幅 = `180pt`, 高さ = `130pt` (背景色: ソフトグレー `#F8F9FA`、境界線なし)。
    - タイトル: "STRATEGIC PARTNERS" (Noto Sans JP 12px Bold, 中央寄せ) を上部に配置.
    - 中に "Integration services", "Technology consulting" 等 of 役割を示すホワイトバッジを等間隔に配置。
  - **スマートコネクタ線 (CONNECTORS)**:
    - 最上段から中段中央へ垂直に 1本、中段中央から左右のカードへ向けて水平に 2本、スマート接続線を描画。
  - **幾何学Blob装飾 (半透明トリプルELLIPSE重ね合わせ)**: 空間をリッチに埋めるため、スライド右上および左下隅に淡いブルーとスカイブルーの半透明楕円をうっすらと重ねて配置（線なし）。

---

## Layout & Spacing (Timeline & Roadmaps Slide Specific)
* **🎯 最適な適用シーン (どういう時に使うか)**:
  - **「初心者がプロになるロードマップ」、「プロジェクトのフェーズ別タイムライン」、「中長期の戦略成長マップ」を提示する場合**。

### A) 左右完全対比プレミアム・タイムライン (Premium Split Timeline)
* **用途**: 左側に「時期・段階バッジ」、右側に「具体的な行動・詳細カード」を綺麗に並列配置し、中央を一本の美しいタイムラインで繋ぐ、最も判読性が高く洗練されたタイムラインレイアウト。
* **レイアウト構成 (時期バッジ ➡ タイムライン丸 ➡ 詳細カード の完璧な左右整列)**:
  - **タイムライン中央縦線 (RECTANGLE)**: X = `200pt`, Y = `80pt`, 幅 = `2pt`, 高さ = `270pt` (背景色: 青 `#1A73E8`)。
  - **ステップごとの垂直位置 (Y座標)**:
    - **ステップ 1**: Y = `90pt`
    - **ステップ 2**: Y = `185pt`
    - **ステップ 3**: Y = `280pt`
  - **各ステップのコンポーネント配置**:
    - **左側 (時期・段階バッジ - ROUNDED_RECTANGLE)**: X = `40pt`, Y = `(各ステップのY座標) + 15pt`, 幅 = `140pt`, 高さ = `40pt` (背景色: 淡いブルー `#E8F0FE`、枠線なし)。
      - バッジテキストは、必ず `add_custom_shape` の `text` 引数を使い、一発で中央寄せ（CENTER/MIDDLE）で埋め込むこと（例: `"1ヶ月目 / 入門期"`）。フォント: Noto Sans JP 12px (Bold, 青 `#1A73E8`)。
    - **中央 (タイムライン丸 - ELLIPSE)**: X = `180pt`, Y = `(各ステップのY座標) + 15pt`, 幅 = `40pt`, 高さ = `40pt` (背景色: `#FFFFFF`、境界線: 青 `#1A73E8` 2pt)。
      - 丸数字は、絶対に上にテキストボックスを重ねてはならず、**必ず `add_custom_shape` の `text` 引数に数字（例: `"1"`, `"2"`, `"3"`）を直接指定して一発で完璧な中央配置で埋め込むこと！** これによりズレを物理的に 100% 排除します。フォント: Noto Sans JP 16px (Bold, 暗い灰色 `#202124`)。
    - **右側 (詳細説明カード - ROUNDED_RECTANGLE)**: X = `240pt`, Y = `各ステップのY座標`, 幅 = `440pt`, 高さ = `75pt` (背景色: ソフトグレー `#F8F9FA`、境界線: 薄いグレー `#DADCE0` 1pt)。
      - この右側詳細説明カードには、`add_custom_shape` の `text` 引数を利用してタイトルと箇条書き説明を直接埋め込みます。
      - 例: `text` = `"【入門期】マナーと基本プロセスの習得\\n温冷交代浴に体を慣らし、無理のない範囲で3ステップを実践する。"`
      - 文字数が多い場合でも、自動フォントサイズ縮小（Autofit）と十分なマージン設計によって、枠内に美しく折り返されて収まります。