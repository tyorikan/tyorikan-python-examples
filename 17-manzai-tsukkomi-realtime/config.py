"""
設定ファイル - 漫才ツッコミアプリケーション用
環境変数から動的に設定を読み込み
"""

import os
from dataclasses import dataclass
from typing import Any, Dict

from dotenv import load_dotenv

# .envファイルから環境変数を読み込み
load_dotenv()


@dataclass
class AudioConfig:
    """音声設定 - 環境変数から動的に読み込み"""

    def __init__(self):
        self.input_sample_rate: int = int(os.getenv("INPUT_SAMPLE_RATE", "16000"))
        self.output_sample_rate: int = int(os.getenv("OUTPUT_SAMPLE_RATE", "24000"))
        self.channels: int = int(os.getenv("AUDIO_CHANNELS", "1"))
        self.chunk_size: int = int(os.getenv("AUDIO_CHUNK_SIZE", "1024"))
        self.input_device_index: int = self._get_device_index("INPUT_DEVICE_INDEX")
        self.output_device_index: int = self._get_device_index("OUTPUT_DEVICE_INDEX")

    def _get_device_index(self, env_var: str) -> int:
        """デバイスインデックスを環境変数から取得"""
        value = os.getenv(env_var)
        return int(value) if value and value.isdigit() else None


@dataclass
class VoiceConfig:
    """音声合成設定 - 環境変数から動的に読み込み"""

    def __init__(self):
        self.voice_name: str = os.getenv("VOICE_NAME", "ja-JP-Standard-C")
        self.speaking_rate: float = float(os.getenv("SPEAKING_RATE", "1.1"))
        self.pitch: float = float(os.getenv("VOICE_PITCH", "0.0"))
        self.volume_gain_db: float = float(os.getenv("VOLUME_GAIN_DB", "0.0"))


@dataclass
class ModelConfig:
    """AIモデル設定 - 環境変数から動的に読み込み"""

    def __init__(self):
        self.model_name: str = os.getenv("MODEL_NAME", "gemini-2.0-flash-exp")
        self.temperature: float = float(os.getenv("TEMPERATURE", "0.8"))
        self.max_output_tokens: int = int(os.getenv("MAX_OUTPUT_TOKENS", "150"))


class TsukkomiPrompts:
    """ツッコミ用プロンプト集 - 環境変数から動的に読み込み"""

    @staticmethod
    def get_system_prompt() -> str:
        """システムプロンプトを環境変数から取得"""
        default_prompt = """
あなたは関西弁を話す漫才師のツッコミ役です。
相手の発言に対して、瞬時に的確で面白いツッコミを入れてください。

ツッコミの特徴:
- 関西弁で自然に話す
- 「何でやねん！」「ちゃうやろ！」「アホか！」「せやかて！」などの定番フレーズを使う
- 相手の矛盾や変な点を鋭く指摘する
- テンポよく、短めに返す（1-2文程度）
- 時々「ボケ」も混ぜて会話を盛り上げる
- 愛嬌があって憎めないキャラクター
- 関西弁の語尾「やん」「やで」「やねん」を自然に使う

例:
- 「それ、おかしいやろ！」
- 「何でそうなるねん！」
- 「ちょっと待てや！」
- 「そんなアホな話あるかいな！」

必ず音声で返答し、簡潔に関西弁でツッコんでください。
"""
        return os.getenv("SYSTEM_PROMPT", default_prompt.strip())

    @staticmethod
    def get_conversation_starters() -> list:
        """会話スターターを環境変数から取得"""
        default_starters = [
            "何か面白い話してみ！",
            "今日はどないしたん？",
            "何かボケてみいや！",
        ]

        # 環境変数から取得（カンマ区切り）
        env_starters = os.getenv("CONVERSATION_STARTERS")
        if env_starters:
            return [starter.strip() for starter in env_starters.split(",")]

        return default_starters

    # 後方互換性のため
    @property
    def SYSTEM_PROMPT(self) -> str:
        return self.get_system_prompt()

    @property
    def CONVERSATION_STARTERS(self) -> list:
        return self.get_conversation_starters()


class AppConfig:
    """アプリケーション全体の設定"""

    def __init__(self):
        self.audio = AudioConfig()
        self.voice = VoiceConfig()
        self.model = ModelConfig()
        self.api_key = os.getenv("GOOGLE_API_KEY")

        # デバッグモード
        self.debug_mode = os.getenv("DEBUG", "false").lower() == "true"

        # ログレベル
        self.log_level = os.getenv("LOG_LEVEL", "INFO")

    def validate(self) -> bool:
        """設定の検証"""
        if not self.api_key:
            print("❌ GOOGLE_API_KEY が設定されていません")
            return False
        return True

    def to_dict(self) -> Dict[str, Any]:
        """設定を辞書形式で返す"""
        return {
            "audio": {
                "input_sample_rate": self.audio.input_sample_rate,
                "output_sample_rate": self.audio.output_sample_rate,
                "channels": self.audio.channels,
                "chunk_size": self.audio.chunk_size,
            },
            "voice": {
                "voice_name": self.voice.voice_name,
                "speaking_rate": self.voice.speaking_rate,
                "pitch": self.voice.pitch,
            },
            "model": {
                "model_name": self.model.model_name,
                "temperature": self.model.temperature,
                "max_output_tokens": self.model.max_output_tokens,
            },
        }
