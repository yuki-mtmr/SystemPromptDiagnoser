"""
OpenAIProvider のテスト
TDD: RED - まずテストを書き、失敗を確認してから実装
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock

from providers.openai_provider import OpenAIProvider
from providers.protocols import LLMProvider, LLMConfig, LLMResponse


class TestOpenAIProvider:
    """OpenAIProvider のテスト"""

    def test_implements_llm_provider_protocol(self):
        """OpenAIProviderがLLMProviderプロトコルを実装"""
        config = LLMConfig(api_key="test-key")
        provider = OpenAIProvider(config)
        assert isinstance(provider, LLMProvider)

    def test_provider_name_is_openai(self):
        """provider_nameがopenaiである"""
        config = LLMConfig(api_key="test-key")
        provider = OpenAIProvider(config)
        assert provider.provider_name == "openai"

    def test_uses_default_model_when_not_specified(self):
        """モデル未指定時にデフォルトモデルを使用"""
        config = LLMConfig(api_key="test-key")
        provider = OpenAIProvider(config)
        assert provider.model_name == "gpt-4o"

    def test_uses_specified_model(self):
        """指定されたモデルを使用"""
        config = LLMConfig(api_key="test-key", model="gpt-4o-mini")
        provider = OpenAIProvider(config)
        assert provider.model_name == "gpt-4o-mini"

    def test_uses_default_temperature_when_not_specified(self):
        """temperature未指定時にデフォルト値を使用"""
        config = LLMConfig(api_key="test-key")
        provider = OpenAIProvider(config)
        assert provider.temperature == 0.7

    def test_uses_specified_temperature(self):
        """指定されたtemperatureを使用"""
        config = LLMConfig(api_key="test-key", temperature=0.3)
        provider = OpenAIProvider(config)
        assert provider.temperature == 0.3

    @patch("providers.openai_provider.ChatOpenAI")
    def test_generate_returns_llm_response(self, mock_chat_openai):
        """generateがLLMResponseを返す"""
        mock_llm = Mock()
        mock_llm.invoke.return_value = Mock(content="Test response")
        mock_chat_openai.return_value = mock_llm

        config = LLMConfig(api_key="test-key")
        provider = OpenAIProvider(config)
        response = provider.generate("Hello")

        assert isinstance(response, LLMResponse)
        assert response.content == "Test response"

    @patch("providers.openai_provider.ChatOpenAI")
    def test_generate_with_system_prompt(self, mock_chat_openai):
        """generateがsystem_promptを使用"""
        mock_llm = Mock()
        mock_llm.invoke.return_value = Mock(content="Response with system")
        mock_chat_openai.return_value = mock_llm

        config = LLMConfig(api_key="test-key")
        provider = OpenAIProvider(config)
        response = provider.generate("Hello", system_prompt="Be helpful")

        assert response.content == "Response with system"
        # invoke が呼ばれたことを確認
        mock_llm.invoke.assert_called_once()

    @patch("providers.openai_provider.ChatOpenAI")
    @pytest.mark.asyncio
    async def test_agenerate_returns_llm_response(self, mock_chat_openai):
        """agenerateがLLMResponseを返す"""
        mock_llm = Mock()
        mock_llm.ainvoke = AsyncMock(return_value=Mock(content="Async response"))
        mock_chat_openai.return_value = mock_llm

        config = LLMConfig(api_key="test-key")
        provider = OpenAIProvider(config)
        response = await provider.agenerate("Hello")

        assert isinstance(response, LLMResponse)
        assert response.content == "Async response"

    @patch("providers.openai_provider.ChatOpenAI")
    def test_handles_api_error_gracefully(self, mock_chat_openai):
        """APIエラーを適切に処理"""
        mock_llm = Mock()
        mock_llm.invoke.side_effect = Exception("API Error")
        mock_chat_openai.return_value = mock_llm

        config = LLMConfig(api_key="test-key")
        provider = OpenAIProvider(config)

        with pytest.raises(Exception) as exc_info:
            provider.generate("Hello")

        assert "API Error" in str(exc_info.value)
