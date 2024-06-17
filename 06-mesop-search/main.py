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

search = Search()


@me.page(
    path="/",
    title="データ検索チャット",
)
def page():
    mel.chat(transform, title="データ検索チャット", bot_user="DX レポ太郎")


def transform(input: str, history: list[mel.ChatMessage]):
    res = search.search(PROJECT_ID, LOCATION, DATA_STORE_ID, input)

    yield (f"""**{res.summary.summary_with_metadata.summary}**<br><br>""")
    print(MessageToDict(res._pb))

    i = 1
    yield "【関連ドキュメント】<br>"
    for item in res.results:
        dict = MessageToDict(item.document._pb)
        data = dict["derivedStructData"]
        link = data["link"].replace("gs://", "https://storage.googleapis.com/")

        yield (
            f"""{i}. **[{data['title']}]({link})**<br>*{data['snippets'][0]['snippet']}*<br><br>"""
        )
        i += 1
