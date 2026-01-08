# TikTok Scraper - TikTokデータ収集・分析ツールキット

![TikTok Scraper](https://img.shields.io/badge/TikTok-Scraper-FF0050.svg)
![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![Vue.js](https://img.shields.io/badge/Vue.js-3-4FC08D.svg)
![TypeScript](https://img.shields.io/badge/TypeScript-5.x-blue.svg)

TikTokの楽曲ページからUGC（ユーザー生成コンテンツ）データを収集し、分析・可視化するための包括的なツールキットです。

## 📋 目次

- [プロジェクト構成](#-プロジェクト構成)
- [各ツールの概要](#-各ツールの概要)
- [クイックスタート](#-クイックスタート)
- [システム要件](#-システム要件)
- [ドキュメント](#-ドキュメント)
- [主要機能](#-主要機能)
- [アーキテクチャ](#-アーキテクチャ)

## 📁 プロジェクト構成

```
tiktok_scraper/
├── tiktok_toolkit/          # 🖥️ GUI型スクレイピングツール
│   ├── tiktok.py           # メインアプリケーション (Tkinter GUI)
│   ├── config.json         # 設定ファイル
│   ├── requirements.txt    # Python依存関係
│   └── initial_settings.xlsx  # 楽曲URL設定ファイル
│
├── tiktok_ugc_scraper/     # ⚡ CLI型スクレイパー（並列処理対応）
│   ├── src/
│   │   ├── main.py         # エントリポイント
│   │   ├── config.py       # 設定管理
│   │   └── modules/        # スクレイピングモジュール
│   │       ├── scraper.py      # UGC取得処理
│   │       ├── excel_utils.py  # Excel操作
│   │       ├── constants.py    # 定数定義
│   │       ├── parsing_utils.py  # パース処理
│   │       └── logger.py       # ログ設定
│   ├── config.json         # 設定ファイル
│   └── requirements.txt    # Python依存関係
│
├── tiktok_ugc_chart/       # 📊 Vue.js Webダッシュボード
│   ├── src/
│   │   ├── App.vue         # メインアプリケーション
│   │   ├── components/     # Vueコンポーネント
│   │   │   ├── UGCChart.vue        # UGCチャート
│   │   │   ├── TikTokRanking.vue   # ランキング
│   │   │   ├── AccountsTable.vue   # アカウント表
│   │   │   └── DateRangeFilter.vue # 日付フィルタ
│   │   ├── types/          # TypeScript型定義
│   │   └── utils/          # ユーティリティ関数
│   ├── package.json        # Node.js依存関係
│   └── vite.config.ts      # Vite設定
│
├── scripts/                # 🔄 並列実行用スクリプト
│   ├── run_collect.bat     # 並列収集の起動
│   ├── run_apply.bat       # 収集結果の統合
│   └── stop_collect.bat    # プロセス停止
│
└── docs/                   # 📚 ドキュメント
```

## 🎯 各ツールの概要

### 🖥️ tiktok_toolkit - GUI型スクレイピングツール

| 項目 | 内容 |
|------|------|
| **技術スタック** | Python 3.x + Tkinter + Selenium |
| **主な機能** | • 直感的なGUI操作<br>• 楽曲ページから動画URL収集<br>• 動画詳細情報（再生数、いいね数等）取得<br>• ログイン状態の自動確認<br>• スクリーンショット保存 |
| **対象ユーザー** | 非技術者・GUI操作希望者 |

### ⚡ tiktok_ugc_scraper - CLI型スクレイパー

| 項目 | 内容 |
|------|------|
| **技術スタック** | Python 3.x + Selenium + openpyxl |
| **主な機能** | • 4つの動作モード（process/retry/collect/apply）<br>• シャーディングによる並列処理<br>• 堅牢なリトライ機能<br>• CSV/Excel連携 |
| **対象ユーザー** | 開発者・自動化運用担当者 |

**動作モード**:
- `process`: 全楽曲のUGC数を取得
- `retry`: 失敗した楽曲を再処理
- `collect`: 並列収集（複数ワーカー）
- `apply`: 収集結果をExcelに統合

### 📊 tiktok_ugc_chart - Webダッシュボード

| 項目 | 内容 |
|------|------|
| **技術スタック** | Vue 3 + TypeScript + Vuetify 3 + Chart.js |
| **主な機能** | • UGC推移チャート表示<br>• アカウントランキング生成<br>• フォロワー数表示<br>• 画像エクスポート |
| **対象ユーザー** | データ分析・マーケティング担当者 |

## 🚀 クイックスタート

### 1️⃣ tiktok_toolkit（GUIツール）

```bash
cd tiktok_toolkit
python -m venv venv
venv\Scripts\activate    # Windows
pip install -r requirements.txt
python tiktok.py
```

### 2️⃣ tiktok_ugc_scraper（CLIツール）

```bash
cd tiktok_ugc_scraper
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt

# 全楽曲のUGC数を取得
python src/main.py process --settings initial_settings.xlsx

# 並列収集
cd ../scripts
run_collect.bat
run_apply.bat
```

### 3️⃣ tiktok_ugc_chart（Webダッシュボード）

```bash
cd tiktok_ugc_chart
npm install
npm run dev
# ブラウザで http://localhost:5173 にアクセス
```

## ⚙️ システム要件

### 共通

- **Google Chrome**: 最新版
- **OS**: Windows 10/11（推奨）、macOS、Linux

### Python環境

```
Python 3.7+
selenium
openpyxl
pandas
webdriver-manager
Pillow
psutil
```

### Node.js環境

```
Node.js 18+
npm 9+
vue ^3.5.13
vuetify ^3.7.12
chart.js ^4.4.8
xlsx ^0.18.5
typescript ~5.7.3
```

## 📚 ドキュメント

詳細なドキュメントは`docs/`ディレクトリにあります：

| ファイル | 内容 |
|---------|------|
| [01_system_overview.md](docs/01_system_overview.md) | システム全体の概要 |
| [02_architecture.md](docs/02_architecture.md) | アーキテクチャ図（Mermaid） |
| [03_tiktok_toolkit.md](docs/03_tiktok_toolkit.md) | GUIツールの詳細仕様 |
| [04_tiktok_ugc_scraper.md](docs/04_tiktok_ugc_scraper.md) | CLIツールの詳細仕様 |
| [05_tiktok_ugc_chart.md](docs/05_tiktok_ugc_chart.md) | Webダッシュボードの詳細 |
| [06_parallel_processing.md](docs/06_parallel_processing.md) | 並列処理スクリプトの解説 |
| [07_setup_guide.md](docs/07_setup_guide.md) | セットアップ・運用ガイド |

## 🔧 主要機能

### データ収集

- **UGC数取得**: TikTok楽曲ページから動画総数を取得
- **動画詳細取得**: 個別動画の再生数、いいね数、コメント数、フォロワー数
- **並列処理**: シャーディングによる効率的な大量データ収集

### データ管理

- **Excel連携**: openpyxlによるExcel読み書き
- **差分管理**: 日次のUGC増減を自動計算
- **CSV出力**: 並列処理結果の中間保存

### 可視化・分析

- **UGCチャート**: 時系列でのUGC推移グラフ
- **ランキング**: 再生数/いいね数/フォロワー数ランキング
- **画像エクスポート**: チャート・ランキングの画像保存

## 🏗️ アーキテクチャ

```
┌─────────────────────────────────────────────────────────────────────┐
│                        入力データ                                    │
│  ・楽曲マスタ（Excel）: 曲名とTikTok楽曲URL                         │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    スクレイピング処理                                │
│  ┌──────────────────┐    ┌──────────────────┐                      │
│  │  tiktok_toolkit  │    │ tiktok_ugc_scraper│                      │
│  │      (GUI)       │    │      (CLI)        │                      │
│  └──────────────────┘    └──────────────────┘                      │
│              │                    │                                  │
│              └────────┬───────────┘                                  │
│                       ▼                                              │
│               Selenium WebDriver + Chrome                            │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      TikTok_UGC.xlsx                                 │
│  ・楽曲マスタ: 曲名とURL                                            │
│  ・UGCシート: 日付ごとのUGC数                                       │
│  ・増減シート: 前日比                                               │
│  ・日付シート: 各動画の詳細                                         │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    tiktok_ugc_chart                                  │
│  ・UGC推移チャート                                                   │
│  ・アカウントランキング                                              │
│  ・画像エクスポート                                                  │
└─────────────────────────────────────────────────────────────────────┘
```

## 🛡️ セキュリティ・倫理的考慮事項

- **利用規約遵守**: TikTok利用規約の厳格な遵守
- **レート制限**: 適切な間隔でのリクエスト送信
- **プライバシー**: 収集データの適切な管理

## 📝 開発・コントリビューション

### コーディング規約

- **Python**: PEP 8準拠
- **Vue.js/TypeScript**: ESLint + Prettier
- **コメント**: 日本語（業務ロジック説明用）

### ビルド

```bash
# Python実行ファイル
cd tiktok_toolkit
pyinstaller --onefile tiktok.py

# Vue.js本番ビルド
cd tiktok_ugc_chart
npm run build
```

## 📄 ライセンス

このプロジェクトは適切なライセンスの下で提供されています。

---

**各ツールの詳細な使用方法は、[docs/](docs/)ディレクトリのドキュメントをご覧ください。**