# `main` をインポートする前に環境変数を設定
import os
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

os.environ["PROJECT_ID"] = "test-project"
os.environ["SPANNER_INSTANCE_ID"] = "test-instance"
os.environ["SPANNER_DATABASE_ID"] = "test-database"
os.environ["SPANNER_TABLE_NAME"] = "test-table"
os.environ["MODEL_NAME"] = "test-model"

from main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def set_env_vars(monkeypatch):
    monkeypatch.setenv("PROJECT_ID", "test-project")
    monkeypatch.setenv("SPANNER_INSTANCE_ID", "test-instance")
    monkeypatch.setenv("SPANNER_DATABASE_ID", "test-database")
    monkeypatch.setenv("SPANNER_TABLE_NAME", "test-table")
    monkeypatch.setenv("MODEL_NAME", "test-model")


@pytest.fixture
def mock_generate_summary():
    """`generate_summary_from_gcs`関数をモック化するフィクスチャ"""
    with patch("main.generate_summary_from_gcs") as mock:
        mock.return_value = "これはテスト用の要約です。"
        yield mock


@pytest.fixture
def mock_save_to_spanner():
    """`save_to_spanner`関数をモック化するフィクスチャ"""
    with patch("main.save_to_spanner") as mock:
        yield mock


def test_process_storage_event_success(mock_generate_summary, mock_save_to_spanner):
    """正常なEventarcイベントを受信した場合のテスト"""
    # Given: Eventarcからの正常なリクエストボディ
    event_data = {"bucket": "test-bucket", "name": "path/to/test-file.pdf"}

    # When: エンドポイントにPOSTリクエストを送信
    response = client.post("/", json=event_data)

    # Then: 正常なレスポンスが返されることを確認
    assert response.status_code == 200
    assert response.json() == {"message": "処理が正常に完了しました。"}

    # Then: モック関数が期待通りに呼び出されたことを確認
    expected_gcs_uri = "gs://test-bucket/path/to/test-file.pdf"
    mock_generate_summary.assert_called_once_with(expected_gcs_uri)
    mock_save_to_spanner.assert_called_once_with(
        "test-file.pdf", expected_gcs_uri, "これはテスト用の要約です。"
    )


def test_process_storage_event_missing_payload():
    """リクエストボディが空のJSONの場合のテスト"""
    # When: 空のJSONでPOSTリクエストを送信
    response = client.post("/", json={})

    # Then: 400エラーが返されることを確認
    assert response.status_code == 400
    assert (
        "リクエストのJSONペイロードに 'bucket' または 'name' キーが含まれていません。"
        in response.json()["detail"]
    )


def test_process_storage_event_missing_key():
    """リクエストボディのキーが不足している場合のテスト"""
    # Given: 'name' キーが不足しているリクエストボディ
    event_data = {"bucket": "test-bucket"}

    # When: エンドポイントにPOSTリクエストを送信
    response = client.post("/", json=event_data)

    # Then: 400エラーが返されることを確認
    assert response.status_code == 400
    assert (
        "リクエストのJSONペイロードに 'bucket' または 'name' キーが含まれていません。"
        in response.json()["detail"]
    )


def test_process_storage_event_summary_generation_fails(mock_generate_summary):
    """要約生成で例外が発生した場合のテスト"""
    # Given: `generate_summary_from_gcs` が例外を発生させる
    mock_generate_summary.side_effect = Exception("Gemini API error")
    event_data = {"bucket": "test-bucket", "name": "path/to/test-file.pdf"}

    # When: エンドポイントにPOSTリクエストを送信
    response = client.post("/", json=event_data)

    # Then: 500エラーが返されることを確認
    assert response.status_code == 500
    assert (
        "サーバー内部でエラーが発生しました。"
        in response.json()["detail"]
    )


def test_process_storage_event_spanner_save_fails(
    mock_generate_summary, mock_save_to_spanner
):
    """Spannerへの保存で例外が発生した場合のテスト"""
    # Given: `save_to_spanner` が例外を発生させる
    mock_save_to_spanner.side_effect = Exception("Spanner connection error")
    event_data = {"bucket": "test-bucket", "name": "path/to/test-file.pdf"}

    # When: エンドポイントにPOSTリクエストを送信
    response = client.post("/", json=event_data)

    # Then: 500エラーが返されることを確認
    assert response.status_code == 500
    assert (
        "サーバー内部でエラーが発生しました。"
        in response.json()["detail"]
    )
