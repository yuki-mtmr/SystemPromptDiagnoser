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

    def _get_formatting_rules(self, detail_orientation: str) -> dict[str, str]:
        """detail_orientationに基づいてformatting_rulesを生成"""
        rules = {
            "high": {
                "paragraph_length": "80-120語/段落",
                "heading_length": "10-20トークン",
                "list_items": "3-7項目",
            },
            "medium": {
                "paragraph_length": "60-100語/段落",
                "heading_length": "10-15トークン",
                "list_items": "3-5項目",
            },
            "low": {
                "paragraph_length": "40-80語/段落",
                "heading_length": "5-10トークン",
                "list_items": "2-4項目",
            },
        }
        return rules.get(detail_orientation, rules["medium"])

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
            formatting_rules=self._get_formatting_rules(parsed["detail_orientation"]),
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
            formatting_rules=self._get_formatting_rules(parsed["detail_orientation"]),
        )
