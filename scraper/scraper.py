# scraper.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv


def lambda_handler():
    url = "https://www.petpochitto.com/"


    options = webdriver.ChromeOptions()

    # headless-chromiumのパスを指定
    options.binary_location = "/opt/headless/headless-chromium"
    options.add_argument("--headless")
    options.add_argument('--single-process')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(
        # chromedriverのパスを指定
        executable_path="/opt/headless/chromedriver",
        options=options
    )

    # 空の辞書を設置
    jan_details = {}

    # URLを開く
    driver.get(url)

    # cdvを読み込む
    with open('aws_test.csv') as f:
        jans = csv.reader(f)
        for jan in jans:

            # 検索欄のidを取得
            element = WebDriverWait(driver, 6).until(
                EC.presence_of_element_located((By.ID, "keyword"))
            )

            # テキストボックスに検索ワードを入力
            element.send_keys(jan)

            # 検索ボタンを探す
            # 見つけるまで最大6秒、動的待機
            search_buttan = WebDriverWait(driver, 6).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".__button.c-button"))
            )


            # 検索ボタンをクリック
            search_buttan.click()

            # ddタグを見つける
            # 見つけるまで最大6秒、動的待機
            all_ddtags = WebDriverWait(driver, 6).until(
                EC.presence_of_all_elements_located((By.TAG_NAME, 'dd'))
            )

            # 現在のページにある価格を全てリスト化する。
            all_ddtag_list = [dd_tag.text for dd_tag in all_ddtags]
            first_ddtag = all_ddtag_list[0]

            # h2タグを見つける
            # 見つけるまで最大6秒、動的待機
            all_titles = WebDriverWait(driver, 6).until(
                EC.presence_of_all_elements_located((By.TAG_NAME, 'h2'))
            )

            # 商品カタログ名
            all_title_list = [title.text for title in all_titles]
            first_title = all_title_list[0]

            # 辞書にまとめる
            jan_details[jan[0]] = (first_title, first_ddtag)

    # output.csvに出力
    with open('output.csv', 'w',newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for index, (key,(title, price)) in enumerate(jan_details.items(), start=1):
            writer.writerow([index, key, title, price])
    
    
    # WebDriverを閉じる
    driver.quit()

lambda_handler()