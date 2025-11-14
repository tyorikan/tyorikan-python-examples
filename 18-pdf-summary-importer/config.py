import os
from functools import lru_cache

from google import genai
from google.cloud import spanner, storage
from google.cloud.spanner_v1.database import Database as SpannerDatabase

# --- 設定値の取得 ---
# @lru_cache(maxsize=None) を使うことで、各関数は初回呼び出し時のみ実行され、
# 結果がキャッシュされる（シングルトン的な振る舞い）。
# これにより、環境変数の読み込みやクライアントの初期化が一度しか行われないことを保証する。


@lru_cache(maxsize=None)
def get_project_id() -> str:
    project_id = os.getenv("PROJECT_ID")
    if not project_id:
        raise ValueError("環境変数 'PROJECT_ID' が設定されていません。")
    return project_id


@lru_cache(maxsize=None)
def get_location() -> str:
    return os.getenv("LOCATION", "us-central1")


@lru_cache(maxsize=None)
def get_spanner_instance_id() -> str:
    instance_id = os.getenv("SPANNER_INSTANCE_ID")
    if not instance_id:
        raise ValueError("環境変数 'SPANNER_INSTANCE_ID' が設定されていません。")
    return instance_id


@lru_cache(maxsize=None)
def get_spanner_database_id() -> str:
    db_id = os.getenv("SPANNER_DATABASE_ID")
    if not db_id:
        raise ValueError("環境変数 'SPANNER_DATABASE_ID' が設定されていません。")
    return db_id


@lru_cache(maxsize=None)
def get_spanner_table_name() -> str:
    table_name = os.getenv("SPANNER_TABLE_NAME")
    if not table_name:
        raise ValueError("環境変数 'SPANNER_TABLE_NAME' が設定されていません。")
    return table_name


@lru_cache(maxsize=None)
def get_upload_bucket_id() -> str:
    bucket_id = os.getenv("UPLOAD_BUCKET_ID")
    if not bucket_id:
        raise ValueError("環境変数 'UPLOAD_BUCKET_ID' が設定されていません。")
    return bucket_id


@lru_cache(maxsize=None)
def get_model_name() -> str:
    return os.getenv("MODEL_NAME", "gemini-2.5-pro")


# --- クライアントの取得 ---


@lru_cache(maxsize=None)
def get_genai_client() -> genai.Client:
    return genai.Client(
        vertexai=True, project=get_project_id(), location=get_location()
    )


@lru_cache(maxsize=None)
def get_spanner_database() -> SpannerDatabase:
    spanner_client = spanner.Client(project=get_project_id())
    instance = spanner_client.instance(get_spanner_instance_id())
    return instance.database(get_spanner_database_id())


@lru_cache(maxsize=None)
def get_storage_client() -> storage.Client:
    return storage.Client()
