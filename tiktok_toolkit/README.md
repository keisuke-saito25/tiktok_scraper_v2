# tiktok_toolkit - GUI型TikTokスクレイピングツール

![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-green.svg)
![Selenium](https://img.shields.io/badge/WebDriver-Selenium-orange.svg)

直感的なGUIインターフェースを提供するTikTokデータ収集ツールです。非技術者でも簡単に操作できるよう設計されており、Excel楽曲データの処理からスクリーンショット取得まで包括的な機能を提供します。

## 🎯 主要機能

### 🖥️ ユーザーインターフェース
- **直感的なGUI**: Tkinterによる使いやすいインターフェース
- **リアルタイム進捗表示**: 処理状況の可視化
- **エラー通知**: 分かりやすいエラーメッセージ
- **設定保存**: 前回の設定値の自動保存

### 📊 データ処理機能
- **Excel楽曲データ処理**: .xlsx/.xlsファイルの自動読み込み
- **楽曲情報スクレイピング**: TikTok楽曲ページからの詳細情報取得
- **データ統合**: 複数ソースからのデータマージ
- **出力形式**: Excel形式での結果保存

### ⚡ 高性能処理
- **マルチスレッド並行処理**: 複数楽曲の同時処理
- **処理効率最適化**: 最適な待機時間とリクエスト管理
- **メモリ効率**: 大容量データセットの効率的処理
- **中断・再開機能**: 処理中断からの復旧サポート

### 📸 画像・スクリーンショット機能
- **自動スクリーンショット**: ページキャプチャ自動取得
- **画像最適化**: 適切なサイズ・品質での保存
- **ファイル管理**: 組織化されたファイル構造

## 🏗️ アーキテクチャ概要

```
┌─────────────────────────────────────┐
│           tiktok_toolkit            │
├─────────────────────────────────────┤
│                                     │
│  ┌─────────────┐  ┌─────────────┐   │
│  │ Tkinter GUI │  │   Config    │   │
│  │             │  │   Manager   │   │
│  │ • UI Components │ • JSON設定   │   │
│  │ • Event Handler │ • 設定保存   │   │
│  │ • Progress View │ • 設定復元   │   │
│  └─────────────┘  └─────────────┘   │
│           │               │         │
│  ┌─────────────────────────────────┐ │
│  │        Excel Processor         │ │
│  │                                │ │
│  │ • openpyxl Integration         │ │
│  │ • Data Validation              │ │
│  │ • Multiple Sheet Support       │ │
│  └─────────────────────────────────┘ │
│           │                         │
│  ┌─────────────────────────────────┐ │
│  │      Selenium WebDriver         │ │
│  │                                │ │
│  │ • Chrome Driver Manager        │ │
│  │ • Multi-threaded Execution     │ │
│  │ • Screenshot Capture           │ │
│  │ • Anti-bot Measures           │ │
│  └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

## 📁 プロジェクト構造

```
tiktok_toolkit/
├── tiktok.py              # メインアプリケーション
├── config.json           # 設定ファイル
├── requirements.txt      # Python依存関係
├── initial_settings.xlsx # サンプル楽曲データ
├── run_tiktok.bat       # Windows実行用バッチファイル
├── vidIQ.crx            # Chrome拡張（必要に応じて）
└── README.md            # このファイル
```

### ファイル詳細

- **`tiktok.py`**: メインのPythonアプリケーション、GUI制御とスクレイピング logic
- **`config.json`**: アプリケーション設定（target_time など）
- **`requirements.txt`**: 必要なPythonパッケージリスト
- **`initial_settings.xlsx`**: サンプル楽曲データファイル
- **`run_tiktok.bat`**: Windows環境での簡単実行用バッチファイル

## ⚙️ システム要件

### 🔧 必須環境
- **Python**: 3.7以上
- **Chrome Browser**: 最新版（WebDriver用）
- **OS**: Windows, macOS, Linux
- **RAM**: 4GB以上推奨
- **ストレージ**: 500MB以上の空き容量

### 📦 依存関係
```
selenium>=4.0.0
openpyxl>=3.0.0
pandas>=1.3.0
webdriver-manager>=3.8.0
Pillow>=8.0.0
requests>=2.25.0
```

## 🚀 インストール・セットアップ

### 1️⃣ リポジトリのクローン
```bash
git clone <リポジトリのURL>
cd tiktok_scraper/tiktok_toolkit
```

### 2️⃣ Python仮想環境の作成
```bash
# Python仮想環境作成
python3 -m venv venv

# 仮想環境の有効化
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### 3️⃣ 依存関係のインストール
```bash
pip install -r requirements.txt
```

### 4️⃣ 設定ファイルの確認
`config.json` ファイルの内容を確認し、必要に応じて調整：

```json
{
  "target_time": 30,
  "output_directory": "./output",
  "screenshot_enabled": true,
  "max_concurrent_threads": 5
}
```

## 🎮 使用方法

### 基本的な実行方法

#### コマンドライン実行
```bash
python3 tiktok.py
```

#### Windows バッチファイル実行
```bash
run_tiktok.bat
```

### 📋 操作手順

1. **アプリケーション起動**: `python3 tiktok.py` でGUIが開きます

2. **楽曲データファイル選択**: 
   - 「ファイル選択」ボタンをクリック
   - Excel楽曲データファイル（.xlsx/.xls）を選択

3. **処理オプション設定**:
   - スクリーンショット取得: チェックボックスで有効/無効
   - 並行処理数: スライダーで調整（1-10スレッド）
   - 出力フォルダ: 結果保存先の指定

4. **処理実行**:
   - 「開始」ボタンをクリック
   - 進捗バーで処理状況を確認
   - エラーが発生した場合、詳細がログに表示

5. **結果確認**:
   - 指定した出力フォルダ内に処理結果を保存
   - Excel形式で楽曲情報・統計データを出力
   - スクリーンショット画像（有効な場合）

### 📊 Excel楽曲データの形式

入力Excelファイルは以下の列を含む必要があります：

| 列名 | 説明 | 例 |
|-----|------|-----|
| song_title | 楽曲タイトル | "Blinding Lights" |
| artist_name | アーティスト名 | "The Weeknd" |
| tiktok_url | TikTok楽曲URL | https://www.tiktok.com/music/... |
| release_date | リリース日 | 2019-11-29 |

## 🔧 カスタマイズ・設定

### ⚙️ config.json 設定項目

```json
{
  "target_time": 30,              // 楽曲再生時間（秒）
  "output_directory": "./output", // 出力フォルダパス
  "screenshot_enabled": true,     // スクリーンショット有効/無効
  "max_concurrent_threads": 5,    // 最大並行スレッド数
  "wait_time_min": 2,            // 最小待機時間（秒）
  "wait_time_max": 5,            // 最大待機時間（秒）
  "retry_attempts": 3,           // リトライ試行回数
  "headless_mode": false,        // ヘッドレス実行（デバッグ用）
  "user_agent": "custom-agent"   // カスタムUser-Agent
}
```

### 🎛️ GUI要素のカスタマイズ

アプリケーションのUIは `tiktok.py` 内のTkinterコンポーネントで定義されています：

```python
# メインウィンドウ設定
self.root = tk.Tk()
self.root.title("TikTok Toolkit - 楽曲データ収集ツール")
self.root.geometry("800x600")

# カスタマイズ例
self.root.configure(bg='#f0f0f0')  # 背景色変更
```

## 🏗️ ビルド・配布

### 📦 実行ファイル作成（PyInstaller）

#### 基本的なビルド
```bash
pyinstaller --onefile tiktok.py
```

#### 詳細な設定でのビルド
```bash
pyinstaller \
    --onefile \
    --windowed \
    --name "TikTok_Toolkit" \
    --icon=icon.ico \
    --add-data "config.json:." \
    --add-data "initial_settings.xlsx:." \
    tiktok.py
```

#### Windows向けビルド設定
```bash
pyinstaller \
    --onefile \
    --windowed \
    --name "TikTok_Toolkit.exe" \
    --distpath ./dist/windows \
    --workpath ./build/windows \
    tiktok.py
```

### 📋 配布パッケージの構成
```
TikTok_Toolkit_v1.0/
├── TikTok_Toolkit.exe       # 実行ファイル
├── config.json             # 設定ファイル
├── initial_settings.xlsx   # サンプルデータ
├── README.txt             # 使用説明書
└── LICENSE.txt           # ライセンス情報
```

## 📊 パフォーマンス・最適化

### ⚡ 処理性能の向上

#### マルチスレッド設定
- **推奨スレッド数**: CPU コア数の2倍
- **メモリ使用量**: スレッド数 × 約50MB
- **最適化**: `max_concurrent_threads` を調整

#### WebDriver最適化
```python
# Chrome オプション例
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
```

### 🧠 メモリ使用量管理
- **大量データ処理**: バッチサイズの調整
- **画像処理**: 適切な圧縮設定
- **ガベージコレクション**: 定期的なメモリ解放

## 🛡️ セキュリティ・倫理的考慮

### 📋 TikTok利用規約遵守
- **Rate Limiting**: 適切な間隔でのリクエスト送信
- **User-Agent**: 適切なブラウザ識別情報
- **robots.txt**: クローリングガイドラインの確認

### 🔒 データ保護
- **個人情報の除外**: ユーザー特定情報の非収集
- **ローカルストレージ**: データの本体外流出防止
- **ログ管理**: 機密情報のログ出力回避

### ⚖️ 法的コンプライアンス
- **著作権**: 楽曲メタデータのフェアユース
- **プライバシー**: 個人データ保護法の遵守
- **商用利用**: 利用規約の範囲内での使用

## 🐛 トラブルシューティング

### よくある問題と解決方法

#### 1. WebDriver関連エラー
**症状**: `ChromeDriver` または WebDriver に関するエラー
```
解決方法:
1. Chrome ブラウザを最新版に更新
2. webdriver-manager で ChromeDriver を再インストール:
   pip install --upgrade webdriver-manager
3. 手動でのChromeDriverパス指定
```

#### 2. Excel ファイル読み込みエラー
**症状**: `openpyxl` または Excel ファイル関連エラー
```
解決方法:
1. Excel ファイルの形式を確認（.xlsx/.xls）
2. ファイルが他のアプリケーションで開かれていないことを確認
3. ファイル権限の確認（読み取り権限）
4. openpyxl の再インストール: pip install --upgrade openpyxl
```

#### 3. GUI表示問題
**症状**: Tkinter GUI が正しく表示されない
```
解決方法:
1. tkinter のインストール確認:
   - Linux: sudo apt-get install python3-tk
   - Mac: brew install python-tk
2. Python バージョンの確認（3.7以上）
3. ディスプレイ設定の確認（リモート環境の場合）
```

#### 4. メモリ・パフォーマンス問題
**症状**: アプリケーションの動作が重い、メモリ不足
```
解決方法:
1. max_concurrent_threads を削減（3-5に設定）
2. screenshot_enabled を無効化
3. 大量データを小分けして処理
4. 不要なアプリケーションの終了
```

#### 5. TikTok接続エラー
**症状**: TikTokページにアクセスできない
```
解決方法:
1. インターネット接続の確認
2. VPN/プロキシ設定の確認
3. TikTok サービス状況の確認
4. User-Agent の更新
5. 待機時間の増加（wait_time_min/max を調整）
```

### 🔧 デバッグモード

デバッグ情報を有効にするには、`config.json` で以下を設定：

```json
{
  "debug_mode": true,
  "verbose_logging": true,
  "headless_mode": false
}
```

### 📞 サポート・ログ情報

問題が発生した場合、以下の情報を収集してください：

1. **エラーメッセージ**: 完全なエラーログ
2. **環境情報**: OS、Pythonバージョン、Chromeバージョン
3. **設定ファイル**: `config.json` の内容
4. **入力データ**: 使用したExcelファイルの形式例
5. **実行ログ**: アプリケーション実行時の出力

## 📈 将来の拡張予定

### 🔮 計画中の機能
- **プラグインシステム**: サードパーティ拡張サポート
- **クラウド統合**: Google Sheets、OneDrive連携
- **高度な分析**: AI powered データ分析機能
- **マルチプラットフォーム**: macOS、Linux向けネイティブ対応

### 🤝 コントリビューション

プロジェクトへの貢献を歓迎します：

1. **Issue 報告**: バグ報告・機能要望
2. **コード提供**: Pull Request での改善提案
3. **ドキュメント**: README、コメントの改善
4. **テスト**: 様々な環境でのテスト実行

### 📄 ライセンス情報

このプロジェクトは適切なライセンスの下で提供されています。商用利用の際は関連する利用規約を確認してください。

---

**🎵 TikTok楽曲データの収集を始めましょう！**

追加の質問やサポートが必要な場合は、プロジェクトのIssueページまたはメンテナーにお問い合わせください。