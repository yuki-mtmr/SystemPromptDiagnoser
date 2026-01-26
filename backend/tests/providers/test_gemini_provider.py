"""
GeminiProvider のテスト
TDD: RED - まずテストを書き、失敗を確認してから実装
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock

from providers.gemini_provider import GeminiProvider
from providers.protocols import LLMProvider, LLMConfig, LLMResponse


class TestGeminiProvider:
    """GeminiProvider のテスト"""

    def test_implements_llm_provider_protocol(self):
        """GeminiProviderがLLMProviderプロトコルを実装"""
        config = LLMConfig(api_key="test-key")
        provider = GeminiProvider(config)
        assert isinstance(provider, LLMProvider)

    def test_provider_name_is_gemini(self):
        """provider_nameがgeminiである"""
        config = LLMConfig(api_key="test-key")
        provider = GeminiProvider(config)
        assert provider.provider_name == "gemini"

    def test_uses_default_model_when_not_specified(self):
        """モデル未指定時にデフォルトモデルを使用"""
        config = LLMConfig(api_key="test-key")
        provider = GeminiProvider(config)
        assert provider.model_name == "gemini-2.0-flash"

    def test_uses_specified_model(self):
        """指定されたモデルを使用"""
        config = LLMConfig(api_key="test-key", model="gemini-1.5-pro")
        provider = GeminiProvider(config)
        assert provider.model_name == "gemini-1.5-pro"

    @patch("providers.gemini_provider.ChatGoogleGenerativeAI")
    def test_generate_returns_llm_response(self, mock_chat_gemini):
        """generateがLLMResponseを返す"""
        mock_llm = Mock()
        mock_llm.invoke.return_value = Mock(content="Gemini response")
        mock_chat_gemini.return_value = mock_llm

        config = LLMConfig(api_key="test-key")
        provider = GeminiProvider(config)
        response = provider.generate("Hello")

        assert isinstance(response, LLMResponse)
        assert response.content == "Gemini response"

    @patch("providers.gemini_provider.ChatGoogleGenerativeAI")
    def test_generate_with_system_prompt(self, mock_chat_gemini):
        """generateがsystem_promptを使用"""
        mock_llm = Mock()
        mock_llm.invoke.return_value = Mock(content="Response with system")
        mock_chat_gemini.return_value = mock_llm

        config = LLMConfig(api_key="test-key")
        provider = GeminiProvider(config)
        response = provider.generate("Hello", system_prompt="Be helpful")

        assert response.content == "Response with system"
        mock_llm.invoke.assert_called_once()

    @patch("providers.gemini_provider.ChatGoogleGenerativeAI")
    @pytest.mark.asyncio
    async def test_agenerate_returns_llm_response(self, mock_chat_gemini):
        """agenerateがLLMResponseを返す"""
        mock_llm = Mock()
        mock_llm.ainvoke = AsyncMock(return_value=Mock(content="Async Gemini"))
        mock_chat_gemini.return_value = mock_llm

        config = LLMConfig(api_key="test-key")
        provider = GeminiProvider(config)
        response = await provider.agenerate("Hello")

        assert isinstance(response, LLMResponse)
        assert response.content == "Async Gemini"
