"""
漫才ツッコミ リアルタイム Web アプリケーション
Cloud Run 対応 FastAPI + WebSocket
"""

import base64
import logging
import os
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict

import uvicorn
from config import AppConfig
from dotenv import load_dotenv
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from web_tsukkomi_processor import WebTsukkomiProcessor

# 環境変数の読み込み
load_dotenv()

# ログ設定（環境変数から動的に設定）
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーションのライフサイクル管理"""
    # 起動時の処理
    logger.info("🎭 漫才ツッコミ Web アプリを起動中...")

    # 設定の検証
    if not config.validate():
        logger.error("❌ 設定エラー: GOOGLE_API_KEY が設定されていません")
        raise Exception("GOOGLE_API_KEY environment variable is required")

    # ツッコミプロセッサーの初期化
    await tsukkomi_processor.initialize()
    logger.info("✅ ツッコミプロセッサーが初期化されました")

    yield

    # 終了時の処理
    logger.info("🛑 漫才ツッコミ Web アプリを終了中...")
    await tsukkomi_processor.cleanup()
    logger.info("✅ クリーンアップが完了しました")


# FastAPIアプリケーション
app = FastAPI(
    title="漫才ツッコミ リアルタイム Web アプリ",
    description="関西弁AIが瞬時にツッコミを入れるWebアプリケーション",
    version="1.0.0",
    lifespan=lifespan,
)

# 静的ファイルとテンプレート
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# アプリケーション設定
config = AppConfig()
tsukkomi_processor = WebTsukkomiProcessor(config)

# アクティブなWebSocket接続を管理
active_connections: Dict[str, WebSocket] = {}


# 非推奨のon_eventを削除（lifespanで処理）


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """メインページ"""
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "title": "漫才ツッコミ リアルタイム Web アプリ"},
    )


@app.get("/health")
async def health_check():
    """ヘルスチェック（Cloud Run用）"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "processor_status": tsukkomi_processor.get_status(),
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket エンドポイント - リアルタイム音声処理"""
    # 接続ID生成
    connection_id = str(uuid.uuid4())

    try:
        # WebSocket接続を受け入れ
        await websocket.accept()
        active_connections[connection_id] = websocket

        logger.info(f"🔌 WebSocket接続が確立されました: {connection_id}")

        # 接続確認メッセージ
        await websocket.send_json(
            {
                "type": "connection_established",
                "connection_id": connection_id,
                "message": "漫才ツッコミアプリに接続されました！",
            }
        )

        # メッセージ処理ループ
        while True:
            # クライアントからのメッセージを受信
            data = await websocket.receive_json()

            if data["type"] == "audio_data":
                # 音声データの処理
                await handle_audio_data(websocket, data)

            elif data["type"] == "text_message":
                # テキストメッセージの処理（テスト用）
                await handle_text_message(websocket, data)

            elif data["type"] == "ping":
                # 接続確認
                await websocket.send_json(
                    {"type": "pong", "timestamp": datetime.now().isoformat()}
                )

    except WebSocketDisconnect:
        logger.info(f"🔌 WebSocket接続が切断されました: {connection_id}")

    except Exception as e:
        logger.error(f"❌ WebSocketエラー: {e}")
        await websocket.send_json(
            {"type": "error", "message": f"エラーが発生しました: {str(e)}"}
        )

    finally:
        # 接続をクリーンアップ
        if connection_id in active_connections:
            del active_connections[connection_id]


async def handle_audio_data(websocket: WebSocket, data: Dict[str, Any]):
    """音声データの処理"""
    try:
        # Base64エンコードされた音声データをデコード
        audio_b64 = data.get("audio_data", "")
        if not audio_b64:
            await websocket.send_json(
                {"type": "error", "message": "音声データが見つかりません"}
            )
            return

        # Base64デコード
        audio_bytes = base64.b64decode(audio_b64)

        # ツッコミ処理
        response = await tsukkomi_processor.process_audio(audio_bytes)

        if response:
            # レスポンスをクライアントに送信
            response_data = {
                "type": "tsukkomi_response",
                "text": response.get("text", ""),
                "timestamp": datetime.now().isoformat(),
            }

            # 音声データがある場合は追加
            if response.get("audio_data"):
                response_data["audio_data"] = base64.b64encode(
                    response["audio_data"]
                ).decode("utf-8")

            await websocket.send_json(response_data)

            logger.info(f"🗣️ ツッコミ送信: {response.get('text', '')}")

        else:
            await websocket.send_json(
                {"type": "error", "message": "ツッコミの生成に失敗しました"}
            )

    except Exception as e:
        logger.error(f"❌ 音声処理エラー: {e}")
        await websocket.send_json(
            {"type": "error", "message": f"音声処理エラー: {str(e)}"}
        )


async def handle_text_message(websocket: WebSocket, data: Dict[str, Any]):
    """テキストメッセージの処理（テスト用）"""
    try:
        text = data.get("text", "")
        if not text:
            return

        # ツッコミ処理
        response = await tsukkomi_processor.process_text(text)

        if response:
            # レスポンスをクライアントに送信
            response_data = {
                "type": "tsukkomi_response",
                "text": response.get("text", ""),
                "original_text": text,
                "timestamp": datetime.now().isoformat(),
            }

            # 音声データがある場合は追加
            if response.get("audio_data"):
                response_data["audio_data"] = base64.b64encode(
                    response["audio_data"]
                ).decode("utf-8")

            await websocket.send_json(response_data)

            logger.info(f"💬 テキストツッコミ: {text} → {response.get('text', '')}")

    except Exception as e:
        logger.error(f"❌ テキスト処理エラー: {e}")
        await websocket.send_json(
            {"type": "error", "message": f"テキスト処理エラー: {str(e)}"}
        )


@app.get("/stats")
async def get_stats():
    """統計情報の取得"""
    return {
        "active_connections": len(active_connections),
        "processor_status": tsukkomi_processor.get_status(),
        "timestamp": datetime.now().isoformat(),
    }


if __name__ == "__main__":
    # 開発用サーバー起動
    port = int(os.getenv("PORT", 8080))
    uvicorn.run("app:app", host="0.0.0.0", port=port, log_level="info", reload=False)
