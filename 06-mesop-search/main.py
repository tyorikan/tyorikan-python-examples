import os

import mesop as me
import mesop.labs as mel
from google.protobuf.json_format import MessageToDict
from search import Search

e = os.environ
PROJECT_ID = e.get("GOOGLE_CLOUD_PROJECT")
DATA_STORE_ID = e.get("DATA_STORE_ID")
MODEL_LOCATION = e.get("MODEL_LOCATION", "asia-northeast1")
LOCATION = e.get("LOCATION", "global")

# Logger初期化
search = Search()


@me.page(
    path="/",
    title="データ検索チャット",
)
def page():
    mel.chat(transform, title="データ検索チャット", bot_user="アドバイザー")


def transform(input: str, history: list[mel.ChatMessage]):
    res = search.search(PROJECT_ID, LOCATION, DATA_STORE_ID, input)
    for item in res.results:
        dict = MessageToDict(item.document._pb)
        data = dict["derivedStructData"]
        link = data["link"].replace("gs://", "https://storage.googleapis.com/")

        yield (f"""**[{data['title']}]({link})**<br>*{data['snippets'][0]['snippet']}*<br><br>""")
