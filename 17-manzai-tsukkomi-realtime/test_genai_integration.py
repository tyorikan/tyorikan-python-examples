#!/usr/bin/env python3
"""
genai-processors 1.0.4+ 統合テスト
"""

import asyncio
import logging
import os

from config import AppConfig, TsukkomiPrompts
from genai_integration import GENAI_PROCESSORS_AVAILABLE, GenAIIntegration

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_genai_integration():
    """genai-processors統合のテスト"""
    print("🧪 genai-processors 1.0.4+ 統合テスト")
    print(f"ライブラリ利用可能: {GENAI_PROCESSORS_AVAILABLE}")

    # API キーの確認
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY 環境変数が設定されていません")
        print("テスト用のフォールバック実装で実行します")
        api_key = "test_key"

    # 統合モジュールの作成
    integration = GenAIIntegration(
        api_key=api_key, system_prompt=TsukkomiPrompts.get_system_prompt()
    )

    try:
        # 初期化テスト
        print("\n📋 初期化テスト...")
        success = await integration.initialize()
        print(f"初期化結果: {'✅ 成功' if success else '❌ 失敗'}")

        if not success:
            print("初期化に失敗しました。フォールバック実装で続行します。")

        # セッション開始テスト
        print("\n🚀 セッション開始テスト...")
        session_started = await integration.start_session()
        print(f"セッション開始: {'✅ 成功' if session_started else '❌ 失敗'}")

        # テキスト処理テスト
        print("\n💬 テキスト処理テスト...")
        test_inputs = [
            "今日はいい天気ですね",
            "私は宇宙人です",
            "1+1=3です",
            "猫が犬を散歩させています",
        ]

        for test_input in test_inputs:
            print(f"\n入力: {test_input}")
            response = await integration.process_text(test_input)

            if response and hasattr(response, "text"):
                print(f"ツッコミ: {response.text}")
            else:
                print("レスポンスなし")

        # 音声処理テスト（ダミーデータ）
        print("\n🎤 音声処理テスト...")
        dummy_audio = b"dummy_audio_data" * 100  # ダミー音声データ
        audio_response = await integration.process_audio(dummy_audio)

        if audio_response:
            if hasattr(audio_response, "text"):
                print(f"音声からのツッコミ: {audio_response.text}")
            if hasattr(audio_response, "audio_data"):
                print(f"音声データサイズ: {len(audio_response.audio_data)} bytes")
        else:
            print("音声処理レスポンスなし")

        # 状態確認テスト
        print("\n📊 状態確認テスト...")
        status = integration.get_status()
        for key, value in status.items():
            print(f"{key}: {value}")

        # セッション終了テスト
        print("\n🛑 セッション終了テスト...")
        session_ended = await integration.end_session()
        print(f"セッション終了: {'✅ 成功' if session_ended else '❌ 失敗'}")

    except Exception as e:
        logger.error(f"テストエラー: {e}")
        import traceback

        traceback.print_exc()
    finally:
        # クリーンアップ
        await integration.cleanup()
        print("\n🧹 クリーンアップ完了")


async def test_config_loading():
    """設定読み込みテスト"""
    print("\n⚙️ 設定読み込みテスト")

    config = AppConfig()
    print(f"設定検証: {'✅ 成功' if config.validate() else '❌ 失敗'}")

    config_dict = config.to_dict()
    print("設定内容:")
    for section, values in config_dict.items():
        print(f"  {section}:")
        for key, value in values.items():
            print(f"    {key}: {value}")


async def main():
    """メインテスト関数"""
    print("🎭 漫才ツッコミアプリ - 統合テスト")
    print("=" * 50)

    await test_config_loading()
    await test_genai_integration()

    print("\n🎉 全テスト完了！")


if __name__ == "__main__":
    asyncio.run(main())
