import openpyxl
import logging
from datetime import datetime, timedelta
from modules.constants import (
    UGC_SHEET_NAME,
    DIFFERENCE_SHEET_NAME,
    URL_COLUMN,
    HEADER_ROW,
    START_ROW,
    DATE_FORMAT,
    ALERT_CELL,
    DELTA_COLUMN,
    RATIO_COLUMN,
    MIN_COL_FOR_COMPARISON,
    ALERT_FILL_COLOR,
    ALERT_FONT_COLOR,
    DEFAULT_FILL_TYPE,
    DEFAULT_FONT_COLOR
)
from openpyxl.styles import PatternFill, Font
from openpyxl.utils import get_column_letter


def read_alert_value(file_path):
    """
    B1セルからアラートの基準値を読み込む関数
    """
    try:
        workbook = openpyxl.load_workbook(file_path)
        sheet = workbook.active
        b1_value = sheet[ALERT_CELL].value

        if b1_value is None:
            logging.error("B1セルが空です。アラート基準値を設定してください。")
            return None

        try:
            alert_value = float(b1_value)
            logging.info(f"アラート基準値を {alert_value}% として読み込みました。")
            return alert_value
        except ValueError:
            logging.error(f"B1セルの値が数値ではありません: {b1_value}")
            return None

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
        column = URL_COLUMN
        header = sheet[f'{column}{HEADER_ROW}'].value

        if header != 'URL':
            logging.warning(f"期待するヘッダー 'URL' がセル {column}{HEADER_ROW} に見つかりません。実際の値: {header}")
            return urls
        
        current_row = HEADER_ROW + 1
        while True:
            cell_value = sheet[f'{column}{current_row}'].value
            if cell_value is None:
                break  # 空セルに達したら終了
            urls.append(cell_value)
            current_row += 1
            
        return urls
        
    except Exception as e:
        logging.error(f"エラーが発生しました: {e}")
        return []

def get_sheet(workbook, sheet_name):
    """
    指定されたシート名のシートを取得する関数
    """
    if sheet_name in workbook.sheetnames:
        return workbook[sheet_name]
    else:
        logging.error(f"シート '{sheet_name}' が存在しません。")
        raise ValueError(f"シート '{sheet_name}' が存在しません。")

def get_or_create_today_column(sheet, header_row=4):
    """
    当日日付の列を取得する。存在しなければ最終列の次に追加
    """
    # シートのクリーニング
    clean_sheet(sheet, header_row)  

    today_str = datetime.now().strftime(DATE_FORMAT)

    # ヘッダー行のセルを取得
    header_cells = sheet[header_row]
    header_values = [cell.value for cell in header_cells]

    # 当日日付がすでに存在するか確認
    try:
        col = header_values.index(today_str) + 1
        return col, False
    except ValueError:
        last_col_with_data = get_last_column_with_data(header_values)
        new_col = last_col_with_data + 1
        sheet.cell(row=header_row, column=new_col).value = today_str
        return new_col, True  # 新規作成

def get_last_column_with_data(header_values):
    """
    ヘッダー行の値から、最後にデータが存在する列番号を返す
    """
    last_col = 0
    for idx, value in enumerate(header_values, start=1):
        if value is not None:
            last_col = idx
    return last_col


def clean_sheet(sheet, header_row=4):
    """
    ヘッダー行以降で不必要な最終列を削除する関数
    """
    for col in range(sheet.max_column, 0, -1):
        # ヘッダー行のセルを基準にチェック
        cell = sheet.cell(row=header_row, column=col)
        if cell.value is None and not any(sheet.cell(row=row, column=col).value for row in range(header_row+1, sheet.max_row+1)):
            sheet.delete_cols(col)
        else:
            break  # データが存在する列が見つかったら終了

def apply_style(cell, fill, font):
    """
    セルにスタイルを適用する関数
    """
    cell.fill = fill
    cell.font = font

def check_and_apply_alert(cell_delta, cell_ratio, ratio, alert_value, styles, row):
    """
    アラート条件をチェックし、セルにスタイルを適用またはリセットする関数
    """
    alert_fill, alert_font, default_fill, default_font = styles
    if alert_value is not None and ratio >= alert_value:
        logging.debug(f"アラート条件を満たしました。行: {row}, ratio: {ratio:.2f}% >= {alert_value}%")
        apply_style(cell_delta, alert_fill, alert_font)
        apply_style(cell_ratio, alert_fill, alert_font)
    else:
        logging.debug(f"アラート条件を満たしていません。行: {row}, ratio: {ratio:.2f}% < {alert_value}%")
        apply_style(cell_delta, default_fill, default_font)
        apply_style(cell_ratio, default_fill, default_font)

def update_ugc_sheet(file_path, ugc_counts):
    """
    UGCシートにUGC数を書き込み、増減数と増減率を更新する関数
    増加がアラート基準値を超えた場合、セルにスタイルを適用する
    増減数をリストで返す
    """
    try:
        workbook = openpyxl.load_workbook(file_path)
        ugc_sheet = get_sheet(workbook, UGC_SHEET_NAME)
    except ValueError as e:
        logging.error(e)
        return[]

    # アラート基準値を読み込む
    alert_value = read_alert_value(file_path)
    if alert_value is None:
        logging.warning("アラート基準値が設定されていません。")

    today_col, is_new = get_or_create_today_column(ugc_sheet)
    if is_new:
        logging.info(f"UGCシートに新しい日付の列を追加しました: {today_col}")

    start_row = START_ROW
    delta_counts = []

    # スタイルの定義
    alert_fill = PatternFill(start_color=ALERT_FILL_COLOR, end_color=ALERT_FILL_COLOR, fill_type="solid")
    alert_font = Font(bold=True, color=ALERT_FONT_COLOR)
    default_fill = PatternFill(fill_type=DEFAULT_FILL_TYPE)
    default_font = Font(bold=False, color=DEFAULT_FONT_COLOR)

    styles = (alert_fill, alert_font, default_fill, default_font)

    for idx, ugc in enumerate(ugc_counts):
        row = start_row + idx
        # 当日のUGC数を書き込む
        ugc_sheet.cell(row=row, column=today_col).value = ugc

         # 前日との比較
        if today_col <= MIN_COL_FOR_COMPARISON:
            delta = 0
            ratio = 0
            logging.debug(f"行 {row} の前日データが不足しています。")
        else:
            prev_col = today_col - 1
            prev_ugc = ugc_sheet.cell(row=row, column=prev_col).value
            if prev_ugc is None or not isinstance(prev_ugc, (int, float)):
                logging.warning(f"行 {row} の前日のUGC数が無効です。")
                delta = 0
                ratio = 0
            else:
                delta = ugc - prev_ugc
                ratio = (delta / prev_ugc) * 100 if prev_ugc != 0 else 0

        logging.debug(f"行 {row}: delta={delta}, ratio={ratio:.2f}%, alert_value={alert_value}")
        delta_counts.append(delta)


        # 増減数 (B列) と増減率 (C列) を更新
        cell_delta = ugc_sheet.cell(row=row, column=DELTA_COLUMN)
        cell_delta.value = delta

        cell_ratio = ugc_sheet.cell(row=row, column=RATIO_COLUMN)
        cell_ratio.value = f"{ratio:.2f}%"

        # アラートチェック
        check_and_apply_alert(cell_delta, cell_ratio, ratio, alert_value, styles, row)

    # ファイルに保存
    workbook.save(file_path)
    logging.info("UGCシートの更新が完了しました。")

    return delta_counts

def update_difference_sheet(file_path, delta_counts):
    """
    増減シートに増減数を書き込む関数
    """
    try:
        workbook = openpyxl.load_workbook(file_path)
        difference_sheet = get_sheet(workbook, DIFFERENCE_SHEET_NAME)
    except ValueError as e:
        logging.error(e)
        return[]
    
    today_str = datetime.now().strftime(DATE_FORMAT)
    today_col, is_new = get_or_create_today_column(difference_sheet)
    if is_new: 
        logging.info(f"増減シートに新しい日付の列を追加しました: {today_str}")
        difference_sheet.cell(row=4, column=today_col).value = today_str

    start_row = START_ROW

    for idx, delta in enumerate(delta_counts):
        row = start_row + idx
        song_name_cell = difference_sheet.cell(row=row, column=1)
        if not song_name_cell.value:
            logging.warning(f"行 {row} に曲名が存在しません。")
            continue
        difference_sheet.cell(row=row, column=today_col).value = delta
    
    workbook.save(file_path)
    logging.info("増減シートの更新が完了しました。")
