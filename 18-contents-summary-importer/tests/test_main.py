# `main` をインポートする前に環境変数を設定
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.fixture(autouse=True)
def set_env_vars(monkeypatch):
    """テスト用の環境変数を設定する"""
    monkeypatch.setenv("PROJECT_ID", "test-project")
    monkeypatch.setenv("SPANNER_INSTANCE_ID", "test-instance")
    monkeypatch.setenv("SPANNER_DATABASE_ID", "test-database")
    monkeypatch.setenv("SPANNER_TABLE_NAME", "test-table")
    monkeypatch.setenv("MODEL_NAME", "test-model")
    monkeypatch.setenv("UPLOAD_BUCKET_ID", "test-upload-bucket")


client = TestClient(app)


# --- Fixtures for PDF processing ---
@pytest.fixture
def mock_generate_summary_from_pdf():
    """`pdf.generate_summary_from_pdf`関数をモック化するフィクスチャ"""
    with patch("pdf.generate_summary_from_pdf") as mock:
        mock.return_value = "これはテスト用のPDF要約です。"
        yield mock


@pytest.fixture
def mock_save_to_spanner_for_pdf_summary():
    """`pdf.save_to_spanner_for_pdf_summary`関数をモック化するフィクスチャ"""
    with patch("pdf.save_to_spanner_for_pdf_summary") as mock:
        yield mock


# --- Fixtures for EPUB processing ---
@pytest.fixture
def mock_download_blob():
    """`epub.download_blob`関数をモック化するフィクスチャ"""
    with patch("epub.download_blob") as mock:
        mock.return_value = "/tmp/fake_epub_path.epub"
        yield mock


@pytest.fixture
def mock_parse_epub():
    """`epub.parse_epub`関数をモック化するフィクスチャ"""
    with patch("epub.parse_epub") as mock:
        mock.return_value = (
            {
                "title": "Test Title",
                "author": "Test Author",
                "publisher": "Test Publisher",
                "published_date": None,
            },
            ["gs://test-upload-bucket/html_chunks/test.html"],  # html_gcs_paths
            ["gs://test-upload-bucket/images/test.jpg"],  # image_gcs_paths
        )
        yield mock


@pytest.fixture
def mock_generate_summary_from_html_chunks():
    """`epub.generate_summary_from_html_chunks`関数をモック化するフィクスチャ"""
    with patch("epub.generate_summary_from_html_chunks") as mock:
        mock.return_value = "これはEPUBのテスト要約です。![画像](gs://test-upload-bucket/images/test.jpg)"
        yield mock


@pytest.fixture
def mock_save_to_spanner_for_epub_content():
    """`epub.save_to_spanner_for_epub_content`関数をモック化するフィクスチャ"""
    with patch("epub.save_to_spanner_for_epub_content") as mock:
        yield mock


@pytest.fixture
def mock_os_utils():
    """`os.remove`と`os.path.exists`をモック化するフィクスチャ"""
    with (
        patch("os.remove") as mock_remove,
        patch("os.path.exists", return_value=True) as mock_exists,
    ):
        yield mock_remove, mock_exists


# --- Test Cases ---


def test_process_storage_event_pdf_success(
    mock_generate_summary_from_pdf, mock_save_to_spanner_for_pdf_summary
):
    """正常系: PDFファイルが正常に処理されることのテスト"""
    event_data = {"bucket": "test-bucket", "name": "path/to/test-file.pdf"}
    response = client.post("/", json=event_data)

    assert response.status_code == 200
    assert response.json() == {"message": "処理が正常に完了しました。"}

    expected_gcs_uri = "gs://test-bucket/path/to/test-file.pdf"
    mock_generate_summary_from_pdf.assert_called_once_with(expected_gcs_uri)
    mock_save_to_spanner_for_pdf_summary.assert_called_once_with(
        "test-file.pdf", expected_gcs_uri, "これはテスト用のPDF要約です。"
    )


def test_process_storage_event_epub_success(
    mock_download_blob,
    mock_parse_epub,
    mock_generate_summary_from_html_chunks,
    mock_save_to_spanner_for_epub_content,
    mock_os_utils,
):
    """正常系: EPUBファイルが正常に処理されることのテスト"""
    mock_remove, _ = mock_os_utils
    event_data = {"bucket": "test-bucket", "name": "path/to/test-file.epub"}

    response = client.post("/", json=event_data)

    assert response.status_code == 200
    assert response.json() == {"message": "処理が正常に完了しました。"}

    # 各モックが期待通りに呼び出されたか検証
    mock_download_blob.assert_called_once_with("test-bucket", "path/to/test-file.epub")
    mock_parse_epub.assert_called_once_with(
        "/tmp/fake_epub_path.epub", "test-upload-bucket", "test-file.epub"
    )

    (
        expected_metadata,
        expected_html_paths,
        expected_images,
    ) = mock_parse_epub.return_value
    mock_generate_summary_from_html_chunks.assert_called_once_with(
        expected_html_paths, expected_images
    )

    expected_summary = mock_generate_summary_from_html_chunks.return_value
    mock_save_to_spanner_for_epub_content.assert_called_once_with(
        "test-file.epub",
        "gs://test-bucket/path/to/test-file.epub",
        expected_metadata,
        expected_html_paths,
        expected_images,
        expected_summary,
    )
    mock_remove.assert_called_once_with("/tmp/fake_epub_path.epub")


def test_process_storage_event_unsupported_file():
    """正常系: サポートされていないファイル形式の場合のテスト"""
    event_data = {"bucket": "test-bucket", "name": "path/to/test-file.txt"}
    response = client.post("/", json=event_data)
    assert response.status_code == 200
    assert response.json() == {"message": "サポートされていないファイル形式です。"}


def test_process_storage_event_missing_payload():
    """異常系: リクエストボディが不正な場合のテスト"""
    response = client.post("/", json={})
    assert response.status_code == 400


def test_process_storage_event_pdf_generation_fails(mock_generate_summary_from_pdf):
    """異常系: PDF要約生成で例外が発生した場合のテスト"""
    # `pdf.handle_pdf`内で呼び出される`generate_summary_from_pdf`が例外を発生させる
    mock_generate_summary_from_pdf.side_effect = Exception("Gemini API error")
    event_data = {"bucket": "test-bucket", "name": "path/to/test-file.pdf"}
    response = client.post("/", json=event_data)
    assert response.status_code == 500
    assert "サーバー内部でエラーが発生しました。" in response.json()["detail"]


def test_process_storage_event_epub_summary_fails(
    mock_download_blob, mock_parse_epub, mock_generate_summary_from_html_chunks
):
    """異常系: EPUB要約生成で例外が発生した場合のテスト"""
    # `epub.handle_epub`内で呼び出される`generate_summary_from_html_chunks`が例外を発生させる
    mock_generate_summary_from_html_chunks.side_effect = Exception("Gemini API error")
    event_data = {"bucket": "test-bucket", "name": "path/to/test-file.epub"}
    response = client.post("/", json=event_data)
    assert response.status_code == 500
    assert "サーバー内部でエラーが発生しました。" in response.json()["detail"]


def test_process_storage_event_spanner_save_fails_for_pdf(
    mock_generate_summary_from_pdf, mock_save_to_spanner_for_pdf_summary
):
    """異常系: PDFのSpannerへの保存で例外が発生した場合のテスト"""
    # `pdf.handle_pdf`内で呼び出される`save_to_spanner_for_pdf_summary`が例外を発生させる
    mock_save_to_spanner_for_pdf_summary.side_effect = Exception(
        "Spanner connection error"
    )
    event_data = {"bucket": "test-bucket", "name": "path/to/test-file.pdf"}
    response = client.post("/", json=event_data)
    assert response.status_code == 500
    assert "サーバー内部でエラーが発生しました。" in response.json()["detail"]
