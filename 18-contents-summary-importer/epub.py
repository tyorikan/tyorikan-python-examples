import asyncio
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


def _parse_best_effort_date(date_str: str) -> datetime.datetime | None:
    """さまざまな形式の日付文字列を解釈し、datetimeオブジェクトを返す試みを行う"""
    if not date_str:
        return None

    # 一般的なフォーマットを優先的に試す
    common_formats = [
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d",
        "%Y/%m/%d",
    ]
    for fmt in common_formats:
        try:
            return datetime.datetime.strptime(date_str, fmt)
        except ValueError:
            continue

    # YYYY-MM 形式のパース
    try:
        return datetime.datetime.strptime(date_str, "%Y-%m")
    except ValueError:
        pass

    # YYYY 形式のパース
    try:
        return datetime.datetime.strptime(date_str, "%Y")
    except ValueError:
        pass

    # dateutil.parserによる最終試行
    from dateutil import parser

    try:
        return parser.parse(date_str)
    except (parser.ParserError, TypeError):
        print(f"[EPUB] 日付のパースに失敗: {date_str}")
        return None


def parse_epub(
    file_path: str, upload_bucket_name: str, original_file_name: str
) -> tuple[dict, list[str], list[str]]:
    """
    EPUBファイルを解析し、メタデータ、HTMLチャンクのGCSパスリスト、画像GCSパスのリストを返す

    Args:
        file_path (str): 解析するEPUBファイルのローカルパス
        upload_bucket_name (str): 画像やHTMLのアップロード先GCSバケット名
        original_file_name (str): 元のファイル名（アップロードパスに使用）

    Returns:
        tuple[dict, list[str], list[str]]: (メタデータ辞書, HTMLチャンクGCSパスリスト, 画像GCSパスのリスト)
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
            metadata["published_date"] = _parse_best_effort_date(dates[0][0])

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

    # --- 3. HTMLチャンクの抽出、画像パス置換、GCSへのアップロード ---
    html_gcs_paths = []
    items = book.get_items_of_type(ebooklib.ITEM_DOCUMENT)
    with tempfile.TemporaryDirectory() as temp_dir:
        for i, item in enumerate(items):
            try:
                soup = BeautifulSoup(item.get_content(), "html.parser")

                # 画像パスをGCSパスに置換
                for img_tag in soup.find_all("img"):
                    original_src = img_tag.get("src")
                    if original_src and original_src in image_paths_map:
                        img_tag["src"] = image_paths_map[original_src]
                        print(
                            f"[EPUB] 画像パスを置換: {original_src} -> {image_paths_map[original_src]}"
                        )

                # 変更されたHTMLを一時ファイルに保存
                temp_html_path = os.path.join(temp_dir, f"chunk_{i}.html")
                with open(temp_html_path, "w", encoding="utf-8") as f:
                    f.write(soup.prettify())

                # HTMLチャンクをGCSにアップロード
                html_gcs_path = upload_blob(
                    bucket_name=upload_bucket_name,
                    source_file_name=temp_html_path,
                    destination_blob_name=f"html_chunks/{original_file_name}/{os.path.basename(item.get_name())}",
                )
                html_gcs_paths.append(html_gcs_path)
            except Exception as e:
                print(f"[EPUB] HTMLチャンク処理中にエラー: {e}")

    print(f"[EPUB] {len(html_gcs_paths)}個のHTMLチャンクをGCSにアップロードしました。")

    return metadata, html_gcs_paths, image_gcs_paths


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
        metadata, html_gcs_paths, image_gcs_paths = await run_in_threadpool(
            parse_epub, temp_epub_path, upload_bucket_id, file_name
        )

        # 3. EPUBコンテンツを要約
        summary_text = await generate_summary_from_html_chunks(
            html_gcs_paths, image_gcs_paths
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
            html_gcs_paths,
            image_gcs_paths,
            summary_text,
        )
    finally:
        # 一時ファイルをクリーンアップ
        if temp_epub_path and os.path.exists(temp_epub_path):
            os.remove(temp_epub_path)
            print(f"[EPUB] 一時ファイルを削除: {temp_epub_path}")


async def generate_summary_from_html_chunks(
    html_gcs_paths: list[str], image_gcs_paths: list[str]
) -> str:
    """HTMLチャンクのGCSパスリストから段階的に要約を生成します（Map-Reduce）"""
    genai_client = get_genai_client()
    model_name = get_model_name()
    upload_bucket_id = get_upload_bucket_id()

    # --- Mapフェーズ: 各HTMLチャンクの要約を並列で生成 ---
    async def _get_intermediate_summary(html_gcs_path: str) -> str:
        # GCSパスからファイル名部分を抽出
        blob_name = html_gcs_path.replace(f"gs://{upload_bucket_id}/", "")

        temp_html_path = None
        try:
            # GCSからHTMLチャンクをダウンロード
            temp_html_path = await run_in_threadpool(
                download_blob, upload_bucket_id, blob_name
            )
            with open(temp_html_path, "r", encoding="utf-8") as f:
                html_content = f.read()

            # 中間要約用のプロンプト
            prompt = f"""
            これは書籍の一部（1つの章またはセクション）のHTMLコンテンツです。
            この部分の要点をまとめた「中間要約」を作成してください。
            後で他の部分の要約と結合して、書籍全体の要約を作成します。
            - 箇条書きで簡潔に。
            - 日本語で出力。
            - 前置きは不要。

            【HTMLコンテンツ】
            {html_content}
            """
            response = await genai_client.aio.models.generate_content(
                model=model_name, contents=[prompt]
            )
            return response.text or ""
        finally:
            if temp_html_path and os.path.exists(temp_html_path):
                os.remove(temp_html_path)

    print(f"[Gemini] Mapフェーズ開始: {len(html_gcs_paths)}個のチャンクを要約します。")
    intermediate_summaries = await asyncio.gather(
        *[_get_intermediate_summary(path) for path in html_gcs_paths]
    )
    print("[Gemini] Mapフェーズ完了。")

    # --- Reduceフェーズ: 中間要約を統合して最終的な要約を生成 ---
    print("[Gemini] Reduceフェーズ開始: 中間要約を統合します。")
    combined_summaries = "\n\n---\n\n".join(
        f"【章/セクションの要約 {i + 1}】\n{s}"
        for i, s in enumerate(intermediate_summaries)
    )
    image_list_str = "\n".join(f"- {path}" for path in image_gcs_paths)

    final_prompt = f"""
    あなたは優秀なドキュメントアナリストです。
    以下に、書籍の各章（またはセクション）ごとに作成された「中間要約」のリストがあります。
    これらすべてを統合し、書籍全体の構造がわかるような「詳細な最終要約」を作成してください。

    要約の中で、本文中の画像について言及する必要がある場合は、
    必ず以下のリストにある対応するGCSパスを使用して、Markdown形式で画像を埋め込んでください。

    形式: `![画像の説明](GCSパス)`

    【利用可能な画像リスト】
    {image_list_str}

    【要件】
    - 書籍全体の主要なトピック、議論の流れ、そして結論が明確にわかるように構成すること。
    - 各章の要点が漏れないようにしつつ、冗長な表現は避けること。
    - 箇条書きを活用し、構造的にまとめること。
    - 日本語で出力すること。
    - 「承知しました」や「アナリストとして」などといった前置きは不要で、コンテンツの内容のみを返却すること。

    【中間要約のリスト】
    {combined_summaries}
    """
    final_response = await genai_client.aio.models.generate_content(
        model=model_name, contents=[final_prompt]
    )
    print("[Gemini] Reduceフェーズ完了。")

    return final_response.text or ""


def save_to_spanner_for_epub_content(
    file_name: str,
    gcs_uri: str,
    metadata: dict,
    html_gcs_paths: list[str],
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
        html_chunks_json = json.dumps(html_gcs_paths)

        transaction.insert(
            table=table_name,
            columns=[
                "Id",
                "GcsUri",
                "FileName",
                "HtmlChunks",
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
                    html_chunks_json,
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
