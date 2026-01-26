"""
LLMProvider Protocol のテスト
TDD: RED - まずテストを書き、失敗を確認してから実装
"""
import pytest
from typing import Protocol, runtime_checkable

from providers.protocols import LLMProvider, LLMResponse, LLMConfig


class TestLLMResponseModel:
    """LLMResponse モデルのテスト"""

    def test_llm_response_has_content_field(self):
        """LLMResponseはcontentフィールドを持つ"""
        response = LLMResponse(content="Hello, world!")
        assert response.content == "Hello, world!"

    def test_llm_response_has_optional_raw_response(self):
        """LLMResponseはオプションのraw_responseを持つ"""
        response = LLMResponse(content="test", raw_response={"key": "value"})
        assert response.raw_response == {"key": "value"}

    def test_llm_response_has_optional_usage(self):
        """LLMResponseはオプションのusage情報を持つ"""
        response = LLMResponse(
            content="test",
            usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}
        )
        assert response.usage["total_tokens"] == 30

    def test_llm_response_has_optional_model_name(self):
        """LLMResponseはオプションのmodel_nameを持つ"""
        response = LLMResponse(content="test", model_name="gpt-4o")
        assert response.model_name == "gpt-4o"


class TestLLMConfigModel:
    """LLMConfig モデルのテスト"""

    def test_llm_config_has_api_key(self):
        """LLMConfigはapi_keyフィールドを持つ"""
        config = LLMConfig(api_key="sk-test-key")
        assert config.api_key == "sk-test-key"

    def test_llm_config_has_optional_model(self):
        """LLMConfigはオプションのmodelフィールドを持つ"""
        config = LLMConfig(api_key="key", model="gpt-4o")
        assert config.model == "gpt-4o"

    def test_llm_config_has_optional_temperature(self):
        """LLMConfigはオプションのtemperatureを持つ"""
        config = LLMConfig(api_key="key", temperature=0.3)
        assert config.temperature == 0.3

    def test_llm_config_has_optional_max_tokens(self):
        """LLMConfigはオプションのmax_tokensを持つ"""
        config = LLMConfig(api_key="key", max_tokens=2048)
        assert config.max_tokens == 2048

    def test_llm_config_has_optional_timeout(self):
        """LLMConfigはオプションのtimeoutを持つ"""
        config = LLMConfig(api_key="key", timeout=30)
        assert config.timeout == 30


class TestLLMProviderProtocol:
    """LLMProvider Protocol のテスト"""

    def test_protocol_is_runtime_checkable(self):
        """LLMProviderはランタイムチェック可能"""
        assert hasattr(LLMProvider, "__protocol_attrs__") or hasattr(LLMProvider, "_is_runtime_protocol")

    def test_protocol_has_generate_method(self):
        """LLMProviderはgenerateメソッドを持つ"""
        # Protocol自体がgenerateを定義しているか確認
        assert hasattr(LLMProvider, "generate")

    def test_protocol_has_agenerate_method(self):
        """LLMProviderはagenerateメソッドを持つ"""
        assert hasattr(LLMProvider, "agenerate")

    def test_protocol_has_provider_name_property(self):
        """LLMProviderはprovider_nameプロパティを持つ"""
        assert "provider_name" in dir(LLMProvider) or hasattr(LLMProvider, "provider_name")

    def test_mock_provider_implements_protocol(self):
        """モックプロバイダーがProtocolを実装していることを確認"""
        class MockProvider:
            @property
            def provider_name(self) -> str:
                return "mock"

            def generate(self, prompt: str, system_prompt: str | None = None, **kwargs) -> LLMResponse:
                return LLMResponse(content="mock response")

            async def agenerate(self, prompt: str, system_prompt: str | None = None, **kwargs) -> LLMResponse:
                return LLMResponse(content="mock async response")

        provider = MockProvider()
        # runtime_checkable プロトコルの isinstance チェック
        assert isinstance(provider, LLMProvider)


class TestLLMProviderContract:
    """LLMProvider の契約テスト"""

    def test_generate_returns_llm_response(self):
        """generateメソッドはLLMResponseを返す"""
        class TestProvider:
            @property
            def provider_name(self) -> str:
                return "test"

            def generate(self, prompt: str, system_prompt: str | None = None, **kwargs) -> LLMResponse:
                return LLMResponse(content=f"Response to: {prompt}")

            async def agenerate(self, prompt: str, system_prompt: str | None = None, **kwargs) -> LLMResponse:
                return LLMResponse(content=f"Async response to: {prompt}")

        provider = TestProvider()
        result = provider.generate("Hello")

        assert isinstance(result, LLMResponse)
        assert "Hello" in result.content

    @pytest.mark.asyncio
    async def test_agenerate_returns_llm_response(self):
        """agenerateメソッドはLLMResponseを返す"""
        class TestProvider:
            @property
            def provider_name(self) -> str:
                return "test"

            def generate(self, prompt: str, system_prompt: str | None = None, **kwargs) -> LLMResponse:
                return LLMResponse(content=f"Response to: {prompt}")

            async def agenerate(self, prompt: str, system_prompt: str | None = None, **kwargs) -> LLMResponse:
                return LLMResponse(content=f"Async response to: {prompt}")

        provider = TestProvider()
        result = await provider.agenerate("Hello")

        assert isinstance(result, LLMResponse)
        assert "Hello" in result.content

    def test_generate_accepts_system_prompt(self):
        """generateメソッドはsystem_promptを受け取る"""
        class TestProvider:
            @property
            def provider_name(self) -> str:
                return "test"

            def generate(self, prompt: str, system_prompt: str | None = None, **kwargs) -> LLMResponse:
                if system_prompt:
                    return LLMResponse(content=f"System: {system_prompt}, User: {prompt}")
                return LLMResponse(content=f"User: {prompt}")

            async def agenerate(self, prompt: str, system_prompt: str | None = None, **kwargs) -> LLMResponse:
                return LLMResponse(content="async")

        provider = TestProvider()
        result = provider.generate("Hello", system_prompt="Be helpful")

        assert "System: Be helpful" in result.content

    def test_generate_accepts_kwargs(self):
        """generateメソッドは追加のkwargsを受け取る"""
        class TestProvider:
            @property
            def provider_name(self) -> str:
                return "test"

            def generate(self, prompt: str, system_prompt: str | None = None, **kwargs) -> LLMResponse:
                temp = kwargs.get("temperature", 1.0)
                return LLMResponse(content=f"temp={temp}")

            async def agenerate(self, prompt: str, system_prompt: str | None = None, **kwargs) -> LLMResponse:
                return LLMResponse(content="async")

        provider = TestProvider()
        result = provider.generate("test", temperature=0.5)

        assert "temp=0.5" in result.content
