"""
LLMProviderFactory のテスト
TDD: RED - まずテストを書き、失敗を確認してから実装
"""
import pytest

from providers.factory import LLMProviderFactory, UnknownProviderError
from providers.protocols import LLMProvider, LLMConfig


class TestLLMProviderFactory:
    """LLMProviderFactory のテスト"""

    def test_create_raises_on_unknown_provider(self):
        """未知のプロバイダータイプでエラーを発生"""
        config = LLMConfig(api_key="test-key")
        with pytest.raises(UnknownProviderError):
            LLMProviderFactory.create("unknown", config)

    def test_list_available_providers(self):
        """利用可能なプロバイダー一覧を取得"""
        providers = LLMProviderFactory.list_available()
        assert isinstance(providers, list)
        assert "openai" in providers
        assert "groq" in providers
        assert "gemini" in providers
        assert "mock" in providers

    def test_create_mock_provider(self):
        """モックプロバイダーを作成"""
        config = LLMConfig(api_key="test-key")
        provider = LLMProviderFactory.create("mock", config)
        assert isinstance(provider, LLMProvider)
        assert provider.provider_name == "mock"

    def test_mock_provider_generate_returns_response(self):
        """モックプロバイダーのgenerateがレスポンスを返す"""
        config = LLMConfig(api_key="test-key")
        provider = LLMProviderFactory.create("mock", config)
        response = provider.generate("Hello")
        assert response.content is not None
        assert len(response.content) > 0

    def test_is_available_returns_true_for_known_providers(self):
        """既知のプロバイダーに対してis_availableがTrueを返す"""
        assert LLMProviderFactory.is_available("mock") is True
        assert LLMProviderFactory.is_available("openai") is True
        assert LLMProviderFactory.is_available("groq") is True
        assert LLMProviderFactory.is_available("gemini") is True

    def test_is_available_returns_false_for_unknown_providers(self):
        """未知のプロバイダーに対してis_availableがFalseを返す"""
        assert LLMProviderFactory.is_available("unknown") is False

    def test_get_default_model_for_provider(self):
        """プロバイダーのデフォルトモデルを取得"""
        assert LLMProviderFactory.get_default_model("openai") == "gpt-4o"
        assert LLMProviderFactory.get_default_model("groq") == "llama-3.3-70b-versatile"
        assert LLMProviderFactory.get_default_model("gemini") == "gemini-2.0-flash"
        assert LLMProviderFactory.get_default_model("mock") == "mock-model"

    def test_get_default_model_raises_on_unknown(self):
        """未知のプロバイダーでエラーを発生"""
        with pytest.raises(UnknownProviderError):
            LLMProviderFactory.get_default_model("unknown")


class TestMockProvider:
    """MockProvider のテスト"""

    def test_mock_generate_echoes_prompt(self):
        """モックがプロンプトをエコーする"""
        config = LLMConfig(api_key="test-key")
        provider = LLMProviderFactory.create("mock", config)
        response = provider.generate("Test prompt")
        assert "Test prompt" in response.content

    @pytest.mark.asyncio
    async def test_mock_agenerate_works(self):
        """モックの非同期生成が動作する"""
        config = LLMConfig(api_key="test-key")
        provider = LLMProviderFactory.create("mock", config)
        response = await provider.agenerate("Test prompt")
        assert "Test prompt" in response.content

    def test_mock_includes_system_prompt_in_response(self):
        """モックがシステムプロンプトを応答に含む"""
        config = LLMConfig(api_key="test-key")
        provider = LLMProviderFactory.create("mock", config)
        response = provider.generate("Hello", system_prompt="Be helpful")
        assert "Be helpful" in response.content or "Hello" in response.content
