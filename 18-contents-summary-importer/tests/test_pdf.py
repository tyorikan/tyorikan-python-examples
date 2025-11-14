# `pdf` をインポートする前に環境変数を設定
from unittest.mock import AsyncMock, MagicMock, patch

# `pdf` モジュールをインポート
import pdf
import pytest


@pytest.fixture(autouse=True)
def set_env_vars(monkeypatch):
    """テスト用の環境変数を設定する"""
    monkeypatch.setenv("PROJECT_ID", "test-project")
    monkeypatch.setenv("SPANNER_INSTANCE_ID", "test-instance")
    monkeypatch.setenv("SPANNER_DATABASE_ID", "test-database")
    monkeypatch.setenv("SPANNER_TABLE_NAME", "test-table")
    monkeypatch.setenv("MODEL_NAME", "test-model")


@pytest.fixture
def mock_run_in_threadpool():
    """fastapi.concurrency.run_in_threadpoolをモック化するフィクスチャ"""

    async def side_effect(func, *args, **kwargs):
        # run_in_threadpoolは非同期関数ではないので、単純に呼び出す
        return func(*args, **kwargs)

    with patch("pdf.run_in_threadpool", new_callable=AsyncMock) as mock:
        mock.side_effect = side_effect
        yield mock


@pytest.fixture
def mock_generate_summary_from_pdf():
    """`pdf.generate_summary_from_pdf`をモック化するフィクスチャ"""
    with patch("pdf.generate_summary_from_pdf", new_callable=AsyncMock) as mock_func:
        mock_func.return_value = "これはテスト用のPDF要約です。"
        yield mock_func


@pytest.fixture
def mock_save_to_spanner_for_pdf_summary():
    """`pdf.save_to_spanner_for_pdf_summary`をモック化するフィクスチャ"""
    with patch("pdf.save_to_spanner_for_pdf_summary") as mock_func:
        yield mock_func


@pytest.mark.asyncio
async def test_handle_pdf(
    mock_generate_summary_from_pdf,
    mock_save_to_spanner_for_pdf_summary,
    mock_run_in_threadpool,
):
    """handle_pdfが内部関数を正しく呼び出すことをテストする"""
    gcs_uri = "gs://test-bucket/test.pdf"
    file_name = "test.pdf"

    await pdf.handle_pdf(gcs_uri, file_name)

    # generate_summary_from_pdfが正しい引数で呼び出されたか
    mock_generate_summary_from_pdf.assert_awaited_once_with(gcs_uri)

    # run_in_threadpoolがsave_to_spanner_for_pdf_summaryを正しい引数で呼び出したか
    mock_run_in_threadpool.assert_awaited_once()
    args, _ = mock_run_in_threadpool.call_args
    assert args[0] == mock_save_to_spanner_for_pdf_summary
    assert args[1] == file_name
    assert args[2] == gcs_uri
    assert args[3] == "これはテスト用のPDF要約です。"


@pytest.mark.asyncio
async def test_generate_summary_from_pdf():
    """generate_summary_from_pdfがGeminiクライアントを正しく呼び出すことをテストする"""
    gcs_uri = "gs://test-bucket/test.pdf"
    expected_summary = "Geminiからの要約"

    # Geminiクライアントのモックを作成
    mock_genai_client = MagicMock()
    mock_genai_client.aio.models.generate_content = AsyncMock(
        return_value=MagicMock(text=expected_summary)
    )

    with patch("pdf.get_genai_client", return_value=mock_genai_client):
        summary = await pdf.generate_summary_from_pdf(gcs_uri)

        # generate_contentが呼び出されたか
        mock_genai_client.aio.models.generate_content.assert_awaited_once()
        # 戻り値が正しいか
        assert summary == expected_summary


@patch("pdf.get_spanner_database")
def test_save_to_spanner_for_pdf_summary(mock_get_spanner_database):
    """save_to_spanner_for_pdf_summaryがSpannerクライアントを正しく呼び出すことをテストする"""
    file_name = "test.pdf"
    gcs_uri = "gs://test-bucket/test.pdf"
    summary = "テスト要約"

    # Spannerデータベースとトランザクションのモックを作成
    mock_database = MagicMock()
    mock_transaction = MagicMock()

    # run_in_transactionに渡される関数をキャプチャし、
    # モックのトランザクションオブジェクトを渡して実行する
    def side_effect(func, *args, **kwargs):
        return func(mock_transaction, *args, **kwargs)

    mock_database.run_in_transaction.side_effect = side_effect
    mock_get_spanner_database.return_value = mock_database

    with patch("uuid.uuid4", return_value="test-uuid"):
        pdf.save_to_spanner_for_pdf_summary(file_name, gcs_uri, summary)

        # run_in_transactionが呼び出されたか
        mock_database.run_in_transaction.assert_called_once()
        # insertが正しい引数で呼び出されたか
        mock_transaction.insert.assert_called_once()
        _, kwargs = mock_transaction.insert.call_args
        assert kwargs["table"] == "test-table"
        assert "Id" in kwargs["columns"]
        assert "GcsUri" in kwargs["columns"]
        assert "FileName" in kwargs["columns"]
        assert "Summary" in kwargs["columns"]
        assert "CreatedAt" in kwargs["columns"]
        assert kwargs["values"][0][0] == "test-uuid"
        assert kwargs["values"][0][1] == gcs_uri
        assert kwargs["values"][0][2] == file_name
        assert kwargs["values"][0][3] == summary
