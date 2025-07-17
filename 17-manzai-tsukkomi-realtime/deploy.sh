#!/bin/bash

# Cloud Run デプロイスクリプト

set -e

# 設定
PROJECT_ID=${1:-"your-project-id"}
REGION=${2:-"asia-northeast1"}
SERVICE_NAME="manzai-tsukkomi-app"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "🎭 漫才ツッコミ Web アプリを Cloud Run にデプロイします"
echo "プロジェクト ID: ${PROJECT_ID}"
echo "リージョン: ${REGION}"
echo "サービス名: ${SERVICE_NAME}"

# Google Cloud プロジェクトの設定
echo "📋 Google Cloud プロジェクトを設定中..."
gcloud config set project ${PROJECT_ID}

# Container Registry の有効化
echo "🔧 Container Registry を有効化中..."
gcloud services enable containerregistry.googleapis.com
gcloud services enable run.googleapis.com

# Docker イメージのビルド
echo "🏗️ Docker イメージをビルド中..."
docker build -t ${IMAGE_NAME}:latest .

# Container Registry にプッシュ
echo "📤 Container Registry にプッシュ中..."
docker push ${IMAGE_NAME}:latest

# GOOGLE_API_KEY の確認
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "❌ GOOGLE_API_KEY 環境変数が設定されていません"
    echo "export GOOGLE_API_KEY='your-api-key' を実行してください"
    exit 1
fi

# Cloud Run にデプロイ
echo "🚀 Cloud Run にデプロイ中..."
gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME}:latest \
    --region ${REGION} \
    --platform managed \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --concurrency 100 \
    --max-instances 10 \
    --set-env-vars GOOGLE_API_KEY=${GOOGLE_API_KEY} \
    --port 8080

# デプロイ結果の取得
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region=${REGION} --format='value(status.url)')

echo ""
echo "🎉 デプロイが完了しました！"
echo "🌐 アプリケーション URL: ${SERVICE_URL}"
echo "📊 ヘルスチェック: ${SERVICE_URL}/health"
echo "📈 統計情報: ${SERVICE_URL}/stats"
echo ""
echo "使用方法:"
echo "1. ブラウザで ${SERVICE_URL} にアクセス"
echo "2. マイクの使用を許可"
echo "3. マイクボタンを押して話しかける"
echo "4. 関西弁AIのツッコミを楽しむ！"