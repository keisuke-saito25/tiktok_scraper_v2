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

def get_ugc_count(driver, url):
    """
    指定されたURLからUGC数を取得する関数
    """
    driver.get(url)
    time.sleep(random.uniform(1, 3))

    try:
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
        logging.error("URL: %s | UGC数の取得がタイムアウトしました。", url)
        return 0
    except Exception as e:
        logging.error("URL: %s | UGC数の取得中にエラーが発生しました: %s", url, e)
        return 0

def initialize_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
    logging.info("Chrome WebDriverを初期化しました。")
    return driver