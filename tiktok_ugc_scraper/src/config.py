import json
import os
import logging
import sys

def resource_path(relative_path):
    """実行可能ファイルのディレクトリを基準にパスを取得する関数"""
    if getattr(sys, 'frozen', False):
        # PyInstaller でバンドルされた場合、実行可能ファイルのディレクトリを基準とする
        base_path = os.path.dirname(sys.executable)
    else:
        # 通常の実行環境の場合、現在のディレクトリを基準とする
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

CONFIG_FILE = resource_path("config.json")

def load_config():
    if not os.path.exists(CONFIG_FILE):
        logging.error(f"設定ファイル {CONFIG_FILE} が見つかりません。")
        raise FileNotFoundError(f"{CONFIG_FILE} が存在しません。")
    
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        try:
            config = json.load(f)
        except json.JSONDecodeError as e:
            logging.error(f"設定ファイルの解析に失敗しました: {e}")
            raise
    
    # 必須項目のチェック
    required_keys = ["EXCEL_FILE_PATH", "LOG_FILE_PATH"]
    missing_keys = [key for key in required_keys if key not in config]
    if missing_keys:
        logging.error(f"設定ファイル {CONFIG_FILE} に必要なキーが欠けています: {', '.join(missing_keys)}")
        raise KeyError(f"{', '.join(missing_keys)} が設定ファイルに存在しません。")
    
    return config

# 設定のロード
try:
    config_data = load_config()
    EXCEL_FILE_PATH = config_data["EXCEL_FILE_PATH"]
    LOG_FILE_PATH = resource_path(config_data["LOG_FILE_PATH"])
except Exception as e:
    logging.basicConfig(level=logging.ERROR)
    logging.error(f"設定のロードに失敗しました: {e}")
    sys.exit(1)