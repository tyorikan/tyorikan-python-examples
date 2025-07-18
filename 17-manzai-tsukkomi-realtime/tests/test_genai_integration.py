import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from src.genai_integration import GenAIIntegration, ProcessorResponse


class TestGenAIIntegration(unittest.TestCase):
    """
    GenAIIntegrationクラスのテスト
    """

    def setUp(self):
        """各テストの前に実行されるセットアップ"""
        self.api_key = "test_api_key"
        self.system_prompt = "test_system_prompt"
        # Use asyncio.run() for cleaner async test execution

    @patch('src.genai_integration.texttospeech.TextToSpeechClient')
    @patch('src.genai_integration.genai_model.GenaiModel')
    @patch('src.genai_integration.realtime.LiveModelProcessor')
    def test_initialize_success(self, mock_live_processor, mock_genai_model, mock_tts_client):
        """initializeメソッドが正常に完了するかのテスト"""
        # --- Mock Setup ---
        mock_tts_client.return_value = MagicMock()
        mock_genai_model.return_value = MagicMock()
        mock_live_processor.return_value = MagicMock()

        # --- Test Execution ---
        integration = GenAIIntegration(self.api_key, self.system_prompt)
        result = asyncio.run(integration.initialize())

        # --- Assertions ---
        self.assertTrue(result)
        self.assertTrue(integration.is_initialized)
        mock_tts_client.assert_called_once()
        # _create_live_processorが呼び出されることを間接的に確認
        mock_genai_model.assert_called_once()
        mock_live_processor.assert_called_once()

    @patch('src.genai_integration.GenAIIntegration._synthesize_speech', new_callable=AsyncMock)
    @patch('src.genai_integration.GenAIIntegration._clean_response_text')
    def test_process_text_success(self, mock_clean_text, mock_synthesize_speech):
        """process_textメソッドが正常に動作するかのテスト"""
        # --- Mock Setup ---
        test_input_text = "これはテスト入力です"
        expected_response_text = "これがレスポンステキストです"
        expected_audio_data = b'test_audio_data'

        mock_clean_text.return_value = expected_response_text
        mock_synthesize_speech.return_value = expected_audio_data

        # LiveModelProcessorの非同期イテレータをモック
        async def mock_processor_stream(*args, **kwargs):
            yield MagicMock(text=expected_response_text)

        # --- Test Execution ---
        integration = GenAIIntegration(self.api_key, self.system_prompt)
        # initializeをモック化して実行
        integration.live_processor = MagicMock()
        integration.live_processor.return_value = mock_processor_stream()
        integration.is_initialized = True

        response = asyncio.run(integration.process_text(test_input_text))

        # --- Assertions ---
        self.assertIsInstance(response, ProcessorResponse)
        self.assertEqual(response.text, expected_response_text)
        self.assertEqual(response.audio_data, expected_audio_data)

        mock_clean_text.assert_called_once()
        mock_synthesize_speech.assert_called_once_with(expected_response_text)

if __name__ == '__main__':
    unittest.main()