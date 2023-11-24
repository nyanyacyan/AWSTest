# scraper.py
from selenium import webdriver  # seleniumのバージョンを4.1にする
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager  # Chromeのバージョンをオートで確認してくれてインストールしてくれる
import csv

url = "https://www.petpochitto.com/"

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)


def lambda_handler():
    # 空の辞書を設置
    jan_details = {}
    # URLを開く
    driver.get(url)

    # cdvを読み込む
    with open('aws_test.csv') as f:
        jans = csv.reader(f)
        for jan in jans:

            # 検索欄のidを取得
            element = driver.find_element(By.ID, "keyword")
            print(element)

            # テキストボックスに検索ワードを入力
            element.send_keys(jan)

            # 検索ボタンを探す
            search_buttan = driver.find_element(By.CSS_SELECTOR,".__button.c-button")

            # 検索ボタンをクリック
            search_buttan.click()

            # 現在のページにある価格を全てリスト化する。
            all_ddtag_list = [dd_tag.text for dd_tag in driver.find_elements(By.TAG_NAME, 'dd')]
            first_ddtag = all_ddtag_list[0]

            # 商品カタログ名
            all_title_list = [title.text for title in driver.find_elements(By.TAG_NAME, 'h2')]
            first_title = all_title_list[0]

            # 辞書にまとめる
            jan_details[jan[0]] = (first_title, first_ddtag)
            print(jan_details)

    # output.csvに出力
    with open('output.csv', 'w',newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for index, (key,(title, price)) in enumerate(jan_details.items(), start=1):
            writer.writerow([index, key, title, price])
    
    
    # WebDriverを閉じる
    driver.quit()

lambda_handler()