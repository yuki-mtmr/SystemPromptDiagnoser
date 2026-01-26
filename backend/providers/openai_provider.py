"""
OpenAI LLMプロバイダー

OpenAI API を使用したLLMプロバイダー実装
"""
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from providers.protocols import LLMConfig, LLMResponse


class OpenAIProvider:
    """
    OpenAI LLMプロバイダー

    OpenAI API (GPT-4o, GPT-4o-mini など) を使用
    """

    DEFAULT_MODEL = "gpt-4o"
    DEFAULT_TEMPERATURE = 0.7
    DEFAULT_MAX_TOKENS = 2048

    def __init__(self, config: LLMConfig):
        """
        OpenAIプロバイダーを初期化

        Args:
            config: LLM設定
        """
        self._config = config
        self._model_name = config.model or self.DEFAULT_MODEL
        self._temperature = config.temperature if config.temperature is not None else self.DEFAULT_TEMPERATURE
        self._max_tokens = config.max_tokens or self.DEFAULT_MAX_TOKENS
        self._llm = None

    @property
    def provider_name(self) -> str:
        return "openai"

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def temperature(self) -> float:
        return self._temperature

    @property
    def llm(self) -> ChatOpenAI:
        """LLMインスタンス（遅延初期化）"""
        if self._llm is None:
            self._llm = ChatOpenAI(
                model=self._model_name,
                api_key=self._config.api_key,
                temperature=self._temperature,
                max_tokens=self._max_tokens,
            )
        return self._llm

    def _build_messages(
        self,
        prompt: str,
        system_prompt: str | None = None,
    ) -> list:
        """メッセージリストを構築"""
        messages = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=prompt))
        return messages

    def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """
        同期的にLLM応答を生成

        Args:
            prompt: ユーザープロンプト
            system_prompt: システムプロンプト（オプション）
            **kwargs: 追加パラメータ

        Returns:
            LLMResponse: LLMからの応答
        """
        messages = self._build_messages(prompt, system_prompt)
        response = self.llm.invoke(messages, **kwargs)

        return LLMResponse(
            content=response.content,
            model_name=self._model_name,
        )

    async def agenerate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """
        非同期的にLLM応答を生成

        Args:
            prompt: ユーザープロンプト
            system_prompt: システムプロンプト（オプション）
            **kwargs: 追加パラメータ

        Returns:
            LLMResponse: LLMからの応答
        """
        messages = self._build_messages(prompt, system_prompt)
        response = await self.llm.ainvoke(messages, **kwargs)

        return LLMResponse(
            content=response.content,
            model_name=self._model_name,
        )
