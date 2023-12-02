import csv
import json
import requests

goods_status_details = {}


start_json = {"path": "/start"}
#  Lambda発火APIにリクエスト
start_response = requests.post(' https://ercldru20j.execute-api.ap-northeast-1.amazonaws.com/prod, json=start_json')

# responseがあった後のデータを受け取る
# 商品名と価格
if start_response.status_code == 200:
    response_data = start_response.json() # jsonファイルを解析してリストに変換
    print(response_data)

else:
    print(f"エラー: {start_response.status_code}")



# Lambda状態取得APIの処理を実施
with open('aws_test.csv') as f:
    jans = csv.reader(f)

    for jan in jans:
        print(jans)
        json_code = json.dumps({"path": "/start","local_jan_code": jan[0]})  # jsonファイルに置き換え
        print(json_code)

        #  lambda状態取得APIにリクエスト
        status_response = requests.post(' https://dfoou098ee.execute-api.ap-northeast-1.amazonaws.com/product/, data=json_code')

        # responseがあった後のデータを受け取る
        # 商品名と価格
        if status_response.status_code == 200:
            response_data = status_response.json() # jsonファイルを解析してリストに変換
            print(response_data)

            product_name = response_data["lambda_product_name"]
            price = response_data["lambda_price"]

            print(product_name, price)

            goods_status_details[jan[0]] = (product_name, price)  # 辞書作成

        else:
            print(f"エラー: {status_response.status_code}")

# csv出力
with open('output.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['JANコード', '商品名', '価格'])
    for jan, (name, price) in goods_status_details.items():
        writer.writerow([jan, name, price])