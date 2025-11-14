# PDF要約&インポート サービス

このプロジェクトは、Google Cloud Storage (GCS) にアップロードされたPDFファイルをトリガーとして、Gemini API を利用して内容を要約し、その結果を Cloud Spanner に保存する FastAPI アプリケーションです。
Eventarc を経由して GCS のイベントを Cloud Run 上のこのサービスに送信することを想定しています。

## 主な機能

-   **PDF要約**: Gemini API (gemini-2.5-pro) を使用して、PDFファイルの詳細な要約を生成します。
-   **データベース保存**: 生成した要約、ファイル名、GCS URI などの情報を Cloud Spanner に保存します。
-   **イベント駆動**: GCS へのファイルアップロードを Eventarc で検知し、非同期に処理を実行します。

## アーキテクチャ概要

1.  ユーザーが GCS バケットに PDF ファイルをアップロードします。
2.  Eventarc が `google.cloud.storage.object.v1.finalized` イベントを検知します。
3.  Eventarc は、Cloud Run でホストされているこの FastAPI アプリケーションのエンドポイントに、CloudEvents 形式でリクエストを送信します。
4.  FastAPI アプリケーションはリクエストを受け取り、PDF の GCS URI を取得します。
5.  Gemini API を呼び出し、PDF の内容を要約します。
6.  要約結果と関連情報を Cloud Spanner の `DocumentSummaries` テーブルに書き込みます。

## API仕様

### エンドポイント

-   `POST /`

### 想定されるリクエストボディ

このサービスは、Eventarc からの Cloud Storage イベントを CloudEvents 形式で受け取ることを想定しています。
リクエストボディには、少なくとも以下のキーを含む JSON オブジェクトが必要です。

```json
{
  "bucket": "your-gcs-bucket-name",
  "name": "path/to/your/file.pdf"
}
```

-   `bucket`: イベントが発生した GCS バケット名。
-   `name`: 作成または更新されたオブジェクト（ファイル）名。

## Cloud Spannerのテーブル定義

このサービスでは、要約結果を保存するために、以下のスキーマを持つ Cloud Spanner テーブルを想定しています。

-   **テーブル名**: `DocumentSummaries` （環境変数 `SPANNER_TABLE_NAME` で変更可能）

### DDL

```sql
CREATE TABLE DocumentSummaries (
  Id STRING(36) NOT NULL,
  GcsUri STRING(MAX),
  FileName STRING(MAX),
  Title STRING(MAX),
  Summary STRING(MAX),
  HtmlChunks JSON,
  Images JSON,
  Author STRING(MAX),
  Publisher STRING(MAX),
  PublishedDate TIMESTAMP,
  CreatedAt TIMESTAMP,
) PRIMARY KEY(Id);
```

## セットアップと実行

### 1. 環境変数の設定

このアプリケーションは、動作に必要な設定値を環境変数から読み込みます。
プロジェクトルートに `.env` ファイルを作成し、以下のキーを設定してください。

```dotenv
PROJECT_ID="your-gcp-project-id"
LOCATION="your-gcp-region"
SPANNER_INSTANCE_ID="your-spanner-instance-id"
SPANNER_DATABASE_ID="your-spanner-database-id"
SPANNER_TABLE_NAME="DocumentSummaries"
MODEL_NAME="gemini-2.5-flash"
UPLOAD_BUCKET_ID="your-gcs-bucket-name"
```

### 2. Docker を使用したローカル実行

`compose.yaml` を使用して、Docker コンテナとしてアプリケーションを起動できます。

```bash
# Dockerイメージをビルドしてコンテナを起動
docker compose up --build
```

アプリケーションは `http://localhost:8080` でリクエストを待ち受けます。

## テストの実行

このプロジェクトでは `pytest` を使用してテストを行います。
テストを実行する前に、開発用の依存関係をインストールする必要があります。

### 1. 依存関係のインストール

`uv` を使用して、必要なパッケージをインストールします。

```bash
# 開発用の依存関係を含むすべてのパッケージをインストール
uv pip install -e '.[dev]'
```

### 2. テストの実行

以下のコマンドでテストスイートを実行します。
`PYTHONPATH=.` を先頭に付けることで、プロジェクトルートを Python の検索パスに追加し、`main` モジュールが見つかるようにします。

```bash
PYTHONPATH=. uv run pytest
```

または

```bash
PYTHONPATH=. uv run python -m pytest
```

テストでは、`main.py` 内の `generate_summary_from_gcs` と `save_to_spanner` 関数はモック化されており、外部APIへの実際のリクエストは発生しません。
