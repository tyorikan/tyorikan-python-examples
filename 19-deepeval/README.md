# ADK Agent with DeepEval (Gemini Judge版)

このプロジェクトは、Google の [Agent Development Kit (ADK)](https://google.github.io/adk-docs/) を使って AI エージェントを構築し、[DeepEval](https://deepeval.com/) を使った Evaluation-Driven Development（評価駆動開発）を実践するサンプルコードです。

**特徴**: DeepEval の評価 Judge として **Gemini (Vertex AI)** を使用しています。OpenAI API は不要です。

## 前提条件

- Python 3.10+
- Google Cloud Project（Vertex AI の Gemini API が有効になっていること）
- GCP の認証設定（Application Default Credentials または サービスアカウントキー）

## セットアップ

### 1. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

インストールされる主要なパッケージ:
- `google-adk>=1.19.0` - Google Agent Development Kit
- `deepeval>=3.7.2` - LLM 評価フレームワーク
- `python-dotenv>=1.2.1` - 環境変数管理

### 2. 環境変数の設定

`my_agent/env.example` を `my_agent/.env` にコピーして、あなたの GCP プロジェクト情報を設定してください。

```bash
cp my_agent/env.example my_agent/.env
```

`.env` ファイルの内容:
```bash
GOOGLE_GENAI_USE_VERTEXAI=1
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
GOOGLE_CLOUD_LOCATION=your-gcp-location  # 例: us-central1, asia-northeast1
```

- `GOOGLE_GENAI_USE_VERTEXAI`: Vertex AI を使用するためのフラグ（必須）
- `GOOGLE_CLOUD_PROJECT`: あなたの GCP プロジェクト ID
- `GOOGLE_CLOUD_LOCATION`: Vertex AI を使用するリージョン

### 3. GCP 認証の設定

以下のいずれかの方法で GCP の認証を設定してください:

```bash
# Application Default Credentials を使う場合
gcloud auth application-default login

# または、サービスアカウントキーを使う場合
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
```

## プロジェクト構成

```
19-deepeval/
├── my_agent/
│   ├── agent.py          # ADK エージェントの実装
│   ├── .env              # 環境変数（gitignore対象）
│   └── env.example       # 環境変数のサンプル
├── tests/
│   └── test_agent.py     # DeepEval によるテストコード
└── requirements.txt      # 依存パッケージ
```

### `my_agent/agent.py`

ADK を使ったエージェントの実装です。

- **Agent**: `root_agent` という名前のエージェントを定義
- **Model**: `gemini-2.5-flash` を使用（コスト効率の良いモデル）
- **Tool**: `get_current_time(city: str)` という関数を Tool として登録
  - 指定された都市の現在時刻を返す（モック実装）

### `tests/test_agent.py`

DeepEval を使った評価テストです。

- **`query_agent(text: str)`**: エージェントにクエリを送信して応答を取得するヘルパー関数
  - `InMemoryRunner` を使用してエージェントを実行
  - 非同期処理を `asyncio.run()` でラップ
- **`test_time_query()`**: テスト関数
  - エージェントに「What time is it in Tokyo?」と質問
  - Gemini Judge (`GeminiModel`) を使って応答の正確性を評価
  - `GEval` メトリクスで評価基準とスコアリングを実施

## 使い方

### テストの実行

DeepEval でテストを実行します:

```bash
# DeepEval コマンドで実行
deepeval test run tests/test_agent.py

# または pytest で直接実行
pytest tests/test_agent.py

# 単独でテストファイルを実行することも可能
python tests/test_agent.py
```

テストが成功すると、以下のような出力が表示されます:
- エージェントの応答内容
- デバッグ情報（環境変数の確認）
- 評価メトリクスのスコアと結果

## 仕組み

このプロジェクトは、以下の流れで動作します:

1. **Agent の定義** (`agent.py`)
   - ADK の `Agent` クラスでエージェントを作成
   - Gemini 2.5 Flash モデルを使用
   - `get_current_time` tool を登録

2. **Agent の実行** (`test_agent.py` の `query_agent()`)
   - `InMemoryRunner` でエージェントを軽量に実行
   - `run_debug()` メソッドでイベントのリストを取得
   - イベントから最終的な応答テキストを抽出

3. **テストケースの定義**
   - `LLMTestCase` で入力・実際の出力・期待する出力を定義
   - 入力: 「What time is it in Tokyo?」
   - 期待する出力: 「The current time in Tokyo is 10:30 AM.」

4. **評価 (Evaluation)**
   - **Judge**: `GeminiModel` (Vertex AI の Gemini 2.5 Flash)
   - **Metric**: `GEval` - LLM ベースの評価メトリクス
   - **評価基準**: 実際の出力に正しい時刻と都市が含まれているか
   - **閾値**: 0.5（スコアがこれ以上なら合格）

5. **アサーション**
   - `assert_test()` でテストケースとメトリクスを実行
   - 評価スコアが閾値を超えていればテスト成功

## Eval-Driven Development (評価駆動開発) のメリット

このアプローチには以下のメリットがあります:

- **自動化された品質評価**: LLM の出力品質を継続的に測定できる
- **リグレッション防止**: コード変更時に既存の品質が維持されているか確認できる
- **Gemini Judge の活用**: OpenAI に依存せず、Google のエコシステム内で完結
- **素早いフィードバック**: pytest / DeepEval で CI/CD パイプラインに組み込める

## トラブルシューティング

### 認証エラーが出る場合

```bash
gcloud auth application-default login
```

を実行して、Application Default Credentials を設定してください。

### Vertex AI API が有効になっていない場合

GCP コンソールで Vertex AI API を有効にしてください:

```bash
gcloud services enable aiplatform.googleapis.com
```

### リージョンエラーが出る場合

`.env` ファイルの `GOOGLE_CLOUD_LOCATION` が正しいか確認してください。Gemini が利用可能なリージョンは限られています（例: `us-central1`, `asia-northeast1` など）。

## 参考資料

- [Google ADK Documentation](https://google.github.io/adk-docs/)
- [DeepEval Documentation](https://docs.confident-ai.com/)
- [Vertex AI Gemini API](https://cloud.google.com/vertex-ai/docs/generative-ai/model-reference/gemini)
