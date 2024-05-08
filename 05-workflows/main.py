import os
from pathlib import Path
from uuid import uuid4

import psycopg2
from fastapi import FastAPI, File, Request, Response, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBearer
from fastapi.staticfiles import StaticFiles
from google.auth.transport import requests
from google.cloud import storage
from google.oauth2 import id_token
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

app = FastAPI()
security = HTTPBearer()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")


def validate_iap_jwt(iap_jwt, expected_audience):
    """Validate an IAP JWT.

    Args:
      iap_jwt: The contents of the X-Goog-IAP-JWT-Assertion header.
      expected_audience: The Signed Header JWT audience. See
          https://cloud.google.com/iap/docs/signed-headers-howto
          for details on how to get this value.

    Returns:
      (user_id, user_email, error_str).
    """
    try:
        decoded_jwt = id_token.verify_token(
            iap_jwt,
            requests.Request(),
            audience=expected_audience,
            certs_url="https://www.gstatic.com/iap/verify/public_key",
        )
        return (decoded_jwt["gcip"]["sub"], decoded_jwt["gcip"]["email"], "")
    except Exception as e:
        return (None, None, f"**ERROR: JWT validation error {e}**")


@app.middleware("http")
async def jwt_authentication_middleware(request: Request, call_next):
    assertion = request.headers.get("X-Goog-IAP-JWT-Assertion")
    if assertion is None:
        return Response(status_code=status.HTTP_403_FORBIDDEN)

    expected_audience = f"/projects/{os.getenv('PROJECT_NUMBER')}/global/backendServices/{os.getenv('BACKEND_SERVICE_ID')}"

    id, email, err = validate_iap_jwt(assertion, expected_audience)
    if err != "":
        print(err)
        return Response(status_code=status.HTTP_403_FORBIDDEN)

    request.state.uid = id
    request.state.email = email

    return await call_next(request)


@app.post("/upload-image")
async def upload_image(image: UploadFile = File(...)):
    # バケット名とBlob名を作成
    bucket_name = os.getenv("TMP_UPLOAD_BUCKET_NAME")
    suffix = Path(image.filename).suffix
    blob_name = f"{uuid4()}{suffix}"

    # Cloud Storage にアップロード
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_file(image.file, content_type=image.content_type)

    # オブジェクトパスを返す
    return {"object_path": blob.name}


@app.post("/incidents")
async def save_incidents(request: Request):
    # 1. Validate request body
    try:
        request_data = await request.json()
        print(request_data)
        validate_request_data(request_data)
    except Exception as e:
        print(e)
        return Response(status_code=status.HTTP_400_BAD_REQUEST)

    # 2. Move Object data from tmp bucket to persistible　bucket
    move_object(request_data["image_path"])

    # 3. Save request data to PostgreSQL
    save_to_db(request_data)

    # 4. Send email (to approvers etc) by using SendGrid API Key
    send_email(request_data)

    # 5. Return success response
    return Response(status_code=status.HTTP_201_CREATED)


@app.get("/")
def index(request: Request):
    print(request.headers)
    print(f"uid= {request.state.uid}")
    print(f"email= {request.state.email}")
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
    source_bucket.copy_blob(source_blob, destination_bucket, object_path)

    # 元のオブジェクトを削除
    # source_blob.delete()


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

    # トランザクションを開始
    cur.execute("BEGIN TRANSACTION;")

    # データを挿入
    try:
        # incidents テーブルにデータを挿入
        incidents_sql = """
            INSERT INTO incidents (
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
                injury_description
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
                %(injury_description)s
            )
            RETURNING id;
        """
        cur.execute(incidents_sql, data)
        incident_id = cur.fetchone()[0]

        # incident_occurrences テーブルにデータを挿入
        incident_occurrences_sql = """
            INSERT INTO incident_occurrences (
                incident_id,
                description,
                image_path
            )
            VALUES (
                %(incident_id)s,
                %(description)s,
                %(image_path)s
            );
        """
        data["incident_id"] = incident_id
        cur.execute(incident_occurrences_sql, data)

        conn.commit()

    except Exception as e:
        # エラーが発生した場合はロールバック
        conn.rollback()
        raise e

    finally:
        # カーソルと接続を閉じる
        cur.close()
        conn.close()


def send_email(data):
    """
    Send email (to approvers etc) by using SendGrid API Key.
    """
    # SendGrid API キーを取得
    sendgrid_api_key = os.getenv("SENDGRID_API_KEY")

    # API キーが無い場合、送信しない
    if sendgrid_api_key is None:
        return

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
        """,
    )

    # メールを送信
    SendGridAPIClient(sendgrid_api_key).send(message)
