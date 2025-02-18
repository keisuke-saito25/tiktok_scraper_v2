import logging
import sys
import os
import config
import time
import random
import openpyxl
from modules.excel_utils import read_urls, update_difference_entry, update_ugc_entry
from modules.scraper import get_ugc_count, initialize_driver
from modules.logger import setup_logging
from selenium.common.exceptions import WebDriverException
from modules.constants import MAX_URLS_TO_PROCESS 

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'modules'))

def main():
    setup_logging()

    # Excelを開く
    try:
        workbook = openpyxl.load_workbook(config.EXCEL_FILE_PATH)
    except Exception as e:
        logging.error(f"Excelファイルの読み込みに失敗しました: {e}")
        return

    # URLを取得
    urls = read_urls(workbook)
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
    try:
        for idx, url in enumerate(limited_urls, start=1):
            logging.info(f"URL {idx}  のUGC数取得を開始 : {url}")
            try:
                ugc_count = get_ugc_count(driver, url)
                logging.info(f"URL {idx} のUGC数: {ugc_count}")
            except Exception as e:
                logging.error(f"URL {idx} のUGC数取得中にエラーが発生しました: {e}")
                ugc_count = "取得失敗"

            # update sheet
            try:
                delta_count = update_ugc_entry(workbook, ugc_count, idx)
                update_difference_entry(workbook, delta_count, idx)
            except Exception as e:
                logging.error(f"URL {idx} のExcel更新中にエラーが発生しました: {e}")

            # save 
            try:
                workbook.save(config.EXCEL_FILE_PATH)
                logging.info(f"URL {idx} のデータをExcelに保存しました。")
            except Exception as e:
                logging.error(f"Excelファイルの保存中にエラーが発生しました: {e}")

            time.sleep(random.uniform(1, 3))

    finally:
        driver.quit()
        logging.info("WebDriverを修了しました。")
        workbook.close()


if __name__ == "__main__":
    main()