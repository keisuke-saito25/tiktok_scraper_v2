import config
import openpyxl
import logging
import os

log_dir = os.path.dirname(config.LOG_FILE_PATH)
if log_dir and not os.path.exists(log_dir):
    os.makedirs(log_dir)

logging.basicConfig(
    filename=config.LOG_FILE_PATH,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def read_a1(file_path):
    """
    テスト用に作成
    """
    try:
        workbook = openpyxl.load_workbook(file_path)
        sheet = workbook.active
        a1_value = sheet['A1'].value
        return a1_value
    except Exception as e:
        logging.error(f"エラーが発生しました： {e}")
        return None

def read_urls(file_path):
    """
    ExcelファイルのB4セルから下にあるURLを全て読み取る関数
    """
    try:
        workbook = openpyxl.load_workbook(file_path)
        sheet = workbook.active
        urls = []
        start_row = 4
        column = 'B'
        header = sheet[f'{column}{start_row}'].value

        if header != 'URL':
            logging.warning(f"期待するヘッダー 'URL' がセル {column}{start_row} に見つかりません。実際の値: {header}")
            return urls
        
        current_row = start_row + 1
        while True:
            cell_value = sheet[f'{column}{current_row}'].value
            if cell_value is None:
                break # 空セルに達したら終了
            urls.append(cell_value)
            current_row += 1
            
        return urls
        
    except Exception as e:
        logging.error(f"エラーが発生しました: {e}")
        return []

def main():
    a1 = read_a1(config.EXCEL_FILE_PATH)
    if a1 is not None:
        logging.info(f"A1の値: {a1}")
    else:
        logging.error("A1の値を取得できませんでした。")

    urls = read_urls(config.EXCEL_FILE_PATH)
    if urls:
        logging.info("取得したURL一覧")
        for idx, url in enumerate(urls, start=1):
            logging.info(f"{idx}. {url}")
    else:
        logging.warning("URLを取得できませんでした。")

if __name__ == "__main__":
    main()