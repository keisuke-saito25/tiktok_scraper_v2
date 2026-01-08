# tiktok_ugc_scraper 詳細ドキュメント

## 概要

`tiktok_ugc_scraper`は、TikTok楽曲ページからUGC数（ユーザー生成コンテンツ数）を収集するためのコマンドラインツールです。シャーディングによる並列処理に対応し、大量データの効率的な収集が可能です。

## ファイル構成

```
tiktok_ugc_scraper/
├── src/
│   ├── main.py              # エントリポイント（684行）
│   ├── config.py            # 設定管理
│   ├── process_runner.py    # processモード実行補助
│   ├── retry_runner.py      # retryモード実行補助
│   └── modules/
│       ├── __init__.py
│       ├── constants.py     # 定数定義
│       ├── scraper.py       # スクレイピング処理
│       ├── excel_utils.py   # Excel操作
│       ├── parsing_utils.py # パース処理
│       └── logger.py        # ログ設定
├── config.json              # 設定ファイル
├── requirements.txt         # Python依存関係
├── scraping.xlsx            # サンプルデータ
└── tiktok_cli.spec          # PyInstaller設定
```

## 動作モード

### 1. process モード

設定ファイルに記載された全楽曲のUGC数を取得します。

```bash
python src/main.py process --settings initial_settings.xlsx
```

**処理内容**:
1. Excelから楽曲URL一覧を読み込み
2. 各URLにアクセスしてUGC数を取得
3. 結果をExcelに書き込み

### 2. retry モード

「取得失敗」とマークされた楽曲を再処理します。

```bash
python src/main.py retry --settings initial_settings.xlsx
```

**処理内容**:
1. Excelから「取得失敗」マークの行を検索
2. 該当URLを再スクレイピング
3. 成功した場合は値を更新

### 3. collect モード（並列収集）

シャーディングを使用して複数ワーカーで並列収集します。

```bash
# ワーカー1（偶数インデックス担当）
python src/main.py collect --settings TikTok_UGC.xlsx --shards 2 --shard-index 0 --out runs/w1/ugc_20241226.csv

# ワーカー2（奇数インデックス担当）
python src/main.py collect --settings TikTok_UGC.xlsx --shards 2 --shard-index 1 --out runs/w2/ugc_20241226.csv
```

**パラメータ**:
| パラメータ | 説明 |
|-----------|------|
| `--shards` | 総シャード数（ワーカー数） |
| `--shard-index` | このワーカーのインデックス（0始まり） |
| `--out` | 出力CSVファイルパス |
| `--profile-dir` | Chromeプロファイルディレクトリ |
| `--timeout` | ページ読み込みタイムアウト（秒） |
| `--retries` | リトライ回数 |
| `--headless` | ヘッドレスモード（デフォルト有効） |

### 4. apply モード

collectモードで生成されたCSVファイルをExcelに統合します。

```bash
python src/main.py apply --target TikTok_UGC.xlsx --in "runs/w*/ugc_20241226.csv"
```

**処理内容**:
1. 指定パターンにマッチするCSVを全て読み込み
2. 曲名でマッチングして該当行を更新
3. UGC数と増減を計算して書き込み

## コアモジュール解説

### scraper.py

```python
def get_ugc_count(driver, url, max_retries=3, retry_delay=5):
    """
    TikTok楽曲URLからUGC数を取得。
    
    処理:
    1. URLにアクセス
    2. DOM完了を待機
    3. UGC数要素を検索
    4. テキストから数値をパース
    
    戻り値: int（成功時）または None（失敗時）
    """

def initialize_driver(profile_dir=None, headless=True, disable_images=True):
    """
    Selenium WebDriverを初期化。
    
    特徴:
    - プロファイル指定可能
    - 起動失敗時はクリーンプロファイルにフォールバック
    - アンチボット対策適用済み
    """
```

### excel_utils.py

```python
def read_song_urls(workbook, stop_on_blank=True):
    """
    Excelから(曲名, URL)の辞書を読み込み。
    
    対応シート:
    - 「取得楽曲URL設定」（優先）
    - 「楽曲マスタ」
    """

def update_ugc_entry(workbook, ugc, row):
    """
    UGCシートに値を書き込み、増減を計算。
    
    処理:
    1. 当日列を取得/作成
    2. UGC数を書き込み
    3. 前日比の増減を計算
    4. アラート色を適用
    """

def find_failed_entries(workbook):
    """
    「取得失敗」マークの行を検索。
    
    戻り値: [{row, song, url}, ...]
    """
```

### constants.py

```python
# UGC数を取得するためのXPath
UGC_COUNT_XPATH = "//h2[contains(@class, 'total')]"

# WebDriver待機時間
WEBDRIVER_WAIT_TIME = 15

# Excelヘッダー行
HEADER_ROW = 3

# 日付列開始位置
DATE_COLUMN_START = 3
```

## シャーディングアルゴリズム

```python
def _build_shard(items: list, shards: int, shard_index: int):
    """
    リストをシャード数で分割し、指定インデックスの要素を返す。
    
    例: items = [A, B, C, D, E], shards = 2
    - shard_index 0: [A, C, E]
    - shard_index 1: [B, D]
    """
    return [item for i, item in enumerate(items) if i % shards == shard_index]
```

## 出力CSVフォーマット

```csv
song,url,ugc_count,timestamp
曲名1,https://www.tiktok.com/music/...,15000,2024-12-26 10:30:00
曲名2,https://www.tiktok.com/music/...,8500,2024-12-26 10:31:15
```

## 設定ファイル

### config.json

```json
{
    "EXCEL_FILE_PATH": "path/to/scraping.xlsx",
    "LOG_FILE_PATH": "logs/scraper.log"
}
```

### config.py

```python
# 基本設定
HEADER_ROW = 3
DATE_COLUMN_START = 3
UGC_SHEET = "UGC"
DIFFERENCE_SHEET = "増減"

# アラート設定
ALERT_THRESHOLD = 100
```

## WebDriver設定

### Chromeオプション

```python
options = Options()
options.add_argument("--headless=new")          # 新ヘッドレスモード
options.add_argument("--no-sandbox")            # サンドボックス無効
options.add_argument("--disable-dev-shm-usage") # 共有メモリ使用無効
options.add_argument("--disable-gpu")           # GPU無効
options.add_argument("--remote-debugging-port=0")  # ポート自動割当
options.page_load_strategy = "eager"            # DOM準備完了で次へ
```

### 画像無効化

```python
prefs = {"profile.managed_default_content_settings.images": 2}
options.add_experimental_option("prefs", prefs)
```

## エラーハンドリング

### リトライ戦略

```python
for attempt in range(max_retries + 1):
    try:
        # スクレイピング処理
        pass
    except TimeoutException:
        if attempt < max_retries:
            # 指数バックオフで待機
            time.sleep(retry_delay * (attempt + 1))
            driver.refresh()
            continue
        return None
```

### 失敗マーク

UGC取得に失敗した場合、Excelセルに「取得失敗」と記録し、`retry`モードでの再試行を可能にします。

## PyInstaller ビルド

```bash
cd src
pyinstaller --onefile --name tiktok_cli main.py --add-data "modules;modules"
```

または spec ファイルを使用:

```bash
pyinstaller tiktok_cli.spec
```

## 依存関係

```
selenium
openpyxl
webdriver-manager
```

## 使用例

### 日次バッチ処理

```batch
@echo off
REM 朝5時に実行するバッチ

REM 1. 並列収集
call run_collect.bat

REM 2. 結果統合
call run_apply.bat

echo 処理完了
```

### Pythonからの直接呼び出し

```python
from src.main import collect_mode, apply_mode
from pathlib import Path

# 収集
collect_mode(
    settings_xlsx=None,
    master_xlsx=Path("TikTok_UGC.xlsx"),
    out_csv="output.csv",
    shards=1,
    shard_index=0
)

# 統合
apply_mode(
    target_xlsx=Path("TikTok_UGC.xlsx"),
    csv_inputs=["output.csv"]
)
```
