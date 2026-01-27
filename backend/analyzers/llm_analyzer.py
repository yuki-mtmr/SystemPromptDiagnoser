"""
LLMベース認知特性分析器

ルールベースマッピングではなく、LLMによる真の個別分析を行う
"""
import json
from typing import Any

from analyzers.protocols import AnalysisInput, PersonalityTraits
from prompts.analysis_prompts import ANALYSIS_SYSTEM_PROMPT, build_analysis_prompt
from providers.protocols import LLMProvider


class LLMPersonalityAnalyzer:
    """
    LLMベース認知特性分析器

    LLMを使用してユーザーの認知特性を分析する
    ルールベースのマッピングではなく、文脈を理解した真の個別分析を行う
    """

    DEFAULT_TEMPERATURE = 0.3  # 一貫性のため低め

    def __init__(self, provider: LLMProvider):
        """
        分析器を初期化

        Args:
            provider: LLMプロバイダー
        """
        self._provider = provider

    def _parse_json_response(self, response: str) -> dict[str, Any]:
        """JSONレスポンスをパース"""
        # マークダウンコードブロックを処理
        if "```json" in response:
            start = response.find("```json") + 7
            end = response.find("```", start)
            response = response[start:end].strip()
        elif "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            response = response[start:end].strip()

        return json.loads(response)

    def _get_formatting_principles(self, parsed: dict[str, Any]) -> list[str]:
        """認知特性から原則ベースのガイドラインを生成"""
        thinking = parsed.get("thinking_pattern", "hybrid")
        detail = parsed.get("detail_orientation", "medium")
        structure = parsed.get("preferred_structure", "hierarchical")
        learning = parsed.get("learning_type", "visual_text")

        principles = []

        # 思考パターンに基づく原則
        if thinking == "structural":
            principles.append("全体構造（マクロ）から詳細（ミクロ）へ順に説明")
            principles.append("階層構造・関係性・位置づけを明確にする")
        elif thinking == "fluid":
            principles.append("文脈と流れを重視し、自然な説明順序で展開")
            principles.append("具体例から一般化へ帰納的に説明")
        else:  # hybrid
            principles.append("状況に応じて全体像と具体例を使い分ける")

        # 詳細志向に基づく原則
        if detail == "high":
            principles.append("網羅的な情報を段階的に提示")
            principles.append("長文では適宜小結論を挟む")
        elif detail == "low":
            principles.append("核心的情報に絞り、簡潔に")
            principles.append("詳細は追加質問を待って展開")
        else:  # medium
            principles.append("バランスの取れた情報量で要点を明確に")

        # 構造の好みに基づく原則
        if structure == "hierarchical":
            principles.append("箇条書き・表・階層構造を活用して整理")
        elif structure == "flat":
            principles.append("フラットな箇条書きでシンプルに")
        else:  # contextual
            principles.append("文脈に応じた柔軟な構造で")

        # 学習タイプに基づく原則
        if learning == "kinesthetic":
            principles.append("実践的な例やハンズオンを優先")
        elif learning == "visual_diagram":
            principles.append("図表やフローで視覚的に表現")

        return principles

    def analyze(self, input: AnalysisInput) -> PersonalityTraits:
        """
        同期的に認知特性を分析

        Args:
            input: 分析入力

        Returns:
            PersonalityTraits: 抽出された認知特性
        """
        # プロンプトを構築
        prompt = build_analysis_prompt(
            answers=input.answers,
            conversation_context=input.conversation_context,
        )

        # LLMを呼び出し
        response = self._provider.generate(
            prompt,
            system_prompt=ANALYSIS_SYSTEM_PROMPT,
            temperature=self.DEFAULT_TEMPERATURE,
        )

        # レスポンスをパース
        parsed = self._parse_json_response(response.content)

        # PersonalityTraitsを構築
        return PersonalityTraits(
            thinking_pattern=parsed["thinking_pattern"],
            learning_type=parsed["learning_type"],
            detail_orientation=parsed["detail_orientation"],
            preferred_structure=parsed["preferred_structure"],
            use_tables=parsed.get("use_tables", False),
            avoid_patterns=parsed.get("avoid_patterns", []),
            persona_summary=parsed["persona_summary"],
            formatting_principles=self._get_formatting_principles(parsed),
        )

    async def aanalyze(self, input: AnalysisInput) -> PersonalityTraits:
        """
        非同期的に認知特性を分析

        Args:
            input: 分析入力

        Returns:
            PersonalityTraits: 抽出された認知特性
        """
        # プロンプトを構築
        prompt = build_analysis_prompt(
            answers=input.answers,
            conversation_context=input.conversation_context,
        )

        # LLMを非同期で呼び出し
        response = await self._provider.agenerate(
            prompt,
            system_prompt=ANALYSIS_SYSTEM_PROMPT,
            temperature=self.DEFAULT_TEMPERATURE,
        )

        # レスポンスをパース
        parsed = self._parse_json_response(response.content)

        # PersonalityTraitsを構築
        return PersonalityTraits(
            thinking_pattern=parsed["thinking_pattern"],
            learning_type=parsed["learning_type"],
            detail_orientation=parsed["detail_orientation"],
            preferred_structure=parsed["preferred_structure"],
            use_tables=parsed.get("use_tables", False),
            avoid_patterns=parsed.get("avoid_patterns", []),
            persona_summary=parsed["persona_summary"],
            formatting_principles=self._get_formatting_principles(parsed),
        )
