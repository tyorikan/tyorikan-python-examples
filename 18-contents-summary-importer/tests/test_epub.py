# `epub` をインポートする前に環境変数を設定
import datetime
import json
from unittest.mock import ANY, AsyncMock, MagicMock, mock_open, patch

import epub
import pytest
from ebooklib import epub as ebooklib_epub


@pytest.fixture(autouse=True)
def set_env_vars(monkeypatch):
    """テスト用の環境変数を設定する"""
    monkeypatch.setenv("PROJECT_ID", "test-project")
    monkeypatch.setenv("LOCATION", "us-central1")
    monkeypatch.setenv("SPANNER_INSTANCE_ID", "test-instance")
    monkeypatch.setenv("SPANNER_DATABASE_ID", "test-database")
    monkeypatch.setenv("SPANNER_TABLE_NAME", "test-table")
    monkeypatch.setenv("UPLOAD_BUCKET_ID", "test-upload-bucket")
    monkeypatch.setenv("MODEL_NAME", "test-model")


@pytest.fixture
def mock_run_in_threadpool():
    """fastapi.concurrency.run_in_threadpoolをモック化するフィクスチャ"""

    async def side_effect(func, *args, **kwargs):
        return func(*args, **kwargs)

    with patch("epub.run_in_threadpool", new_callable=AsyncMock) as mock:
        mock.side_effect = side_effect
        yield mock


@pytest.fixture
def mock_upload_blob():
    """epub.upload_blobをモック化するフィクスチャ"""

    def upload_side_effect(bucket_name, source_file_name, destination_blob_name):
        return f"gs://{bucket_name}/{destination_blob_name}"

    with patch("epub.upload_blob") as mock_upload:
        mock_upload.side_effect = upload_side_effect
        yield mock_upload


@pytest.fixture
def mock_genai_client():
    """Geminiクライアントをモック化するフィクスチャ"""
    with patch("epub.get_genai_client") as mock_get_client:
        mock_client = MagicMock()
        # generate_content を AsyncMock に設定
        # side_effectは各テストで設定する
        mock_client.aio.models.generate_content = AsyncMock()
        mock_get_client.return_value = mock_client
        yield mock_client


@pytest.fixture
def mock_ebooklib():
    """ebooklibをモック化するフィクスチャ"""
    with patch("ebooklib.epub.read_epub", autospec=True) as mock_read_epub:
        mock_book = MagicMock(spec=ebooklib_epub.EpubBook)
        mock_book.get_metadata.side_effect = [
            [("Test Title",)],
            [("Test Author",)],
            [("Test Publisher",)],
            [("2025-01-01T00:00:00Z",)],
        ]
        mock_doc_item = MagicMock()
        mock_doc_item.get_content.return_value = (
            "<html><body><img src='../images/test.jpg'/></body></html>"
        )
        mock_doc_item.get_name.return_value = "item1.xhtml"
        mock_img_item = MagicMock()
        mock_img_item.get_name.return_value = "images/test.jpg"
        mock_img_item.get_content.return_value = b"image_content"
        mock_book.get_items_of_type.side_effect = [
            [mock_img_item],  # ITEM_IMAGE
            [mock_doc_item],  # ITEM_DOCUMENT
        ]
        mock_read_epub.return_value = mock_book
        yield mock_read_epub


def test_download_blob():
    """download_blobがGCSからファイルをダウンロードすることをテストする"""
    with patch("epub.get_storage_client") as mock_get_client:
        mock_gcs_client = MagicMock()
        mock_blob = MagicMock()
        mock_bucket = MagicMock()
        mock_bucket.blob.return_value = mock_blob
        mock_gcs_client.bucket.return_value = mock_bucket
        mock_get_client.return_value = mock_gcs_client

        with patch("tempfile.mkstemp", return_value=(None, "/tmp/test.epub")):
            result = epub.download_blob("test-bucket", "test.epub")

            mock_gcs_client.bucket.assert_called_once_with("test-bucket")
            mock_bucket.blob.assert_called_once_with("test.epub")
            mock_blob.download_to_filename.assert_called_once_with("/tmp/test.epub")
            assert result == "/tmp/test.epub"


def test_upload_blob():
    """upload_blobがGCSにファイルをアップロードすることをテストする"""
    with patch("epub.get_storage_client") as mock_get_client:
        mock_gcs_client = MagicMock()
        mock_blob = MagicMock()
        mock_bucket = MagicMock()
        mock_bucket.blob.return_value = mock_blob
        mock_gcs_client.bucket.return_value = mock_bucket
        mock_get_client.return_value = mock_gcs_client

        result = epub.upload_blob("test-bucket", "/tmp/test.jpg", "images/test.jpg")

        mock_gcs_client.bucket.assert_called_once_with("test-bucket")
        mock_bucket.blob.assert_called_once_with("images/test.jpg")
        mock_blob.upload_from_filename.assert_called_once_with("/tmp/test.jpg")
        assert result == "gs://test-bucket/images/test.jpg"


def test_parse_epub(mock_ebooklib, mock_upload_blob):
    """parse_epubがEPUBを解析し、画像とHTMLチャンクをGCSにアップロードし、日付をパースすることをテストする"""
    # このテスト用に日付の戻り値を上書き
    mock_book = mock_ebooklib.return_value
    mock_book.get_metadata.side_effect = [
        [("Test Title",)],
        [("Test Author",)],
        [("Test Publisher",)],
        [("2025-01-15",)],  # YYYY-MM-DD 形式
    ]

    with (
        patch("builtins.open", MagicMock()),
        patch("tempfile.TemporaryDirectory", MagicMock()),
        patch("uuid.uuid4", return_value="test-uuid"),
    ):
        metadata, html_paths, image_paths = epub.parse_epub(
            "/path/to/fake.epub", "test-upload-bucket", "fake.epub"
        )

    # メタデータの検証
    assert metadata["title"] == "Test Title"
    assert metadata["published_date"] == datetime.datetime(2025, 1, 15)

    # 画像アップロードの検証
    assert len(image_paths) == 1
    mock_upload_blob.assert_any_call(
        bucket_name="test-upload-bucket",
        source_file_name=ANY,
        destination_blob_name="images/fake.epub/test.jpg",
    )
    assert image_paths[0] == "gs://test-upload-bucket/images/fake.epub/test.jpg"
    # HTMLチャンクアップロードの検証
    assert len(html_paths) == 1
    mock_upload_blob.assert_any_call(
        bucket_name="test-upload-bucket",
        source_file_name=ANY,
        destination_blob_name="html_chunks/fake.epub/item1.xhtml",
    )
    assert html_paths[0] == "gs://test-upload-bucket/html_chunks/fake.epub/item1.xhtml"


@pytest.mark.asyncio
async def test_handle_epub(mock_run_in_threadpool):
    """handle_epubがチャンクベースの処理フローを正しく呼び出すことをテストする"""
    with (
        patch("epub.download_blob") as mock_download,
        patch("epub.parse_epub") as mock_parse,
        patch(
            "epub.generate_summary_from_html_chunks", new_callable=AsyncMock
        ) as mock_summarize,
        patch("epub.save_to_spanner_for_epub_content") as mock_save,
        patch("os.path.exists", return_value=True),
        patch("os.remove") as mock_remove,
    ):
        # モックの戻り値を設定
        mock_download.return_value = "/tmp/fake.epub"
        mock_html_paths = ["gs://bucket/chunk1.html"]
        mock_image_paths = ["gs://bucket/image1.png"]
        mock_parse.return_value = ({}, mock_html_paths, mock_image_paths)
        mock_summarize.return_value = "summary"

        await epub.handle_epub("bucket", "path/file.epub", "file.epub", "gs://uri")

        # 呼び出し順序と内容を検証
        assert mock_run_in_threadpool.call_count == 3
        call1_args, _ = mock_run_in_threadpool.call_args_list[0]
        assert call1_args[0] == mock_download
        call2_args, _ = mock_run_in_threadpool.call_args_list[1]
        assert call2_args[0] == mock_parse
        mock_summarize.assert_awaited_once_with(mock_html_paths, mock_image_paths)
        call3_args, _ = mock_run_in_threadpool.call_args_list[2]
        assert call3_args[0] == mock_save
        assert call3_args[4] == mock_html_paths  # html_gcs_pathsが渡されているか
        mock_remove.assert_called_once_with("/tmp/fake.epub")


@pytest.mark.asyncio
async def test_generate_summary_from_html_chunks(
    mock_genai_client, mock_run_in_threadpool
):
    """generate_summary_from_html_chunksがMap-Reduceアプローチで動作することをテストする"""
    # このテストケース用のGeminiモックの戻り値を設定
    mock_genai_client.aio.models.generate_content.side_effect = [
        MagicMock(text="中間要約"),
        MagicMock(text="最終的な要約"),
    ]

    html_paths = ["gs://test-upload-bucket/chunk1.html"]
    image_paths = ["gs://path/to/image1.jpg"]

    # download_blobとopenをモック
    with (
        patch("epub.download_blob", return_value="/tmp/fake.html"),
        patch("builtins.open", mock_open(read_data="<html>chunk content</html>")),
        patch("os.path.exists", return_value=True),
        patch("os.remove"),
    ):
        summary = await epub.generate_summary_from_html_chunks(html_paths, image_paths)

        # Mapフェーズの検証
        assert mock_genai_client.aio.models.generate_content.await_count == 2
        _, map_kwargs = mock_genai_client.aio.models.generate_content.await_args_list[0]
        map_prompt = map_kwargs["contents"][0]
        assert "これは書籍の一部" in map_prompt
        assert "<html>chunk content</html>" in map_prompt

        # Reduceフェーズの検証
        _, reduce_kwargs = (
            mock_genai_client.aio.models.generate_content.await_args_list[1]
        )
        reduce_prompt = reduce_kwargs["contents"][0]
        assert "中間要約のリスト" in reduce_prompt
        assert "【章/セクションの要約 1】\n中間要約" in reduce_prompt
        assert "【利用可能な画像リスト】" in reduce_prompt
        assert "gs://path/to/image1.jpg" in reduce_prompt

        # 最終結果の検証
        assert summary == "最終的な要約"


@patch("epub.get_spanner_database")
def test_save_to_spanner_for_epub_content(mock_get_spanner_database):
    """save_to_spannerがHtmlChunksを正しく保存することをテストする"""
    metadata = {"title": "Test Title"}
    html_paths = ["gs://bucket/chunk1.html"]
    image_paths = ["gs://bucket/image.jpg"]
    mock_database = MagicMock()
    mock_transaction = MagicMock()
    mock_database.run_in_transaction.side_effect = lambda func: func(mock_transaction)
    mock_get_spanner_database.return_value = mock_database

    with patch("uuid.uuid4", return_value="test-uuid"):
        epub.save_to_spanner_for_epub_content(
            "file.epub", "gs://uri", metadata, html_paths, image_paths, "summary"
        )

        mock_transaction.insert.assert_called_once()
        _, kwargs = mock_transaction.insert.call_args

        # カラムの検証
        expected_columns = [
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
        ]
        assert kwargs["columns"] == expected_columns

        # 値の検証
        values = kwargs["values"][0]
        assert values[expected_columns.index("Id")] == "test-uuid"
        assert values[expected_columns.index("GcsUri")] == "gs://uri"
        assert values[expected_columns.index("HtmlChunks")] == json.dumps(html_paths)
        assert values[expected_columns.index("Images")] == json.dumps(image_paths)
        assert values[expected_columns.index("Summary")] == "summary"
        assert values[expected_columns.index("Title")] == "Test Title"


@pytest.mark.parametrize(
    "date_str, expected_date",
    [
        ("2025-01-15T10:30:00Z", datetime.datetime(2025, 1, 15, 10, 30, 0)),
        ("2024-12-20", datetime.datetime(2024, 12, 20)),
        ("2023-11", datetime.datetime(2023, 11, 1)),
        ("2022", datetime.datetime(2022, 1, 1)),
        ("invalid-date-string", None),
        ("", None),
        (None, None),
    ],
)
def test_parse_best_effort_date(date_str, expected_date):
    """_parse_best_effort_dateが様々な日付形式を正しくパースすることをテストする"""
    assert epub._parse_best_effort_date(date_str) == expected_date
