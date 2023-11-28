import csv
import json
import requests

with open('aws_test.csv') as f:
    jans = csv.reader(f)
    print(jans)

goods_status_details = {}

for jan in jans:
    json_code = json.dumps({"local_jan_code": jan[0]})  # jsonファイルに置き換え

    #  lambdaにリクエスト
    response = requests.post(' lambda URL, data=json_code')

    # responseがあった後のデータを受け取る
    # 商品名と価格
    if response.status_code == 200:
        response_data = response.json() # jsonファイルを解析してリストに変換
        print(response_data)

        product_name = response_data["lambda_product_name"]
        price = response_data["lambda_price"]

        print(product_name, price)

        goods_status_details[jan[0]] = (product_name, price)  # 辞書作成

    else:
        print(f"エラー: {response.status_code}")

# csv出力
with open('output.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['JANコード', '商品名', '価格'])
    for jan, (name, price) in goods_status_details.items():
        writer.writerow([jan, name, price])