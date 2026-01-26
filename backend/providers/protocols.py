"""
LLMプロバイダー Protocol 定義

SOLID原則に従い、依存性逆転を実現するためのProtocol定義
"""
from typing import Any, Protocol, runtime_checkable

from pydantic import BaseModel, Field


class LLMResponse(BaseModel):
    """
    LLM応答モデル

    全てのプロバイダーからの応答を統一的に表現
    """

    content: str = Field(..., description="LLMからの応答テキスト")
    raw_response: dict[str, Any] | None = Field(
        default=None, description="プロバイダー固有の生レスポンス"
    )
    usage: dict[str, int] | None = Field(
        default=None, description="トークン使用量（prompt_tokens, completion_tokens, total_tokens）"
    )
    model_name: str | None = Field(
        default=None, description="使用されたモデル名"
    )


class LLMConfig(BaseModel):
    """
    LLM設定モデル

    プロバイダーの初期化に必要な設定を定義
    """

    api_key: str = Field(..., description="APIキー")
    model: str | None = Field(default=None, description="モデル名（省略時はプロバイダーのデフォルト）")
    temperature: float | None = Field(default=None, description="温度パラメータ（0.0-2.0）")
    max_tokens: int | None = Field(default=None, description="最大トークン数")
    timeout: int | None = Field(default=None, description="タイムアウト秒数")


@runtime_checkable
class LLMProvider(Protocol):
    """
    LLMプロバイダー Protocol

    全てのLLMプロバイダーが実装すべきインターフェース
    """

    @property
    def provider_name(self) -> str:
        """プロバイダー名を返す"""
        ...

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
            **kwargs: プロバイダー固有の追加パラメータ

        Returns:
            LLMResponse: LLMからの応答
        """
        ...

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
            **kwargs: プロバイダー固有の追加パラメータ

        Returns:
            LLMResponse: LLMからの応答
        """
        ...
