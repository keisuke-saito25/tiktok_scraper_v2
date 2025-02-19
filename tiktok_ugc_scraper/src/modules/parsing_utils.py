import re
import logging
from modules.constants import MULTIPLIERS

def parse_number(text):
    """
    テキストから数値を抽出し、KやMを考慮して数値を返す関数
    例:
    "50.3K" -> 50300
    "1.2M" -> 1200000
    "123" -> 123
    """
    match = re.match(r'^([\d,.]+)([KMB]?)$', text.strip(), re.IGNORECASE)
    if not match:
        logging.warning("数値として解析できませんでした: '%s'", text)
        return 0
    number, suffix = match.groups()
    number = number.replace(',', '').replace('.', '')
    try:
        value = float(number)
        if suffix.upper() in MULTIPLIERS:
            value *= MULTIPLIERS[suffix.upper()]
        return int(value)
    except ValueError:
        logging.error("数値変換エラー: '%s'", text)
        return 0