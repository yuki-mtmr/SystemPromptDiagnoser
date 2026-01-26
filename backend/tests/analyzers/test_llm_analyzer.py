"""
LLMPersonalityAnalyzer のテスト
TDD: RED - まずテストを書き、失敗を確認してから実装
"""
import pytest
from unittest.mock import Mock, AsyncMock
import json

from analyzers.llm_analyzer import LLMPersonalityAnalyzer
from analyzers.protocols import PersonalityAnalyzer, AnalysisInput, PersonalityTraits
from providers.protocols import LLMProvider, LLMResponse


class TestLLMPersonalityAnalyzer:
    """LLMPersonalityAnalyzer のテスト"""

    def test_implements_personality_analyzer_protocol(self):
        """LLMPersonalityAnalyzerがPersonalityAnalyzerプロトコルを実装"""
        mock_provider = Mock(spec=LLMProvider)
        analyzer = LLMPersonalityAnalyzer(mock_provider)
        assert isinstance(analyzer, PersonalityAnalyzer)

    def test_analyze_uses_llm_provider(self):
        """analyzeがLLMプロバイダーを使用"""
        mock_provider = Mock(spec=LLMProvider)
        mock_provider.generate.return_value = LLMResponse(
            content=json.dumps({
                "thinking_pattern": "structural",
                "learning_type": "visual_text",
                "detail_orientation": "high",
                "preferred_structure": "hierarchical",
                "use_tables": True,
                "avoid_patterns": ["過度な絵文字"],
                "persona_summary": "私は構造的な学習者です。",
                "analysis_reasoning": "回答から判断",
            })
        )

        analyzer = LLMPersonalityAnalyzer(mock_provider)
        input_data = AnalysisInput(
            answers={"purpose": "コードレビュー", "autonomy": "collaborative"}
        )
        result = analyzer.analyze(input_data)

        mock_provider.generate.assert_called_once()
        assert result.thinking_pattern == "structural"

    def test_analyze_returns_personality_traits(self):
        """analyzeがPersonalityTraitsを返す"""
        mock_provider = Mock(spec=LLMProvider)
        mock_provider.generate.return_value = LLMResponse(
            content=json.dumps({
                "thinking_pattern": "fluid",
                "learning_type": "kinesthetic",
                "detail_orientation": "low",
                "preferred_structure": "flat",
                "use_tables": False,
                "avoid_patterns": ["長すぎる説明"],
                "persona_summary": "I am a hands-on learner.",
                "analysis_reasoning": "Based on responses",
            })
        )

        analyzer = LLMPersonalityAnalyzer(mock_provider)
        input_data = AnalysisInput(
            answers={"purpose": "quick coding help", "autonomy": "autonomous"}
        )
        result = analyzer.analyze(input_data)

        assert isinstance(result, PersonalityTraits)
        assert result.thinking_pattern == "fluid"
        assert result.learning_type == "kinesthetic"
        assert result.detail_orientation == "low"

    def test_different_answers_produce_different_calls(self):
        """異なる回答で異なるLLM呼び出しが行われる"""
        mock_provider = Mock(spec=LLMProvider)
        mock_provider.generate.return_value = LLMResponse(
            content=json.dumps({
                "thinking_pattern": "hybrid",
                "learning_type": "visual_text",
                "detail_orientation": "medium",
                "preferred_structure": "contextual",
                "use_tables": True,
                "avoid_patterns": [],
                "persona_summary": "test",
                "analysis_reasoning": "test",
            })
        )

        analyzer = LLMPersonalityAnalyzer(mock_provider)

        # 異なる回答で呼び出し
        input1 = AnalysisInput(answers={"purpose": "研究支援", "autonomy": "obedient"})
        input2 = AnalysisInput(answers={"purpose": "creative writing", "autonomy": "autonomous"})

        analyzer.analyze(input1)
        analyzer.analyze(input2)

        # 2回呼び出されたことを確認
        assert mock_provider.generate.call_count == 2

        # 呼び出し引数が異なることを確認
        call1_prompt = mock_provider.generate.call_args_list[0][0][0]
        call2_prompt = mock_provider.generate.call_args_list[1][0][0]
        assert call1_prompt != call2_prompt

    def test_includes_conversation_context_when_provided(self):
        """会話コンテキストが提供された場合に含める"""
        mock_provider = Mock(spec=LLMProvider)
        mock_provider.generate.return_value = LLMResponse(
            content=json.dumps({
                "thinking_pattern": "structural",
                "learning_type": "visual_text",
                "detail_orientation": "high",
                "preferred_structure": "hierarchical",
                "use_tables": True,
                "avoid_patterns": [],
                "persona_summary": "test",
                "analysis_reasoning": "test",
            })
        )

        analyzer = LLMPersonalityAnalyzer(mock_provider)
        input_data = AnalysisInput(
            answers={"purpose": "help", "autonomy": "collaborative"},
            conversation_context="User: How do I fix this?\nAssistant: Let me help..."
        )
        analyzer.analyze(input_data)

        # 呼び出し引数に会話コンテキストが含まれる
        call_prompt = mock_provider.generate.call_args[0][0]
        assert "How do I fix this" in call_prompt or "conversation" in call_prompt.lower()

    def test_handles_json_in_markdown_code_block(self):
        """マークダウンコードブロック内のJSONを処理"""
        mock_provider = Mock(spec=LLMProvider)
        mock_provider.generate.return_value = LLMResponse(
            content="""```json
{
    "thinking_pattern": "hybrid",
    "learning_type": "auditory",
    "detail_orientation": "medium",
    "preferred_structure": "contextual",
    "use_tables": false,
    "avoid_patterns": ["jargon"],
    "persona_summary": "I learn by discussion.",
    "analysis_reasoning": "test"
}
```"""
        )

        analyzer = LLMPersonalityAnalyzer(mock_provider)
        input_data = AnalysisInput(
            answers={"purpose": "discussion", "autonomy": "collaborative"}
        )
        result = analyzer.analyze(input_data)

        assert result.thinking_pattern == "hybrid"
        assert result.learning_type == "auditory"

    def test_uses_low_temperature_for_consistency(self):
        """一貫性のため低いtemperatureを使用"""
        mock_provider = Mock(spec=LLMProvider)
        mock_provider.generate.return_value = LLMResponse(
            content=json.dumps({
                "thinking_pattern": "structural",
                "learning_type": "visual_text",
                "detail_orientation": "high",
                "preferred_structure": "hierarchical",
                "use_tables": True,
                "avoid_patterns": [],
                "persona_summary": "test",
                "analysis_reasoning": "test",
            })
        )

        analyzer = LLMPersonalityAnalyzer(mock_provider)
        input_data = AnalysisInput(answers={"purpose": "test", "autonomy": "obedient"})
        analyzer.analyze(input_data)

        # temperatureが渡されていることを確認
        call_kwargs = mock_provider.generate.call_args[1]
        assert "temperature" in call_kwargs
        assert call_kwargs["temperature"] <= 0.5


class TestLLMPersonalityAnalyzerAsync:
    """LLMPersonalityAnalyzer 非同期テスト"""

    @pytest.mark.asyncio
    async def test_aanalyze_uses_agenerate(self):
        """aanalyzeがagenerateを使用"""
        mock_provider = Mock(spec=LLMProvider)
        mock_provider.agenerate = AsyncMock(return_value=LLMResponse(
            content=json.dumps({
                "thinking_pattern": "fluid",
                "learning_type": "kinesthetic",
                "detail_orientation": "low",
                "preferred_structure": "flat",
                "use_tables": False,
                "avoid_patterns": [],
                "persona_summary": "test",
                "analysis_reasoning": "test",
            })
        ))

        analyzer = LLMPersonalityAnalyzer(mock_provider)
        input_data = AnalysisInput(
            answers={"purpose": "quick help", "autonomy": "autonomous"}
        )
        result = await analyzer.aanalyze(input_data)

        mock_provider.agenerate.assert_called_once()
        assert result.thinking_pattern == "fluid"


class TestAnalysisInputModel:
    """AnalysisInput モデルのテスト"""

    def test_analysis_input_has_answers(self):
        """AnalysisInputはanswersフィールドを持つ"""
        input_data = AnalysisInput(
            answers={"purpose": "test", "autonomy": "collaborative"}
        )
        assert input_data.answers["purpose"] == "test"

    def test_analysis_input_has_optional_conversation_context(self):
        """AnalysisInputはオプションのconversation_contextを持つ"""
        input_data = AnalysisInput(
            answers={"purpose": "test", "autonomy": "collaborative"},
            conversation_context="Some conversation"
        )
        assert input_data.conversation_context == "Some conversation"

    def test_analysis_input_conversation_context_defaults_to_none(self):
        """conversation_contextのデフォルトはNone"""
        input_data = AnalysisInput(
            answers={"purpose": "test", "autonomy": "collaborative"}
        )
        assert input_data.conversation_context is None


class TestPersonalityTraitsModel:
    """PersonalityTraits モデルのテスト"""

    def test_personality_traits_has_all_required_fields(self):
        """PersonalityTraitsは全ての必須フィールドを持つ"""
        traits = PersonalityTraits(
            thinking_pattern="structural",
            learning_type="visual_text",
            detail_orientation="high",
            preferred_structure="hierarchical",
            use_tables=True,
            avoid_patterns=["test"],
            persona_summary="Test persona",
        )
        assert traits.thinking_pattern == "structural"
        assert traits.learning_type == "visual_text"
        assert traits.detail_orientation == "high"
        assert traits.preferred_structure == "hierarchical"
        assert traits.use_tables is True
        assert traits.avoid_patterns == ["test"]
        assert traits.persona_summary == "Test persona"
