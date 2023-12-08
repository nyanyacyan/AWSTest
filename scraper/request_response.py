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
        print(jans)
        json_code = json.dumps({"local_jan_code": jan[0].strip()})  # jsonファイルに置き換え
        print(json_code)

        #  lambda発火APIのURL
        first_api_url = "https://1433bwhqog.execute-api.ap-northeast-1.amazonaws.com/prod/status"
        
        try:
            first_response = requests.post(first_api_url, data=json_code)
            # レスポンス情報をログに記録
            logging.info(f"Received response: {first_response.status_code}, {first_response.text}")
        except requests.RequestException as e:
            # エラー情報をログに記録
            logging.error(f"Request failed: {e}")
            continue



        # Lambda発火APIからのレスポンス処理→レスポンスから実行ARNを抽出
        if first_response.status_code == 200:
            first_response_data = first_response.json()  # 実行Arn取得
            print("Lambda発火APIからのレスOK")

            execution_arn = first_response_data["executionArn"]

            # Lambda状態取得APIのURL
            second_api_url = "https://202g7nx6k4.execute-api.ap-northeast-1.amazonaws.com/prod/status-check"

            second_request_data = {
                "executionArn": execution_arn
            }


            # 開始時間の記録
            start_time = time.time()

            # 特定の処理があるまではずっとループ処理する→statusがRUNNINGからSUCCEEDEDになるまで
            while True:
                # Lambda状態取得APIにリクエスト
                second_response = requests.post(second_api_url, json=second_request_data)

                # Lambda状態取得APIからのレスポンス処理
                # 商品名と価格
                if second_response.status_code == 200:
                    second_response_data = second_response.json() # jsonファイルを解析してリストに変換
                    # print(second_response_data)  # レスポンスの詳細

                    if second_response_data.get('status') == 'RUNNING':
                        print("lambda関数からのレスポンス待ち")

                    # ステータスチェック
                    if second_response_data.get('status') == 'SUCCEEDED':
                        output_dict = second_response_data.get('output')
                        output_data = json.loads(output_dict)
                        body_dict = output_data.get('body')
                        print(f"スクレイピング成功:{body_dict}")
                        break
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