import logging
import sys
import os
import config
import time
import random
from modules.excel_utils import read_urls, update_ugc_sheet, update_difference_sheet
from modules.scraper import get_ugc_count, initialize_driver
from modules.logger import setup_logging
from selenium.common.exceptions import WebDriverException
from modules.constants import MAX_URLS_TO_PROCESS 

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'modules'))

def main():
    setup_logging()

    # URLを取得
    urls = read_urls(config.EXCEL_FILE_PATH)
    if urls:
        logging.info("取得したURL一覧")
        for idx, url in enumerate(urls, start=1):
            logging.info(f"{idx}. {url}")
    else:
        logging.warning("URLを取得できませんでした。")
        return
    
    # debug
    limited_urls = urls[:MAX_URLS_TO_PROCESS]
    if len(urls) > MAX_URLS_TO_PROCESS:
        logging.info(f"URLの処理数を {MAX_URLS_TO_PROCESS} に制限します。")

    # WebDriverを初期化
    try:
        driver = initialize_driver()
        logging.info("WebDriverの初期化に成功しました。")
    except WebDriverException as e:
        logging.error(f"WebDriverの初期化中にエラーが発生しました: {e}")
        return

    ugc_counts = []

    # URLからUGC数を取得
    try:
        for idx, url in enumerate(limited_urls, start=1): # limited_urls
            logging.info(f"URL {idx} のUGC数取得を開始: {url}")
            try:
                ugc_count = get_ugc_count(driver, url)
                logging.info(f"URL {idx} のUGC数: {ugc_count}")
                ugc_counts.append(ugc_count)
                time.sleep(random.uniform(1, 3))
            except Exception as e:
                logging.error(f"URL {idx} のUGC数取得中にエラーが発生しました: {e}")
                ugc_counts.append("取得失敗")

        logging.info("全てのURLのUGC数取得が完了しました。")

    finally:
        # WebDriverを終了
        driver.quit()
        logging.info("WebDriverを終了しました。")

    # UGCシートを更新し、delta_countsを取得
    delta_counts = update_ugc_sheet(config.EXCEL_FILE_PATH, ugc_counts)

    # 増減シートを更新
    update_difference_sheet(config.EXCEL_FILE_PATH, delta_counts)

if __name__ == "__main__":
    main()