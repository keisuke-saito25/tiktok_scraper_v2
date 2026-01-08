# アーキテクチャ図

## 1. システム全体アーキテクチャ

```mermaid
graph TB
    subgraph "入力"
        EXCEL_MASTER["楽曲マスタ<br/>(Excel)"]
        EXCEL_SETTINGS["設定ファイル<br/>(initial_settings.xlsx)"]
    end

    subgraph "スクレイピング層"
        subgraph "GUIモード"
            TOOLKIT["tiktok_toolkit<br/>(Tkinter GUI)"]
        end
        
        subgraph "CLIモード（並列対応）"
            SCRAPER["tiktok_ugc_scraper<br/>(Python CLI)"]
            WORKER1["Worker 1"]
            WORKER2["Worker 2"]
            SCRAPER --> WORKER1
            SCRAPER --> WORKER2
        end
    end

    subgraph "外部サービス"
        TIKTOK["TikTok Web"]
        CHROME["Chrome WebDriver"]
    end

    subgraph "データストレージ"
        CSV["中間CSV<br/>(並列結果)"]
        EXCEL_UGC["TikTok_UGC.xlsx<br/>(統合データ)"]
    end

    subgraph "可視化層"
        CHART["tiktok_ugc_chart<br/>(Vue.js Dashboard)"]
    end

    EXCEL_MASTER --> TOOLKIT
    EXCEL_SETTINGS --> TOOLKIT
    EXCEL_MASTER --> SCRAPER
    
    TOOLKIT --> CHROME
    WORKER1 --> CHROME
    WORKER2 --> CHROME
    
    CHROME --> TIKTOK
    
    TOOLKIT --> EXCEL_UGC
    WORKER1 --> CSV
    WORKER2 --> CSV
    CSV --> SCRAPER
    SCRAPER --> EXCEL_UGC
    
    EXCEL_UGC --> CHART
```

## 2. データ処理フロー

```mermaid
sequenceDiagram
    participant User as ユーザー
    participant Script as 実行スクリプト
    participant Scraper as スクレイパー
    participant Chrome as Chrome
    participant TikTok as TikTok
    participant Excel as Excelファイル
    participant Dashboard as ダッシュボード

    User->>Script: run_collect.bat 実行
    Script->>Scraper: Worker1 起動 (shard 0)
    Script->>Scraper: Worker2 起動 (shard 1)
    
    par 並列収集
        Scraper->>Chrome: WebDriver初期化
        Chrome->>TikTok: 楽曲ページアクセス
        TikTok-->>Chrome: HTML返却
        Chrome-->>Scraper: UGC数取得
        Scraper->>Script: CSV書き出し
    end
    
    Script->>User: 収集完了通知
    
    User->>Script: run_apply.bat 実行
    Script->>Scraper: CSV読み込み
    Scraper->>Excel: UGC数更新
    Scraper->>Excel: 増減計算・保存
    
    User->>Dashboard: Excelアップロード
    Dashboard->>Dashboard: データ解析
    Dashboard-->>User: チャート・ランキング表示
```

## 3. コンポーネント詳細アーキテクチャ

### 3.1 tiktok_toolkit（GUIツール）

```mermaid
graph LR
    subgraph "tiktok.py"
        GUI["Tkinter GUI"]
        DRIVER["WebDriver管理"]
        EXCEL_IO["Excel I/O"]
        SCRAPE["スクレイピング処理"]
        LOGIN["ログイン確認"]
    end
    
    GUI --> DRIVER
    GUI --> EXCEL_IO
    GUI --> SCRAPE
    GUI --> LOGIN
    DRIVER --> SCRAPE
    EXCEL_IO --> SCRAPE
```

**主要機能**:
- `function1`: 楽曲ページから動画URLリストを収集
- `function2`: 動画詳細情報（再生数、いいね数など）を取得
- `check_tiktok_login_status`: TikTokログイン状態確認

### 3.2 tiktok_ugc_scraper（CLIツール）

```mermaid
graph TB
    subgraph "src/"
        MAIN["main.py<br/>(エントリポイント)"]
        CONFIG["config.py<br/>(設定管理)"]
        
        subgraph "modules/"
            SCRAPER_MOD["scraper.py<br/>(UGC取得)"]
            EXCEL_UTILS["excel_utils.py<br/>(Excel操作)"]
            CONSTANTS["constants.py<br/>(定数定義)"]
            PARSING["parsing_utils.py<br/>(パース処理)"]
            LOGGER["logger.py<br/>(ログ設定)"]
        end
    end
    
    MAIN --> CONFIG
    MAIN --> SCRAPER_MOD
    MAIN --> EXCEL_UTILS
    SCRAPER_MOD --> CONSTANTS
    SCRAPER_MOD --> PARSING
    EXCEL_UTILS --> CONSTANTS
```

**動作モード**:
| モード | 説明 |
|--------|------|
| `process` | 設定ファイルに基づき全楽曲のUGC数を取得 |
| `retry` | 「取得失敗」とマークされた楽曲を再処理 |
| `collect` | シャーディングを使用した並列収集 |
| `apply` | 収集結果CSVをExcelに統合 |

### 3.3 tiktok_ugc_chart（Webダッシュボード）

```mermaid
graph TB
    subgraph "src/"
        APP["App.vue<br/>(メイン)"]
        
        subgraph "components/"
            UGC_CHART["UGCChart.vue<br/>(チャート表示)"]
            RANKING["TikTokRanking.vue<br/>(ランキング)"]
            ACCOUNTS["AccountsTable.vue<br/>(アカウント表)"]
            DATE_FILTER["DateRangeFilter.vue<br/>(日付フィルタ)"]
            ICON["DraggableIcon.vue<br/>(アイコン)"]
            UPLOAD["FileUploadButton.vue<br/>(ファイル読込)"]
        end
        
        subgraph "utils/"
            FILE_HANDLER["fileHandler.ts<br/>(データ抽出)"]
            DATE_UTILS["dateUtils.ts<br/>(日付処理)"]
        end
        
        subgraph "types/"
            TYPES["型定義"]
        end
    end
    
    APP --> UGC_CHART
    APP --> RANKING
    APP --> ACCOUNTS
    APP --> DATE_FILTER
    APP --> UPLOAD
    UGC_CHART --> ICON
    UGC_CHART --> FILE_HANDLER
    RANKING --> FILE_HANDLER
    FILE_HANDLER --> DATE_UTILS
```

## 4. Excel データ構造

```mermaid
erDiagram
    MUSIC_MASTER ||--o{ UGC_SHEET : "曲名参照"
    MUSIC_MASTER ||--o{ DIFFERENCE_SHEET : "曲名参照"
    UGC_SHEET ||--o{ DATE_SHEET : "日付シート生成"
    
    MUSIC_MASTER {
        string song_name "曲名 (A列)"
        string tiktok_url "TikTok楽曲URL (B列)"
    }
    
    UGC_SHEET {
        string song_name "曲名参照 (A列)"
        int date_column "日付ごとのUGC数 (C列以降)"
    }
    
    DIFFERENCE_SHEET {
        string song_name "曲名参照 (A列)"
        int delta "増減数"
        float ratio "増減率"
    }
    
    DATE_SHEET {
        string video_url "動画URL"
        string account_name "アカウント名"
        datetime post_date "投稿日"
        int play_count "再生数"
        int like_count "いいね数"
        int comment_count "コメント数"
        int follower_count "フォロワー数"
        string icon_url "アイコンURL"
    }
```

## 5. 並列処理アーキテクチャ

```mermaid
graph LR
    subgraph "run_collect.bat"
        LAUNCHER["起動スクリプト"]
    end
    
    subgraph "Worker 1"
        W1_EXE["tiktok_cli.exe"]
        W1_PROFILE["chrome_profile/worker_1"]
        W1_CSV["runs/w1/ugc_YYYYMMDD.csv"]
    end
    
    subgraph "Worker 2"
        W2_EXE["tiktok_cli.exe"]
        W2_PROFILE["chrome_profile/worker_2"]
        W2_CSV["runs/w2/ugc_YYYYMMDD.csv"]
    end
    
    subgraph "run_apply.bat"
        APPLY["統合処理"]
        TARGET["TikTok_UGC.xlsx"]
    end
    
    LAUNCHER -->|"shard-index 0"| W1_EXE
    LAUNCHER -->|"shard-index 1"| W2_EXE
    W1_EXE --> W1_PROFILE
    W2_EXE --> W2_PROFILE
    W1_EXE --> W1_CSV
    W2_EXE --> W2_CSV
    
    W1_CSV --> APPLY
    W2_CSV --> APPLY
    APPLY --> TARGET
```

**シャーディング処理**:
- 全楽曲リストを `shards` 数で分割
- 各ワーカーが `shard-index` に対応する楽曲のみを処理
- 例: 100曲を2ワーカーで処理 → Worker1: 0,2,4,..., Worker2: 1,3,5,...

## 6. 技術スタックまとめ

```mermaid
mindmap
  root((TikTok Scraper))
    Python
      Selenium
      openpyxl
      pandas
      Tkinter
      webdriver-manager
      PyInstaller
    JavaScript/TypeScript
      Vue 3
      Vuetify 3
      Chart.js
      xlsx
      html2canvas
      Vite
    Infrastructure
      Chrome WebDriver
      Windows Batch
      PowerShell
```
