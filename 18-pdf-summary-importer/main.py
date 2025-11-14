import os

import epub
import pdf
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()


# --- Pydanticモデル ---
class StorageObjectData(BaseModel):
    bucket: str
    name: str


# --- 例外ハンドラ ---
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.errors(), "body": exc.body},
    )


# --- メイン処理 ---
@app.post("/")
async def process_storage_event(event: StorageObjectData):
    """
    EventarcからCloud Storageイベントを受け取り、ファイルの拡張子に応じて処理を分岐します。
    - .pdf: ファイル内容を要約し、結果をSpannerに保存します。
    - .epub: ファイルを解析・要約し、テキスト、画像、メタデータをSpannerとGCSに保存します。
    """
    bucket_name = event.bucket
    file_name_with_path = event.name
    gcs_uri = f"gs://{bucket_name}/{file_name_with_path}"
    file_name = os.path.basename(file_name_with_path)
    print(f"[Event] 対象ファイル: {gcs_uri}")

    try:
        if file_name_with_path.lower().endswith(".pdf"):
            await pdf.handle_pdf(gcs_uri, file_name)
        elif file_name_with_path.lower().endswith(".epub"):
            await epub.handle_epub(bucket_name, file_name_with_path, file_name, gcs_uri)
        else:
            print(f"[Info] サポートされていないファイル形式です: {file_name}")
            return JSONResponse(
                content={"message": "サポートされていないファイル形式です。"},
                status_code=200,
            )

        return JSONResponse(
            content={"message": "処理が正常に完了しました。"}, status_code=200
        )

    except Exception as e:
        print(f"[Error] 処理中に予期せぬエラーが発生しました: {e}")
        import traceback

        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail="サーバー内部でエラーが発生しました。"
        )
