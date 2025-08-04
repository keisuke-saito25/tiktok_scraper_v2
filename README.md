# TikTok Scraper - 包括的なTikTokデータ分析・収集ツールキット

![TikTok Scraper](https://img.shields.io/badge/TikTok-Scraper-FF0050.svg)
![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![Vue.js](https://img.shields.io/badge/Vue.js-3-4FC08D.svg)
![TypeScript](https://img.shields.io/badge/TypeScript-4.x-blue.svg)

TikTokデータの収集、分析、可視化のための包括的なツールキットです。GUI、Web、CLIの3つの異なるインターフェースを提供し、用途に応じて最適なツールを選択できます。

## 🏗️ プロジェクト構成

このリポジトリは3つのメインコンポーネントで構成されています：

```
tiktok_scraper/
├── tiktok_toolkit/          # 🖥️ GUI型スクレイピングツール
│   ├── tiktok.py           # メインアプリケーション（Tkinter GUI）
│   ├── requirements.txt    # Python依存関係
│   ├── config.json        # 設定ファイル
│   └── run_tiktok.bat     # Windows実行用バッチファイル
├── tiktok_ugc_chart/       # 📊 Vue.js Webダッシュボード
│   ├── src/
│   │   ├── App.vue        # メインアプリケーション
│   │   ├── components/    # Vueコンポーネント
│   │   ├── types/         # TypeScript型定義
│   │   └── utils/         # ユーティリティ関数
│   ├── package.json       # Node.js依存関係・スクリプト
│   └── vite.config.ts     # Vite設定
└── tiktok_ugc_scraper/     # ⚡ コマンドライン型スクレイパー
    ├── src/
    │   ├── main.py        # エントリーポイント
    │   ├── config.py      # 設定管理
    │   └── modules/       # スクレイパーモジュール
    ├── requirements.txt   # Python依存関係
    └── config.json       # 設定ファイル
```

## 🎯 各プロジェクトの概要

### 🖥️ tiktok_toolkit - GUI型スクレイピングツール
- **技術スタック**: Python 3.x + Tkinter + Selenium
- **主要機能**: 
  - 直感的なGUIインターフェース
  - Excel楽曲データの処理
  - マルチスレッド並行処理
  - スクリーンショット機能
  - PyInstaller実行ファイル作成
- **対象ユーザー**: 非技術者・GUI操作希望者
- **詳細**: [tiktok_toolkit/README.md](./tiktok_toolkit/README.md)

### 📊 tiktok_ugc_chart - Vue.js Webダッシュボード
- **技術スタック**: Vue 3 + TypeScript + Vuetify + Chart.js
- **主要機能**:
  - インタラクティブデータ可視化
  - Material Designベース UI
  - リアルタイムチャート更新
  - Excel データインポート・エクスポート
  - レスポンシブWebデザイン
- **対象ユーザー**: データ分析・可視化担当者
- **詳細**: [tiktok_ugc_chart/README.md](./tiktok_ugc_chart/README.md)

### ⚡ tiktok_ugc_scraper - コマンドライン型スクレイパー
- **技術スタック**: Python 3.x + Selenium + pandas
- **主要機能**:
  - Process/Retryモード対応
  - モジュラーアーキテクチャ
  - UGC差分管理
  - 包括的ログシステム
  - 実行ファイル生成
- **対象ユーザー**: 開発者・自動化運用担当者
- **詳細**: [tiktok_ugc_scraper/README.md](./tiktok_ugc_scraper/README.md)

## 🔄 アーキテクチャ概要

```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│   tiktok_toolkit    │    │  tiktok_ugc_chart   │    │ tiktok_ugc_scraper  │
│   (GUI Interface)   │    │  (Web Dashboard)    │    │  (CLI Interface)    │
├─────────────────────┤    ├─────────────────────┤    ├─────────────────────┤
│ • Tkinter GUI       │    │ • Vue 3 + TypeScript│    │ • Command Line      │
│ • User-friendly     │    │ • Interactive Charts│    │ • Batch Processing  │
│ • Excel Processing  │    │ • Data Visualization│    │ • Process/Retry     │
│ • Screenshot        │    │ • Export Functions  │    │ • Module Structure  │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
           │                         │                         │
           └─────────────────────────┼─────────────────────────┘
                                     │
                    ┌─────────────────────────────────┐
                    │        Selenium WebDriver       │
                    │      + TikTok Data Source       │
                    │                                 │
                    │  • Chrome WebDriver             │
                    │  • Anti-bot Measures           │
                    │  • Rate Limiting                │
                    │  • Excel Data I/O               │
                    └─────────────────────────────────┘
```

## ⚙️ システム要件

### 🔧 必須環境
- **Python**: 3.7以上
- **Node.js**: 14.x以上 (tiktok_ugc_chartのみ)
- **Chrome Browser**: 最新版
- **OS**: Windows, macOS, Linux

### 📦 主要依存関係

#### Python共通
```
selenium
pandas
openpyxl
webdriver-manager
```

#### Vue.js (tiktok_ugc_chart)
```
vue: ^3.x
typescript: ^5.x
vuetify: ^3.x
chart.js: ^4.x
vite: ^5.x
```

## 🚀 クイックスタート

### 1️⃣ GUI型ツール (tiktok_toolkit)
```bash
cd tiktok_toolkit
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or venv\Scripts\activate  # Windows
pip install -r requirements.txt
python3 tiktok.py
```

### 2️⃣ Webダッシュボード (tiktok_ugc_chart)
```bash
cd tiktok_ugc_chart
npm install
npm run dev
# ブラウザで http://localhost:5173 にアクセス
```

### 3️⃣ CLI型スクレイパー (tiktok_ugc_scraper)
```bash
cd tiktok_ugc_scraper
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 src/main.py process
```

## 📊 主要機能詳細

### 🎵 データ処理機能
- **楽曲情報スクレイピング**: TikTok UGCデータの自動収集
- **Excel統合**: .xlsx/.xlsファイルの読み込み・書き出し
- **差分管理**: データ更新履歴の追跡・管理
- **画像処理**: スクリーンショット自動取得

### 📈 可視化・分析機能
- **インタラクティブチャート**: Chart.jsによる動的グラフ
- **フィルタリング**: 日付範囲・カテゴリ別データ絞り込み
- **エクスポート**: CSV/Excel形式での分析結果出力
- **リアルタイム更新**: ライブデータフィード対応

### 🔧 運用・保守機能
- **ログシステム**: 包括的な実行ログ管理
- **エラー復旧**: 失敗処理の自動リトライ機能
- **設定管理**: JSON設定ファイルによる柔軟な制御
- **実行ファイル作成**: PyInstaller/npmビルドサポート

## 🛡️ セキュリティ・倫理的考慮事項

### 📋 Webスクレイピング倫理
- **利用規約遵守**: TikTok Terms of Serviceの厳格な遵守
- **レート制限**: 適切な間隔でのリクエスト送信
- **robots.txt尊重**: クローリングガイドラインの遵守
- **データプライバシー**: 個人情報の適切な取り扱い

### 🔒 セキュリティ対策
- **API キー保護**: 設定ファイルの適切な管理
- **ログ情報**: 機密情報の非出力設定
- **ファイル権限**: 実行権限の最小化
- **依存関係更新**: セキュリティパッチの定期適用

## 🔧 開発・カスタマイズ

### 📝 コーディング規約
- **Python**: PEP 8準拠
- **Vue.js/TypeScript**: ESLint + Prettier
- **命名規則**: snake_case (Python), kebab-case (Vue)
- **コメント**: 日本語による業務ロジック説明

### 🧪 品質管理
- **型検査**: `npm run type-check` (Vue.js)
- **Linting**: `npm run lint` (Vue.js)
- **手動テスト**: Selenium-based動作確認

### 🏗️ ビルド・配布
```bash
# Python実行ファイル作成
pyinstaller --onefile tiktok.py

# Vue.js本番ビルド
npm run build

# ビルド成果物の配布準備
```

## 📚 トラブルシューティング

### 🔍 よくある問題
- **WebDriver エラー**: Chromeバージョンとの互換性確認
- **Excel 読み込み失敗**: ファイル形式・権限の確認
- **UI レンダリング問題**: ブラウザキャッシュクリア
- **依存関係エラー**: 仮想環境の再作成

### 📞 サポート情報
- **ログファイル**: `app.log` (Python), Developer Tools (Vue.js)
- **設定確認**: `config.json` ファイル内容検証
- **環境変数**: PATH, PYTHONPATH設定確認

## 📄 ライセンス・著作権

このプロジェクトは適切なライセンスの下で提供されています。商用利用・再配布の際は関連する利用規約を確認してください。

## 🤝 コントリビューション

プロジェクトへの貢献を歓迎します：
- **Issue報告**: バグ・機能要望の投稿
- **Pull Request**: コード改善・新機能の提案
- **ドキュメント改善**: README・コメントの充実
- **テスト追加**: 品質向上への協力

---

**🚀 さあ、TikTokデータ分析を始めましょう！**

各プロジェクトの詳細な使用方法は、それぞれのREADMEファイルをご覧ください。