# modules/scraper.py
import os
import shutil
import logging
import time
import random
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

from modules.parsing_utils import parse_number
from modules.constants import UGC_COUNT_XPATH, WEBDRIVER_WAIT_TIME


# -----------------------------
# UGC 取得（int か None を返す）
# -----------------------------
def get_ugc_count(driver, url, max_retries: int = 3, retry_delay: int = 5):
    """
    指定された TikTok 楽曲URL から UGC 総数を取得する。
    正常時: int を返す / 失敗時: None を返す（呼び出し側で扱いを決める）

    :param driver: Selenium WebDriver
    :param url:    楽曲ページURL
    :param max_retries: 最大リトライ回数
    :param retry_delay: リトライ間隔（指数バックオフの基準秒）
    :return: int | None
    """
    for attempt in range(max_retries + 1):
        try:
            driver.get(url)

            # DOM 完了待ち
            WebDriverWait(driver, WEBDRIVER_WAIT_TIME).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            # 描画安定のため少し待つ
            time.sleep(random.uniform(1, 3))

            # UGC 数の要素を待機
            total_ugc_element = WebDriverWait(driver, WEBDRIVER_WAIT_TIME).until(
                EC.presence_of_element_located((By.XPATH, UGC_COUNT_XPATH))
            )

            # 表示文字列→数値
            txt = total_ugc_element.text.replace("本の動画", "").replace(",", "").strip()
            val = parse_number(txt)  # 例: "66.6K" や "8,030" などにも対応する想定

            if val is None:
                logging.warning("URL: %s | UGC数の解析に失敗: %r", url, txt)
                if attempt < max_retries:
                    logging.info("リトライします... (%d/%d)", attempt + 1, max_retries)
                    # まれに真っ白対策で refresh
                    try:
                        driver.refresh()
                    except Exception:
                        pass
                    time.sleep(retry_delay * (attempt + 1))
                    continue
                return None

            logging.info("URL: %s | 取得したUGC数: %d", url, val)
            return val

        except TimeoutException:
            if attempt < max_retries:
                logging.warning("URL: %s | タイムアウト。リトライ中... (%d/%d)", url, attempt + 1, max_retries)
                try:
                    driver.refresh()
                except Exception:
                    pass
                time.sleep(retry_delay * (attempt + 1))
                continue
            logging.error("URL: %s | 最大リトライ回数に到達（Timeout）。", url)
            return None

        except Exception as e:
            if attempt < max_retries:
                logging.warning("URL: %s | 取得中に例外: %s | リトライ中... (%d/%d)", url, e, attempt + 1, max_retries)
                try:
                    driver.refresh()
                except Exception:
                    pass
                time.sleep(retry_delay * (attempt + 1))
                continue
            logging.error("URL: %s | 取得失敗: %s", url, e)
            return None

    return None


# -----------------------------
# WebDriver 初期化（堅牢版）
# -----------------------------
def initialize_driver(
    profile_dir: str | None = None,
    headless: bool = True,
    disable_images: bool = True,
    user_agent: str | None = None,
):
    """
    Selenium WebDriver を初期化（CLI/GUI 共用・並列起動に強い版）。

    - profile_dir を指定するとそのプロファイルで起動。起動に失敗した場合は
      自動的に <profile_dir>_clean のクリーンプロファイルへフォールバック。
    - 画像 OFF/ヘッドレス/UA などの基本オプションも設定。
    """
    def _make_options(pdir: str | None) -> Options:
        o = Options()

        # 新ヘッドレス（必要時のみ）
        if headless:
            o.add_argument("--headless=new")

        # 安定化オプション
        o.add_argument("--no-sandbox")
        o.add_argument("--disable-dev-shm-usage")
        o.add_argument("--disable-gpu")
        o.add_argument("--disable-extensions")
        o.add_argument("--no-first-run")
        o.add_argument("--no-default-browser-check")
        o.add_argument("--disable-notifications")
        o.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        o.add_argument("--remote-debugging-port=0")  # ポート衝突の回避
        o.page_load_strategy = "eager"

        # プロファイル
        if pdir:
            Path(pdir).mkdir(parents=True, exist_ok=True)
            o.add_argument(f"--user-data-dir={os.path.abspath(pdir)}")

        # 画像 OFF
        if disable_images:
            prefs = {"profile.managed_default_content_settings.images": 2}
            o.add_experimental_option("prefs", prefs)

        # UA
        if user_agent:
            o.add_argument(f"--user-agent={user_agent}")
        else:
            o.add_argument(
                "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
            )
        return o

    def _launch_with(pdir: str | None):
        return webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()),
            options=_make_options(pdir),
        )

    # --- 1st try: 指定プロファイルで起動
    try:
        drv = _launch_with(profile_dir)
        _post_boot_patch(drv)
        logging.info(
            "Chrome WebDriver 初期化: profile=%s, headless=%s, images=%s",
            profile_dir,
            headless,
            "OFF" if disable_images else "ON",
        )
        return drv
    except WebDriverException as e:
        logging.error("WebDriver 起動失敗（指定プロファイル）: %s", e)

    # --- 2nd try: クリーンプロファイルでリトライ
    clean_dir = None
    try:
        if profile_dir:
            clean_dir = str(Path(profile_dir).with_name(Path(profile_dir).name + "_clean"))
            shutil.rmtree(clean_dir, ignore_errors=True)
            Path(clean_dir).mkdir(parents=True, exist_ok=True)
        drv = _launch_with(clean_dir)
        _post_boot_patch(drv)
        logging.info(
            "Chrome WebDriver 初期化（クリーンフォールバック）: profile=%s, headless=%s, images=%s",
            clean_dir,
            headless,
            "OFF" if disable_images else "ON",
        )
        return drv
    except WebDriverException as e2:
        logging.error("WebDriver 起動失敗（クリーンフォールバック）: %s", e2)
        raise


def _post_boot_patch(driver):
    """起動後の軽微な検出回避パッチ（失敗しても無視）"""
    try:
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    except Exception:
        pass
