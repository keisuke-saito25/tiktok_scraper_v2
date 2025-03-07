import os
import random
import re
import sys
import time
import logging
import pandas as pd
import threading
from datetime import datetime, timedelta
from openpyxl import load_workbook, Workbook
from openpyxl.utils.exceptions import InvalidFileException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
import tkinter as tk
from tkinter import messagebox, scrolledtext
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import gc
from concurrent.futures import ThreadPoolExecutor
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
import psutil
import pytz
import json
import shutil
import requests
# os.chdir(os.path.dirname(os.path.abspath(__file__)))
def get_executable_dir():
    if getattr(sys, 'frozen', False):
        # PyInstallerでコンパイルされた実行ファイルの場合
        return os.path.dirname(sys.executable)
    else:
        # 通常のPythonスクリプトの場合
        return os.path.dirname(os.path.abspath(__file__))

exec_dir = get_executable_dir()
os.chdir(exec_dir)

images_dir = os.path.join(exec_dir, 'images')

# ログ設定
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

# グローバルで管理される停止フラグ
stop_flag = threading.Event()

class TextHandler(logging.Handler):
    def __init__(self, text_widget, log_display_var):
        super().__init__()
        self.text_widget = text_widget
        self.log_display_var = log_display_var

    def emit(self, record):
        if self.log_display_var.get():
            msg = self.format(record)
            def append():
                self.text_widget.configure(state='normal')
                self.text_widget.insert(tk.END, msg + '\n')
                self.text_widget.configure(state='disabled')
                self.text_widget.yview(tk.END)
            self.text_widget.after(0, append)

def clean_logs():
    log_dir = '.'
    now = time.time()
    for filename in os.listdir(log_dir):
        if filename.startswith('app.log'):
            filepath = os.path.join(log_dir, filename)
            if os.stat(filepath).st_mtime < now - 7 * 86400:
                os.remove(filepath)

clean_logs()

def read_initial_settings():
    try:
        settings_file = 'initial_settings.xlsx'
        if not os.path.exists(settings_file):
            raise FileNotFoundError('初期設定Excelファイルが見つかりませんでした。')
        df_settings = pd.read_excel(settings_file, sheet_name='初期設定', header=None)
        save_path = df_settings.iloc[0, 1]
        max_items = df_settings.iloc[2, 1]
        max_items = int(max_items) if pd.notna(max_items) else 0
        df_urls = pd.read_excel(settings_file, sheet_name='取得楽曲URL設定')

        # 空行のインデックスを取得
        empty_row_index = df_urls[(df_urls['曲名'].isnull()) & (df_urls['URL'].isnull())].index
        if not empty_row_index.empty:
            # .iloc を使用して整数位置でスライス
            df_urls = df_urls.iloc[:empty_row_index[0]]

        # '曲名' または 'URL' が欠損している行を削除
        df_urls = df_urls.dropna(subset=['曲名', 'URL'])
        df_urls['曲名'] = df_urls['曲名'].astype(str)
        df_urls['URL'] = df_urls['URL'].astype(str)
        return save_path, max_items, df_urls[['曲名', 'URL']].values.tolist()
    except Exception as e:
        logging.error(f'初期設定の読み込み中にエラーが発生しました: {e}')
        messagebox.showerror('エラー', f'初期設定の読み込み中にエラーが発生しました: {e}')
        return None, None, None
        
def sanitize_filename(name):
    name = name if isinstance(name, str) else 'unknown_song'
    invalid_chars = r'[\\/:*?"<>|\r\n]+'
    sanitized_name = re.sub(invalid_chars, '_', name)
    return sanitized_name

def kill_chrome_processes():
    global webdriver_processes
    for pid in webdriver_processes:
        try:
            p = psutil.Process(pid)
            p.terminate()  # プロセスを優雅に終了
        except psutil.NoSuchProcess:
            logging.warning(f'プロセス {pid} は存在しませんでした。')

    webdriver_processes = []  # プロセスリストをクリア

webdriver_processes = []

def init_driver(headless=False, for_function1=False):
    chrome_options = Options()
    # 高速化のための設定
    prefs = {"profile.managed_default_content_settings.images": 1, 
             "disk-cache-size": 4096}  # キャッシュのサイズを指定
    chrome_options.add_experimental_option("prefs", prefs)
    
    if headless:
        chrome_options.add_argument("--headless=new")

    if for_function1:
        # chrome_options.add_argument("--blink-settings=imagesEnabled=false")
        chrome_options.add_argument("--disable-extensions")
    extension_path = os.path.abspath('vidIQ.crx')
    chrome_options.add_extension(extension_path)
    
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-gpu")  # GPUの使用を制限
    chrome_options.add_argument("--disable-infobars")  # インフォバーの非表示
    # chrome_options.add_argument("--disable-dev-shm-usage")  # 特にLinuxでのメモリ制限回避
    # chrome_options.add_argument("--no-sandbox")  # サンドボックスの無効化

    # 明確にPC用のUser-Agentを設定
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    chrome_options.add_argument(f'user-agent={user_agent}')

    user_data_dir = os.path.abspath('chrome_profile/User Data')
    chrome_options.add_argument(f'--user-data-dir={user_data_dir}')
    profile_directory = 'Default'
    chrome_options.add_argument(f'--profile-directory={profile_directory}')
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_window_size(1420, 1080)  
        driver.execute_script("document.body.style.zoom='{}'".format(0.8 * 100))
        webdriver_processes.append(driver.service.process.pid)
        return driver
    except Exception as e:
        logging.error(f'WebDriverの初期化に失敗しました: {e}')
        messagebox.showerror('エラー', f'WebDriverの初期化に失敗しました: {e}')
        return None

def create_backup_if_exists(excel_filename):
    backup_dir = os.path.join(os.path.dirname(excel_filename), 'backup')
    # フォルダが存在しない場合は作成
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    # ファイルが存在する場合はバックアップを作成
    if os.path.exists(excel_filename):
        try:
            # 現在の日付を取得してフォーマット（例：20231007）
            current_date = datetime.now().strftime('%Y%m%d')
            # 元のファイル名と拡張子を取得
            base_filename = os.path.basename(excel_filename)
            name, ext = os.path.splitext(base_filename)
            # バックアップファイル名を作成（例：filename_20231007.xlsx）
            backup_filename = f"{name}_{current_date}{ext}"
            backup_path = os.path.join(backup_dir, backup_filename)
            # ファイルをコピー
            shutil.copy2(excel_filename, backup_path)
            logging.info(f'バックアップが作成されました: {backup_path}')
            # 古いバックアップを削除
            delete_old_backups(backup_dir, name, ext)
        except Exception as e:
            logging.error(f'バックアップ作成中にエラーが発生しました: {e}') 

def delete_old_backups(backup_dir, name, ext):
    now = time.time()
    for filename in os.listdir(backup_dir):
        if filename.startswith(name) and filename.endswith(ext):
            file_path = os.path.join(backup_dir, filename)
            # ファイルの最終更新日時を取得
            file_mtime = os.path.getmtime(file_path)
            # 7日（604800秒）以上前なら削除
            if file_mtime < now - 7 * 86400:
                try:
                    os.remove(file_path)
                    logging.info(f'古いバックアップファイルを削除しました: {file_path}')
                except Exception as e:
                    logging.error(f'古いバックアップファイルの削除中にエラーが発生しました: {e}')

def function1(save_path, max_items, song_urls, headless=False):
    logging.info('#機能1 処理実行開始')

    for song_name, song_url in song_urls:
        if stop_flag.is_set():
            logging.info('#機能1 処理が停止されました')
            break

        driver = init_driver(headless=headless, for_function1=True)
        driver.execute_script("document.body.style.zoom='{}'".format(0.8 * 100))

        if not driver:
            logging.error('WebDriverの初期化に失敗しました。')
            break

        try:
            sanitized_name = sanitize_filename(song_name)
            excel_filename = os.path.join(save_path, f'{sanitized_name}.xlsx')

            # グローバルの images_dir を使用
            if not os.path.exists(images_dir):
                os.makedirs(images_dir)
                logging.info(f'"images"フォルダを作成しました: {images_dir}')

            # 既存Excelファイルのバックアップ作成
            create_backup_if_exists(excel_filename)

            # ファイルが存在しない場合は新規作成
            if not os.path.exists(excel_filename):
                workbook = create_excel_file(excel_filename)
            else:
                workbook = load_workbook(excel_filename)
                # "ユーザーアイコン"シートが存在しない場合は作成
                if 'ユーザーアイコン' not in workbook.sheetnames:
                    icon_sheet = workbook.create_sheet(title='ユーザーアイコン')
                    icon_sheet.append(['アカウント名', 'アイコンパス'])
                    icon_sheet.column_dimensions['A'].width = 25  # アカウント名
                    icon_sheet.column_dimensions['B'].width = 40  # アイコンパス

            # 楽曲情報シートの更新
            update_music_info_sheet(driver, workbook, song_name, song_url, excel_filename)
            date_sheet = create_or_clear_date_sheet(workbook)

            driver.get(song_url)
            time.sleep(random.uniform(1, 3))

            video_urls = get_video_urls(driver, max_items)
            write_video_links(date_sheet, video_urls)

            write_update_dates(date_sheet)

            # 保存処理に例外処理を追加
            while True:
                try:
                    workbook.save(excel_filename)
                    break
                except PermissionError:
                    messagebox.showwarning('警告', f'ファイルが開かれているため保存できませんでした。\nファイルを閉じて「OK」を押してください。')
                except Exception as e:
                    logging.error(f'ファイルの保存中にエラーが発生しました: {e}')
                    messagebox.showerror('エラー', f'ファイルの保存中にエラーが発生しました: {e}')
                    break

            logging.info(f'#{song_name} 取得完了')

        except Exception as e:
            logging.error(f'楽曲 {song_name} の処理中にエラーが発生しました: {e}')
            # エラーが発生した場合でも保存を試みる
            while True:
                try:
                    workbook.save(excel_filename)
                    break
                except PermissionError:
                    messagebox.showwarning('警告', f'ファイルが開かれているため保存できませんでした。\nファイルを閉じて「OK」を押してください。')
                except Exception as e:
                    logging.error(f'ファイルの保存中にエラーが発生しました: {e}')
                    messagebox.showerror('エラー', f'ファイルの保存中にエラーが発生しました: {e}')
                    break

        finally:
            # driverを終了させる
            driver.quit()

    logging.info('#機能1 処理実行停止')

def create_excel_file(filename):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = '楽曲情報'
    sheet.append(['楽曲名', '楽曲URL', '日付', '総UGC数'])

    # 楽曲情報シートの列幅を設定
    sheet.column_dimensions['A'].width = 30  # 楽曲名
    sheet.column_dimensions['B'].width = 20  # 楽曲URL
    sheet.column_dimensions['C'].width = 18  # 日付
    sheet.column_dimensions['D'].width = 9   # 総UGC数

    # "ユーザーアイコン"シートを作成
    icon_sheet = workbook.create_sheet(title='ユーザーアイコン')
    icon_sheet.append(['アカウント名', 'アイコンパス'])

    # ユーザーアイコンシートの列幅を設定
    icon_sheet.column_dimensions['A'].width = 25 # アカウント名
    icon_sheet.column_dimensions['B'].width = 40 # アイコンパス

    # "images"フォルダを作成（実行ファイルと同じディレクトリ）
    images_dir = os.path.join(exec_dir, 'images')
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)
        logging.info(f'"images"フォルダを作成しました: {images_dir}')

    workbook.save(filename)
    return workbook

def update_music_info_sheet(driver, workbook, song_name, song_url, excel_filename):
    sheet = workbook['楽曲情報']
    driver.get(song_url)
    time.sleep(random.uniform(1, 3))

    try:
        total_ugc_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="main-content-single_song"]/div/div[1]/div[1]/div[2]/h2[2]/strong'))
        )
        # 「本の動画」を削除して数値に変換
        total_ugc = parse_number(total_ugc_element.text.replace('本の動画', '').replace(',', '').strip())
    except TimeoutException:
        total_ugc = 0
        logging.error('総UGC数の取得中にエラーが発生しました')

    # 年、月、日フォーマットで現在の日付を取得
    today_date_only = datetime.today().date()

    found = False
    for row in sheet.iter_rows(min_row=2):
        cell_song_name = row[0].value   # 列A：楽曲名
        cell_date = row[2].value        # 列C：日付

        if isinstance(cell_date, datetime):
            cell_date_only = cell_date.date()  # 日付のみを比較
        elif isinstance(cell_date, str) and cell_date:
            cell_date_only = datetime.strptime(cell_date.split(' ')[0], '%Y/%m/%d').date()
        else:
            cell_date_only = None

        if cell_song_name == song_name and cell_date_only == today_date_only:
            # 同じ楽曲名と日付が見つかれば総UGC数だけ更新
            row[3].value = total_ugc  # 列D：総UGC数
            found = True
            break

    if not found:
        # 同じ日付のエントリがない場合、新しい行を追加
        today_str = datetime.today().strftime('%Y/%m/%d %H:%M')  # 初期保存時に必要
        sheet.append([song_name, song_url, today_str, total_ugc])

    workbook.save(excel_filename)

def create_or_clear_date_sheet(workbook):
    date_sheet_name = datetime.today().strftime('%Y%m%d')
    if date_sheet_name not in workbook.sheetnames:
        sheet = workbook.create_sheet(title=date_sheet_name)
        sheet.append(['投稿ID', '投稿日', 'アカウント名', 'ニックネーム', 'いいね数', 'コメント数', '保存数', 'シェア数', '再生回数', 'フォロワー数', '動画リンク(URL)', '更新日'])

        # データ情報シートの列幅を設定
        sheet.column_dimensions['A'].width = 25  # 投稿ID
        sheet.column_dimensions['B'].width = 12  # 投稿日
        sheet.column_dimensions['C'].width = 13  # アカウント名
        sheet.column_dimensions['D'].width = 13  # ニックネーム
        sheet.column_dimensions['E'].width = 10  # いいね数
        sheet.column_dimensions['F'].width = 10  # コメント数
        sheet.column_dimensions['G'].width = 10  # 保存数
        sheet.column_dimensions['H'].width = 10  # シェア数
        sheet.column_dimensions['I'].width = 10  # 再生回数
        sheet.column_dimensions['J'].width = 10  # フォロワー数
        sheet.column_dimensions['K'].width = 26  # 動画リンク
        sheet.column_dimensions['L'].width = 18  # 更新日
    else:
        sheet = workbook[date_sheet_name]
        # 既存のデータ行（2行目以降）を削除
        if sheet.max_row > 1:
            sheet.delete_rows(2, sheet.max_row - 1)
    return sheet

def get_video_urls(driver, max_items, timeout=10):
    video_urls = []  # 順序を保持するためのリスト
    seen_urls = set()  # 重複を検出するためのセット
    wait = WebDriverWait(driver, timeout)
    scroll_attempts = 0  # 新しい動画が見つからなかった回数
    max_scroll_attempts = 5  # 最大試行回数を5回に設定
    
    scroll_origin = ScrollOrigin.from_viewport(0, 0)  # ビューポートの左上を起点とする
    
    # ページの初期読み込み待機
    time.sleep(random.uniform(1, 2))
    
    while len(video_urls) < max_items:
        if stop_flag.is_set():
            logging.info('動画URLの取得が停止されました')
            break
        
        # 現在のスクロール位置とページの高さを取得
        last_height = driver.execute_script("return document.body.scrollHeight")
        
        # ページ下部までスクロールするループ
        while True:
            # マウスのスクロール動作をシミュレートして下にスクロール
            ActionChains(driver).scroll_from_origin(scroll_origin, 0, 2000).perform()
            time.sleep(random.uniform(0.2, 0.5))  # スクロール後の待機時間を短縮

            new_height = driver.execute_script("return window.pageYOffset + window.innerHeight")
            total_height = driver.execute_script("return document.body.scrollHeight")

            # ページ下部に到達したかチェック
            if abs(new_height - total_height) < 5:
                logging.info('ページ下部に到達しました')
                time.sleep(random.uniform(2, 3))  # 2～3秒待機

            break

        try:
            video_elements = wait.until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, '//*[@data-e2e="music-item-list"]//a[contains(@href, "/video/") or contains(@href, "/photo/")]')
                )
            )
            
            previous_count = len(video_urls)  # 現在の動画URL数を保存
            
            for element in video_elements:
                video_url = element.get_attribute('href')
                if video_url and video_url not in seen_urls:
                    video_urls.append(video_url)
                    seen_urls.add(video_url)
            
            logging.info(f'取得動画URL数: {len(video_urls)}/{max_items}')
            
            if previous_count == len(video_urls):
                # 新しい動画が見つからなかった場合
                scroll_attempts += 1
                logging.info(f'新しい動画が見つからない試行回数: {scroll_attempts}')
                if scroll_attempts >= max_scroll_attempts:
                    logging.info('新しい動画が見つからなくなったため終了します。')
                    break
                else:
                    logging.info('上にスクロールして再試行します。')
                    # 上にスクロール
                    ActionChains(driver).scroll_from_origin(scroll_origin, 0, -2000).perform()
                    time.sleep(random.uniform(0.2, 0.5))  # スクロール後の待機時間を短縮
            else:
                # 新しい動画が見つかった場合、カウントをリセット
                scroll_attempts = 0

            if len(video_urls) >= max_items:
                break

        except TimeoutException:
            logging.warning('動画要素がロードされませんでした。')
            break
    
    logging.info('最終取得動画URL件数: {}'.format(len(video_urls)))
    return video_urls

def write_video_links(sheet, video_urls):
    for url in video_urls:
        sheet.append([None] * 10 + [url] + [None])

def write_update_dates(sheet):
    today_str = datetime.today().strftime('%Y/%m/%d %H:%M')
    for row in sheet.iter_rows(min_row=2, max_row=sheet.max_row, min_col=12, max_col=12):
        for cell in row:
            cell.value = today_str

def function2(save_path, song_urls, headless=False):
    logging.info('#機能2 処理実行開始')
    driver = init_driver(headless=headless)
    if not driver: return

    original_window = driver.current_window_handle
    driver.execute_script("window.open('');")
    driver.execute_script("document.body.style.zoom='{}'".format(0.8 * 100))

    follower_window_handle = driver.window_handles[-1]

    operations_count = 0

    # グローバルの images_dir を使用
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)
        logging.info(f'"images"フォルダを作成しました: {images_dir}')

    for song_name, _ in song_urls:
        if stop_flag.is_set():
            logging.info('#機能2 処理が停止されました')
            break

        sanitized_name = sanitize_filename(song_name)
        excel_filename = os.path.join(save_path, f'{sanitized_name}.xlsx')

        if not os.path.exists(excel_filename):
            logging.error(f'ファイルが存在しません: {excel_filename}')
            continue

        workbook = load_workbook(excel_filename)
        today_str = datetime.today().strftime('%Y%m%d')

        # ユーザーアイコンシートの確認と作成
        if 'ユーザーアイコン' not in workbook.sheetnames:
            icon_sheet = workbook.create_sheet(title='ユーザーアイコン')
            icon_sheet.append(['アカウント名', 'アイコンパス'])
            icon_sheet.column_dimensions['A'].width = 25  # アカウント名
            icon_sheet.column_dimensions['B'].width = 40  # アイコンパス
        else:
            icon_sheet = workbook['ユーザーアイコン']

        if today_str not in workbook.sheetnames:
            logging.error(f'シートが存在しません: {today_str}')
            continue

        sheet = workbook[today_str]

        # 総URL件数をカウント
        total_urls_count = sum(1 for row in sheet.iter_rows(min_row=2, min_col=11, max_col=11) if row[0].value)

        song_operations_count = 0  # 各曲ごとに取得した件数をカウント

        # ユーザーアイコン情報を保持する辞書
        account_icons = {}

        # 既存のアカウント名とアイコンパスをロード
        for row in icon_sheet.iter_rows(min_row=2):
            if row[0].value and row[1].value:
                account_icons[row[0].value] = row[1].value

        for row in sheet.iter_rows(min_row=2, max_col=13):
            if all(cell.value for cell in row[:10]):
                continue

            link = row[10].value
            if not link:
                logging.warning('動画リンクが不正です。')
                continue

            driver.switch_to.window(original_window)
            driver.get(link)
            time.sleep(random.uniform(1, 2))

            data = extract_video_data(driver, original_window, follower_window_handle)
            write_video_data_to_row(sheet, row, data)

            # アイコン処理
            account_name = data.get('アカウント名')
            avatar_url = data.get('アバターURL')

            if account_name and avatar_url and account_name not in account_icons:
                try:
                    # アイコン画像をダウンロード
                    icon_filename = f"{sanitize_filename(account_name)}.jpg"  # アカウント名.jpg
                    icon_path = os.path.join(images_dir, icon_filename)

                    # 相対パスを設定（imagesフォルダ名とファイル名のみ）
                    relative_path = f"images/{icon_filename}"

                    # requestsを使ってダウンロード
                    response = requests.get(avatar_url, stream=True)
                    if response.status_code == 200:
                        with open(icon_path, 'wb') as f:
                            for chunk in response.iter_content(1024):
                                f.write(chunk)

                        # 相対パスを記録
                        account_icons[account_name] = relative_path

                        logging.info(f'アイコンを保存しました: {account_name} -> {relative_path}')
                except Exception as e:
                    logging.error(f'アイコン保存中にエラーが発生しました: {e}')

            operations_count += 1
            song_operations_count += 1  # 各曲ごとの取得件数をインクリメント

            # 10件ごとにログを記録
            if song_operations_count % 10 == 0:
                logging.info(f'{song_name} - 現在の取得件数: {song_operations_count}, 総URL件数: {total_urls_count}')

            # WebDriverの再起動
            if operations_count % 50 == 0:
                logging.info('WebDriverを再起動します。')
                driver.quit()
                time.sleep(5)
                driver = init_driver(headless=headless)
                if not driver:
                    return
                original_window = driver.current_window_handle
                driver.execute_script("window.open('');")
                driver.execute_script("document.body.style.zoom='{}'".format(0.8 * 100))
                follower_window_handle = driver.window_handles[-1]

            if operations_count % 5 == 0:
                # 保存処理に例外処理を追加
                while True:
                    try:
                        workbook.save(excel_filename)
                        break
                    except PermissionError:
                        messagebox.showwarning('警告', f'ファイルが開かれているため保存できませんでした。\nファイルを閉じて「OK」を押してください。')
                    except Exception as e:
                        logging.error(f'ファイルの保存中にエラーが発生しました: {e}')
                        messagebox.showerror('エラー', f'ファイルの保存中にエラーが発生しました: {e}')
                        break

        # アカウントアイコン情報の更新
        # 現在のシートをクリア（ヘッダー行は残す）
        if icon_sheet.max_row > 1:
            icon_sheet.delete_rows(2, icon_sheet.max_row - 1)

        # 新しいデータを書き込み
        for account_name, icon_path in account_icons.items():
            icon_sheet.append([account_name, icon_path])

        # Log the final count for the current song
        logging.info(f'{song_name} - 最終取得件数: {song_operations_count}, 総URL件数: {total_urls_count}')

        # 保存処理に例外処理を追加
        while True:
            try:
                workbook.save(excel_filename)
                break
            except PermissionError:
                messagebox.showwarning('警告', f'ファイルが開かれているため保存できませんでした。\nファイルを閉じて「OK」を押してください。')
            except Exception as e:
                logging.error(f'ファイルの保存中にエラーが発生しました: {e}')
                messagebox.showerror('エラー', f'ファイルの保存中にエラーが発生しました: {e}')
                break

    driver.quit()
    logging.info('#機能2 処理実行停止')
def parse_date_posted(date_posted_str, update_datetime):
    date_posted_str = date_posted_str.strip()

    # 'n日前' の形式
    m = re.match(r'(\d+)日前', date_posted_str)
    if m:
        days_ago = int(m.group(1))
        date_posted = update_datetime - timedelta(days=days_ago)
        return date_posted.strftime('%m/%d')

    # 'n時間前' の形式
    m = re.match(r'(\d+)時間前', date_posted_str)
    if m:
        hours_ago = int(m.group(1))
        date_posted = update_datetime - timedelta(hours=hours_ago)
        return date_posted.strftime('%m/%d')

    # 'n週間前' の形式
    m = re.match(r'(\d+)週間前', date_posted_str)
    if m:
        weeks_ago = int(m.group(1))
        date_posted = update_datetime - timedelta(weeks=weeks_ago)
        return date_posted.strftime('%m/%d')

    # 'mm-dd' の形式
    m = re.match(r'(\d{1,2})-(\d{1,2})', date_posted_str)
    if m:
        month = int(m.group(1))
        day = int(m.group(2))
        return f'{month:02}/{day:02}'

    # 'yyyy-mm-dd' の形式
    m = re.match(r'(\d{4})-(\d{1,2})-(\d{1,2})', date_posted_str)
    if m:
        year = int(m.group(1))
        month = int(m.group(2))
        day = int(m.group(3))
        return f'{year}/{month:02}/{day:02}'

    # その他の形式はそのまま返す
    return date_posted_str

def write_video_data_to_row(sheet, row, data):
    keys = ['投稿ID', '投稿日', 'アカウント名', 'ニックネーム', 'いいね数', 'コメント数', '保存数', 'シェア数', '再生回数', 'フォロワー数', '動画リンク(URL)', '更新日', 'アバターURL']
    for i, key in enumerate(keys):
        value = data.get(key)
        row[i].value = value 

# 動画のデータを抽出
def extract_video_data(driver, original_window, follower_window_handle):
    data = {}
    try:
        current_url = driver.current_url
        try:
            post_id = current_url.rstrip('/').split('/')[-1].split('?')[0]
            data['投稿ID'] = post_id
        except ValueError:
            data['投稿ID'] = 'NaN'
        driver.execute_script("window.scrollBy(0, 100);")

        # アカウント名
        data['アカウント名'] = extract_text_with_retry(driver, By.XPATH, '//span[@data-e2e="browse-username"]', 'アカウント名')

        # 日付とニックネーム
        nickname, date_posted = extract_nickname_and_date(driver)

        # '更新日' を取得
        update_datetime = datetime.now()

        # 'date_posted' をパースして指定の形式に変換
        date_posted = parse_date_posted(date_posted, update_datetime)

        data['ニックネーム'] = nickname
        data['投稿日'] = date_posted

        # いいね数、コメント数、保存数、シェア数、再生回数
        data['いいね数'] = extract_and_parse_number(driver, '//strong[@data-e2e="like-count"]', 'いいね数')
        data['コメント数'] = extract_and_parse_number(driver, '//strong[@data-e2e="comment-count"]', 'コメント数')
        data['保存数'] = extract_and_parse_number(driver, '//strong[@data-e2e="undefined-count"]', '保存数')
        data['シェア数'] = extract_and_parse_number(driver, '//strong[@data-e2e="share-count"]', 'シェア数')
        if data['シェア数'] == None:
            data['シェア数'] = 0
        data['再生回数'] = extract_and_parse_number(driver, '//*[@id="main-content-video_detail"]/div/div[2]/div/div[1]/div[1]/div[2]/div[1]/div/div/div[2]/p', '再生回数')

        # フォロワー数を非同期タスクとして実行
        with ThreadPoolExecutor() as executor:
            future = executor.submit(get_follower_count, driver, original_window, follower_window_handle)
            data['フォロワー数'] = future.result()

        data['動画リンク(URL)'] = current_url
        data['更新日'] = datetime.today().strftime('%Y/%m/%d %H:%M')
        img_element = driver.find_element(By.XPATH, '//img[@alt=""]')
        avatar_url = img_element.get_attribute('src')
        data['アバターURL'] = avatar_url
    except Exception as e:
        logging.error(f'動画データの抽出中にエラーが発生しました: {e}', exc_info=True)
        # データが取得できなかった場合は空欄にする
        data = {key: '' for key in ['投稿ID', '投稿日', 'アカウント名', 'ニックネーム',
                                    'いいね数', 'コメント数', '保存数', 'シェア数',
                                    '再生回数', 'フォロワー数', '動画リンク(URL)', '更新日', 'アバターURL']}
    return data

def handle_photo_page_interference(driver):
    """写真ページでオーバーレイや干渉を処理する"""
    try:
        # 指定された文言が含まれるスパン要素を探し、オーバーレイを閉じる
        puzzle_element = WebDriverWait(driver, 1).until(
            EC.presence_of_element_located(
                (By.XPATH, '//span[contains(text(), "スライダーをドラッグしてパズルを完成させてください") or contains(text(), "パズルのピースを正しい場所にドラッグしてください")]')
            )
        )
        if puzzle_element:
            logging.info('スライダーをドラッグしてパズルを完成させてください 文言が見つかりました。')
            try:
                close_button_element = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//button[@id="captcha_close_button"]')))
            except:
                pass
            try:
                close_button_element = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//svg[contains(@viewBox, '0 0 48 48') and @xmlns='http://www.w3.org/2000/svg']//path[contains(@d, 'M10.19 36.19')]")))
            except:
                pass
            close_button_element.click()
            logging.info('閉じるボタンをクリックしました。')
            driver.execute_script("window.scrollBy(0, 100);")

    except:
        pass

def extract_nickname_and_date(driver):
    element_text = ''
    date_text = ''

    try:
        # 試行1: 提供された構造に基づく取得
        element_text = extract_text_with_retry(driver, By.XPATH, '//span[@data-e2e="browser-nickname"]/span[@class="css-1xccqfx-SpanNickName e17fzhrb1"]', 'ニックネーム')
        date_text = extract_text_with_retry(driver, By.XPATH, '//span[@data-e2e="browser-nickname"]/span[3]', '投稿日')
    except Exception:
        pass

    if not element_text or not date_text:
        try:
            # 試行2: 別のアプローチで確認
            combined_text = extract_text_with_retry(driver, By.XPATH, '//span[@data-e2e="browser-nickname"]', '日付とニックネーム')
            if combined_text:
                split_data = combined_text.split('·')
                element_text = split_data[0].strip()
                date_text = split_data[1].strip() if len(split_data) > 1 else ''
        except Exception:
            pass

    if not element_text or not date_text:
        try:
            # 試行3: 例外的な構造に対応
            element_text = extract_text_with_retry(driver, By.XPATH, '//span[@data-e2e="browser-nickname"]/span[@class="css-1xccqfx-SpanNickName e17fzhrb1"]', 'ニックネーム') or element_text
            date_text = extract_text_with_retry(driver, By.XPATH, '//span[@data-e2e="browser-nickname"]/span[contains(text(), "時間前")]', '投稿日') or date_text
        except Exception:
            pass

    if not element_text or not date_text:
        logging.error('ニックネームと日付の取得中にエラーが発生しました')

    return element_text, date_text

def extract_text_with_retry(driver, by, value, description):
    """指定された要素からテキストを効率的に取得するための関数。要素の視認性は不要。"""
    locator = (by, value)
    max_attempts = 1  # 最大リトライ回数を増加
    attempts = 0
    while attempts < max_attempts:
        try:
            # 要素が存在するまで待機（最大5秒）
            element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located(locator)
            )
            text = element.text
            if text:
                return text
            else:
                logging.warning(f'{description}のテキストが取得できませんでした。再試行します... ({attempts + 1}/{max_attempts})')
                attempts += 1
                time.sleep(0.5)
        except TimeoutException:
            logging.warning(f'{description}の要素が見つかりませんでした。再試行します... ({attempts + 1}/{max_attempts})')
            attempts += 1
        except Exception as e:
            logging.warning(f'{description}の取得中にエラーが発生しました: {e}。再試行します... ({attempts + 1}/{max_attempts})')
            attempts += 1

    logging.error(f'{description}の取得に失敗しました。')
    return ''

def extract_and_parse_number(driver, xpath, description):
    """指定されたXPathからテキストを取得し、数値に解析する。取得失敗時は空を返す。"""
    text = extract_text_with_retry(driver, By.XPATH, xpath, description)
    if text:  
        return parse_number(text)
    else:
        return ''

def parse_number(text):
    """数値をパースし、KやMの単位変換を行う"""
    multipliers = {'K': 1000, 'M': 1000000}
    multiplier = 1
    if text[-1] in multipliers:
        multiplier = multipliers[text[-1]]
        text = text[:-1]
    try:
        return int(float(text.replace(',', '').strip()) * multiplier)
    except ValueError:
        return None

def get_follower_count(driver, original_window, follower_window_handle):
    follower_count = ''
    try:
        account_url_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//a[@data-e2e="browse-user-avatar"]'))
        )
        account_url = account_url_element.get_attribute('href')
        driver.switch_to.window(follower_window_handle)
        driver.get(account_url)
        try:
            followers_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//strong[@data-e2e="followers-count"]'))
            )
            follower_count = parse_number(followers_element.text)
        except (NoSuchElementException, TimeoutException):
            follower_count = ''
        driver.switch_to.window(original_window)
    except Exception as e:
        logging.error(f'フォロワー数の取得中にエラーが発生しました: {e}')
    return follower_count

def login_authentication():
    driver = init_driver(headless=False)
    if not driver:
        return
    driver.get('https://www.tiktok.com/login')
    messagebox.showinfo('ログイン', 'TikTokのログイン画面が表示されました。ログインが完了したらブラウザを閉じてください。')
    while True:
        time.sleep(5)
        try:
            if driver.current_url:
                continue
        except WebDriverException:
            break
    messagebox.showinfo('成功', 'ログインが完了しました。')
    driver.quit()

def stop_all_operations():
    global stop_flag
    stop_flag.set()  # ストップフラグを立てる
    clean_up_resources()

def clean_up_resources():
    logging.info('リソースをクリーンアップ中...')
    try:
        kill_chrome_processes()
    except Exception as e:
        logging.error(f'WebDriverの停止中にエラーが発生しました: {e}')
    gc.collect()  # ガベージコレクションを実行
    logging.info('ガベージコレクション実行済み')
    messagebox.showinfo('停止', '全ての操作が停止され、リソースが解放されました。')

def stop_processing():
    stop_all_operations()
    logging.info('処理が停止されました。')
    messagebox.showinfo('停止', '全ての処理が停止されました。')

# def schedule_task(entry_widget, next_run_var):
#     """指定した時間になったらrun_both_functionsを実行するスケジューラ関数"""
#     last_run_date = None  # 最後に実行された日時を保存する変数

#     while True:
#         now = datetime.now()

#         target_time_str = entry_widget.get()
#         try:
#             target_time = datetime.strptime(target_time_str, '%H:%M').time()
#             target_datetime = datetime.combine(now.date(), target_time)

#             if last_run_date is None:
#                 # 初回実行: 現在の時間が初回セット日時を超えた場合に実行
#                 if now > target_datetime:
#                     logging.info('初回起動を開始します。指定時間に達しました。')
#                     perform_scheduled_task()
#                     last_run_date = now
#                     update_next_run_time_label(next_run_var, target_time)
#             else:
#                 # 2回目以降: 処理完了日時が前回の実行を超えた場合に実行
#                 if now > target_datetime and now.date() != last_run_date.date():
#                     logging.info('再起動を開始します。次回実行時間に達しました。')
#                     perform_scheduled_task()
#                     last_run_date = now
#                     update_next_run_time_label(next_run_var, target_time)

#         except ValueError:
#             logging.error('入力された時刻の形式が不正です (HH:MM 形式で入力してください)')
#             break

        # time.sleep(60)


def update_next_run_time_label(next_run_var, next_run_time):
    """次回の実行時間をラベルに表示する"""
    next_run_var.set(f'次回起動日時: {next_run_time.strftime("%Y-%m-%d %H:%M")}')

def calculate_next_run_time(target_time):
    """次回実行時間を計算する関数"""
    jst = pytz.timezone('Asia/Tokyo')  # JSTタイムゾーンを指定
    now = datetime.now(jst)  # 現在のJST時刻を取得
    target_datetime_today = datetime.combine(now.date(), target_time)
    target_datetime_today = jst.localize(target_datetime_today)  # target_datetime_todayをJSTでローカライズ

    return target_datetime_today + timedelta(days=1) if now >= target_datetime_today else target_datetime_today

def perform_scheduled_task(entry_widget, next_run_var):
    """時間になったらrun_both_functionsを実行"""
    save_path, max_items, song_urls = read_initial_settings()
    if save_path and song_urls:
        headless = False  # タスクスケジューラの場合、ヘッドレスモードが適切
        function1(save_path, max_items, song_urls, headless=headless)
        function2(save_path, song_urls, headless=headless)
        logging.info('スケジュールされた自動起動が完了しました。')
        # 次回実行日時を更新
        target_time = datetime.strptime(entry_widget.get(), '%H:%M').time()
        next_run_time = calculate_next_run_time(target_time)
        update_next_run_time_label(next_run_var, next_run_time)

def schedule_task(entry_widget, next_run_var):
    """指定した時間になったらrun_both_functionsを実行するスケジューラ関数"""
    jst = pytz.timezone('Asia/Tokyo')
    last_run_date = datetime.today().date()  # 初期化を現在の日付に設定

    while True:
        now = datetime.now(jst)
        target_time_str = entry_widget.get()
        try:
            target_time = datetime.strptime(target_time_str, '%H:%M').time()
            target_datetime = datetime.combine(now.date(), target_time)
            target_datetime = jst.localize(target_datetime)

            # 設定日時のみで確認、初日の実行を避けるためにlast_run_dateでチェック
            if now >= target_datetime and now.date() > last_run_date:
                # 設定日時に到達した場合に実行
                perform_scheduled_task(entry_widget, next_run_var)
                # 次回実行日時を次の日に設定
                last_run_date = now.date()
                next_run_time = target_datetime + timedelta(days=1)
                update_next_run_time_label(next_run_var, next_run_time)

        except ValueError:
            logging.error('入力された時刻の形式が不正です (HH:MM 形式で入力してください)')
            break

        time.sleep(60)
        
def schedule_run():
    """指定時刻が入力されたときに次回実行日時を計算し表示する"""
    target_time_str = time_entry.get()
    try:
        target_time = datetime.strptime(target_time_str, '%H:%M').time()
        next_run_time = calculate_next_run_time(target_time)
        update_next_run_time_label(next_run_time_var, next_run_time)
        threading.Thread(target=schedule_task, args=(time_entry, next_run_time_var)).start()
    except ValueError:
        messagebox.showerror('エラー', '時刻の形式が不正です。HH:MM 形式で入力してください。')

def save_schedule_time(time_str):
    with open('config.json', 'w') as config_file:
        json.dump({'target_time': time_str}, config_file)

def load_schedule_time():
    try:
        with open('config.json', 'r') as config_file:
            config = json.load(config_file)
            return config.get('target_time', '')
    except FileNotFoundError:
        return ''

def clear_schedule():
    """スケジュールを取り消して設定をクリアします"""
    if os.path.exists('config.json'):
        os.remove('config.json')
    next_run_time_var.set('')  # 次回実行時間表示をクリア
    time_entry.delete(0, tk.END)  # エントリーをクリア
    messagebox.showinfo('スケジュール取消', 'スケジュールが正常に取り消されました。')

def create_gui():
    global time_entry
    global next_run_time_var

    def run_function1():
        headless = False
        save_path, max_items, song_urls = read_initial_settings()
        if save_path and song_urls:
            threading.Thread(target=thread_function1, args=(save_path, max_items, song_urls, headless)).start()

    def run_function2():
        headless = False
        save_path, _, song_urls = read_initial_settings()
        if save_path and song_urls:
            threading.Thread(target=thread_function2, args=(save_path, song_urls, headless)).start()

    def run_both_functions():
        headless = False
        save_path, max_items, song_urls = read_initial_settings()
        if save_path and song_urls:
            threading.Thread(target=thread_both_functions, args=(save_path, max_items, song_urls, headless)).start()

    def thread_function1(save_path, max_items, song_urls, headless):
        function1(save_path, max_items, song_urls, headless=headless)
        messagebox.showinfo('完了', '機能1が終了しました。')

    def thread_function2(save_path, song_urls, headless):
        function2(save_path, song_urls, headless=headless)
        messagebox.showinfo('完了', '機能2が終了しました。')

    def thread_both_functions(save_path, max_items, song_urls, headless):
        function1(save_path, max_items, song_urls, headless=headless)
        function2(save_path, song_urls, headless=headless)
        messagebox.showinfo('完了', '機能1と機能2が終了しました。')

    def start_login_authentication():
        threading.Thread(target=login_authentication).start()

    def schedule_run():
        target_time_str = time_entry.get()
        try:
            target_time = datetime.strptime(target_time_str, '%H:%M').time()
            next_run_time = calculate_next_run_time(target_time)
            update_next_run_time_label(next_run_time_var, next_run_time)
            save_schedule_time(target_time_str)  # 保存
            threading.Thread(target=schedule_task, args=(time_entry, next_run_time_var)).start()
        except ValueError:
            messagebox.showerror('エラー', '時刻の形式が不正です。HH:MM 形式で入力してください。')

    def cancel_schedule():
        clear_schedule()

    root = tk.Tk()
    root.title('TikTokデータ取得ツール')
    root.geometry('800x600')

    main_frame = tk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    button_frame = tk.Frame(main_frame)
    button_frame.pack(fill=tk.X)

    button1 = tk.Button(button_frame, text='機能1: 楽曲一覧URL取得 実行', command=run_function1)
    button1.grid(row=0, column=0, padx=5, pady=5)

    button2 = tk.Button(button_frame, text='機能2: データ抽出機能 実行', command=run_function2)
    button2.grid(row=0, column=1, padx=5, pady=5)

    button3 = tk.Button(button_frame, text='機能1 + 機能2 実行', command=run_both_functions)
    button3.grid(row=0, column=2, padx=5, pady=5)

    login_button = tk.Button(button_frame, text='ログイン認証', command=start_login_authentication)
    login_button.grid(row=0, column=3, padx=5, pady=5)

    stop_button = tk.Button(button_frame, text='停止', command=stop_processing)
    stop_button.grid(row=0, column=4, padx=5, pady=5)

    checkbox_frame = tk.Frame(main_frame)
    checkbox_frame.pack(fill=tk.X)

    log_display_var = tk.BooleanVar(value=True)
    log_display_checkbox = tk.Checkbutton(checkbox_frame, text='ログ表示ON/OFF', variable=log_display_var)
    log_display_checkbox.grid(row=0, column=0, padx=5, pady=5)

    log_frame = tk.Frame(main_frame)
    log_frame.pack(fill=tk.BOTH, expand=True)

    log_text = scrolledtext.ScrolledText(log_frame, state='disabled')
    log_text.pack(fill=tk.BOTH, expand=True)

    time_entry_label = tk.Label(button_frame, text='毎日実行する時刻 (HH:MM):')
    time_entry_label.grid(row=1, column=0, padx=5, pady=5)

    schedule_time = load_schedule_time()
    time_entry = tk.Entry(button_frame, width=10)
    time_entry.insert(0, schedule_time)
    time_entry.grid(row=1, column=1, padx=5, pady=5)

    schedule_button = tk.Button(button_frame, text='時指定刻に実行', command=schedule_run)
    schedule_button.grid(row=1, column=2, padx=5, pady=5)

    cancel_button = tk.Button(button_frame, text='スケジュール取消', command=cancel_schedule)
    cancel_button.grid(row=1, column=3, padx=5, pady=5)

    next_run_time_var = tk.StringVar()
    next_run_time_label = tk.Label(button_frame, textvariable=next_run_time_var)
    next_run_time_label.grid(row=1, column=4, padx=5, pady=5)

    text_handler = TextHandler(log_text, log_display_var)
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    text_handler.setFormatter(formatter)
    logging.getLogger().addHandler(text_handler)

    root.mainloop()

def run_command_line_mode():
    # タスクスケジューラから実行するためのコマンドラインエントリポイント
    save_path, max_items, song_urls = read_initial_settings()
    if save_path and song_urls:
        headless = False  # タスクスケジューラの場合、ヘッドレスモードが適切
        function1(save_path, max_items, song_urls, headless=headless)
        function2(save_path, song_urls, headless=headless)
        logging.info("自動実行が完了しました。")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == "run":
        logging.info("スクリプトとして実行されています。")
        logging.info("コマンドライン引数 'run' が検出されました。コマンドラインモードを開始します。")
        run_command_line_mode()
    else:
        logging.info("GUIモードを開始します。")
        create_gui()