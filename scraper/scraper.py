# scraper.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import logging
import io

# ローカルデバック時に使用
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager


def lambda_handler(event, context):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    url = "https://www.petpochitto.com/"

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--hide-scrollbars")
    options.add_argument("--single-process")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--window-size=880x996")
    options.add_argument("--no-sandbox")
    options.add_argument("--homedir=/tmp")
    options.binary_location = "/opt/headless/headless-chromium"

    # ローカルデバック時に使用
    # service = Service(ChromeDriverManager().install())
    # browser = webdriver.Chrome(service=service)


    browser = webdriver.Chrome(
        # chromedriverのパスを指定
        executable_path="/opt/headless/chromedriver",
        options=options
    )

    # 空の辞書を設置
    jan_details = {}

    # URLを開く
    browser.get(url)

    # URLのロード状況をログに記録
    logger.info("Opened URL: " + url)

    # cdvを読み込む
    with open('aws_test.csv') as f:
        jans = csv.reader(f)
        rows = list(jans)
        print(rows)

        for jan in jans:
            # 検索欄のidを取得
            element = WebDriverWait(browser, 60).until(
                EC.element_to_be_clickable((By.ID, "keyword"))
            )

            # テキストボックスに検索ワードを入力
            element.send_keys(jan)

            # 検索ボタンを探す
            # クリックができるようになるまで最大6秒、動的待機
            search_buttan = WebDriverWait(browser, 6).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".__button.c-button"))
            )


            # 検索ボタンをクリック
            search_buttan.click()

            # ddタグを見つける
            # 見つけるまで最大6秒、動的待機
            all_ddtags = WebDriverWait(browser, 6).until(
                EC.presence_of_all_elements_located((By.TAG_NAME, 'dd'))
            )

            # 現在のページにある価格を全てリスト化する。
            all_ddtag_list = [dd_tag.text for dd_tag in all_ddtags]
            first_ddtag = all_ddtag_list[0]
            print(first_ddtag)

            # h2タグを見つける
            # 見つけるまで最大6秒、動的待機
            all_titles = WebDriverWait(browser, 6).until(
                EC.presence_of_all_elements_located((By.TAG_NAME, 'h2'))
            )

            # 商品カタログ名
            all_title_list = [title.text for title in all_titles]
            first_title = all_title_list[0]
            print(first_title)

            # 辞書にまとめる
            jan_details[jan[0]] = (first_title, first_ddtag)

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Index', 'JANコード', '商品名', '価格'])
        for index, (jan, (first_title, first_ddtag)) in enumerate(jan_details.items(), start=1):
            writer.writerow([index, jan, first_title, first_ddtag])


        # CSVデータを取得
        csv_data = output.getvalue()
    
    # WebDriverを閉じる
    browser.quit()

    # CSVデータをレスポンスとして返す
    return {
        'statusCode': 200,
        'body': csv_data,
        'headers': {
            'Content-Type': 'text/csv',
            'Content-Disposition': 'attachment; filename="output.csv"'
        }
    }