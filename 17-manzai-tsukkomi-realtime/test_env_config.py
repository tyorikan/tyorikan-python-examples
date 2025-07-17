#!/usr/bin/env python3
"""
環境変数設定テスト - dotenv対応確認
"""

import os
import sys

from config import AppConfig, TsukkomiPrompts
from dotenv import load_dotenv


def test_env_loading():
    """環境変数の読み込みテスト"""
    print("🧪 環境変数設定テスト")
    print("=" * 50)

    # .envファイルの読み込み
    load_dotenv()
    print("✅ .envファイルを読み込みました")

    # 設定オブジェクトの作成
    config = AppConfig()

    print("\n📋 現在の設定:")
    print("-" * 30)

    # Google API Key
    api_key_status = (
        "✅ 設定済み"
        if config.api_key and config.api_key != "your_google_api_key_here"
        else "❌ 未設定"
    )
    print(f"GOOGLE_API_KEY: {api_key_status}")

    # アプリケーション設定
    print(f"DEBUG: {os.getenv('DEBUG', 'false')}")
    print(f"LOG_LEVEL: {os.getenv('LOG_LEVEL', 'INFO')}")
    print(f"PORT: {os.getenv('PORT', '8080')}")

    # AIモデル設定
    print("\n🤖 AIモデル設定:")
    print(f"  MODEL_NAME: {config.model.model_name}")
    print(f"  TEMPERATURE: {config.model.temperature}")
    print(f"  MAX_OUTPUT_TOKENS: {config.model.max_output_tokens}")

    # 音声合成設定
    print("\n🗣️ 音声合成設定:")
    print(f"  VOICE_NAME: {config.voice.voice_name}")
    print(f"  SPEAKING_RATE: {config.voice.speaking_rate}")
    print(f"  VOICE_PITCH: {config.voice.pitch}")
    print(f"  VOLUME_GAIN_DB: {config.voice.volume_gain_db}")

    # 音声処理設定
    print("\n🎤 音声処理設定:")
    print(f"  INPUT_SAMPLE_RATE: {config.audio.input_sample_rate}")
    print(f"  OUTPUT_SAMPLE_RATE: {config.audio.output_sample_rate}")
    print(f"  AUDIO_CHANNELS: {config.audio.channels}")
    print(f"  AUDIO_CHUNK_SIZE: {config.audio.chunk_size}")

    # プロンプト設定
    print("\n💬 プロンプト設定:")
    system_prompt = TsukkomiPrompts.get_system_prompt()
    print(f"  SYSTEM_PROMPT: {len(system_prompt)} 文字")
    print(f"  プロンプト先頭: {system_prompt[:100]}...")

    conversation_starters = TsukkomiPrompts.get_conversation_starters()
    print(f"  CONVERSATION_STARTERS: {len(conversation_starters)} 個")
    for i, starter in enumerate(conversation_starters[:3]):
        print(f"    {i + 1}. {starter}")

    # 設定検証
    print("\n🔍 設定検証:")
    is_valid = config.validate()
    validation_status = "✅ 有効" if is_valid else "❌ 無効"
    print(f"  設定状態: {validation_status}")

    return is_valid


def test_env_override():
    """環境変数の上書きテスト"""
    print("\n🔄 環境変数上書きテスト")
    print("-" * 30)

    # 一時的に環境変数を設定
    test_vars = {
        "MODEL_NAME": "gemini-2.5-flash",
        "TEMPERATURE": "0.5",
        "VOICE_NAME": "ja-JP-Standard-A",
        "SPEAKING_RATE": "0.9",
    }

    # 元の値を保存
    original_vars = {}
    for key in test_vars:
        original_vars[key] = os.getenv(key)

    try:
        # テスト用の値を設定
        for key, value in test_vars.items():
            os.environ[key] = value

        # 新しい設定オブジェクトを作成
        test_config = AppConfig()

        print("テスト用設定:")
        print(f"  MODEL_NAME: {test_config.model.model_name}")
        print(f"  TEMPERATURE: {test_config.model.temperature}")
        print(f"  VOICE_NAME: {test_config.voice.voice_name}")
        print(f"  SPEAKING_RATE: {test_config.voice.speaking_rate}")

        # 期待値と比較
        success = (
            test_config.model.model_name == "gemini-2.5-flash"
            and test_config.model.temperature == 0.5
            and test_config.voice.voice_name == "ja-JP-Standard-A"
            and test_config.voice.speaking_rate == 0.9
        )

        result = "✅ 成功" if success else "❌ 失敗"
        print(f"  上書きテスト: {result}")

    finally:
        # 元の値を復元
        for key, value in original_vars.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def show_env_examples():
    """環境変数設定例の表示"""
    print("\n📝 環境変数設定例:")
    print("-" * 30)

    examples = [
        ("# 基本設定", ""),
        ("GOOGLE_API_KEY", "your-actual-api-key"),
        ("DEBUG", "true"),
        ("LOG_LEVEL", "DEBUG"),
        ("", ""),
        ("# モデル変更例", ""),
        ("MODEL_NAME", "gemini-2.5-flash"),
        ("TEMPERATURE", "0.3"),
        ("MAX_OUTPUT_TOKENS", "200"),
        ("", ""),
        ("# 音声カスタマイズ例", ""),
        ("VOICE_NAME", "ja-JP-Wavenet-B"),
        ("SPEAKING_RATE", "1.3"),
        ("VOICE_PITCH", "-1.0"),
        ("", ""),
        ("# カスタムプロンプト例", ""),
        ("SYSTEM_PROMPT", "あなたは優しい関西弁のAIです..."),
        ("CONVERSATION_STARTERS", "おはよう！,元気？,何してる？"),
    ]

    for key, value in examples:
        if key.startswith("#"):
            print(f"\n{key}")
        elif key == "":
            continue
        else:
            print(f"export {key}='{value}'")


def main():
    """メイン関数"""
    print("🎭 漫才ツッコミアプリ - 環境変数設定テスト")
    print("=" * 60)

    # 基本テスト
    is_valid = test_env_loading()

    # 上書きテスト
    test_env_override()

    # 設定例表示
    show_env_examples()

    print("\n🎉 テスト完了!")

    if not is_valid:
        print("⚠️ GOOGLE_API_KEY を設定してからアプリを起動してください")
        print("例: export GOOGLE_API_KEY='your-actual-api-key'")
        sys.exit(1)
    else:
        print("✅ 設定は有効です。アプリを起動できます！")


if __name__ == "__main__":
    main()
