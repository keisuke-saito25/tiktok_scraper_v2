# tiktok_toolkit 詳細ドキュメント

## 概要

`tiktok_toolkit`は、TikTokデータを収集するためのGUIベースのデスクトップアプリケーションです。Tkinterを使用した直感的なインターフェースで、非技術者でも簡単に操作できます。

## ファイル構成

```
tiktok_toolkit/
├── tiktok.py              # メインアプリケーション（2132行）
├── config.json            # 設定ファイル
├── requirements.txt       # Python依存関係
├── run_tiktok.bat         # Windows実行用バッチ
├── initial_settings.xlsx  # 楽曲URL設定ファイル
├── tiktok.spec            # PyInstaller設定
├── chrome_profile/        # Chromeプロファイル保存先
├── images/                # スクリーンショット保存先
├── build/                 # ビルド中間ファイル
└── dist/                  # ビルド成果物
```

## 主要機能

### 機能1: 動画URL収集

楽曲ページから、その楽曲を使用している動画のURLリストを収集します。

**処理フロー**:
1. 設定ファイル（initial_settings.xlsx）から楽曲URLリストを読み込み
2. 各楽曲ページにアクセス
3. ページ内の動画一覧をスクロールしながら収集
4. 日付シートに動画URLを保存

**関連関数**:
- `function1()`: メイン処理
- `get_video_urls()`: 動画URL抽出
- `resolve_final_url()`: リダイレクト解決

### 機能2: 動画詳細収集

収集した動画URLから、各動画の詳細情報を取得します。

**収集データ**:
- 投稿日
- 再生数
- いいね数
- コメント数
- アカウント名
- フォロワー数
- アイコンURL

**関連関数**:
- `extract_video_data()`: 動画データ抽出
- `extract_date()`: 投稿日取得
- `extract_video_stats_from_json()`: 統計情報取得
- `get_follower_count()`: フォロワー数取得

## 設定ファイル

### config.json

```json
{
  "target_time": "05:00"
}
```

- `target_time`: 自動実行時のターゲット時刻

### 内部設定 (_DEFAULT_CFG)

```python
_DEFAULT_CFG = {
    "WEBDRIVER_CMD_TIMEOUT_SEC": 600,    # WebDriverコマンドタイムアウト
    "SCRIPT_TIMEOUT_SEC": 180,           # スクリプトタイムアウト
    "EXPLICIT_WAIT_SEC": 30,             # 明示的待機時間
    "PER_SONG_TIME_BUDGET_SEC": 300,     # 楽曲あたりの最大処理時間
    "PARALLEL_ENABLED": False,           # 並列処理有効化
    "PARALLEL_WORKERS": 2,               # 並列ワーカー数
    "SCROLL_TIMEOUT_SEC": 20,            # スクロールタイムアウト
    "ERROR_PAGE_EXTRA_WAIT_SEC": 10,     # エラーページ追加待機
    "MAX_CONSECUTIVE_ERRORS": 3,         # 連続エラー上限
    "LONG_WAIT_AFTER_ERRORS_SEC": 60,    # エラー後の長時間待機
    "CHECK_LOGIN_BEFORE_START": True,    # 起動時ログイン確認
    "LOGIN_WAIT_TIMEOUT_SEC": 120        # ログイン待機タイムアウト
}
```

## GUI コンポーネント

### メインウィンドウ

| 要素 | 説明 |
|------|------|
| 設定ファイル選択 | initial_settings.xlsx のパス指定 |
| 保存先ファイル選択 | 出力Excelファイルのパス指定 |
| 最大件数設定 | 1楽曲あたりの最大動画収集数 |
| ヘッドレスモード | ブラウザ表示/非表示切替 |
| 機能1ボタン | URL収集を開始 |
| 機能2ボタン | 詳細収集を開始 |
| 停止ボタン | 処理を中断 |
| ログ表示エリア | 処理状況を表示 |

## WebDriver管理

### プロファイル分離

各ワーカーに独立したChromeプロファイルを割り当て、セッション干渉を防止します。

```python
# プロファイルパス例
chrome_profile/
├── User Data/          # ベースプロファイル
├── isolated_w0/        # ワーカー0用
├── isolated_w1/        # ワーカー1用
└── ...
```

### アンチボット対策

```python
# navigator.webdriver 隠蔽
driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
    'source': '''
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        })
    '''
})
```

## ログイン確認機能

### 確認方法

```python
def check_tiktok_login_status(driver):
    """
    TikTokにログインしているかどうかを確認。
    
    確認手順:
    1. TikTokのプロフィールページにアクセス
    2. ログインボタンの有無を確認
    3. ユーザー名要素の存在を確認
    
    戻り値: (ログイン済みか, ユーザー名または状態メッセージ)
    """
```

### 手動ログイン待機

ヘッドレスモードが無効の場合、ユーザーが手動でログインするまで待機します。

## Excel I/O

### シート構成

| シート名 | 用途 |
|---------|------|
| music_info | 楽曲基本情報 |
| [YYYYMMDD] | 日付ごとの動画詳細 |

### 日付シートのカラム構成

| 列 | 内容 |
|----|------|
| A | 動画URL |
| B | 投稿日 |
| C | 再生数 |
| D | いいね数 |
| E | コメント数 |
| F | アカウント名 |
| G | フォロワー数 |
| H | アイコンURL |
| I | 更新日時 |

## エラーハンドリング

### エラーページ検知

```python
ERROR_XPATHS_STRICT = [
    '//p[contains(text(), "不明なエラーが発生しました")]',
    '//p[contains(text(), "ページを表示できません")]',
    '//p[contains(text(), "動画は現在ご利用できません")]',
    '//div[contains(@class, "error") and contains(text(), "エラー")]',
]
```

### リトライロジック

- 連続エラー上限を超えた場合、長時間待機後に再試行
- セッション無効エラーはWebDriverを再初期化

## 実行方法

### 開発環境

```bash
cd tiktok_toolkit
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python tiktok.py
```

### 実行ファイル作成

```bash
pyinstaller --onefile tiktok.py
# または
pyinstaller tiktok.spec
```

## 依存関係

```
selenium
pandas
openpyxl
webdriver-manager
Pillow
psutil
```
