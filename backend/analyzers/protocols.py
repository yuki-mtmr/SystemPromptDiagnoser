"""
分析 Protocol 定義

認知特性分析のための Protocol と データモデル
"""
from typing import Any, Literal, Protocol, runtime_checkable

from pydantic import BaseModel, Field


class AnalysisInput(BaseModel):
    """
    分析入力モデル

    分析に必要なユーザー回答と追加コンテキスト
    """

    answers: dict[str, Any] = Field(..., description="ユーザーの回答")
    conversation_context: str | None = Field(
        default=None, description="過去のAI会話からのコンテキスト"
    )


class PersonalityTraits(BaseModel):
    """
    認知特性モデル

    分析結果として抽出された認知特性
    """

    thinking_pattern: Literal["structural", "fluid", "hybrid"] = Field(
        ..., description="思考パターン"
    )
    learning_type: Literal["visual_text", "visual_diagram", "auditory", "kinesthetic"] = Field(
        ..., description="学習タイプ"
    )
    detail_orientation: Literal["high", "medium", "low"] = Field(
        ..., description="詳細志向度"
    )
    preferred_structure: Literal["hierarchical", "flat", "contextual"] = Field(
        ..., description="好む情報構造"
    )
    use_tables: bool = Field(default=False, description="表の使用好み")
    avoid_patterns: list[str] = Field(
        default_factory=list, description="回避すべきパターン"
    )
    persona_summary: str = Field(..., description="ペルソナの一文説明")
    formatting_rules: dict[str, str] = Field(
        default_factory=dict, description="フォーマットルール"
    )


@runtime_checkable
class PersonalityAnalyzer(Protocol):
    """
    認知特性分析 Protocol

    ユーザー回答からの認知特性抽出を行う分析器のインターフェース
    """

    def analyze(self, input: AnalysisInput) -> PersonalityTraits:
        """
        同期的に認知特性を分析

        Args:
            input: 分析入力

        Returns:
            PersonalityTraits: 抽出された認知特性
        """
        ...

    async def aanalyze(self, input: AnalysisInput) -> PersonalityTraits:
        """
        非同期的に認知特性を分析

        Args:
            input: 分析入力

        Returns:
            PersonalityTraits: 抽出された認知特性
        """
        ...
