# scraper.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import logging
import json

# ローカルデバック時に使用
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager


def lambda_handler(event, context):
        # エンドポイントのパスを取得
    path = event['path']

    # 発火エンドポイントの処理
    if path == '/start':
        return handle_start_execution(event)

    # 状態維持エンドポイントの処理
    elif path == '/status':
        return handle_check_status(event)

    # 未知のエンドポイントの場合
    else:
        return {'statusCode': 404, 'body': 'Not Found'}


# 発火エンドポイントの処理関数
def handle_start_execution(event):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    logger.info(f"処理スタート")

    url = "https://www.petpochitto.com/"

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--hide-scrollbars")
    options.add_argument("--single-process")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--window-size=1200x1000")  # サイズを大きくすることでsend_keysでの
    options.add_argument("--no-sandbox")
    options.add_argument("--homedir=/tmp")
    options.binary_location = "/opt/headless/headless-chromium"

    logger.info(f"ブラウザのパスを指定")

    browser = webdriver.Chrome(
        # chromedriverのパスを指定
        executable_path="/opt/headless/chromedriver",
        options=options
    )

    logger.info(f"ブラウザを開く")

    try:
        browser.get(url)
        start_response = browser.title
    except Exception as e:
        logger.error(f"エラー発生: {e}")
        return{
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({"error": str(e)})
        }
    finally:
        browser.quit()
        logger.info(f"処理完了")

    return{
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({"title": start_response})
    }

# 〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜

# 状態維持エンドポイントの処理関数
def handle_check_status(event):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    logger.info(f"処理スタート")

    url = "https://www.petpochitto.com/"

    json_response = ""  # 変数の初期化

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--hide-scrollbars")
    options.add_argument("--single-process")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--window-size=1200x1000")  # サイズを大きくすることでsend_keysでの
    options.add_argument("--no-sandbox")
    options.add_argument("--homedir=/tmp")
    options.binary_location = "/opt/headless/headless-chromium"

    logger.info(f"ブラウザのパスを指定")

    browser = webdriver.Chrome(
        # chromedriverのパスを指定
        executable_path="/opt/headless/chromedriver",
        options=options
    )

    logger.info(f"ブラウザを開く")

    # URLを開く
    browser.get(url)


    # リクエストのBODYを取得
    # テスト用
    # Lambdaのテストイベントでは、テストイベントのJSONオブジェクト自体が event オブジェクトとして渡されます。そのため、event.get('body') は None を返す
    
    request_body = event.get('local_jan_code')

    # デプロイ用
    # request_body = event.get('body')

    logger.info("リクエストボディが存在します: %s", request_body)

    logger.info("ページロードを待機しています...")

    # ページが完全にロードされるのを待つ
    WebDriverWait(browser, 3).until(
        lambda browser: browser.execute_script('return document.readyState') == 'complete'
    )

    logger.info("ページが完全にロードされました。")

    if request_body:
        try:
            request_data = json.loads(request_body)  # jsonを解析
            # jan = request_data["local_jan_code"]  辞書からjanだけを抽出する
            request_data_str = str(request_data)
            logger.info(f"解析完了: {request_data_str}")
            logger.info("Opened URL: " + url)

        except json.JSONDecodeError as e:
            logger.error(f"解析エラー:{e}")

        try:
            elements = browser.find_elements_by_id("keyword")
            if elements:
                element = elements[0] 
                name_attribute = element.get_attribute('name')
                logger.info(f"ID:keywordをサーチ済み")
                logger.info(f"Element tag name: {element.tag_name}")
                logger.info(f"Element name attribute: {name_attribute}")
                logger.info(f"{request_data_str}")
                # logger.info(f"request_dataのデータ型: {type(request_data_str)}")

            else:
                logger.info(f"ID:keywordが見つからない")

        except TimeoutException:
            logger.error(f"設定した時間で見つけられない。")

        # テキストボックスに検索ワードを入力
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

        # jsonへと変換
        json_response = json.dumps(response_data)

    else:
        logger.error("リクエストボディがありません。")
        json_response = json.dumps({"error": "リクエストボディがありません。"})

    # WebDriverを閉じる
    browser.quit()

    # jsonデータをレスポンスとして返す
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
        },
        'body': json_response
    }