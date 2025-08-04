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
                try:
                    os.remove(filepath)
                except PermissionError:
                    print(f"Cannot delete {filepath}: File is in use.")
                    
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
    # extension_path = os.path.abspath('vidIQ.crx')
    # chrome_options.add_extension(extension_path)
    
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
            EC.presence_of_element_located((By.XPATH, '//*[@data-e2e="music-video-count"]'))
        )
        # 「本の動画」を削除して数値に変換
        total_ugc = parse_number(total_ugc_element.text.replace('動画', '').replace(',', '').strip())
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
    video_urls = []         # 順序を保持するためのリスト
    seen_urls = set()       # 重複を検出するためのセット
    wait = WebDriverWait(driver, timeout)
    
    driver.set_script_timeout(300)

    scroll_attempts = 0       # 新しい動画が読み込まれなかった試行回数
    max_scroll_attempts = 5  # 最大の試行回数

    while True:
        if stop_flag.is_set():
            logging.info('動画URLの取得が停止されました')
            break
        
        prev_height = driver.execute_script("return document.body.scrollHeight")
        # 5回連続でスクロール
        for _ in range(10):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(1.0, 2.0))
        
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == prev_height:
            scroll_attempts += 1
            logging.info(f'新しい投稿が見つからない試行回数: {scroll_attempts}/{max_scroll_attempts}')
            if scroll_attempts >= max_scroll_attempts:
                logging.info('これ以上新規投稿が読み込まれないため、スクロール終了')
                break
        else:
            scroll_attempts = 0  # 新規投稿が検出されたので失敗回数をリセット

        try:
            # JavaScriptでhref属性を一括取得（Setで重複除外）
            all_urls = driver.execute_script("""
                const urls = Array.from(document.querySelectorAll(
                    '[data-e2e="music-item-list"] a[href*="/video/"], [data-e2e="music-item-list"] a[href*="/photo/"]'
                )).map(a => a.href);
                return Array.from(new Set(urls));
            """)
        except (TimeoutException, Exception) as e:
            logging.warning(f'JavaScript実行時にエラーが発生しました: {e}')
            continue

        new_urls = [url for url in all_urls if url and url not in seen_urls]
        video_urls.extend(new_urls)
        seen_urls.update(new_urls)
        
        # 現在の取得件数をログに出力
        logging.info(f'現在の取得件数: {len(video_urls)}')
            
        if max_items and len(video_urls) >= max_items:
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

prefer_account_name_alt = True

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
            driver.execute_script("document.body.style.zoom='90%'")
            time.sleep(random.uniform(1, 2))

            try:
                # エラーメッセージの要素が存在するかチェック（待機時間を0.5秒に設定）
                error_element = WebDriverWait(driver, 0.5).until(
                    EC.presence_of_element_located(
                        (By.XPATH, '//p[contains(text(), "ページを表示できません")]')

                    )
                )
                if error_element:

                    logging.info(f'エラーページが表示されました。ページを再読み込みします。')
                    driver.refresh()
                    time.sleep(random.uniform(1, 2))
                else:
                    # エラーメッセージが見つからない場合は正常にページが表示されている
                    pass
            except TimeoutException:
                # エラーメッセージが見つからない場合は正常にページが表示されている
                pass

            try:
                # エラーメッセージの要素が存在するかチェック（待機時間を0.5秒に設定）
                error_element = WebDriverWait(driver, 0.5).until(
                    EC.presence_of_element_located(
                        (By.XPATH, '//p[contains(text(), "動画は現在ご利用できません")]')
                    )
                )
                if error_element:
                    logging.info('動画が利用できないため、次の動画に進みます。')
                    continue
            except TimeoutException:
                # エラーメッセージが見つからない場合は正常にページが表示されている
                pass

            try:
                # エラーメッセージの要素が存在するかチェック（待機時間を0.5秒に設定）
                error_element = WebDriverWait(driver, 0.5).until(
                    EC.presence_of_element_located(
                        (By.XPATH, '//p[contains(text(), "このアカウントは非公開です")]')
                    )
                )
                if error_element:
                    logging.info('動画が利用できないため、次の動画に進みます。')
                    continue
            except TimeoutException:
                # エラーメッセージが見つからない場合は正常にページが表示されている
                pass
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

def extract_video_stats_from_json(driver):
    try:
        # 特定のスクリプト要素からJSONデータを取得
        script_content = driver.execute_script(
            "return document.getElementById('__UNIVERSAL_DATA_FOR_REHYDRATION__').innerText;")
        
        # JSONデータをパース
        data = json.loads(script_content)
        
        # 統計情報を取得
        stats = data["__DEFAULT_SCOPE__"]["webapp.video-detail"]["itemInfo"]["itemStruct"]["stats"]
        digg_count = stats["diggCount"]
        comment_count = stats["commentCount"]
        share_count = stats["shareCount"]
        play_count = stats["playCount"]
        collect_count = int(stats["collectCount"])

        # フォロワー数とアカウント名を取得
        author_stats = data["__DEFAULT_SCOPE__"]["webapp.video-detail"]["itemInfo"]["itemStruct"]["authorStats"]
        follower_count = author_stats["followerCount"]

        author_info = data["__DEFAULT_SCOPE__"]["webapp.video-detail"]["itemInfo"]["itemStruct"]["author"]
        account_name = author_info["uniqueId"]
        nickname = author_info["nickname"]

        # ログに取得した値を記録
        logging.info(f'いいね数: {digg_count}, コメント数: {comment_count}, '
                     f'シェア数: {share_count}, 再生回数: {play_count}, 保存数: {collect_count}, '
                     f'フォロワー数: {follower_count}, アカウント名: {account_name}, ニックネーム: {nickname}')

        return {
            'いいね数': digg_count,
            'コメント数': comment_count,
            'シェア数': share_count,
            '再生回数': play_count,
            '保存数': collect_count,
            'フォロワー数': follower_count,
            'アカウント名': account_name,
            'ニックネーム': nickname
        }
    except Exception as e:
        logging.error(f'動画統計情報の取得中にエラーが発生しました: {e}')
        return {
            'いいね数': '',
            'コメント数':'',
            'シェア数':'',
            '再生回数':'',
            '保存数':'',
            'フォロワー数':'',
            'アカウント名': '',
            'ニックネーム': ''
        }
    
# 動画のデータを抽出
def extract_video_data(driver, original_window, follower_window_handle):
    data = {}
    try:
        current_url = driver.current_url
        try:
            post_id = current_url.rstrip('/').split('/')[-1].split('?')[0]
            data['投稿ID'] = post_id
        except Exception as e:
            logging.error(f'投稿IDの取得中にエラーが発生しました: {e}')
            data['投稿ID'] = ''

        # URLからアカウント名を取得
        try:
            url = current_url
            start_index = url.find('/@') + 2  # '/@' の直後から
            end_index = url.find('/', start_index)
            account_name = url[start_index:end_index]
        except Exception as e:
            logging.error(f'URLからアカウント名の取得中にエラーが発生しました: {e}')
            account_name = ''

        # 投稿日
        date_posted = extract_date(driver)
        # '更新日' を取得
        update_datetime = datetime.now()
        # 'date_posted' をパースして指定の形式に変換
        date_posted = parse_date_posted(date_posted, update_datetime)
        
        data['投稿日'] = date_posted

        # '更新日' を取得
        data['更新日'] = datetime.today().strftime('%Y/%m/%d %H:%M')

        if '/video/' in current_url:
            # JSONから統計情報を取得してデータに追加
            video_stats = extract_video_stats_from_json(driver)
            data.update(video_stats)
        else:
            # 各データ項目を個別に取得
            data['アカウント名'] = account_name
            data['いいね数'] = extract_and_parse_number(driver, '//strong[@data-e2e="like-count"]', 'いいね数')
            data['コメント数'] = extract_and_parse_number(driver, '//strong[@data-e2e="comment-count"]', 'コメント数')
            data['保存数'] = extract_and_parse_number(driver, '//strong[@data-e2e="undefined-count"]', '保存数')
            data['シェア数'] = extract_and_parse_number(driver, '//strong[@data-e2e="share-count"]', 'シェア数')
            if data['シェア数'] is None:
                data['シェア数'] = 0
            data['再生回数'] = ''

            # フォロワー数とニックネームを取得
            try:
                with ThreadPoolExecutor() as executor:
                    future = executor.submit(get_follower_count, driver, account_name, original_window, follower_window_handle)
                    follower_count, nickname = future.result()
                    data['フォロワー数'] = follower_count
                    data['ニックネーム'] = nickname
            except Exception as e:
                logging.error(f'フォロワー数の取得中にエラーが発生しました: {e}')
                data['フォロワー数'] = ''
                data['ニックネーム'] = ''

        data['動画リンク(URL)'] = current_url

        # アバターURLの取得
        data['アバターURL'] = extract_avatar_url(driver, account_name)

    except Exception as e:
        logging.error(f'動画データの抽出中にエラーが発生しました: {e}', exc_info=True)
        # 全体でエラーが発生した場合でも、これまで取得したデータを返す
        pass

    # データが取得できなかった項目を空欄に設定
    keys = ['投稿ID', '投稿日', 'アカウント名', 'ニックネーム',
            'いいね数', 'コメント数', '保存数', 'シェア数',
            '再生回数', 'フォロワー数', '動画リンク(URL)', '更新日', 'アバターURL']
    for key in keys:
        if key not in data:
            data[key] = ''

    return data

def extract_date_from_span_pattern1(driver):
    """基本的なspan要素からの日付抽出"""
    try:
        span_element = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.XPATH, '//span[@data-e2e="browser-nickname"]'))
        )
        # 既存の処理: <span> からアカウント名と投稿日を取得
        span_elements = span_element.find_elements(By.XPATH, './span')
        span_elements = span_element.find_elements(By.XPATH, './span')
        if len(span_elements) >= 3:
            date_text = span_elements[2].text
            logging.info(f'span_pattern1で日付取得成功: {date_text}')
            return date_text
        else:
            logging.warning('span_pattern1: 十分なspan要素が見つかりませんでした')
            return None
    except Exception as e:
        logging.warning(f'span_pattern1で日付取得失敗: {e}')
        return None

def extract_date_from_span_pattern2(driver):
    """SpanOtherInfosクラスからの日付抽出"""
    try:
        # css-1kcycbd-SpanOtherInfosクラスを含む要素を検索
        other_info_elements = WebDriverWait(driver, 3).until(
            EC.presence_of_all_elements_located((By.XPATH, '//span[contains(@class, "SpanOtherInfos")]'))
        )
        
        for element in other_info_elements:
            text_content = element.text  # 例: "박보성 · 7-8"
            if "·" in text_content:
                parts = text_content.split("·")
                if len(parts) >= 2:
                    date_text = parts[1].strip()
                    logging.info(f'span_pattern2で日付取得成功: {date_text}')
                    return date_text
        
        logging.warning('span_pattern2: 適切なテキスト形式が見つかりませんでした')
        return None
    except Exception as e:
        logging.warning(f'span_pattern2で日付取得失敗: {e}')
        return None

def extract_date_from_json_data(driver):
    """JSONデータからの投稿日抽出"""
    try:
        # 特定のスクリプト要素からJSONデータを取得
        script_content = driver.execute_script(
            "return document.getElementById('__UNIVERSAL_DATA_FOR_REHYDRATION__').innerText;")
        
        # JSONデータをパース
        data = json.loads(script_content)
        
        # createTimeタイムスタンプを取得
        create_time = data.get("__DEFAULT_SCOPE__", {}).get("webapp.video-detail", {}).get("itemInfo", {}).get("itemStruct", {}).get("createTime")
        
        # Unixタイムスタンプから日付に変換
        if create_time:
            # JST timezone設定
            jst = pytz.timezone('Asia/Tokyo')
            
            # Unixタイムスタンプから日付に変換（JSTで）
            post_date = datetime.fromtimestamp(create_time, tz=jst)
            date_text = f"{post_date.month:02d}/{post_date.day:02d}"
            
            logging.info(f'json_dataで日付取得成功: {date_text}')
            return date_text
        
        logging.warning('json_data: createTimeが見つかりませんでした')
        return None
    except Exception as e:
        logging.warning(f'json_dataで日付取得失敗: {e}')
        return None

def extract_date(driver):
    """マルチパターン抽出アプローチで投稿日を取得"""
    logging.info('投稿日の抽出を開始します')
    
    # 3つのパターンを順次試行
    extraction_patterns = [
        extract_date_from_span_pattern1,  # 基本的なspan検索
        extract_date_from_span_pattern2,  # SpanOtherInfos直接検索
        extract_date_from_json_data,      # JSONデータからの抽出
    ]
    
    for i, pattern_func in enumerate(extraction_patterns, 1):
        try:
            result = pattern_func(driver)
            if result:
                logging.info(f'パターン{i}で投稿日取得成功: {result}')
                return result
        except Exception as e:
            logging.warning(f'パターン{i}でエラー: {e}')
            continue
    
    logging.error('全ての抽出パターンで投稿日取得に失敗しました')
    return ''

def extract_avatar_url(driver, account_name):
    global prefer_account_name_alt
    try:
        if prefer_account_name_alt:
            # アカウント名がaltにあるimg要素を優先して使用
            img_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, f'//img[@alt="{account_name}"]'))
            )
        else:
            # altが空のimg要素を優先して使用
            img_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//a[@data-e2e="browse-user-avatar"]//img[@alt=""]'))
            )

        avatar_url = img_element.get_attribute('src')
        return avatar_url
    
    except TimeoutException:
        logging.warning(f'フラグ {prefer_account_name_alt} に基づいた要素が見つかりませんでした。')
        # フラグがTrueなら反転して再試行、すでにFalseなら空文字を返す
        if prefer_account_name_alt:
            prefer_account_name_alt = False
            return extract_avatar_url(driver, account_name)
        else:
            logging.info("両方の方法で要素が見つからなかったため、空文字を返します。")
            return ''
    except Exception as e:
        logging.error(f'アバターURLの取得中にエラーが発生しました: {e}')
        return ''
      
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

def get_follower_count(driver, account_name, original_window, follower_window_handle):
    follower_count = ''
    nickname = ''
    try:
        # アカウントページに移動
        account_url = f'https://www.tiktok.com/@{account_name}'
        driver.switch_to.window(follower_window_handle)
        driver.get(account_url)
        time.sleep(random.uniform(1, 2))
        
        # アカウント名を取得
        nickname = extract_text_with_retry(driver, By.XPATH, '//h2[@data-e2e="user-subtitle"]', 'ニックネーム')

        # フォロワー数を取得
        followers_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//strong[@data-e2e="followers-count"]'))
        )
        follower_count = parse_number(followers_element.text)

        # 元のウィンドウに戻る
        driver.switch_to.window(original_window)
    except Exception as e:
        logging.error(f'フォロワー数またはアカウント名の取得中にエラーが発生しました: {e}')

    return follower_count, nickname

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
