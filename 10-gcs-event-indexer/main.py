import os

import vertexai
import time
from fastapi import FastAPI, Response
from google.cloud import firestore, storage
from google.cloud.firestore_v1.base_vector_query import DistanceMeasure
from google.cloud.firestore_v1.vector import Vector
from pydantic import BaseModel
from pypdf import PdfReader
from vertexai.generative_models import (
    Content,
    GenerativeModel,
    HarmBlockThreshold,
    HarmCategory,
    Part,
)
from vertexai.language_models import TextEmbeddingModel

# 環境変数からプロジェクトIDなどを取得
project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
location = os.environ.get("REGION", "asia-northeast1")  # デフォルトは 'asia-northeast1'

# Vertex AI と Firestore の初期化
vertexai.init(project=project_id, location=location)
db = firestore.Client(project=project_id)
storage_client = storage.Client(project=project_id)

# Embedding モデルとテキスト生成モデルの読み込み
embedding_model = TextEmbeddingModel.from_pretrained("textembedding-gecko@001")
generation_model = GenerativeModel(
    model_name="gemini-1.5-flash-001",
    system_instruction="""
    あなたは、レストランのメニューにある食べ物についての質問に答えることができる、役に立つ AI アシスタントとして行動します。
    質問に答えるのに、提供されたコンテキストのみを使用してください。
    わからない場合は、答えをでっち上げないでください。
    メニューのアイテムを追加または変更しないでください。
    """,
    safety_settings={
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    },
)

app = FastAPI()

COLLECTION_NAME = "menuInfo"
EMB_FIELD_NAME = "embedding"


class Data(BaseModel):
    bucket: str
    name: str


@app.post("/events/gcs-indexer")
async def gcs_event_indexer(data: Data, response: Response):
    """Cloud Storage イベントをトリガーにファイルを処理する"""
    bucket_name = data.bucket
    file_name = data.name

    try:
        # Cloud Storage からファイルを読み込む
        start_time = time.perf_counter()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(file_name)
        tmp_file_path = f"/tmp/{file_name}"
        blob.download_to_filename(tmp_file_path)
        end_time = time.perf_counter()
        print("{}", end_time - start_time)

        collection = db.collection(COLLECTION_NAME)

        # テキストをチャンクに分割する
        # 各チャンクの Embedding データを取得する
        reader = PdfReader(tmp_file_path)
        for page in reader.pages:
            chunk = page.extract_text()
            embeddings = embedding_model.get_embeddings([chunk])[0].values
            collection.add({"description": chunk, EMB_FIELD_NAME: Vector(embeddings)})

        return {"message": "success", "file": file_name}

    except Exception as e:
        print(f"Error processing file {file_name}: {e}")
        response.status_code = 500
        return {"message": "error", "file": file_name, "error": str(e)}


class Query(BaseModel):
    query: str


@app.post("/retriever")
async def retriever(query: Query):
    """クエリを受け取り、Firestore から関連する情報を探し、VertexAI に問い合わせて回答を返す"""
    try:
        collection = db.collection(COLLECTION_NAME)

        # クエリのembeddingを取得
        query_embedding = embedding_model.get_embeddings([query.query])[0].values

        # Requires a single-field vector index
        vector_query = collection.find_nearest(
            vector_field=EMB_FIELD_NAME,
            query_vector=Vector(query_embedding),
            distance_measure=DistanceMeasure.EUCLIDEAN,
            limit=5,
        )

        history = []
        for snapshot in vector_query.get():
            text_chunk = snapshot.get("description")
            history.append(Content(role="model", parts=[Part.from_text(text_chunk)]))
        history.append(Content(role="user", parts=[Part.from_text(query.query)]))

        responses = generation_model.generate_content(
            contents=history,
            generation_config={
                "max_output_tokens": 8192,
                "temperature": 1,
                "top_p": 0.95,
            },
        )

        return responses.text

    except Exception as e:
        print(f"Error processing query: {e}")
        return {"message": "error", "error": str(e)}
