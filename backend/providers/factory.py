"""
LLMプロバイダー ファクトリー

プロバイダータイプからLLMProviderインスタンスを生成
"""
from providers.protocols import LLMConfig, LLMProvider, LLMResponse
from providers.openai_provider import OpenAIProvider
from providers.groq_provider import GroqProvider
from providers.gemini_provider import GeminiProvider


class UnknownProviderError(Exception):
    """未知のプロバイダータイプ"""

    def __init__(self, provider_type: str):
        self.provider_type = provider_type
        super().__init__(f"Unknown provider type: {provider_type}")


class MockProvider:
    """
    テスト用モックプロバイダー

    実際のAPI呼び出しを行わず、プロンプトをエコーする
    """

    def __init__(self, config: LLMConfig):
        self._config = config

    @property
    def provider_name(self) -> str:
        return "mock"

    def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        **kwargs,
    ) -> LLMResponse:
        """モック応答を生成"""
        content_parts = []
        if system_prompt:
            content_parts.append(f"[System: {system_prompt}]")
        content_parts.append(f"[Mock response to: {prompt}]")

        return LLMResponse(
            content=" ".join(content_parts),
            model_name="mock-model",
        )

    async def agenerate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        **kwargs,
    ) -> LLMResponse:
        """モック非同期応答を生成"""
        return self.generate(prompt, system_prompt, **kwargs)


# プロバイダーのデフォルトモデル
DEFAULT_MODELS = {
    "openai": "gpt-4o",
    "groq": "llama-3.3-70b-versatile",
    "gemini": "gemini-2.0-flash",
    "mock": "mock-model",
}


class LLMProviderFactory:
    """
    LLMプロバイダー ファクトリー

    プロバイダータイプからLLMProviderインスタンスを生成する
    """

    _providers = {
        "openai": OpenAIProvider,
        "groq": GroqProvider,
        "gemini": GeminiProvider,
        "mock": MockProvider,
    }

    @classmethod
    def create(cls, provider_type: str, config: LLMConfig) -> LLMProvider:
        """
        プロバイダーインスタンスを作成

        Args:
            provider_type: プロバイダータイプ（openai, groq, gemini, mock）
            config: LLM設定

        Returns:
            LLMProvider: プロバイダーインスタンス

        Raises:
            UnknownProviderError: 未知のプロバイダータイプの場合
        """
        if provider_type not in cls._providers:
            raise UnknownProviderError(provider_type)

        provider_class = cls._providers[provider_type]
        return provider_class(config)

    @classmethod
    def register(cls, provider_type: str, provider_class: type) -> None:
        """
        プロバイダーを登録

        Args:
            provider_type: プロバイダータイプ
            provider_class: プロバイダークラス
        """
        cls._providers[provider_type] = provider_class

    @classmethod
    def list_available(cls) -> list[str]:
        """
        利用可能なプロバイダー一覧を返す

        Returns:
            list[str]: プロバイダータイプのリスト
        """
        # 登録済みと予定されているプロバイダーを含む
        return ["openai", "groq", "gemini", "mock"]

    @classmethod
    def is_available(cls, provider_type: str) -> bool:
        """
        プロバイダーが利用可能かどうか

        Args:
            provider_type: プロバイダータイプ

        Returns:
            bool: 利用可能な場合True
        """
        return provider_type in cls.list_available()

    @classmethod
    def get_default_model(cls, provider_type: str) -> str:
        """
        プロバイダーのデフォルトモデルを取得

        Args:
            provider_type: プロバイダータイプ

        Returns:
            str: デフォルトモデル名

        Raises:
            UnknownProviderError: 未知のプロバイダータイプの場合
        """
        if provider_type not in DEFAULT_MODELS:
            raise UnknownProviderError(provider_type)
        return DEFAULT_MODELS[provider_type]
