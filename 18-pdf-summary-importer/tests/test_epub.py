# `epub` をインポートする前に環境変数を設定
import datetime
import json
from unittest.mock import AsyncMock, MagicMock, patch

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
        # run_in_threadpoolは非同期関数ではないので、単純に呼び出す
        return func(*args, **kwargs)

    with patch("epub.run_in_threadpool", new_callable=AsyncMock) as mock:
        mock.side_effect = side_effect
        yield mock


@pytest.fixture
def mock_storage_client():
    """GCSクライアントをモック化するフィクスチャ"""
    with patch("epub.get_storage_client") as mock_get_client:
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        yield mock_client


# --- Spanner関連のFixtures ---


# --- Gemini関連のFixtures ---
@pytest.fixture
def mock_genai_client():
    """Geminiクライアントをモック化するフィクスチャ"""
    with patch("epub.get_genai_client") as mock_get_client:
        mock_client = MagicMock()
        # generate_content を AsyncMock に設定
        mock_client.aio.models.generate_content = AsyncMock(
            return_value=MagicMock(text="GeminiからのEPUB要約")
        )
        mock_get_client.return_value = mock_client
        yield mock_client


# --- Ebooklib関連のFixtures ---
@pytest.fixture
def mock_ebooklib():
    """ebooklibをモック化するフィクスチャ"""
    with patch("ebooklib.epub.read_epub", autospec=True) as mock_read_epub:
        mock_book = MagicMock(spec=ebooklib_epub.EpubBook)
        # メタデータの設定
        mock_book.get_metadata.side_effect = [
            [("Test Title",)],  # title
            [("Test Author",)],  # creator
            [("Test Publisher",)],  # publisher
            [("2025-01-01T00:00:00Z",)],  # date
        ]
        # アイテムの設定 (ドキュメントと画像)
        mock_doc_item = MagicMock()
        mock_doc_item.get_content.return_value = (
            "<html><body><img src='images/test.jpg'/></body></html>"
        )
        mock_img_item = MagicMock()
        mock_img_item.get_name.return_value = "images/test.jpg"
        mock_img_item.get_content.return_value = b"image_content"
        mock_book.get_items_of_type.side_effect = [
            [mock_img_item],  # ITEM_IMAGE
            [mock_doc_item],  # ITEM_DOCUMENT
        ]
        mock_read_epub.return_value = mock_book
        yield mock_read_epub


# --- テストケース ---


def test_download_blob(mock_storage_client):
    """download_blobがGCSからファイルをダウンロードすることをテストする"""
    mock_blob = MagicMock()
    mock_bucket = MagicMock()
    mock_bucket.blob.return_value = mock_blob
    mock_storage_client.bucket.return_value = mock_bucket

    with patch("tempfile.mkstemp", return_value=(None, "/tmp/test.epub")):
        result = epub.download_blob("test-bucket", "test.epub")

        mock_storage_client.bucket.assert_called_once_with("test-bucket")
        mock_bucket.blob.assert_called_once_with("test.epub")
        mock_blob.download_to_filename.assert_called_once_with("/tmp/test.epub")
        assert result == "/tmp/test.epub"


def test_upload_blob(mock_storage_client):
    """upload_blobがGCSにファイルをアップロードすることをテストする"""
    mock_blob = MagicMock()
    mock_bucket = MagicMock()
    mock_bucket.blob.return_value = mock_blob
    mock_storage_client.bucket.return_value = mock_bucket

    result = epub.upload_blob("test-bucket", "/tmp/test.jpg", "images/test.jpg")

    mock_storage_client.bucket.assert_called_once_with("test-bucket")
    mock_bucket.blob.assert_called_once_with("images/test.jpg")
    mock_blob.upload_from_filename.assert_called_once_with("/tmp/test.jpg")
    assert result == "gs://test-bucket/images/test.jpg"


def test_parse_epub(mock_ebooklib, mock_storage_client):
    """parse_epubがEPUBを解析し、画像をアップロードし、コンテンツを返すことをテストする"""
    with (
        patch("builtins.open", MagicMock()),
        patch("tempfile.TemporaryDirectory", MagicMock()),
    ):
        metadata, content, image_paths = epub.parse_epub(
            "/path/to/fake.epub", "test-upload-bucket", "fake.epub"
        )

    # メタデータの検証
    assert metadata["title"] == "Test Title"
    assert metadata["author"] == "Test Author"
    # 画像アップロードの検証
    assert len(image_paths) == 1
    assert "gs://test-upload-bucket/images/fake.epub/test.jpg" in image_paths[0]
    # コンテンツの検証 (画像パスが置換されているか)
    assert 'src="gs://test-upload-bucket/images/fake.epub/test.jpg' in content


@pytest.mark.asyncio
async def test_handle_epub(mock_run_in_threadpool):
    """handle_epubが内部のヘルパー関数を正しい順序で呼び出すことをテストする"""
    # 各ヘルパー関数をモック化
    with (
        patch("epub.download_blob") as mock_download,
        patch("epub.parse_epub") as mock_parse,
        patch(
            "epub.generate_summary_from_epub_content", new_callable=AsyncMock
        ) as mock_summarize,
        patch("epub.save_to_spanner_for_epub_content") as mock_save,
        patch("os.path.exists", return_value=True),
        patch("os.remove") as mock_remove,
    ):
        # モックの戻り値を設定
        mock_download.return_value = "/tmp/fake.epub"
        mock_parse.return_value = ({}, "content", ["image_path"])
        mock_summarize.return_value = "summary"

        # handle_epubを呼び出し
        await epub.handle_epub("bucket", "path/file.epub", "file.epub", "gs://uri")

        # 各関数がrun_in_threadpool経由で呼び出されたか検証
        # (呼び出し順序と引数を厳密にチェック)
        assert mock_run_in_threadpool.call_count == 3
        # 1. download_blob
        call1_args, _ = mock_run_in_threadpool.call_args_list[0]
        assert call1_args[0] == mock_download
        # 2. parse_epub
        call2_args, _ = mock_run_in_threadpool.call_args_list[1]
        assert call2_args[0] == mock_parse
        # 3. save_to_spanner
        call3_args, _ = mock_run_in_threadpool.call_args_list[2]
        assert call3_args[0] == mock_save

        # summarizeが直接呼び出されたか
        mock_summarize.assert_awaited_once_with("content", ["image_path"])
        # 一時ファイルが削除されたか
        mock_remove.assert_called_once_with("/tmp/fake.epub")


@pytest.mark.asyncio
async def test_generate_summary_from_epub_content(mock_genai_client):
    """generate_summary_from_epub_contentが正しいプロンプトでGeminiを呼び出すことをテストする"""
    content = "<html>test</html>"
    image_paths = ["gs://path/to/image1.jpg", "gs://path/to/image2.jpg"]

    summary = await epub.generate_summary_from_epub_content(content, image_paths)

    mock_genai_client.aio.models.generate_content.assert_awaited_once()
    _, kwargs = mock_genai_client.aio.models.generate_content.call_args
    prompt = kwargs["contents"][0]

    # プロンプトの内容を検証
    assert "【HTMLコンテンツ】" in prompt
    assert "<html>test</html>" in prompt
    assert "【利用可能な画像リスト】" in prompt
    assert "gs://path/to/image1.jpg" in prompt
    assert "gs://path/to/image2.jpg" in prompt
    assert summary == "GeminiからのEPUB要約"


@patch("epub.get_spanner_database")
def test_save_to_spanner_for_epub_content(mock_get_spanner_database):
    """save_to_spanner_for_epub_contentがSpannerに正しくデータを保存することをテストする"""
    metadata = {
        "title": "Test Title",
        "author": "Test Author",
        "publisher": "Test Publisher",
        "published_date": datetime.datetime(2025, 1, 1),
    }
    image_paths = ["gs://path/to/image.jpg"]
    mock_database = MagicMock()
    mock_transaction = MagicMock()

    def side_effect(func, *args, **kwargs):
        return func(mock_transaction, *args, **kwargs)

    mock_database.run_in_transaction.side_effect = side_effect
    mock_get_spanner_database.return_value = mock_database

    with patch("uuid.uuid4", return_value="test-epub-uuid"):
        epub.save_to_spanner_for_epub_content(
            "file.epub", "gs://uri", metadata, "content", image_paths, "summary"
        )

        mock_database.run_in_transaction.assert_called_once()
        mock_transaction.insert.assert_called_once()
        _, kwargs = mock_transaction.insert.call_args
        assert kwargs["table"] == "test-table"
        assert kwargs["values"][0][0] == "test-epub-uuid"
        assert kwargs["values"][0][1] == "gs://uri"
        assert kwargs["values"][0][6] == "Test Title"
        assert json.loads(kwargs["values"][0][4]) == image_paths
