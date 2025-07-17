"""
Web用ツッコミプロセッサー - Cloud Run対応
"""

import logging
from typing import Any, Dict, Optional

from config import AppConfig, TsukkomiPrompts
from genai_integration import GenAIIntegration

logger = logging.getLogger(__name__)


class WebTsukkomiProcessor:
    """Web用漫才ツッコミプロセッサー"""

    def __init__(self, config: AppConfig):
        self.config = config
        self.genai_integration = GenAIIntegration(
            api_key=config.api_key, system_prompt=TsukkomiPrompts.get_system_prompt()
        )
        self.is_initialized = False
        self.request_count = 0

    async def initialize(self) -> bool:
        """プロセッサーの初期化"""
        try:
            # genai-processors統合モジュールの初期化
            success = await self.genai_integration.initialize()
            if not success:
                logger.error("genai-processors の初期化に失敗しました")
                return False

            # セッションの開始
            await self.genai_integration.start_session()

            self.is_initialized = True
            logger.info("Web用ツッコミプロセッサーが初期化されました")
            return True

        except Exception as e:
            logger.error(f"初期化エラー: {e}")
            return False

    async def process_audio(self, audio_data: bytes) -> Optional[Dict[str, Any]]:
        """音声データの処理"""
        if not self.is_initialized:
            logger.error("プロセッサーが初期化されていません")
            return None

        try:
            self.request_count += 1

            # genai-integration経由で音声データを処理
            response = await self.genai_integration.process_audio(audio_data)

            if response:
                result = {
                    "text": getattr(response, "text", "何でやねん！"),
                    "audio_data": getattr(response, "audio_data", None),
                    "request_id": self.request_count,
                    "processing_time": 0.5,  # 実際の処理時間を測定する場合
                }

                logger.info(f"音声処理完了: {result['text']}")
                return result

            else:
                # フォールバック用の簡易ツッコミ
                return await self._generate_fallback_tsukkomi("音声入力")

        except Exception as e:
            logger.error(f"音声処理エラー: {e}")
            return await self._generate_fallback_tsukkomi("エラー発生")

    async def process_text(self, text: str) -> Optional[Dict[str, Any]]:
        """テキストの処理"""
        if not self.is_initialized:
            logger.error("プロセッサーが初期化されていません")
            return None

        try:
            self.request_count += 1

            # genai-integration経由でテキストを処理
            response = await self.genai_integration.process_text(text)

            if response:
                result = {
                    "text": getattr(response, "text", "何でやねん！"),
                    "audio_data": getattr(response, "audio_data", None),
                    "original_text": text,
                    "request_id": self.request_count,
                }

                logger.info(f"テキスト処理完了: {text} → {result['text']}")
                return result

            else:
                # フォールバック用の簡易ツッコミ
                return await self._generate_fallback_tsukkomi(text)

        except Exception as e:
            logger.error(f"テキスト処理エラー: {e}")
            return await self._generate_fallback_tsukkomi(text)

    async def _generate_fallback_tsukkomi(self, input_text: str) -> Dict[str, Any]:
        """フォールバック用の簡易ツッコミ生成"""
        import random

        # 関西弁ツッコミパターン
        tsukkomi_patterns = [
            f"何でやねん、{input_text}って！",
            "ちゃうやろ、それ！",
            "アホか！",
            "せやかて、おかしいやん！",
            "そんなん、あるかいな！",
            "ボケ！何言うてんねん！",
            "ツッコミどころ満載やがな！",
            "もうええわ！",
            "しょーもな！",
            "やめとけって！",
        ]

        tsukkomi_text = random.choice(tsukkomi_patterns)

        return {
            "text": tsukkomi_text,
            "audio_data": None,  # フォールバック時は音声なし
            "original_text": input_text,
            "request_id": self.request_count,
            "fallback": True,
        }

    async def cleanup(self):
        """リソースのクリーンアップ"""
        try:
            if self.genai_integration:
                await self.genai_integration.end_session()
                await self.genai_integration.cleanup()

            self.is_initialized = False
            logger.info("Web用ツッコミプロセッサーをクリーンアップしました")

        except Exception as e:
            logger.error(f"クリーンアップエラー: {e}")

    def get_status(self) -> Dict[str, Any]:
        """プロセッサーの状態取得"""
        return {
            "is_initialized": self.is_initialized,
            "request_count": self.request_count,
            "genai_status": self.genai_integration.get_status()
            if self.genai_integration
            else {},
            "config": {
                "model_name": self.config.model.model_name,
                "temperature": self.config.model.temperature,
                "voice_name": self.config.voice.voice_name,
            },
        }
