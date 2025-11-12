import datetime
import os
import uuid

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.concurrency import run_in_threadpool
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from google import genai
from google.cloud import spanner
from google.genai.types import Part
from pydantic import BaseModel

# --- 設定値 ---
PROJECT_ID = os.getenv("PROJECT_ID")
if not PROJECT_ID:
    raise ValueError("環境変数 'PROJECT_ID' が設定されていません。")
LOCATION = os.getenv("LOCATION", "us-central1")
SPANNER_INSTANCE_ID = os.getenv("SPANNER_INSTANCE_ID")
if not SPANNER_INSTANCE_ID:
    raise ValueError("環境変数 'SPANNER_INSTANCE_ID' が設定されていません。")
SPANNER_DATABASE_ID = os.getenv("SPANNER_DATABASE_ID")
if not SPANNER_DATABASE_ID:
    raise ValueError("環境変数 'SPANNER_DATABASE_ID' が設定されていません。")
SPANNER_TABLE_NAME = os.getenv("SPANNER_TABLE_NAME")
if not SPANNER_TABLE_NAME:
    raise ValueError("環境変数 'SPANNER_TABLE_NAME' が設定されていません。")

# 想定される Spanner テーブルスキーマ:
# CREATE TABLE DocumentSummaries (
#     Id STRING(36) NOT NULL,    -- UUID (Primary Key)
#     GcsUri STRING(MAX),        -- GS Util URI (例: gs://bucket/file.pdf)
#     FileName STRING(MAX),      -- ファイル名
#     Summary STRING(MAX),       -- 生成された要約
#     CreatedAt TIMESTAMP,
# ) PRIMARY KEY (Id);

MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.5-pro")

# Geminiクライアントの初期化
genai_client = genai.Client(
    vertexai=True,
    project=PROJECT_ID,
    location=LOCATION,
)

spanner_client = spanner.Client(project=PROJECT_ID)
instance = spanner_client.instance(SPANNER_INSTANCE_ID)

app = FastAPI()


# RequestValidationErrorを捕捉し、400 Bad Requestを返す例外ハンドラ
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.errors(), "body": exc.body},
    )


class StorageObjectData(BaseModel):
    bucket: str
    name: str


class CloudEvent(BaseModel):
    data: StorageObjectData


@app.post("/")
async def process_storage_event(event: CloudEvent):
    """
    EventarcからCloud Storageイベントを受け取り、PDF要約処理を実行します。
    """
    # GCSのオブジェクト情報を取得
    bucket = event.data.bucket
    name = event.data.name
    gcs_uri = f"gs://{bucket}/{name}"
    file_name = os.path.basename(name)
    print(f"[Event] 対象ファイル: {gcs_uri}")

    try:
        # 1. Gemini で要約生成
        summary_text = await generate_summary_from_gcs(gcs_uri)

        print("-" * 40)
        print(f"【要約結果】\n{summary_text[:200]}...\n(省略)")
        print("-" * 40)

        # 2. Spanner に保存
        await run_in_threadpool(save_to_spanner, file_name, gcs_uri, summary_text)

        return JSONResponse(
            content={"message": "処理が正常に完了しました。"}, status_code=200
        )

    except Exception as e:
        print(f"[Error] 処理中にエラーが発生しました: {e}")
        # 必要であれば、ここでスタックトレースをログに出力します
        # import traceback
        # traceback.print_exc()
        raise HTTPException(
            status_code=500, detail="サーバー内部でエラーが発生しました。"
        )


async def generate_summary_from_gcs(gcs_uri: str) -> str:
    """
    GCS上のPDFファイルをGeminiに読み込ませ、詳細な要約を生成します。
    """
    print(f"[Gemini] GCSファイルを参照中: {gcs_uri}")

    prompt = """
    あなたは優秀なドキュメントアナリストです。
    以下のPDFファイルの内容を読み取り、後でデータベースで検索した際に
    内容が十分に把握できるレベルの「詳細な要約」を作成してください。

    【要件】
    - 文書の主要なトピック、結論、重要な数値を漏らさないこと。
    - 箇条書きを活用し、構造的にまとめること。
    - 日本語で出力すること。
    """

    response = await genai_client.aio.models.generate_content(
        model=f"projects/{PROJECT_ID}/locations/{LOCATION}/models/{MODEL_NAME}",
        contents=[
            Part.from_uri(
                file_uri=gcs_uri,
                mime_type="application/pdf",
            ),
            prompt,
        ],
    )
    print(response)

    return response.text if response.text is not None else ""


def save_to_spanner(file_name: str, gcs_uri: str, summary: str):
    """
    要約結果とファイル情報をCloud Spannerに保存します。
    """
    print(f"[Spanner] データベースへ保存中: {file_name}")
    database = instance.database(SPANNER_DATABASE_ID)

    def insert_summary(transaction):
        row_id = str(uuid.uuid4())
        created_at = datetime.datetime.now(datetime.timezone.utc)

        transaction.insert(
            table=SPANNER_TABLE_NAME,
            columns=["Id", "GcsUri", "FileName", "Summary", "CreatedAt"],
            values=[(row_id, gcs_uri, file_name, summary, created_at)],
        )
        print(f"[Spanner] 生成されたID: {row_id}")

    database.run_in_transaction(insert_summary)
    print("[Spanner] 保存完了")
