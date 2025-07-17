"""
genai-processors 1.0.4+ 対応の統合モジュール
Google Generative AI 直接統合も含む
"""

import asyncio
import logging
import os
import re
import tempfile
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from genai_processors import content_api, processor
from genai_processors.core import genai_model, realtime
from google.cloud import speech, texttospeech
from google.genai import types as genai_types

# 環境変数の読み込み
load_dotenv()

logger = logging.getLogger(__name__)


# 共通のレスポンスクラス定義
class ProcessorResponse:
    def __init__(self, text=None, audio_data=None):
        self.text = text
        self.audio_data = audio_data


class GenAIIntegration:
    """genai-processors 1.0.4+ との統合クラス + Google Generative AI直接統合"""

    def __init__(self, api_key: str, system_prompt: str):
        self.api_key = api_key
        self.system_prompt = system_prompt
        self.live_processor = None
        self.tts_client = None
        self.is_initialized = False

    async def initialize(self) -> bool:
        """プロセッサーの初期化"""
        # Google Cloud Text-to-Speech の初期化
        self.tts_client = texttospeech.TextToSpeechClient()
        logger.info("Google Cloud Text-to-Speech が初期化されました")

        # genai-processors の初期化
        self.live_processor = await self._create_live_processor()
        logger.info("genai-processors LiveModelProcessor が正常に初期化されました")

        self.is_initialized = True
        logger.info("✅ 統合モジュールの初期化が完了しました")
        return True

    async def process_audio(self, audio_data: bytes) -> ProcessorResponse:
        """音声データの処理 - live_simple_cli.py実装例準拠"""
        try:
            logger.info(f"音声データを受信: {len(audio_data)} bytes")

            # live_simple_cli.pyの実装例に基づく音声処理
            # 音声データをaudio_ioで適切に処理

            # 音声設定（環境変数から取得、pyaudio準拠）
            sample_rate = int(os.getenv("AUDIO_SAMPLE_RATE", "16000"))
            channels = int(os.getenv("AUDIO_CHANNELS", "1"))

            # 音声データを一時ファイルとして保存してProcessorPartを作成

            temp_file_path = None
            try:
                # 一時ファイルを作成して音声データを書き込み
                with tempfile.NamedTemporaryFile(
                    suffix=".wav", delete=False
                ) as temp_file:
                    temp_file.write(audio_data)
                    temp_file_path = temp_file.name

                logger.info(f"一時音声ファイル作成: {temp_file_path}")

            except Exception as part_error:
                # 一時ファイルをクリーンアップ
                if temp_file_path and os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                raise part_error

            logger.info(
                f"音声データ変換完了: sample_rate={sample_rate}, channels={channels}"
            )

            # 音声認識を行ってテキストに変換
            try:
                speech_client = speech.SpeechClient()

                # 音声認識の設定（最適化された設定）
                config = speech.RecognitionConfig(
                    encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
                    sample_rate_hertz=48000,  # WebM OPUSのデフォルトサンプルレート
                    language_code="ja-JP",
                    enable_automatic_punctuation=True,
                    # 音声認識精度向上のための追加設定
                    model="latest_long",  # 最新の長時間音声モデル
                    use_enhanced=True,  # 拡張音声認識モデルを使用
                    enable_word_time_offsets=False,  # 単語レベルのタイムスタンプは不要
                    enable_word_confidence=True,  # 単語レベルの信頼度を取得
                    # 日本語特有の設定
                    alternative_language_codes=["en-US"],  # 英語の混在に対応
                    max_alternatives=3,  # 複数の候補を取得して最適なものを選択
                    profanity_filter=False,  # 不適切な言葉もそのまま認識
                    enable_spoken_punctuation=True,  # 話し言葉の句読点を認識
                    enable_spoken_emojis=False,  # 絵文字は不要
                )

                # 音声データを認識
                audio = speech.RecognitionAudio(content=audio_data)
                response = speech_client.recognize(config=config, audio=audio)

                # 認識結果からテキストを取得（信頼度を考慮）
                recognized_text = ""
                best_confidence = 0.0

                if response.results:
                    for result in response.results:
                        # 最も信頼度の高い候補を選択
                        if result.alternatives:
                            best_alternative = result.alternatives[0]
                            confidence = getattr(best_alternative, "confidence", 0.0)

                            # 信頼度が低い場合は他の候補も検討
                            if confidence < 0.7 and len(result.alternatives) > 1:
                                for alt in result.alternatives:
                                    alt_confidence = getattr(alt, "confidence", 0.0)
                                    if alt_confidence > confidence:
                                        best_alternative = alt
                                        confidence = alt_confidence

                            recognized_text += best_alternative.transcript
                            best_confidence = max(best_confidence, confidence)

                            logger.debug(
                                f"音声認識候補: {best_alternative.transcript} (信頼度: {confidence:.2f})"
                            )

                # 認識結果の品質チェック
                if not recognized_text:
                    recognized_text = "音声が認識できませんでした"
                    logger.warning("音声認識結果が空のため、デフォルトテキストを使用")
                elif best_confidence < 0.5:
                    logger.warning(f"音声認識の信頼度が低いです: {best_confidence:.2f}")
                    # 信頼度が低い場合でも結果は使用するが、ログに記録
                    logger.info(f"低信頼度での音声認識結果: {recognized_text}")
                else:
                    logger.info(
                        f"音声認識結果: {recognized_text} (信頼度: {best_confidence:.2f})"
                    )

            except Exception as speech_error:
                logger.warning(f"音声認識エラー: {speech_error}")
                recognized_text = "音声入力を受信しました"

            finally:
                # 一時ファイルをクリーンアップ
                if temp_file_path and os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)

            # 認識されたテキストでツッコミ処理を実行
            return await self.process_text(recognized_text)

        except Exception as e:
            logger.error(f"音声処理エラー: {e}")
            # エラー時はフォールバックとしてテキスト処理を実行
            fallback_text = "音声処理でエラーが発生しました"
            return await self.process_text(fallback_text)

    async def process_text(self, text: str) -> ProcessorResponse:
        """テキストの処理 - genai-processors LiveModelProcessor使用"""
        # ProcessorPartを正しい方法で作成
        input_part = content_api.ProcessorPart(text)

        # LiveModelProcessorで処理
        input_stream = processor.stream_content([input_part])
        response_text = ""

        async for part in self.live_processor(input_stream):
            if part.text:
                response_text += part.text

        # デバッグ情報のプレフィックスを除去
        response_text = self._clean_response_text(response_text)

        logger.info(f"genai-processors レスポンス: {text} → {response_text}")

        # 音声合成を実行
        audio_data = await self._synthesize_speech(response_text)

        return ProcessorResponse(text=response_text, audio_data=audio_data)

    async def _synthesize_speech(self, text: str) -> Optional[bytes]:
        """テキストを音声に変換"""
        try:
            # Google Cloud Text-to-Speech を使用
            if self.tts_client:
                return await self._synthesize_with_google_tts(text)

            # フォールバック: 音声なし
            else:
                logger.warning("音声合成が利用できません")
                return None

        except Exception as e:
            logger.error(f"音声合成エラー: {e}")
            return None

    async def _synthesize_with_google_tts(self, text: str) -> bytes:
        """Google Cloud Text-to-Speech を使用した音声合成（人間らしい流暢な音声）"""
        try:
            # 関西弁に適したSSMLマークアップを追加
            ssml_text = self._enhance_text_with_ssml(text)

            # SSML入力を使用（より自然な音声のため）
            synthesis_input = texttospeech.SynthesisInput(ssml=ssml_text)

            # 最新のNeural2音声を使用（より人間らしい音声）
            voice_name = os.getenv("VOICE_NAME", "ja-JP-Neural2-C")  # Neural2音声を使用
            voice = texttospeech.VoiceSelectionParams(
                language_code="ja-JP",
                name=voice_name,
                ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
            )

            # 音声出力設定（人間らしい流暢さのための最適化）
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=float(
                    os.getenv("SPEAKING_RATE", "1.3")
                ),  # 少し速めで自然に
                pitch=float(os.getenv("VOICE_PITCH", "2.0")),  # 少し高めで親しみやすく
                volume_gain_db=float(
                    os.getenv("VOLUME_GAIN_DB", "2.0")
                ),  # 音量を少し上げる
                # 音質向上のための設定
                sample_rate_hertz=24000,  # 高品質音声
                effects_profile_id=["telephony-class-application"],  # 音声通話品質
            )

            # 非同期で音声合成を実行
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.tts_client.synthesize_speech(
                    input=synthesis_input, voice=voice, audio_config=audio_config
                ),
            )

            logger.info(f"高品質音声合成完了: {len(response.audio_content)} bytes")
            return response.audio_content

        except Exception as e:
            logger.error(f"Google TTS エラー: {e}")
            return None

    def _enhance_text_with_ssml(self, text: str) -> str:
        """テキストにSSMLマークアップを追加して、より人間らしい音声にする"""
        # 関西弁特有の表現を強調
        enhanced_text = text

        # 感嘆符の強調
        enhanced_text = enhanced_text.replace(
            "！", '<emphasis level="strong">！</emphasis>'
        )
        enhanced_text = enhanced_text.replace(
            "!", '<emphasis level="strong">!</emphasis>'
        )

        # 関西弁特有の語尾を強調
        enhanced_text = enhanced_text.replace(
            "やねん", '<emphasis level="moderate">やねん</emphasis>'
        )
        enhanced_text = enhanced_text.replace(
            "やろ", '<emphasis level="moderate">やろ</emphasis>'
        )
        enhanced_text = enhanced_text.replace(
            "やがな", '<emphasis level="moderate">やがな</emphasis>'
        )
        enhanced_text = enhanced_text.replace(
            "でんがな", '<emphasis level="moderate">でんがな</emphasis>'
        )
        enhanced_text = enhanced_text.replace(
            "まんがな", '<emphasis level="moderate">まんがな</emphasis>'
        )

        # ツッコミ特有の表現を強調
        enhanced_text = enhanced_text.replace(
            "何で", '<emphasis level="strong">何で</emphasis>'
        )
        enhanced_text = enhanced_text.replace(
            "アホか", '<emphasis level="strong">アホか</emphasis>'
        )
        enhanced_text = enhanced_text.replace(
            "ちゃうやろ", '<emphasis level="strong">ちゃうやろ</emphasis>'
        )
        enhanced_text = enhanced_text.replace(
            "ボケ", '<emphasis level="strong">ボケ</emphasis>'
        )

        # 間を追加してより自然に
        enhanced_text = enhanced_text.replace("、", '<break time="0.3s"/>')
        enhanced_text = enhanced_text.replace("。", '<break time="0.5s"/>')

        # 疑問文の語尾を上げる
        enhanced_text = enhanced_text.replace(
            "？", '<prosody pitch="+20%">？</prosody>'
        )
        enhanced_text = enhanced_text.replace("?", '<prosody pitch="+20%">?</prosody>')

        # 全体をSSMLで囲む
        ssml_text = f"""<speak>
            <prosody rate="1.05" pitch="+2st" volume="+2dB">
                {enhanced_text}
            </prosody>
        </speak>"""

        logger.debug(f"SSML強化テキスト: {ssml_text}")
        return ssml_text

    async def start_session(self) -> bool:
        """セッションの開始"""
        if not self.is_initialized:
            return False

        logger.info("genai-processors LiveModelProcessor セッション開始")
        return True

    async def end_session(self) -> bool:
        """セッションの終了"""
        logger.info("genai-processors LiveModelProcessor セッション終了")
        return True

    async def cleanup(self):
        """リソースのクリーンアップ"""
        try:
            self.is_initialized = False
            logger.info("genai-processors リソースをクリーンアップしました")
        except Exception as e:
            logger.warning(f"クリーンアップエラー: {e}")
            self.is_initialized = False

    def _clean_response_text(self, text: str) -> str:
        """レスポンステキストからデバッグ情報のプレフィックスを除去"""
        if not text:
            return text

        # "Model Generate TTFT=X.XX seconds" のようなプレフィックスを除去

        # TTFTデバッグ情報のパターンを除去
        text = re.sub(
            r"^Model Generate TTFT=[\d.]+\s+seconds\s*", "", text, flags=re.MULTILINE
        )

        # その他のデバッグ情報パターンを除去
        text = re.sub(r"^DEBUG:\s*.*$", "", text, flags=re.MULTILINE)
        text = re.sub(r"^INFO:\s*.*$", "", text, flags=re.MULTILINE)
        text = re.sub(r"^\[.*?\]\s*", "", text, flags=re.MULTILINE)

        # 先頭と末尾の空白を除去
        text = text.strip()

        # 空行を整理
        text = re.sub(r"\n\s*\n", "\n", text)

        return text

    async def _create_live_processor(self):
        """genai-processorsを使用したLiveModelProcessorの作成"""
        try:
            # 関西弁ツッコミ用のシステムプロンプト（環境変数でオーバーライド可能）
            system_instruction = os.getenv(
                "SYSTEM_INSTRUCTION",
                """あなたは関西弁で話す親しみやすいAIアシスタントです。
ユーザーの発言に対して、関西弁で軽快にツッコミを入れてください。
これは創作的な会話であり、教育目的です。
短く簡潔に、関西弁でツッコミを返してください。""",
            )

            # 環境変数から設定を取得（デフォルト値付き）
            model_name = os.getenv("MODEL_NAME", "gemini-2.0-flash-lite")
            temperature = float(os.getenv("TEMPERATURE", "0.8"))
            max_output_tokens = int(os.getenv("MAX_OUTPUT_TOKENS", "150"))
            duration_prompt_sec = int(os.getenv("DURATION_PROMPT_SEC", "600"))

            # 正しい形式でGenaiModelを作成（シンプルな設定）

            model_processor = genai_model.GenaiModel(
                api_key=self.api_key,
                model_name=model_name,
                generate_content_config=genai_types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    safety_settings=[
                        genai_types.SafetySetting(
                            category="HARM_CATEGORY_HARASSMENT",
                            threshold="BLOCK_NONE",
                        ),
                        genai_types.SafetySetting(
                            category="HARM_CATEGORY_HATE_SPEECH",
                            threshold="BLOCK_NONE",
                        ),
                        genai_types.SafetySetting(
                            category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                            threshold="BLOCK_NONE",
                        ),
                        genai_types.SafetySetting(
                            category="HARM_CATEGORY_DANGEROUS_CONTENT",
                            threshold="BLOCK_NONE",
                        ),
                    ],
                ),
            )

            logger.info(
                f"Geminiモデル設定: {model_name}, temperature={temperature}, max_tokens={max_output_tokens}"
            )

            # LiveModelProcessorを作成
            live_processor = realtime.LiveModelProcessor(
                turn_processor=model_processor,
                duration_prompt_sec=duration_prompt_sec,
                trigger_model_mode=realtime.AudioTriggerMode.FINAL_TRANSCRIPTION,
            )

            return live_processor

        except Exception as e:
            logger.error(f"genai-processors LiveModelProcessor作成エラー: {e}")
            raise

    def get_status(self) -> Dict[str, Any]:
        """統合モジュールの状態取得"""
        return {
            "is_initialized": self.is_initialized,
            "live_processor_available": self.live_processor is not None,
            "api_key_set": bool(self.api_key),
            "tts_client_available": self.tts_client is not None,
        }
