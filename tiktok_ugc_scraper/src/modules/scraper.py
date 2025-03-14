import logging
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from modules.parsing_utils import parse_number
from modules.constants import UGC_COUNT_XPATH, WEBDRIVER_WAIT_TIME 

def get_ugc_count(driver, url, max_retries=3, retry_delay=5):
    """
    指定されたURLからUGC数を取得する関数
    
    Parameters:
    - driver: Selenium WebDriverのインスタンス
    - url: スクレイピング対象のURL
    - max_retries: タイムアウト時の最大リトライ回数
    - retry_delay: リトライ間の待機時間（秒）
    
    Returns:
    - int: 取得したUGC数
    - str: "取得失敗" (すべてのリトライが失敗した場合)
    """
    for attempt in range(max_retries + 1):  # 初回 + リトライ回数
        try:
            driver.get(url)

            # ページの読み込みが完了するまで待機
            WebDriverWait(driver, WEBDRIVER_WAIT_TIME).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
            
            # ランダムな待機時間（ブロック対策）
            time.sleep(random.uniform(1, 3))
            
            total_ugc_element = WebDriverWait(driver, WEBDRIVER_WAIT_TIME).until(
                EC.presence_of_element_located(
                    (By.XPATH, UGC_COUNT_XPATH)
                )
            )
            total_ugc_text = total_ugc_element.text.replace('本の動画', '').replace(',', '').strip()
            total_ugc = parse_number(total_ugc_text)
            logging.info("URL: %s | 取得したUGC数: %d", url, total_ugc)
            return total_ugc
            
        except TimeoutException:
            if attempt < max_retries:
                logging.warning(
                    "URL: %s | UGC数の取得がタイムアウトしました。リトライ中... (%d/%d)", 
                    url, attempt + 1, max_retries
                )
                # ブラウザの更新を試みる
                driver.refresh()
                # リトライ前の待機
                wait_time = retry_delay * (attempt + 1)
                time.sleep(wait_time)
            else:
                logging.error(
                    "URL: %s | UGC数の取得に失敗しました。最大リトライ回数 (%d) に達しました。", 
                    url, max_retries
                )
                return "取得失敗"
                
        except Exception as e:
            if attempt < max_retries:
                logging.warning(
                    "URL: %s | UGC数の取得中にエラーが発生しました: %s. リトライ中... (%d/%d)", 
                    url, e, attempt + 1, max_retries
                )
                # ブラウザの更新を試みる
                try:
                    driver.refresh()
                except:
                    pass
                # リトライ前の待機
                wait_time = retry_delay * (attempt + 1)
                time.sleep(wait_time)
            else:
                logging.error(
                    "URL: %s | UGC数の取得に失敗しました: %s. 最大リトライ回数 (%d) に達しました。", 
                    url, e, max_retries
                )
                return "取得失敗"
    
    # ここには到達しないはずだが、念のため
    return "取得失敗"

def initialize_driver():
    """
    Selenium WebDriverを初期化する関数
    """
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.page_load_strategy = 'eager'
    # タイムアウト設定
    chrome_options.add_argument('--disable-gpu')
    # 追加のブロック対策
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36')
    
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
    
    # JavaScriptを実行してWebDriverを検出されないようにする
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    logging.info("Chrome WebDriverを初期化しました。")
    return driver