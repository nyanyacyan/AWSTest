# scraper.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import logging
import json


def lambda_handler(event, context):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    logger.info(f"処理スタート")

    url = "https://www.petpochitto.com/"

    # webdriver（Chrome）のオプションを使うことを宣言
    options = webdriver.ChromeOptions()

    # webdriverのどんなオプション使うのかを選定
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--hide-scrollbars")
    options.add_argument("--single-process")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--window-size=1200x1000")  # サイズを大きくすることでsend_keysでの
    options.add_argument("--no-sandbox")
    options.add_argument("--homedir=/tmp")

    # headlessのChromeバージョンを選定
    options.binary_location = "/opt/headless/headless-chromium"

    logger.info(f"ブラウザのパスを指定")

    browser = webdriver.Chrome(
        # Chromeを操作できるようにするためのdriverをAWSにあるパスを選定
        executable_path="/opt/headless/chromedriver",
        options=options
    )

    logger.info(f"ブラウザを開く")

    # URLを開く
    browser.get(url)


    # リクエストのBODYを取得
    request_body = event.get('local_jan_code')

    logger.info("リクエストボディが存在します: %s", request_body)
    logger.info("ページロードを待機しています...")

    # ページが完全にロードされるのを待つ
    WebDriverWait(browser, 3).until(
        lambda browser: browser.execute_script('return document.readyState') == 'complete'
    )

    logger.info("ページが完全にロードされました。")

    if request_body:
        # jsonファイルの読み込みを実施
        # 読み込みができなかったらログを残す。
        try:
            request_data = json.loads(request_body)  # jsonを解析
            request_data_str = str(request_data)
            logger.info(f"解析完了: {request_data_str}")
            logger.info("Opened URL: " + url)

        except json.JSONDecodeError as e:
            logger.error(f"解析エラー:{e}")

        # "keyword"→最初の要素→name属性の値
        # 検索バー（IDがkeyword）が見つからなかったらログを残す
        try:
            elements = browser.find_elements_by_id("keyword")
            if elements:
                element = elements[0] 
                name_attribute = element.get_attribute('name')
                logger.info(f"ID:keywordをサーチ済み")
                logger.info(f"Element tag name: {element.tag_name}")
                logger.info(f"Element name attribute: {name_attribute}")
                logger.info(f"{request_data_str}")

            else:
                logger.info(f"ID:keywordが見つからない")

        except TimeoutException:
            logger.error(f"設定した時間で見つけられない。")

        # テキストボックスに検索ワードを入力
        # キーワードが入力できなかったらログを残す。
        try:
            if element.is_displayed():
                element.send_keys(request_data_str)
                logger.info("キーワード入力に成功")
            else:
                logger.info("要素が表示されていません")

        except Exception as e:
            logger.error(f"キーワード入力失敗: {e}")

        # 検索ボタンを探す
        # クリックができるようになるまで最大6秒、動的待機
        search_buttan = browser.find_element_by_css_selector(".__button.c-button")

        logger.info("検索ボタンを探すことを開始")

        # 検索ボタンをクリック
        search_buttan.click()

        logger.info("検索ボタンをクリック")

        # ddタグを見つける
        # 見つけるまで最大6秒、動的待機
        all_ddtags = WebDriverWait(browser, 3).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, 'dd'))
        )
        logger.info("ddタグリスト作成")

        # 現在のページにある価格を全てリスト化する。
        all_ddtag_list = [dd_tag.text for dd_tag in all_ddtags]
        lambda_price = all_ddtag_list[0]
        logger.info(f"{lambda_price}")

        # h2タグを見つける
        # 見つけるまで最大6秒、動的待機
        all_titles = WebDriverWait(browser, 6).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, 'h2'))
        )
        logger.info("h2タグリスト作成")
        

        # 商品カタログ名
        all_title_list = [title.text for title in all_titles]
        lambda_product_name = all_title_list[0]
        logger.info(f"{lambda_product_name}")

        # jsonオブジェクトの作成
        response_data = {
            "lambda_product_name": lambda_product_name,
            "lambda_price": lambda_price
        }


    else:
        logger.error("リクエストボディがありません。")

    # WebDriverを閉じる
    browser.quit()

    # jsonデータをレスポンスとして返す
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
        },
        'body': response_data
    }