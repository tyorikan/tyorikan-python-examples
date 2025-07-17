# 🎭 漫才ツッコミ リアルタイム Web アプリ

**Cloud Run 対応**の関西弁 AI が瞬時にツッコミを入れるモダンな Web アプリケーション！

## ✨ 特徴

- 🎤 **リアルタイム音声処理** - マイクで話すと即座にツッコミ
- �️ **関西弁 AI 信** - 「何でやねん！」「ちゃうやろ！」など自然な関西弁
- 🌐 **モダン Web UI** - レスポンシブデザインで美しいインター face
- ☁️ **Cloud Run 対応** - スケーラブルなサーバーレス実行
- � **We 環 bSocket 通信** - リアルタイム双方向通信
- 📱 **マルチデバイス対応** - PC・スマホ・タブレット対応

## 🚀 Cloud Run デプロイ

### 前提条件

- Google Cloud プロジェクト
- Google Cloud CLI (`gcloud`) インストール済み
- Docker インストール済み
- Gemini API キー

### デプロイ手順

```bash
# 1. リポジトリをクローン
git clone <repository-url>
cd 17-manzai-tsukkomi-realtime

# 2. Google API キーを設定
export GOOGLE_API_KEY="your-gemini-api-key"

# 3. デプロイスクリプトを実行
./deploy.sh your-project-id asia-northeast1
```

### 手動デプロイ

```bash
# Google Cloud プロジェクト設定
gcloud config set project YOUR_PROJECT_ID

# Docker イメージビルド & プッシュ
docker build -t gcr.io/YOUR_PROJECT_ID/manzai-tsukkomi-app .
docker push gcr.io/YOUR_PROJECT_ID/manzai-tsukkomi-app

# Cloud Run デプロイ
gcloud run deploy manzai-tsukkomi-app \
    --image gcr.io/YOUR_PROJECT_ID/manzai-tsukkomi-app \
    --region asia-northeast1 \
    --platform managed \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --set-env-vars GOOGLE_API_KEY=${GOOGLE_API_KEY}
```

## 🖥️ ローカル開発

### Docker Compose を使用

```bash
# 環境変数設定
echo "GOOGLE_API_KEY=your-api-key" > .env

# Web アプリ起動
docker-compose up manzai-tsukkomi-web

# 開発モード（ホットリロード）
docker-compose --profile dev up manzai-tsukkomi-dev
```

### 直接実行

```bash
# 依存関係インストール
pip install -r requirements.txt

# 環境変数設定
export GOOGLE_API_KEY="your-api-key"

# アプリ起動
python app.py
```

## 🎯 使用方法

1. **ブラウザでアクセス** - デプロイされた URL または `http://localhost:8080`
2. **マイク許可** - ブラウザでマイクの使用を許可
3. **録音開始** - 大きなマイクボタンを押して話す
4. **ツッコミ体験** - 関西弁 AI が瞬時にツッコミを返します！

### テキストモード

マイクが使えない場合は、テキスト入力欄でもツッコミを試せます。

## 🏗️ アーキテクチャ

```
┌─────────────────┐    WebSocket    ┌──────────────────┐
│   Frontend      │ ←──────────────→ │   FastAPI        │
│   (HTML/JS/CSS) │                 │   WebSocket      │
└─────────────────┘                 └──────────────────┘
                                              │
                                              ▼
                                    ┌──────────────────┐
                                    │ genai-processors │
                                    │ + Gemini API     │
                                    └──────────────────┘
```

## 📁 プロジェクト構造

```
17-manzai-tsukkomi-realtime/
├── app.py                    # FastAPI メインアプリ
├── web_tsukkomi_processor.py # Web用ツッコミプロセッサー
├── genai_integration.py     # genai-processors統合
├── config.py                # 設定管理
├── templates/
│   └── index.html           # メインHTML
├── static/
│   ├── css/style.css        # モダンCSS
│   └── js/app.js           # フロントエンドJS
├── Dockerfile              # Cloud Run用
├── docker-compose.yml      # ローカル開発用
├── cloudbuild.yaml         # Cloud Build設定
├── deploy.sh              # デプロイスクリプト
└── requirements.txt       # Python依存関係
```

## � 設定

### 環境変数

| 変数名           | 説明            | 必須                   |
| ---------------- | --------------- | ---------------------- |
| `GOOGLE_API_KEY` | Gemini API キー | ✅                     |
| `PORT`           | サーバーポート  | ❌ (デフォルト: 8080)  |
| `DEBUG`          | デバッグモード  | ❌ (デフォルト: false) |
| `LOG_LEVEL`      | ログレベル      | ❌ (デフォルト: INFO)  |

### カスタマイズ

`config.py` で AI の設定をカスタマイズできます：

- **音声合成設定** - 声の種類、話速、ピッチ
- **モデル設定** - 温度、最大トークン数
- **ツッコミプロンプト** - 関西弁のスタイル調整

## 🧪 テスト・デバッグ

```bash
# 環境変数設定のテスト
python test_env_config.py

# 統合テスト
python test_genai_integration.py

# ヘルスチェック
curl http://localhost:8080/health

# 統計情報
curl http://localhost:8080/stats
```

## 🌟 技術スタック

- **Backend**: FastAPI + WebSocket
- **Frontend**: Vanilla JavaScript + Modern CSS
- **AI**: genai-processors + Google Gemini
- **Deployment**: Google Cloud Run
- **Container**: Docker

## 🤝 貢献

プルリクエストやイシューを歓迎します！

## 📄 ライセンス

MIT License

---

**関西弁 AI と一緒に楽しい漫才体験をお楽しみください！** 🎭✨
