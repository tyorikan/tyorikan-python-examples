import datetime
import json
import os
import tempfile
import uuid

import ebooklib
from bs4 import BeautifulSoup
from config import (
    get_genai_client,
    get_model_name,
    get_spanner_database,
    get_spanner_table_name,
    get_storage_client,
    get_upload_bucket_id,
)
from ebooklib import epub
from fastapi.concurrency import run_in_threadpool


def download_blob(bucket_name: str, source_blob_name: str) -> str:
    """GCSからファイルをダウンロードし、一時ファイルのパスを返す"""
    storage_client = get_storage_client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)

    # 一時ファイルを作成してダウンロード
    _, temp_local_filename = tempfile.mkstemp(
        suffix=os.path.splitext(source_blob_name)[1]
    )
    print(
        f"[GCS] ファイルをダウンロード中: {source_blob_name} -> {temp_local_filename}"
    )
    blob.download_to_filename(temp_local_filename)
    print("[GCS] ダウンロード完了")
    return temp_local_filename


def upload_blob(
    bucket_name: str, source_file_name: str, destination_blob_name: str
) -> str:
    """ローカルファイルをGCSにアップロードし、公開URLを返す"""
    storage_client = get_storage_client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    print(
        f"[GCS] ファイルをアップロード中: {source_file_name} -> gs://{bucket_name}/{destination_blob_name}"
    )
    blob.upload_from_filename(source_file_name)
    print("[GCS] アップロード完了")
    return f"gs://{bucket_name}/{destination_blob_name}"


def parse_epub(
    file_path: str, upload_bucket_name: str, original_file_name: str
) -> tuple[dict, str, list[str]]:
    """
    EPUBファイルを解析し、メタデータ、テキストコンテンツ、画像GCSパスのリストを返す

    Args:
        file_path (str): 解析するEPUBファイルのローカルパス
        upload_bucket_name (str): 画像のアップロード先GCSバケット名
        original_file_name (str): 元のファイル名（アップロードパスに使用）

    Returns:
        tuple[dict, str, list[str]]: (メタデータ辞書, テキストコンテンツ, 画像GCSパスのリスト)
    """
    print(f"[EPUB] 解析開始: {file_path}")
    book = epub.read_epub(file_path)

    # --- 1. メタデータの抽出 ---
    metadata = {
        "title": "No title",
        "author": "Unknown author",
        "publisher": "Unknown publisher",
        "published_date": None,
    }
    try:
        # Ebooklib uses namespaces, so we need to specify them
        dc_namespace = "http://purl.org/dc/elements/1.1/"
        titles = book.get_metadata(dc_namespace, "title")
        if titles:
            metadata["title"] = titles[0][0]

        creators = book.get_metadata(dc_namespace, "creator")
        if creators:
            metadata["author"] = ", ".join([c[0] for c in creators])

        publishers = book.get_metadata(dc_namespace, "publisher")
        if publishers:
            metadata["publisher"] = publishers[0][0]

        dates = book.get_metadata(dc_namespace, "date")
        if dates:
            # TODO: 日付形式のパースをより堅牢にする
            # 例: '2023-01-01T00:00:00Z'
            from dateutil import parser

            try:
                metadata["published_date"] = parser.parse(dates[0][0])
            except (parser.ParserError, TypeError):
                metadata["published_date"] = None

    except Exception as e:
        print(f"[EPUB] メタデータ抽出中にエラー: {e}")

    print(f"[EPUB] 抽出メタデータ: {metadata}")

    # --- 2. 画像の抽出とアップロード ---
    image_paths_map = {}  # 元のパス -> GCSパス
    image_gcs_paths = []
    images = book.get_items_of_type(ebooklib.ITEM_IMAGE)
    with tempfile.TemporaryDirectory() as temp_dir:
        for image in images:
            try:
                # 画像を一時ファイルに保存
                _, temp_image_ext = os.path.splitext(image.get_name())
                temp_image_path = os.path.join(
                    temp_dir, f"{uuid.uuid4()}{temp_image_ext}"
                )
                with open(temp_image_path, "wb") as f:
                    f.write(image.get_content())

                # GCSにアップロード
                image_gcs_path = upload_blob(
                    bucket_name=upload_bucket_name,
                    source_file_name=temp_image_path,
                    destination_blob_name=f"images/{original_file_name}/{os.path.basename(image.get_name())}",
                )
                image_paths_map[image.get_name()] = image_gcs_path
                image_gcs_paths.append(image_gcs_path)
            except Exception as e:
                print(f"[EPUB] 画像処理中にエラー: {e}")

    print(f"[EPUB] {len(image_gcs_paths)}個の画像をGCSにアップロードしました。")

    # --- 3. テキストの抽出と画像パスの置換 ---
    content_html = []
    items = book.get_items_of_type(ebooklib.ITEM_DOCUMENT)
    for item in items:
        soup = BeautifulSoup(item.get_content(), "html.parser")

        # 画像パスをGCSパスに置換
        for img_tag in soup.find_all("img"):
            original_src = img_tag.get("src")
            if original_src and original_src in image_paths_map:
                img_tag["src"] = image_paths_map[original_src]
                print(
                    f"[EPUB] 画像パスを置換: {original_src} -> {image_paths_map[original_src]}"
                )

        content_html.append(soup.prettify())

    full_content = "\n".join(content_html)
    print(f"[EPUB] テキストコンテンツ抽出完了（{len(full_content)}文字）")

    return metadata, full_content, image_gcs_paths


async def handle_epub(
    bucket_name: str, file_name_with_path: str, file_name: str, gcs_uri: str
):
    """EPUBファイルを処理します。"""
    print(f"[EPUB] EPUBの処理を開始: {file_name}")
    temp_epub_path = None
    try:
        # 1. GCSからEPUBファイルをダウンロード
        temp_epub_path = await run_in_threadpool(
            download_blob, bucket_name, file_name_with_path
        )

        # 2. EPUBを解析 (画像のGCSアップロードも含む)
        upload_bucket_id = get_upload_bucket_id()
        metadata, content, image_gcs_paths = await run_in_threadpool(
            parse_epub, temp_epub_path, upload_bucket_id, file_name
        )

        # 3. EPUBコンテンツを要約
        summary_text = await generate_summary_from_epub_content(
            content, image_gcs_paths
        )
        print("-" * 40)
        print(f"【EPUB要約結果】\n{summary_text[:200]}...\n(省略)")
        print("-" * 40)

        # 4. Spannerに保存
        await run_in_threadpool(
            save_to_spanner_for_epub_content,
            file_name,
            gcs_uri,
            metadata,
            content,
            image_gcs_paths,
            summary_text,
        )
    finally:
        # 一時ファイルをクリーンアップ
        if temp_epub_path and os.path.exists(temp_epub_path):
            os.remove(temp_epub_path)
            print(f"[EPUB] 一時ファイルを削除: {temp_epub_path}")


async def generate_summary_from_epub_content(
    content: str, image_gcs_paths: list[str]
) -> str:
    """EPUBのHTMLコンテンツをGeminiに読み込ませ、画像参照を含む要約を生成します。"""
    genai_client = get_genai_client()
    model_name = get_model_name()
    print("[Gemini] EPUBコンテンツの要約を生成中...")

    image_list_str = "\n".join(f"- {path}" for path in image_gcs_paths)

    prompt = f"""
    あなたは優秀なドキュメントアナリストです。
    以下のHTMLコンテンツの内容を読み取り、後でデータベースで検索した際に
    内容が十分に把握できるレベルの「詳細な要約」を作成してください。

    HTML内の`<img>`タグの`src`は、GCS上の画像パスに置換されています。
    要約の中で、本文中の画像について言及する必要がある場合は、
    必ず以下のリストにある対応するGCSパスを使用して、Markdown形式で画像を埋め込んでください。

    形式: `![画像の説明](GCSパス)`

    【利用可能な画像リスト】
    {image_list_str}

    【要件】
    - 文書の主要なトピック、結論、重要な数値を漏らさないこと。
    - 箇条書きを活用し、構造的にまとめること。
    - 日本語で出力すること。
    - 「承知しました」や「アナリストとして」などといった前置きは不要で、コンテンツの内容のみを返却すること。

    【HTMLコンテンツ】
    {content}
    """

    response = await genai_client.aio.models.generate_content(
        model=model_name,
        contents=[prompt],
    )
    return response.text if response.text is not None else ""


def save_to_spanner_for_epub_content(
    file_name: str,
    gcs_uri: str,
    metadata: dict,
    content: str,
    image_gcs_paths: list[str],
    summary: str,
):
    """EPUBの解析結果と要約をCloud Spannerに保存します。"""
    spanner_database = get_spanner_database()
    table_name = get_spanner_table_name()
    print(f"[Spanner] EPUBコンテンツと要約をデータベースへ保存中: {file_name}")

    def insert_epub_content(transaction):
        row_id = str(uuid.uuid4())
        created_at = datetime.datetime.now(datetime.timezone.utc)
        images_json = json.dumps(image_gcs_paths)

        transaction.insert(
            table=table_name,
            columns=[
                "Id",
                "GcsUri",
                "FileName",
                "Content",
                "Images",
                "Summary",
                "Title",
                "Author",
                "Publisher",
                "PublishedDate",
                "CreatedAt",
            ],
            values=[
                (
                    row_id,
                    gcs_uri,
                    file_name,
                    content,
                    images_json,
                    summary,
                    metadata.get("title"),
                    metadata.get("author"),
                    metadata.get("publisher"),
                    metadata.get("published_date"),
                    created_at,
                )
            ],
        )
        print(f"[Spanner] 生成されたID: {row_id}")

    spanner_database.run_in_transaction(insert_epub_content)
    print("[Spanner] 保存完了")
