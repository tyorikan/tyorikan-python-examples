import os, pytz

from pytrends.request import TrendReq
from google.cloud import bigquery
from datetime import datetime

# pytrendsを初期化
pytrends = TrendReq(hl='ja-JP', tz=360)

# トレンドを取得したいキーワードを設定
keywords = os.getenv("KEYWORDS", "Google").split(",")

# Googleトレンドデータを取得
pytrends.build_payload(keywords, timeframe='now 7-d')

# 関連クエリを取得
related_queries = pytrends.related_queries()

# BigQuery へ insert
#-------------------------
client = bigquery.Client()
project_id = os.environ.get("PROJECT_ID")
dataset = os.environ.get("DATASET")
table = os.environ.get("TABLE")
table_id = '{}.{}.{}'.format(project_id, dataset, table)

now = datetime.now(pytz.timezone("Asia/Tokyo")).strftime("%Y-%m-%dT%H:%M:%S")
#now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ") # TIMESTAMP 型の場合
rows_to_insert = []

for keyword, data in related_queries.items():
    result_dict = {
        "keyword": keyword,
        "top": [],
        "rising": []
    }

    top_data = data['top'].to_dict()
    rising_data = data['rising'].to_dict()

    # Top queries (key = query or value)
    tmp_array = {}
    for key, values in top_data.items():
        for i, val in values.items():
            tmp_array.setdefault(i, {"type": "top"})
            tmp_array[i].update({key: val})

    for _, d in tmp_array.items():
        rows_to_insert.append({
            "keyword": keyword,
            "type": d["type"],
            "query": d["query"],
            "value": d["value"],
            "datetime": now
        })

    # Rising queries (key = query or value)
    tmp_array = {}
    for key, values in rising_data.items():
        for i, val in values.items():
            tmp_array.setdefault(i, {"type": "rising"})
            tmp_array[i].update({key: val})

    for _, d in tmp_array.items():
        rows_to_insert.append({
            "keyword": keyword,
            "type": d["type"],
            "query": d["query"],
            "value": d["value"],
            "datetime": now
        })

errors = client.insert_rows_json(table_id, rows_to_insert)
if errors == []:
    print("New rows have been added to BigQuery. {}".format(rows_to_insert))
else:
    print(errors)
    exit(1)