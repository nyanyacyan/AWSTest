# scraper.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import json

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


    # URLを開く
    browser.get(url)

    # URLのロード状況をログに記録
    logger.info("Opened URL: " + url)

    # リクエストのBODYを取得
    request_body = event.get('body')

    if request_body:
        request_data = json.loads(event["body"])  # jsonを解析

        jan = request_data["local_jan_code"]

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
        lambda_price = all_ddtag_list[0]
        print(lambda_price)

        # h2タグを見つける
        # 見つけるまで最大6秒、動的待機
        all_titles = WebDriverWait(browser, 6).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, 'h2'))
        )

        # 商品カタログ名
        all_title_list = [title.text for title in all_titles]
        lambda_product_name = all_title_list[0]
        print(lambda_product_name)

        # jsonオブジェクトの作成
        response_data = {
            "lambda_product_name": lambda_product_name,
            "lambda_price": lambda_price
        }



        # jsonへと変換
        json_response = json.dumps(response_data)

    
    # WebDriverを閉じる
    browser.quit()

    # CSVデータをレスポンスとして返す
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
        },
        'body': json_response
    }