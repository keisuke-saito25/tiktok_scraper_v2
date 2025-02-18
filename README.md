# tiktok_scraper

## Installation

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

## Configuration

プロジェクトルートにある `config.py` ファイルを編集して、必要なパスを設定します。

```python
# config.py
EXCEL_FILE_PATH  = "scraping.xlsx"
LOG_FILE_PATH = "logs/scraper.log"
```
