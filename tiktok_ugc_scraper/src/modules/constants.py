from typing import Dict

# main.py
MAX_URLS_TO_PROCESS: int = 3 # デバッグ用

# scraper.py
UGC_COUNT_XPATH: str = '//*[@id="main-content-single_song"]/div/div[1]/div[1]/div[2]/h2[2]/strong'
WEBDRIVER_WAIT_TIME: int = 15  # 秒
MAX_RETRIES: int = 3  # 最大リトライ回数
RETRY_DELAY: int = 5  # リトライ間の基本待機時間（秒）

# excel_utils.py 
ALERT_CELL: str = 'B1'
URL_COLUMN: str = 'B'

UGC_SHEET_NAME: str = 'UGC'
DIFFERENCE_SHEET_NAME: str = '増減'

HEADER_ROW: int = 4
START_ROW: int = 5 # データの書き込み開始位置

DELTA_COLUMN: int = 2
RATIO_COLUMN: int = 3

MIN_COL_FOR_COMPARISON: int = 4

ALERT_FILL_COLOR: str = "FFFF00"  # 黄色の背景
ALERT_FONT_COLOR: str = "FF0000"  # 赤色の太字
DEFAULT_FILL_TYPE: str = None
DEFAULT_FONT_COLOR: str = "000000"  # 黒色のフォント

DATE_FORMAT: str = '%Y-%m-%d'

# parsing_utils.py 
MULTIPLIERS: Dict[str, int] = {'K': 1_000, 'M': 1_000_000, 'B': 1_000_000_000}

# logger.py
LOG_FORMAT: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT: str = '%Y-%m-%d %H:%M:%S'