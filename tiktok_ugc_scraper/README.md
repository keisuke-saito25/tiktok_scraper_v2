# tiktok_ugc_scraper

## インストール

1. **リポジトリのクローン**

   ```bash
   git clone <リポジトリのURL>
   cd tiktok_ugc_scraper
   ```

2. **仮想環境の作成**

   ```bash
   python3 -m venv venv
   ```

3. **仮想環境の有効化**

   ```bash
   source venv/bin/activate
   ```

4. **依存関係のインストール**

   ```bash
   pip install -r requirements.txt
   ```
## 実行方法

- **通常**

    ```bash
    python3 src/main.py process
    ```

- **失敗レコードのみリトライ**

    ```bash
    python3 src/main.py retry

## ビルド方法

PyInstallerを使用

- **通常**

    ```bash
    pyinstaller --onefile --name tiktok_scraper_process \
    --add-data="src/modules/*:modules" \
    src/process_runner.py
    ```

- **失敗レコードのみリトライ**

    ```bash
    pyinstaller --onefile --name tiktok_scraper_retry \
    --add-data="src/modules/*:modules" \
    src/retry_runner.py
    ```
