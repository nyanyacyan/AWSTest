import csv
import json
import requests
import logging
import time

# 最大待機時間と待機間隔（秒）
MAX_WAIT_TIME = 180
POLL_INTERVAL = 10

logging.basicConfig(level=logging.INFO)

goods_status_details = {}


# Lambda状態取得APIの処理を実施
with open('aws_test.csv') as f:
    jans = csv.reader(f)

    for jan in jans:
        json_code = json.dumps({"local_jan_code": jan[0].strip()})  # jsonファイルに置き換え
        print(json_code)

        #  lambda発火APIのURL
        first_api_url = "https://1433bwhqog.execute-api.ap-northeast-1.amazonaws.com/prod/status"
        
        try:
            first_response = requests.post(first_api_url, data=json_code)
            # レスポンス情報をログに記録
            logging.info(f"Lambda発火APIからのレスOK")
        except requests.RequestException as e:
            # エラー情報をログに記録
            logging.error(f"レスエラー: {e}")
            continue



        # Lambda発火APIからのレスポンス処理→レスポンスから実行ARNを抽出
        if first_response.status_code == 200:
            first_response_data = first_response.json()  # 実行Arn取得
            # print("Lambda発火APIからのレスOK")

            execution_arn = first_response_data["executionArn"]

            # Lambda状態取得APIのURL
            second_api_url = "https://202g7nx6k4.execute-api.ap-northeast-1.amazonaws.com/prod/status-check"

            second_request_data = {
                "executionArn": execution_arn
            }


            # 開始時間の記録
            start_time = time.time()

            print("lambda関数からのレスポンス待ち", end="")

            # 特定の処理があるまではずっとループ処理する→statusがRUNNINGからSUCCEEDEDになるまで
            while True:
                # Lambda状態取得APIにリクエスト
                second_response = requests.post(second_api_url, json=second_request_data)

                # Lambda状態取得APIからのレスポンス処理
                # 商品名と価格
                if second_response.status_code == 200:
                    second_response_data = second_response.json() # jsonファイルを解析してリストに変換
                    # print(second_response_data)  # レスポンスの詳細

                    # ステータスがSUCCEEDEDになってからの処理　　各値を抽出
                    if second_response_data.get('status') == 'SUCCEEDED':
                        output_dict = second_response_data.get('output')
                        output_data = json.loads(output_dict)
                        body_dict = output_data.get('body')

                        # 各値
                        lambda_product_name = body_dict.get('lambda_product_name')
                        lambda_price = body_dict.get('lambda_price')

                        # 辞書に追加
                        goods_status_details[jan[0]] = (lambda_product_name, lambda_price)

                        print(f"スクレイピング成功:{lambda_product_name},{lambda_price}")
                        break

                    # RUNNINGの際に進捗がわかるように処理
                    elif second_response_data.get('status') == 'RUNNING':
                        current_time = time.time()
                        if current_time - start_time >= 10:  # 10秒ごとにチェック
                            print(".", end="", flush=True)  # flush=Trueは現在の行に '.' を追加
                            start_time = current_time  # 次の10秒間のカウントを開始
                        

                else:
                    # Lambda状態取得APIエラー時の処理
                    print("Lambda状態取得APIエラー:", second_response.text)
                    continue  # 次の反復へ

                if time.time() - start_time > MAX_WAIT_TIME:
                    print("タイムアウト：処理が完了しませんでした。")
                    break

                time.sleep(POLL_INTERVAL)
        else:
            # Lambda発火APIエラー時の処理
            print("Lambda発火APIエラー:", first_response.text)
            continue


# csv出力
with open('output.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['JANコード', '商品名', '価格'])
    for jan, (name, price) in goods_status_details.items():
        writer.writerow([jan, name, price])