"""
プロバイダー設定スキーマ

プロバイダー情報とAPI設定用のスキーマ
"""
from typing import Literal

from pydantic import BaseModel, Field


class ProviderInfo(BaseModel):
    """プロバイダー情報"""

    id: str = Field(..., description="プロバイダーID")
    name: str = Field(..., description="プロバイダー名")
    default_model: str = Field(..., description="デフォルトモデル")
    available_models: list[str] = Field(
        default_factory=list, description="利用可能なモデル一覧"
    )
    description: str = Field(..., description="プロバイダーの説明")


class ProvidersResponse(BaseModel):
    """プロバイダー一覧レスポンス"""

    providers: list[ProviderInfo] = Field(..., description="プロバイダー一覧")


class ProviderConfig(BaseModel):
    """プロバイダー設定"""

    provider: Literal["openai", "groq", "gemini"] = Field(
        ..., description="プロバイダータイプ"
    )
    api_key: str = Field(..., description="APIキー")
    model: str | None = Field(default=None, description="使用するモデル（省略時はデフォルト）")
