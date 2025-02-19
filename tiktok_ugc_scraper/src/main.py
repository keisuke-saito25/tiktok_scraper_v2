import logging
import sys
import os
import config
import time
import random
import openpyxl
import argparse
from datetime import datetime

from modules.excel_utils import (
    read_song_urls,
    update_difference_entry,
    update_ugc_entry,
    get_row_by_song,
    find_failed_entries,
    get_sheet
)
from modules.scraper import get_ugc_count, initialize_driver
from modules.logger import setup_logging
from modules.constants import (
    MAX_URLS_TO_PROCESS,
    UGC_SHEET_NAME,
    DIFFERENCE_SHEET_NAME,
    URL_COLUMN,
    HEADER_ROW,
    START_ROW,
    DATE_FORMAT
)
from selenium.common.exceptions import WebDriverException

def process_mode(workbook, driver):
    # 曲名とURLのマップを取得
    song_url_map = read_song_urls(workbook)
    if song_url_map:
        logging.info("曲名とURLの一覧を取得しました。")
        for idx, (song, url) in enumerate(song_url_map.items(), start=1):
            logging.info("%d. 曲名: %s, URL: %s", idx, song, url)
    else:
        logging.warning("曲名とURLのマップを取得できませんでした。処理を中断します。")
        return

    for idx, (song, url) in enumerate(song_url_map.items(), start=1):
        logging.info("曲 %d (%s) のUGC数取得を開始します。URL: %s", idx, song, url)
        try:
            ugc_count = get_ugc_count(driver, url)
            logging.info("曲 '%s' のUGC数: %d", song, ugc_count)
        except Exception as e:
            logging.error("曲 '%s' のUGC数取得中にエラーが発生しました: %s", song, e)
            ugc_count = "取得失敗"

        # 曲名から行番号を取得
        ugc_sheet = workbook[UGC_SHEET_NAME]
        row = get_row_by_song(ugc_sheet, song, workbook)
        if row is None:
            logging.error("曲 '%s' に対応する行が見つかりません。スキップします。", song)
            continue

        # UGCシートを更新
        try:
            delta_count = update_ugc_entry(workbook, ugc_count, row)
            update_difference_entry(workbook, delta_count, row)
        except Exception as e:
            logging.error("曲 '%s' のExcel更新中にエラーが発生しました: %s", song, e)

        # 保存
        try:
            workbook.save(config.EXCEL_FILE_PATH)
            logging.info("曲 '%s' のデータをExcelに保存しました。", song)
        except Exception as e:
            logging.error("Excelファイルの保存中にエラーが発生しました: %s", e)

        time.sleep(random.uniform(1, 3))


def retry_mode(workbook, driver):
    # 失敗したエントリを取得
    failed_entries = find_failed_entries(workbook)
    if not failed_entries:
        logging.info("再試行対象の '取得失敗' エントリがありません。処理を終了します。")
        return

    logging.info("再試行対象のエントリ数: %d", len(failed_entries))

    # 更新のためにExcelを再度読み込む（数式を維持）
    try:
        workbook_update = openpyxl.load_workbook(config.EXCEL_FILE_PATH)
    except Exception as e:
        logging.error("Excelファイルの再読み込みに失敗しました: %s", e)
        return

    try:
        for entry in failed_entries:
            row = entry['row']
            song = entry['song']
            url = entry['url']
            logging.info("曲 '%s' のUGC数再取得を開始します。URL: %s", song, url)

            try:
                ugc_count = get_ugc_count(driver, url)
                logging.info("曲 '%s' のUGC数: %d", song, ugc_count)
            except Exception as e:
                logging.error("曲 '%s' のUGC数再取得中にエラーが発生しました: %s", song, e)
                ugc_count = "取得失敗"

            # UGCシートを更新
            try:
                delta = update_ugc_entry(workbook_update, ugc_count, row)
                update_difference_entry(workbook_update, delta, row)
            except Exception as e:
                logging.error("曲 '%s' のExcel更新中にエラーが発生しました: %s", song, e)

            # Excelを保存
            try:
                workbook_update.save(config.EXCEL_FILE_PATH)
                logging.info("曲 '%s' のデータをExcelに保存しました。", song)
            except Exception as e:
                logging.error("Excelファイルの保存中にエラーが発生しました: %s", e)

            time.sleep(random.uniform(1, 3))

    finally:
        workbook_update.close()

def main():
    parser = argparse.ArgumentParser(description="UGCデータ処理スクリプト")
    parser.add_argument(
        'mode',
        choices=['process', 'retry'],
        help="実行モードを選択します。'process' で通常処理、'retry' で再試行処理を実行します。"
    )
    args = parser.parse_args()

    setup_logging()

    # Excelを開く
    try:
        workbook = openpyxl.load_workbook(config.EXCEL_FILE_PATH)
        logging.info("Excelファイルを正常に読み込みました: %s", config.EXCEL_FILE_PATH)
    except Exception as e:
        logging.error("Excelファイルの読み込みに失敗しました: %s", e)
        sys.exit(1)

    # WebDriverを初期化
    try:
        driver = initialize_driver()
        logging.info("WebDriverを正常に初期化しました。")
    except WebDriverException as e:
        logging.error("WebDriverの初期化に失敗しました: %s", e)
        workbook.close()
        sys.exit(1)

    try:
        if args.mode == 'process':
            process_mode(workbook, driver)
        elif args.mode == 'retry':
            retry_mode(workbook, driver)
    finally:
        driver.quit()
        logging.info("WebDriverを終了しました。")
        workbook.close()
        logging.info("スクリプトの実行を終了します。")


if __name__ == "__main__":
    main()