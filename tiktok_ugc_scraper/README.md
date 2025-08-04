# tiktok_ugc_scraper - CLI型TikTok UGCスクレイピングツール

![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![Selenium](https://img.shields.io/badge/WebDriver-Selenium-orange.svg)
![CLI](https://img.shields.io/badge/Interface-CLI-green.svg)
![Modular](https://img.shields.io/badge/Architecture-Modular-purple.svg)

コマンドライン型の高性能TikTok UGCデータ収集ツールです。モジュラーアーキテクチャにより拡張性と保守性を重視し、Process/Retryモードによる堅牢な運用を実現します。

## 🎯 主要機能

### ⚡ 高性能処理
- **Process/Retryモード**: 初回処理と失敗レコード再処理の分離
- **バッチ処理**: 大量データの効率的な並行処理
- **エラー復旧**: 失敗した処理の自動リトライシステム
- **差分管理**: 前回処理からの変更データのみ処理

### 🏗️ モジュラーアーキテクチャ
- **分離された責任**: 各機能の独立したモジュール設計
- **設定管理**: JSON-based の柔軟な設定システム
- **ログシステム**: 包括的なログ記録・監視機能
- **データ統合**: Excel ベースのデータ入出力管理

### 📊 データ処理機能
- **UGCデータスクレイピング**: TikTok投稿データの自動収集
- **差分検出**: 既存データとの比較・更新管理
- **Excel統合**: .xlsx ファイルの読み書き・差分記録
- **データ検証**: 収集データの品質チェック

### 🔧 運用・メンテナンス
- **コマンドライン操作**: 自動化・スケジューリング対応
- **実行ファイル生成**: PyInstaller による配布用バイナリ
- **設定カスタマイズ**: 環境に応じた柔軟な設定変更
- **エラー監視**: 詳細なエラー追跡・レポート

## 🏗️ アーキテクチャ概要

```
┌─────────────────────────────────────┐
│        tiktok_ugc_scraper           │
├─────────────────────────────────────┤
│                                     │
│  ┌─────────────┐  ┌─────────────┐   │
│  │   main.py   │  │  config.py  │   │
│  │             │  │             │   │
│  │ • Entry     │  │ • Settings  │   │
│  │ • Mode      │  │ • Validation│   │
│  │ • Control   │  │ • Defaults  │   │
│  └─────────────┘  └─────────────┘   │
│           │               │         │
│  ┌─────────────────────────────────┐ │
│  │         Core Modules            │ │
│  │                                │ │
│  │ ┌─────────────┐ ┌─────────────┐ │ │
│  │ │   logger    │ │excel_utils  │ │ │
│  │ └─────────────┘ └─────────────┘ │ │
│  │ ┌─────────────┐ ┌─────────────┐ │ │
│  │ │  scraper    │ │parsing_utils│ │ │
│  │ └─────────────┘ └─────────────┘ │ │
│  │ ┌─────────────┐ ┌─────────────┐ │ │
│  │ │ constants   │ │ __init__.py │ │ │
│  │ └─────────────┘ └─────────────┘ │ │
│  └─────────────────────────────────┘ │
│           │                         │
│  ┌─────────────────────────────────┐ │
│  │     Processing Runners          │ │
│  │                                │ │
│  │ • process_runner.py            │ │
│  │ • retry_runner.py              │ │
│  │                                │ │
│  │ • Selenium Integration         │ │
│  │ • Excel I/O Management         │ │
│  │ • Error Handling & Recovery    │ │
│  └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

## 📁 プロジェクト構造

```
tiktok_ugc_scraper/
├── src/                          # ソースコードディレクトリ
│   ├── main.py                   # メインエントリーポイント
│   ├── config.py                 # 設定管理モジュール
│   ├── process_runner.py         # Process モード実行
│   ├── retry_runner.py           # Retry モード実行
│   └── modules/                  # コアモジュール
│       ├── __init__.py           # モジュール初期化
│       ├── constants.py          # 定数定義
│       ├── excel_utils.py        # Excel操作ユーティリティ
│       ├── logger.py             # ログシステム
│       ├── parsing_utils.py      # データパーシング
│       └── scraper.py            # Web スクレイピング
├── config.json                   # アプリケーション設定
├── requirements.txt              # Python依存関係
├── scraping.xlsx                 # データ入出力Excel ファイル
└── README.md                     # このファイル
```

### モジュール詳細

#### 🎮 コア実行ファイル
- **`main.py`**: アプリケーションエントリーポイント、モード選択・実行制御
- **`config.py`**: 設定ファイル読み込み、バリデーション、デフォルト値管理
- **`process_runner.py`**: Process モードの実行ロジック
- **`retry_runner.py`**: Retry モードの実行ロジック

#### 🔧 ユーティリティモジュール
- **`logger.py`**: 包括的ログシステム、ファイル・コンソール出力
- **`excel_utils.py`**: Excel ファイル読み書き、データ検証
- **`parsing_utils.py`**: HTML パーシング、データ抽出・変換
- **`scraper.py`**: Selenium WebDriver 制御、スクレイピング実行

#### 📊 設定・定数
- **`constants.py`**: アプリケーション全体で使用する定数定義
- **`config.json`**: 実行時設定、URL、待機時間、出力設定

## ⚙️ システム要件

### 🔧 必須環境
- **Python**: 3.7以上 (推奨: 3.9+)
- **Chrome Browser**: 最新版 (WebDriver 用)
- **OS**: Windows, macOS, Linux
- **RAM**: 2GB以上 (並行処理時: 4GB以上推奨)
- **ストレージ**: 1GB以上の空き容量

### 📦 依存関係
```python
selenium>=4.0.0        # WebDriver 制御
pandas>=1.3.0          # データフレーム操作
openpyxl>=3.0.0        # Excel ファイル処理
webdriver-manager>=3.8.0  # WebDriver 自動管理
requests>=2.25.0       # HTTP リクエスト
beautifulsoup4>=4.9.0  # HTML パーシング
```

## 🚀 インストール・セットアップ

### 1️⃣ プロジェクトの準備
```bash
# リポジトリクローン
git clone <リポジトリのURL>
cd tiktok_scraper/tiktok_ugc_scraper
```

### 2️⃣ Python仮想環境の構築
```bash
# 仮想環境作成
python3 -m venv venv

# 仮想環境有効化
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### 3️⃣ 依存関係のインストール
```bash
# 必要パッケージインストール
pip install -r requirements.txt

# 必要に応じて個別インストール
pip install selenium pandas openpyxl webdriver-manager
```

### 4️⃣ 設定ファイルの確認・調整
`config.json` の内容を環境に合わせて設定：

```json
{
  "base_url": "https://www.tiktok.com",
  "wait_time": 3,
  "max_retries": 3,
  "output_excel": "scraping.xlsx",
  "log_level": "INFO",
  "headless_mode": false,
  "concurrent_limit": 5
}
```

## 🎮 使用方法

### 基本的な実行方法

#### Process モード (初回・全データ処理)
```bash
# 基本実行
python3 src/main.py process

# 詳細実行（設定指定）
python3 src/main.py process --config config.json

# ヘッドレスモード実行
python3 src/main.py process --headless
```

#### Retry モード (失敗レコード再処理)
```bash
# リトライ実行
python3 src/main.py retry

# 強制リトライ（全失敗レコード）
python3 src/main.py retry --force

# 特定の失敗理由のみリトライ
python3 src/main.py retry --error-type timeout
```

### 📋 実行フロー

#### 1. データ準備
1. **Excel ファイル準備**: `scraping.xlsx` に対象データを入力
2. **データ形式確認**: 必須列の存在・形式チェック
3. **設定確認**: `config.json` の内容確認・調整

#### 2. Process モード実行
```bash
python3 src/main.py process
```
- 全レコードの処理実行
- TikTok ページからのデータ収集
- Excel ファイルへの結果記録
- エラーログの出力

#### 3. Retry モード実行（必要に応じて）
```bash
python3 src/main.py retry
```
- 前回失敗したレコードのみ再処理
- エラー原因の分析・対応
- 成功レコードの結果更新

#### 4. 結果確認
- **Excel ファイル**: 処理結果・エラー情報の確認
- **ログファイル**: 詳細な実行ログの確認
- **差分データ**: UGC 数の変化・トレンド分析

### 📊 Excel データ形式

#### 入力データ形式
| 列名 | 説明 | 例 | 必須 |
|-----|------|-----|------|
| song_id | 楽曲ID | 123456789 | ✅ |
| song_title | 楽曲タイトル | "Sample Song" | ✅ |
| artist_name | アーティスト名 | "Artist Name" | ✅ |
| tiktok_url | TikTok楽曲URL | https://www.tiktok.com/music/... | ✅ |
| last_check | 前回チェック日時 | 2024-01-01 12:00:00 | ❌ |

#### 出力データ形式
上記入力データに加えて以下の列が追加されます：

| 列名 | 説明 | 例 |
|-----|------|-----|
| ugc_count | UGC投稿数 | 15420 |
| check_time | チェック日時 | 2024-01-15 14:30:22 |
| status | 処理状態 | "SUCCESS" / "ERROR" |
| error_message | エラー内容 | "Timeout occurred" |
| previous_count | 前回UGC数 | 14850 |
| count_diff | 差分 | +570 |

### 🎛️ コマンドラインオプション

#### Process モード
```bash
python3 src/main.py process [options]

Options:
  --config FILE       設定ファイルパス (デフォルト: config.json)
  --headless         ヘッドレスモード実行
  --parallel N       並行処理数 (1-10)
  --output FILE      出力Excelファイル名
  --log-level LEVEL  ログレベル (DEBUG, INFO, WARNING, ERROR)
  --dry-run          実際の処理を行わず、動作確認のみ
```

#### Retry モード
```bash
python3 src/main.py retry [options]

Options:
  --config FILE       設定ファイルパス
  --force            全失敗レコードを強制リトライ
  --error-type TYPE  特定エラータイプのみリトライ
  --max-attempts N   最大リトライ回数
  --wait-time N      リトライ間隔（秒）
```

## 🔧 設定・カスタマイズ

### ⚙️ config.json 詳細設定

```json
{
  "scraping": {
    "base_url": "https://www.tiktok.com",
    "wait_time": 3,
    "max_retries": 3,
    "timeout": 30,
    "user_agent": "Mozilla/5.0 (compatible; TikTokScraper/1.0)"
  },
  "selenium": {
    "headless_mode": false,
    "window_size": [1920, 1080],
    "implicit_wait": 10,
    "page_load_timeout": 30,
    "chrome_options": [
      "--no-sandbox",
      "--disable-dev-shm-usage",
      "--disable-blink-features=AutomationControlled"
    ]
  },
  "excel": {
    "input_file": "scraping.xlsx",
    "output_file": "scraping.xlsx",
    "sheet_name": "data",
    "backup_enabled": true,
    "backup_prefix": "backup_"
  },
  "logging": {
    "level": "INFO",
    "file_enabled": true,
    "log_file": "app.log",
    "console_enabled": true,
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  },
  "performance": {
    "concurrent_limit": 5,
    "batch_size": 100,
    "memory_limit_mb": 1024,
    "enable_cache": true
  }
}
```

### 🎨 ログ設定のカスタマイズ

#### ログレベル設定
```python
# src/modules/logger.py のカスタマイズ例
import logging

# カスタムログフォーマット
CUSTOM_FORMAT = '%(asctime)s | %(levelname)-8s | %(funcName)s:%(lineno)d | %(message)s'

# ログレベル設定
LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}
```

#### ログローテーション設定
```python
from logging.handlers import RotatingFileHandler

# ログファイルローテーション
handler = RotatingFileHandler(
    'app.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
```

### 🔧 Selenium WebDriver カスタマイズ

#### Chrome オプションの追加
```python
# src/modules/scraper.py での Chrome オプション例
chrome_options = webdriver.ChromeOptions()

# パフォーマンス向上
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-gpu')

# Bot 検知回避
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)

# プロキシ設定（必要に応じて）
chrome_options.add_argument('--proxy-server=http://proxy-server:port')
```

## 🏗️ ビルド・配布

### 📦 PyInstaller による実行ファイル作成

#### Process モード用実行ファイル
```bash
pyinstaller \
    --onefile \
    --name "tiktok_scraper_process" \
    --add-data "src/modules:modules" \
    --add-data "config.json:." \
    --hidden-import selenium \
    --hidden-import pandas \
    --hidden-import openpyxl \
    src/process_runner.py
```

#### Retry モード用実行ファイル
```bash
pyinstaller \
    --onefile \
    --name "tiktok_scraper_retry" \
    --add-data "src/modules:modules" \
    --add-data "config.json:." \
    --hidden-import selenium \
    --hidden-import pandas \
    --hidden-import openpyxl \
    src/retry_runner.py
```

#### 統合実行ファイル（推奨）
```bash
pyinstaller \
    --onefile \
    --name "tiktok_ugc_scraper" \
    --add-data "src/modules:modules" \
    --add-data "config.json:." \
    --console \
    --hidden-import selenium \
    --hidden-import pandas \
    --hidden-import openpyxl \
    --hidden-import webdriver_manager \
    src/main.py
```

### 📋 配布パッケージ構成
```
TikTok_UGC_Scraper_v1.0/
├── tiktok_ugc_scraper.exe    # 実行ファイル
├── config.json              # 設定ファイル
├── scraping.xlsx            # サンプル Excel テンプレート
├── README.txt              # 使用説明書
├── LICENSE.txt            # ライセンス情報
└── docs/                  # 追加ドキュメント
    ├── setup_guide.md     # セットアップガイド
    ├── troubleshooting.md # トラブルシューティング
    └── api_reference.md   # API リファレンス
```

### 🐳 Docker コンテナ化

#### Dockerfile
```dockerfile
FROM python:3.9-slim

# Chrome のインストール
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "src/main.py"]
```

#### docker-compose.yml
```yaml
version: '3.8'
services:
  tiktok-scraper:
    build: .
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    environment:
      - DISPLAY=:99
    command: python src/main.py process
```

## 📊 パフォーマンス・最適化

### ⚡ 処理性能の向上

#### 並行処理の最適化
```python
# src/modules/scraper.py での並行処理例
import concurrent.futures
from threading import Semaphore

class ScraperManager:
    def __init__(self, max_workers=5):
        self.max_workers = max_workers
        self.semaphore = Semaphore(max_workers)
    
    def process_batch(self, urls):
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_url = {
                executor.submit(self.scrape_url, url): url 
                for url in urls
            }
            
            results = []
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as exc:
                    logger.error(f'URL {url} generated an exception: {exc}')
            
            return results
```

#### メモリ効率の改善
```python
# バッチ処理によるメモリ最適化
def process_excel_in_batches(excel_file, batch_size=100):
    df = pd.read_excel(excel_file)
    total_rows = len(df)
    
    for start_idx in range(0, total_rows, batch_size):
        end_idx = min(start_idx + batch_size, total_rows)
        batch_df = df.iloc[start_idx:end_idx].copy()
        
        # バッチ処理実行
        process_batch(batch_df)
        
        # メモリ解放
        del batch_df
        gc.collect()
```

### 🧠 キャッシュ・データベース統合

#### ローカルキャッシュシステム
```python
# src/modules/cache.py
import pickle
import time
from pathlib import Path

class DataCache:
    def __init__(self, cache_dir='cache', ttl=3600):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.ttl = ttl
    
    def get(self, key):
        cache_file = self.cache_dir / f"{key}.pkl"
        if cache_file.exists():
            with open(cache_file, 'rb') as f:
                data, timestamp = pickle.load(f)
                if time.time() - timestamp < self.ttl:
                    return data
        return None
    
    def set(self, key, data):
        cache_file = self.cache_dir / f"{key}.pkl"
        with open(cache_file, 'wb') as f:
            pickle.dump((data, time.time()), f)
```

## 🛡️ セキュリティ・倫理的配慮

### 📋 TikTok利用規約遵守

#### Rate Limiting の実装
```python
import time
from functools import wraps

def rate_limit(calls_per_minute=30):
    min_interval = 60.0 / calls_per_minute
    last_called = [0.0]
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = min_interval - elapsed
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            ret = func(*args, **kwargs)
            last_called[0] = time.time()
            return ret
        return wrapper
    return decorator

# 使用例
@rate_limit(calls_per_minute=20)  # 1分間に20回まで
def scrape_tiktok_page(url):
    # スクレイピング処理
    pass
```

#### User-Agent ローテーション
```python
import random

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
]

def get_random_user_agent():
    return random.choice(USER_AGENTS)
```

### 🔒 データ保護・プライバシー

#### 機密データの暗号化
```python
from cryptography.fernet import Fernet
import base64

class DataEncryption:
    def __init__(self, key=None):
        if key is None:
            key = Fernet.generate_key()
        self.cipher_suite = Fernet(key)
        self.key = key
    
    def encrypt_data(self, data):
        if isinstance(data, str):
            data = data.encode('utf-8')
        encrypted_data = self.cipher_suite.encrypt(data)
        return base64.urlsafe_b64encode(encrypted_data).decode('utf-8')
    
    def decrypt_data(self, encrypted_data):
        encrypted_data = base64.urlsafe_b64decode(encrypted_data.encode('utf-8'))
        decrypted_data = self.cipher_suite.decrypt(encrypted_data)
        return decrypted_data.decode('utf-8')
```

### ⚖️ 法的コンプライアンス

#### robots.txt 確認機能
```python
import urllib.robotparser

def check_robots_txt(url, user_agent='*'):
    try:
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(f"{url}/robots.txt")
        rp.read()
        return rp.can_fetch(user_agent, url)
    except Exception as e:
        logger.warning(f"Could not check robots.txt: {e}")
        return False  # 安全側に倒す
```

## 🐛 トラブルシューティング

### よくある問題と解決方法

#### 1. WebDriver 関連エラー
**症状**: `ChromeDriver` の起動エラーや互換性問題

```bash
# 解決方法
# 1. Chrome ブラウザの更新
sudo apt-get update && sudo apt-get upgrade google-chrome-stable

# 2. webdriver-manager の更新
pip install --upgrade webdriver-manager

# 3. Chrome バージョンの確認
google-chrome --version

# 4. 手動 ChromeDriver 設定
export PATH=$PATH:/path/to/chromedriver
```

#### 2. Excel ファイル処理エラー
**症状**: openpyxl や pandas でのファイル読み込み失敗

```python
# 解決方法
# 1. ファイル権限の確認
import os
print(f"File exists: {os.path.exists('scraping.xlsx')}")
print(f"File readable: {os.access('scraping.xlsx', os.R_OK)}")
print(f"File writable: {os.access('scraping.xlsx', os.W_OK)}")

# 2. ファイル形式の確認
try:
    df = pd.read_excel('scraping.xlsx', engine='openpyxl')
except Exception as e:
    logger.error(f"Excel read error: {e}")

# 3. バックアップからの復元
import shutil
if os.path.exists('backup_scraping.xlsx'):
    shutil.copy2('backup_scraping.xlsx', 'scraping.xlsx')
```

#### 3. メモリ不足エラー
**症状**: 大量データ処理時のメモリ不足

```python
# 解決方法
# 1. バッチサイズの調整
BATCH_SIZE = 50  # デフォルトから減らす

# 2. ガベージコレクションの明示的実行
import gc
gc.collect()

# 3. pandas の dtype 最適化
df = df.astype({
    'song_id': 'int32',
    'ugc_count': 'int32',
    'status': 'category'
})
```

#### 4. 接続・タイムアウトエラー
**症状**: TikTok サイトへの接続失敗やタイムアウト

```python
# 解決方法
# 1. 待機時間の増加
config['wait_time'] = 5  # デフォルトから増加

# 2. リトライ回数の増加
config['max_retries'] = 5

# 3. ネットワーク確認
import requests
try:
    response = requests.get('https://www.tiktok.com', timeout=10)
    print(f"Status: {response.status_code}")
except Exception as e:
    print(f"Network error: {e}")
```

#### 5. ログファイル・権限エラー
**症状**: ログファイル書き込み権限エラー

```bash
# 解決方法
# 1. ログディレクトリの作成
mkdir -p logs
chmod 755 logs

# 2. ログファイル権限の設定
touch logs/app.log
chmod 644 logs/app.log

# 3. 実行ユーザーの確認
whoami
ls -la logs/
```

### 🔧 デバッグモード

#### 詳細ログの有効化
```json
{
  "logging": {
    "level": "DEBUG",
    "selenium_debug": true,
    "network_debug": true,
    "performance_debug": true
  }
}
```

#### デバッグ用コマンドライン実行
```bash
# デバッグモード実行
python3 src/main.py process --log-level DEBUG --dry-run

# 特定URL のみテスト
python3 src/main.py process --test-url "https://www.tiktok.com/music/..."

# ブラウザ表示モードでのデバッグ
python3 src/main.py process --no-headless --wait-debug
```

### 📞 サポート・診断情報

#### 環境情報の収集
```python
# システム情報収集スクリプト
import sys
import platform
import selenium
import pandas as pd
import openpyxl

def collect_system_info():
    info = {
        'Python': sys.version,
        'Platform': platform.platform(),
        'Selenium': selenium.__version__,
        'Pandas': pd.__version__,
        'OpenPyXL': openpyxl.__version__,
    }
    
    for key, value in info.items():
        print(f"{key}: {value}")
    
    return info

if __name__ == "__main__":
    collect_system_info()
```

## 📈 将来の拡張予定

### 🔮 計画中の機能

#### データベース統合
- **PostgreSQL**: 大規模データの効率的管理
- **MongoDB**: 非構造化データの柔軟な保存
- **Redis**: 高速キャッシュシステム
- **SQLite**: 軽量ローカルデータベース

#### API・クラウド統合
- **REST API**: 外部システムとの連携
- **GraphQL**: 柔軟なデータクエリ
- **AWS/GCP**: クラウドインフラ統合
- **Webhook**: リアルタイム通知システム

#### 高度な分析機能
- **機械学習**: トレンド予測・異常検知
- **自動レポート**: 定期的な分析レポート生成
- **ダッシュボード**: リアルタイムデータ可視化
- **アラートシステム**: 重要な変化の自動通知

### 🤝 コントリビューション

プロジェクトへの貢献方法：

1. **Issue 報告**: バグ・機能要望・改善提案
2. **Pull Request**: コード改善・新機能追加
3. **ドキュメント**: README・コメント・ガイドの改善
4. **テスト**: ユニットテスト・統合テスト追加
5. **パフォーマンス**: 処理効率・メモリ使用量の最適化

#### 開発環境セットアップ（コントリビューター向け）
```bash
# 開発用依存関係インストール
pip install -r requirements-dev.txt

# コード品質チェック
flake8 src/
black src/
pylint src/

# テスト実行
pytest tests/
coverage run -m pytest tests/
coverage report -m
```

### 📄 ライセンス・著作権

このプロジェクトは適切なライセンスの下で提供されています。

#### 主要依存関係のライセンス
- **Selenium**: Apache License 2.0
- **Pandas**: BSD License
- **OpenPyXL**: MIT License
- **Requests**: Apache License 2.0

---

**⚡ 高性能TikTok UGCデータ収集を始めましょう！**

tiktok_ugc_scraperで、効率的なデータ収集・分析を実現してください。技術的なサポートや追加機能のご要望は、プロジェクトのIssueページまでお気軽にお寄せください。