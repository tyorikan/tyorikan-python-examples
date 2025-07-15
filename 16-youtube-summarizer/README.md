# YouTube動画要約＆英語学習アプリケーション

このアプリケーションは、指定されたYouTube動画のトランスクリプト（字幕）を取得し、Vertex AI の生成AIモデル（Gemini）を利用して動画の内容を要約し、さらに英語学習者向けのコンテンツ（重要な英単語や文法）を生成するWebアプリケーションです。

## 主な機能

- **動画の要約:** YouTube動画のURLを入力すると、動画全体の概要を日本語で生成します。
- **英語学習コンテンツの生成:** 動画の内容に基づき、キーとなる英単語や文法ルールを例文付きで解説します。

## アーキテクチャ

```mermaid
graph TD
    subgraph "ユーザーのブラウザ"
        A[Frontend (HTML/JS)]
    end

    subgraph "バックエンドサーバー (FastAPI)"
        B[Web Server]
    end

    subgraph "外部サービス"
        C[YouTube Transcript API]
        D[Vertex AI (Gemini API)]
    end

    A -- "1. 要約リクエスト (URL)" --> B
    B -- "2. 字幕取得リクエスト" --> C
    C -- "3. 字幕テキスト" --> B
    B -- "4. 要約生成リクエスト (プロンプト)" --> D
    D -- "5. 要約テキスト (Stream)" --> B
    B -- "6. 要約テキスト (Stream)" --> A
```

## 必要なもの

- Python 3.8 以降
- Google Cloud プロジェクト
- 上記プロジェクトで有効化された Vertex AI API

## セットアップと実行方法

1.  **リポジトリのクローン:**

    ```bash
    git clone https://github.com/tyorikan/python-examples.git
    cd python-examples/16-youtube-summarizer
    ```

2.  **Python仮想環境の作成と有効化:**

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **必要なライブラリのインストール:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **環境変数の設定:**

    プロジェクトのルートに `.env` ファイルを作成し、以下の内容を記述します。ご自身のGoogle Cloud プロジェクトIDとロケーションに置き換えてください。

    ```
    PROJECT_ID="your-gcp-project-id"
    LOCATION="your-gcp-location" # 例: us-central1
    ```

5.  **アプリケーションの起動:**

    `src` ディレクトリから `uvicorn` を使ってサーバーを起動します。

    ```bash
    uvicorn src.main:app --reload
    ```

6.  **アクセス:**

    Webブラウザで `http://127.0.0.1:8080` にアクセスします。

## 使い方

1.  Webページの入力欄に、要約したいYouTube動画のURLを貼り付けます。
2.  「Summarize」ボタンをクリックします。
3.  処理が開始され、生成された要約と英語学習コンテンツがリアルタイムで表示されます。