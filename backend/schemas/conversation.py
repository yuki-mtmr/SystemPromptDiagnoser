"""
会話アップロード用スキーマ

過去のAI会話をアップロードするためのリクエスト/レスポンスモデル
"""
from typing import Literal

from pydantic import BaseModel, Field


class ConversationUploadRequest(BaseModel):
    """会話アップロードリクエスト"""

    content: str = Field(..., description="会話データ（JSON文字列またはマークダウン）")
    format: Literal["chatgpt_json", "claude_json", "markdown", "auto"] = Field(
        default="auto", description="会話データのフォーマット"
    )


class ConversationUploadResponse(BaseModel):
    """会話アップロードレスポンス"""

    success: bool = Field(..., description="パース成功フラグ")
    message_count: int = Field(..., description="抽出されたメッセージ数")
    user_message_count: int = Field(..., description="ユーザーメッセージ数")
    detected_format: str = Field(..., description="検出されたフォーマット")
    context_preview: str = Field(..., description="コンテキストのプレビュー（最初の500文字）")
