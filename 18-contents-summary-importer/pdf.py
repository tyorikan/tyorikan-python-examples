import datetime
import uuid

from config import (
    get_genai_client,
    get_model_name,
    get_spanner_database,
    get_spanner_table_name,
)
from fastapi.concurrency import run_in_threadpool
from google.genai.types import Part


async def handle_pdf(gcs_uri: str, file_name: str):
    """PDFファイルを処理します。"""
    print(f"[PDF] PDFの処理を開始: {file_name}")
    summary_text = await generate_summary_from_pdf(gcs_uri)
    print("-" * 40)
    print(f"【PDF要約結果】\n{summary_text[:200]}...\n(省略)")
    print("-" * 40)
    await run_in_threadpool(
        save_to_spanner_for_pdf_summary, file_name, gcs_uri, summary_text
    )


async def generate_summary_from_pdf(gcs_uri: str) -> str:
    """GCS上のPDFファイルをGeminiに読み込ませ、詳細な要約を生成します。"""
    genai_client = get_genai_client()
    model_name = get_model_name()
    print(f"[Gemini] PDFファイルを参照中: {gcs_uri}")
    prompt = """
    あなたは優秀なドキュメントアナリストです。
    以下のPDFファイルの内容を読み取り、後でデータベースで検索した際に
    内容が十分に把握できるレベルの「詳細な要約」を作成してください。
    【要件】
    - 文書の主要なトピック、結論、重要な数値を漏らさないこと。
    - 箇条書きを活用し、構造的にまとめること。
    - 日本語で出力すること。
    - 「承知しました」や「アナリストとして」などといった前置きは不要で、コンテンツの内容のみを返却すること。
    """
    response = await genai_client.aio.models.generate_content(
        model=model_name,
        contents=[
            Part.from_uri(file_uri=gcs_uri, mime_type="application/pdf"),
            prompt,
        ],
    )
    return response.text if response.text is not None else ""


def save_to_spanner_for_pdf_summary(file_name: str, gcs_uri: str, summary: str):
    """PDFの要約結果をCloud Spannerに保存します。"""
    spanner_database = get_spanner_database()
    table_name = get_spanner_table_name()
    print(f"[Spanner] PDF要約をデータベースへ保存中: {file_name}")

    def insert_summary(transaction):
        row_id = str(uuid.uuid4())
        created_at = datetime.datetime.now(datetime.timezone.utc)
        transaction.insert(
            table=table_name,
            columns=["Id", "GcsUri", "FileName", "Summary", "CreatedAt"],
            values=[(row_id, gcs_uri, file_name, summary, created_at)],
        )
        print(f"[Spanner] 生成されたID: {row_id}")

    spanner_database.run_in_transaction(insert_summary)
    print("[Spanner] 保存完了")
