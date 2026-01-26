"""
分析プロンプトのテスト
TDD: RED - まずテストを書き、失敗を確認してから実装
"""
import pytest

from prompts.analysis_prompts import (
    PERSONALITY_ANALYSIS_PROMPT,
    ANALYSIS_SYSTEM_PROMPT,
    build_analysis_prompt,
)


class TestAnalysisPrompts:
    """分析プロンプトのテスト"""

    def test_personality_analysis_prompt_exists(self):
        """PERSONALITY_ANALYSIS_PROMPTが存在する"""
        assert PERSONALITY_ANALYSIS_PROMPT is not None
        assert len(PERSONALITY_ANALYSIS_PROMPT) > 100

    def test_personality_analysis_prompt_contains_placeholders(self):
        """プロンプトに必要なプレースホルダーが含まれる"""
        assert "{answers}" in PERSONALITY_ANALYSIS_PROMPT
        assert "{conversation_context}" in PERSONALITY_ANALYSIS_PROMPT

    def test_personality_analysis_prompt_requests_json_output(self):
        """プロンプトがJSON出力を要求"""
        assert "JSON" in PERSONALITY_ANALYSIS_PROMPT or "json" in PERSONALITY_ANALYSIS_PROMPT

    def test_personality_analysis_prompt_includes_required_traits(self):
        """プロンプトが必要な特性を含む"""
        required_traits = [
            "thinking_pattern",
            "learning_type",
            "detail_orientation",
            "preferred_structure",
            "avoid_patterns",
            "persona_summary",
        ]
        for trait in required_traits:
            assert trait in PERSONALITY_ANALYSIS_PROMPT, f"Missing trait: {trait}"

    def test_analysis_system_prompt_exists(self):
        """ANALYSIS_SYSTEM_PROMPTが存在する"""
        assert ANALYSIS_SYSTEM_PROMPT is not None
        assert len(ANALYSIS_SYSTEM_PROMPT) > 50

    def test_analysis_system_prompt_emphasizes_individuality(self):
        """システムプロンプトが個別分析を強調"""
        # 個別分析の重要性を示す言葉が含まれる
        assert any(word in ANALYSIS_SYSTEM_PROMPT.lower() for word in [
            "unique", "individual", "specific", "personalized",
            "固有", "個別", "具体的"
        ])


class TestBuildAnalysisPrompt:
    """build_analysis_prompt関数のテスト"""

    def test_build_prompt_with_answers_only(self):
        """回答のみでプロンプトを構築"""
        answers = {
            "purpose": "コードレビュー",
            "autonomy": "collaborative"
        }

        prompt = build_analysis_prompt(answers)

        assert "コードレビュー" in prompt
        assert "collaborative" in prompt

    def test_build_prompt_with_conversation_context(self):
        """会話コンテキスト付きでプロンプトを構築"""
        answers = {
            "purpose": "coding help",
            "autonomy": "autonomous"
        }
        conversation = "User: How do I fix this bug?\nAssistant: Let me analyze..."

        prompt = build_analysis_prompt(answers, conversation_context=conversation)

        assert "coding help" in prompt
        assert "fix this bug" in prompt or "conversation" in prompt.lower()

    def test_build_prompt_handles_empty_conversation(self):
        """空の会話コンテキストを処理"""
        answers = {"purpose": "test", "autonomy": "obedient"}

        prompt = build_analysis_prompt(answers, conversation_context="")

        assert "test" in prompt
        # 空のコンテキストでもプロンプトが生成される
        assert len(prompt) > 0

    def test_build_prompt_escapes_special_characters(self):
        """特殊文字をエスケープ"""
        answers = {
            "purpose": "Help with {templates} and \"quotes\"",
            "autonomy": "collaborative"
        }

        prompt = build_analysis_prompt(answers)

        # プロンプトが生成されることを確認（例外が発生しない）
        assert len(prompt) > 0
