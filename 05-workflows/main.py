from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from io import BytesIO
from PIL import Image
from uuid import uuid4
from google.cloud import storage
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

import os
import psycopg2

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.post("/upload-image")
async def upload_image(image: UploadFile = File(...)):
    # バケット名とBlob名を作成
    bucket_name = os.getenv("TMP_UPLOAD_BUCKET_NAME")
    blob_name = f"{uuid4()}.jpg"

    # 画像をリサイズ
    image_bytes = await image.read()
    image = Image.open(BytesIO(image_bytes))
    image = image.resize((256, 256))

    # Cloud Storage にアップロード
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_file(image)

    # オブジェクトパスを返す
    return {"object_path": blob.name}

@app.post("/incidents")
def save_incidents(request: Request):
    # 1. Validate request body
    try:
        request_data = request.json()
        validate_request_data(request_data)
    except Exception as e:
        return HTMLResponse(content=str(e), status_code=400)

    # 2. Move Object data from tmp bucket to persistible　bucket
    move_object(request_data["image_path"])

    # 3. Save request data to PostgreSQL
    save_to_db(request_data)

    # 4. Send email (to approvers etc) by using SendGrid API Key
    send_email(request_data)

    # 5. Return success response
    return HTMLResponse("User saved successfully")

@app.get("/")
def index(request: Request):
    return HTMLResponse(content=open("static/index.html").read(), status_code=200)

def validate_request_data(data):
    # TODO: Implement request data validation
    return

def move_object(object_path):
    """
    Move object from tmp bucket to persistible bucket.
    """
    # バケット名を取得
    tmp_bucket_name = os.getenv("TMP_UPLOAD_BUCKET_NAME")
    persistible_bucket_name = os.getenv("PERSISTIBLE_BUCKET_NAME")

    # クライアントを作成
    storage_client = storage.Client()

    # オブジェクトをコピー
    source_bucket = storage_client.bucket(tmp_bucket_name)
    source_blob = source_bucket.blob(object_path)
    destination_bucket = storage_client.bucket(persistible_bucket_name)
    destination_blob = destination_bucket.blob(object_path)
    destination_blob.content_type = "image/png"
    destination_blob.copy_from(source_blob)

    # 元のオブジェクトを削除
    source_blob.delete()

def save_to_db(data):
    """
    Save data to PostgreSQL.
    """
    # データベースに接続
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT", 5432),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
    )
    cur = conn.cursor()

    # テーブル名を取得
    table_name = "incidents"

    # データを挿入
    sql = f"""
        INSERT INTO {table_name} (
            title,
            submit_date,
            location_id,
            department_id,
            type,
            occurred_at,
            occurred_place_id,
            occurred_place_detail,
            cause_id,
            witness_id,
            witness_manager_id,
            reporter_id,
            reporter_phone_number,
            manager_id,
            worker_id,
            work_members,
            disaster_type_id,
            injury_classification_id,
            injured_part_id,
            injury_description,
            description,
            image_path
        )
        VALUES (
            %(title)s,
            %(submit_date)s,
            %(location_id)s,
            %(department_id)s,
            %(type)s,
            %(occurred_at)s,
            %(occurred_place_id)s,
            %(occurred_place_detail)s,
            %(cause_id)s,
            %(witness_id)s,
            %(witness_manager_id)s,
            %(reporter_id)s,
            %(reporter_phone_number)s,
            %(manager_id)s,
            %(worker_id)s,
            %(work_members)s,
            %(disaster_type_id)s,
            %(injury_classification_id)s,
            %(injured_part_id)s,
            %(injury_description)s,
            %(description)s,
            %(image_path)s
        );
    """
    cur.execute(sql, data)
    conn.commit()

    # カーソルと接続を閉じる
    cur.close()
    conn.close()

def send_email(data):
    """
    Send email (to approvers etc) by using SendGrid API Key.
    """
    # SendGrid API キーを取得
    sendgrid_api_key = os.getenv("SENDGRID_API_KEY")

    # メールを作成
    message = Mail(
        from_email="sender@example.com",
        to_emails=["recipient@example.com"],
        subject="Incident Report",
        html_content=f"""
        <p>新しいインシデントが報告されました。</p>
        <p>タイトル: {data["title"]}</p>
        <p>発生日時: {data["occurred_at"]}</p>
        <p>場所: {data["occurred_place_detail"]}</p>
        <p>詳細: {data["description"]}</p>
        <p>画像: {data["image_path"]}</p>
        """
    )

    # メールを送信
    try:
        sg = SendGridAPIClient(sendgrid_api_key)
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.message)
