"""
GroqProvider のテスト
TDD: RED - まずテストを書き、失敗を確認してから実装
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock

from providers.groq_provider import GroqProvider
from providers.protocols import LLMProvider, LLMConfig, LLMResponse


class TestGroqProvider:
    """GroqProvider のテスト"""

    def test_implements_llm_provider_protocol(self):
        """GroqProviderがLLMProviderプロトコルを実装"""
        config = LLMConfig(api_key="test-key")
        provider = GroqProvider(config)
        assert isinstance(provider, LLMProvider)

    def test_provider_name_is_groq(self):
        """provider_nameがgroqである"""
        config = LLMConfig(api_key="test-key")
        provider = GroqProvider(config)
        assert provider.provider_name == "groq"

    def test_uses_default_model_when_not_specified(self):
        """モデル未指定時にデフォルトモデルを使用"""
        config = LLMConfig(api_key="test-key")
        provider = GroqProvider(config)
        assert provider.model_name == "llama-3.3-70b-versatile"

    def test_uses_specified_model(self):
        """指定されたモデルを使用"""
        config = LLMConfig(api_key="test-key", model="mixtral-8x7b-32768")
        provider = GroqProvider(config)
        assert provider.model_name == "mixtral-8x7b-32768"

    @patch("providers.groq_provider.ChatGroq")
    def test_generate_returns_llm_response(self, mock_chat_groq):
        """generateがLLMResponseを返す"""
        mock_llm = Mock()
        mock_llm.invoke.return_value = Mock(content="Groq response")
        mock_chat_groq.return_value = mock_llm

        config = LLMConfig(api_key="test-key")
        provider = GroqProvider(config)
        response = provider.generate("Hello")

        assert isinstance(response, LLMResponse)
        assert response.content == "Groq response"

    @patch("providers.groq_provider.ChatGroq")
    def test_generate_with_system_prompt(self, mock_chat_groq):
        """generateがsystem_promptを使用"""
        mock_llm = Mock()
        mock_llm.invoke.return_value = Mock(content="Response with system")
        mock_chat_groq.return_value = mock_llm

        config = LLMConfig(api_key="test-key")
        provider = GroqProvider(config)
        response = provider.generate("Hello", system_prompt="Be helpful")

        assert response.content == "Response with system"
        mock_llm.invoke.assert_called_once()

    @patch("providers.groq_provider.ChatGroq")
    @pytest.mark.asyncio
    async def test_agenerate_returns_llm_response(self, mock_chat_groq):
        """agenerateがLLMResponseを返す"""
        mock_llm = Mock()
        mock_llm.ainvoke = AsyncMock(return_value=Mock(content="Async Groq"))
        mock_chat_groq.return_value = mock_llm

        config = LLMConfig(api_key="test-key")
        provider = GroqProvider(config)
        response = await provider.agenerate("Hello")

        assert isinstance(response, LLMResponse)
        assert response.content == "Async Groq"
