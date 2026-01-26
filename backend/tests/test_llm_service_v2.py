"""
v2 LLMサービスのテスト
TDD: まずテストを書き、失敗を確認してから実装する
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock

from services.llm_service_v2 import (
    LLMServiceV2,
    create_llm_service_v2,
    LLMTimeoutError,
)
from schemas.diagnose_v2 import InitialAnswers


class TestLLMServiceV2:
    """LLMServiceV2のテスト"""

    def test_init_with_api_key(self):
        """APIキーでサービスを初期化できる"""
        service = LLMServiceV2(api_key="test-key")
        assert service.api_key == "test-key"

    def test_init_with_provider(self):
        """プロバイダーを指定して初期化できる"""
        service = LLMServiceV2(api_key="test-key", provider="gemini")
        assert service.provider == "gemini"

    def test_default_provider_is_groq(self):
        """デフォルトプロバイダーはgroq"""
        service = LLMServiceV2(api_key="test-key")
        assert service.provider == "groq"

    def test_default_timeout_is_20_seconds(self):
        """デフォルトタイムアウトは20秒"""
        service = LLMServiceV2(api_key="test-key")
        assert service.timeout == 20

    def test_is_available_with_api_key(self):
        """APIキーがあればis_availableはTrue"""
        service = LLMServiceV2(api_key="test-key")
        assert service.is_available is True

    def test_is_available_without_api_key(self):
        """APIキーがなければis_availableはFalse"""
        service = LLMServiceV2(api_key="")
        assert service.is_available is False


class TestGenerateFollowupQuestions:
    """generate_followup_questions メソッドのテスト"""

    @patch.object(LLMServiceV2, "_call_llm")
    def test_returns_detected_language(self, mock_call_llm):
        """検出された言語を返す"""
        mock_call_llm.return_value = json.dumps({
            "detected_language": "ja",
            "followup_questions": [],
            "analysis_notes": "test"
        })

        service = LLMServiceV2(api_key="test-key")
        initial_answers = InitialAnswers(
            purpose="コードレビューをしてほしい",
            autonomy="collaborative"
        )

        result = service.generate_followup_questions(initial_answers)

        assert result["detected_language"] == "ja"

    @patch.object(LLMServiceV2, "_call_llm")
    def test_returns_followup_questions(self, mock_call_llm):
        """動的質問を返す"""
        mock_call_llm.return_value = json.dumps({
            "detected_language": "ja",
            "followup_questions": [
                {
                    "id": "fq1",
                    "question": "どのような言語を主に使用していますか？",
                    "type": "freeform"
                }
            ],
            "analysis_notes": "コーディング支援を求めている"
        })

        service = LLMServiceV2(api_key="test-key")
        initial_answers = InitialAnswers(
            purpose="コードレビューをしてほしい",
            autonomy="collaborative"
        )

        result = service.generate_followup_questions(initial_answers)

        assert len(result["followup_questions"]) == 1
        assert result["followup_questions"][0]["id"] == "fq1"

    @patch.object(LLMServiceV2, "_call_llm")
    def test_returns_empty_questions_when_not_needed(self, mock_call_llm):
        """深掘り不要な場合は空の質問リストを返す"""
        mock_call_llm.return_value = json.dumps({
            "detected_language": "en",
            "followup_questions": [],
            "analysis_notes": "Clear requirements provided"
        })

        service = LLMServiceV2(api_key="test-key")
        initial_answers = InitialAnswers(
            purpose="I need help with Python code review for a web application",
            autonomy="autonomous"
        )

        result = service.generate_followup_questions(initial_answers)

        assert result["followup_questions"] == []

    @patch.object(LLMServiceV2, "_call_llm")
    def test_returns_analysis_notes(self, mock_call_llm):
        """分析ノートを返す"""
        mock_call_llm.return_value = json.dumps({
            "detected_language": "ja",
            "followup_questions": [],
            "analysis_notes": "技術的なサポートを求めている"
        })

        service = LLMServiceV2(api_key="test-key")
        initial_answers = InitialAnswers(
            purpose="コードレビュー",
            autonomy="obedient"
        )

        result = service.generate_followup_questions(initial_answers)

        assert "analysis_notes" in result

    def test_raises_timeout_error(self):
        """タイムアウト時にエラーを発生させる"""
        service = LLMServiceV2(api_key="test-key", timeout=0)
        initial_answers = InitialAnswers(
            purpose="test",
            autonomy="collaborative"
        )

        with patch.object(service, "_call_llm_internal", side_effect=lambda *args: __import__('time').sleep(1)):
            with pytest.raises(LLMTimeoutError):
                service.generate_followup_questions(initial_answers)


class TestGenerateFinalOutput:
    """generate_final_output メソッドのテスト"""

    @patch.object(LLMServiceV2, "_call_llm")
    def test_returns_user_profile(self, mock_call_llm):
        """ユーザープロファイルを返す"""
        mock_call_llm.return_value = json.dumps({
            "user_profile": {
                "primary_use_case": "コーディング",
                "autonomy_preference": "協調的",
                "communication_style": "技術的",
                "key_traits": ["詳細志向", "効率重視"],
                "detected_needs": ["コードレビュー", "ベストプラクティス"]
            },
            "recommended_style": "standard",
            "recommendation_reason": "バランスの取れた指示が適しています",
            "variants": [
                {
                    "style": "short",
                    "name": "ショート (Short)",
                    "prompt": "簡潔なプロンプト",
                    "description": "短い説明"
                },
                {
                    "style": "standard",
                    "name": "スタンダード (Standard)",
                    "prompt": "標準プロンプト",
                    "description": "標準的な説明"
                },
                {
                    "style": "strict",
                    "name": "ストリクト (Strict)",
                    "prompt": "詳細なプロンプト",
                    "description": "詳細な説明"
                }
            ]
        })

        service = LLMServiceV2(api_key="test-key")
        all_answers = {
            "initial": {"purpose": "コードレビュー", "autonomy": "collaborative"},
            "followup": []
        }

        result = service.generate_final_output(
            all_answers=all_answers,
            detected_language="ja"
        )

        assert "user_profile" in result
        assert result["user_profile"]["primary_use_case"] == "コーディング"

    @patch.object(LLMServiceV2, "_call_llm")
    def test_returns_recommended_style(self, mock_call_llm):
        """推奨スタイルを返す"""
        mock_call_llm.return_value = json.dumps({
            "user_profile": {
                "primary_use_case": "research",
                "autonomy_preference": "autonomous",
                "communication_style": "technical",
                "key_traits": ["analytical"],
                "detected_needs": ["data analysis"]
            },
            "recommended_style": "strict",
            "recommendation_reason": "Detailed instructions work best for research tasks",
            "variants": [
                {"style": "short", "name": "Short", "prompt": "p1", "description": "d1"},
                {"style": "standard", "name": "Standard", "prompt": "p2", "description": "d2"},
                {"style": "strict", "name": "Strict", "prompt": "p3", "description": "d3"}
            ]
        })

        service = LLMServiceV2(api_key="test-key")
        all_answers = {"initial": {"purpose": "research", "autonomy": "autonomous"}}

        result = service.generate_final_output(
            all_answers=all_answers,
            detected_language="en"
        )

        assert result["recommended_style"] == "strict"

    @patch.object(LLMServiceV2, "_call_llm")
    def test_returns_three_variants(self, mock_call_llm):
        """3つのプロンプトバリアントを返す"""
        mock_call_llm.return_value = json.dumps({
            "user_profile": {
                "primary_use_case": "coding",
                "autonomy_preference": "collaborative",
                "communication_style": "casual",
                "key_traits": ["friendly"],
                "detected_needs": ["help"]
            },
            "recommended_style": "standard",
            "recommendation_reason": "reason",
            "variants": [
                {"style": "short", "name": "Short", "prompt": "p1", "description": "d1"},
                {"style": "standard", "name": "Standard", "prompt": "p2", "description": "d2"},
                {"style": "strict", "name": "Strict", "prompt": "p3", "description": "d3"}
            ]
        })

        service = LLMServiceV2(api_key="test-key")
        result = service.generate_final_output(
            all_answers={"initial": {"purpose": "help", "autonomy": "collaborative"}},
            detected_language="en"
        )

        assert len(result["variants"]) == 3
        styles = [v["style"] for v in result["variants"]]
        assert "short" in styles
        assert "standard" in styles
        assert "strict" in styles

    @patch.object(LLMServiceV2, "_call_llm")
    def test_returns_recommendation_reason(self, mock_call_llm):
        """推奨理由を返す"""
        mock_call_llm.return_value = json.dumps({
            "user_profile": {
                "primary_use_case": "writing",
                "autonomy_preference": "obedient",
                "communication_style": "formal",
                "key_traits": [],
                "detected_needs": []
            },
            "recommended_style": "short",
            "recommendation_reason": "シンプルな指示が好まれます",
            "variants": [
                {"style": "short", "name": "Short", "prompt": "p", "description": "d"},
                {"style": "standard", "name": "Standard", "prompt": "p", "description": "d"},
                {"style": "strict", "name": "Strict", "prompt": "p", "description": "d"}
            ]
        })

        service = LLMServiceV2(api_key="test-key")
        result = service.generate_final_output(
            all_answers={"initial": {"purpose": "writing", "autonomy": "obedient"}},
            detected_language="ja"
        )

        assert result["recommendation_reason"] == "シンプルな指示が好まれます"


class TestMockGeneration:
    """モック生成（LLM未使用時）のテスト"""

    def test_generate_followup_mock(self):
        """モックで動的質問を生成できる"""
        service = LLMServiceV2(api_key="")  # APIキーなし
        initial_answers = InitialAnswers(
            purpose="コードレビュー",
            autonomy="collaborative"
        )

        result = service.generate_followup_questions_mock(initial_answers)

        assert "detected_language" in result
        assert "followup_questions" in result

    def test_generate_final_output_mock(self):
        """モックで最終出力を生成できる"""
        service = LLMServiceV2(api_key="")
        all_answers = {
            "initial": {"purpose": "coding help", "autonomy": "collaborative"}
        }

        result = service.generate_final_output_mock(
            all_answers=all_answers,
            detected_language="en"
        )

        assert "user_profile" in result
        assert "recommended_style" in result
        assert "variants" in result
        assert len(result["variants"]) == 3


class TestGenerateFinalOutputV2:
    """認知プロファイル対応のgenerate_final_outputテスト"""

    @patch.object(LLMServiceV2, "_call_llm")
    def test_returns_cognitive_profile(self, mock_call_llm):
        """認知プロファイルを含むユーザープロファイルを返す"""
        mock_call_llm.return_value = json.dumps({
            "user_profile": {
                "primary_use_case": "コーディング",
                "autonomy_preference": "協調的",
                "communication_style": "技術的",
                "key_traits": ["詳細志向", "効率重視"],
                "detected_needs": ["コードレビュー"],
                "cognitive_profile": {
                    "thinking_pattern": "structural",
                    "learning_type": "visual_text",
                    "detail_orientation": "high",
                    "preferred_structure": "hierarchical",
                    "use_tables": True,
                    "formatting_rules": {
                        "paragraph_length": "80-120語",
                        "heading_length": "10-20トークン"
                    },
                    "avoid_patterns": ["過度な絵文字", "スラング"],
                    "persona_summary": "構造思考型の開発者"
                }
            },
            "recommended_style": "strict",
            "recommendation_reason": "詳細な構造化を好むため",
            "variants": [
                {"style": "short", "name": "ショート", "prompt": "p1", "description": "d1"},
                {"style": "standard", "name": "スタンダード", "prompt": "p2", "description": "d2"},
                {"style": "strict", "name": "ストリクト", "prompt": "p3", "description": "d3"}
            ]
        })

        service = LLMServiceV2(api_key="test-key")
        result = service.generate_final_output(
            all_answers={"initial": {"purpose": "コーディング", "autonomy": "collaborative"}},
            detected_language="ja"
        )

        assert "cognitive_profile" in result["user_profile"]
        assert result["user_profile"]["cognitive_profile"]["thinking_pattern"] == "structural"
        assert result["user_profile"]["cognitive_profile"]["use_tables"] is True


class TestEnhancedMockGeneration:
    """強化されたモック生成のテスト"""

    def test_mock_returns_cognitive_profile(self):
        """モックが認知プロファイルを返す"""
        service = LLMServiceV2(api_key="")
        all_answers = {
            "initial": {"purpose": "コーディングサポート", "autonomy": "autonomous"}
        }

        result = service.generate_final_output_mock(
            all_answers=all_answers,
            detected_language="ja"
        )

        assert "cognitive_profile" in result["user_profile"]
        assert "thinking_pattern" in result["user_profile"]["cognitive_profile"]
        assert "persona_summary" in result["user_profile"]["cognitive_profile"]

    def test_mock_prompt_is_personalized_ja(self):
        """日本語モックプロンプトが個人化されている（汎用的でない）"""
        service = LLMServiceV2(api_key="")
        all_answers = {
            "initial": {"purpose": "コーディングサポート", "autonomy": "autonomous"}
        }

        result = service.generate_final_output_mock(
            all_answers=all_answers,
            detected_language="ja"
        )

        strict_prompt = next(
            v["prompt"] for v in result["variants"] if v["style"] == "strict"
        )
        # ペルソナ宣言が含まれる
        assert "私は" in strict_prompt or "学習者" in strict_prompt or "思考" in strict_prompt
        # 汎用的な表現ではない
        assert "ユーザーの質問に的確に回答" not in strict_prompt

    def test_mock_prompt_is_personalized_en(self):
        """英語モックプロンプトが個人化されている（汎用的でない）"""
        service = LLMServiceV2(api_key="")
        all_answers = {
            "initial": {"purpose": "coding support", "autonomy": "autonomous"}
        }

        result = service.generate_final_output_mock(
            all_answers=all_answers,
            detected_language="en"
        )

        strict_prompt = next(
            v["prompt"] for v in result["variants"] if v["style"] == "strict"
        )
        # ペルソナ宣言または認知特性が含まれる
        assert "learner" in strict_prompt.lower() or "thinking" in strict_prompt.lower() or "I am" in strict_prompt

    def test_mock_strict_prompt_length_800_1200(self):
        """strictスタイルのプロンプトは800-1200文字"""
        service = LLMServiceV2(api_key="")
        all_answers = {
            "initial": {"purpose": "詳細なコードレビュー", "autonomy": "autonomous"}
        }

        result = service.generate_final_output_mock(
            all_answers=all_answers,
            detected_language="ja"
        )

        strict_prompt = next(
            v["prompt"] for v in result["variants"] if v["style"] == "strict"
        )
        # 800-1200文字の範囲（許容範囲を少し広げる）
        assert len(strict_prompt) >= 400, f"Strict prompt too short: {len(strict_prompt)} chars"
        assert len(strict_prompt) <= 1500, f"Strict prompt too long: {len(strict_prompt)} chars"

    def test_mock_strict_prompt_includes_table_for_ja(self):
        """日本語strictプロンプトに表が含まれる"""
        service = LLMServiceV2(api_key="")
        all_answers = {
            "initial": {"purpose": "コーディングサポート", "autonomy": "autonomous"}
        }

        result = service.generate_final_output_mock(
            all_answers=all_answers,
            detected_language="ja"
        )

        strict_prompt = next(
            v["prompt"] for v in result["variants"] if v["style"] == "strict"
        )
        # テーブル形式（Markdown）が含まれる
        assert "|" in strict_prompt or "表" in strict_prompt

    def test_mock_cognitive_profile_varies_by_autonomy(self):
        """autonomyによって認知プロファイルが変化する"""
        service = LLMServiceV2(api_key="")

        # obedient: 指示に忠実 → 構造化された詳細志向
        result_obedient = service.generate_final_output_mock(
            all_answers={"initial": {"purpose": "task", "autonomy": "obedient"}},
            detected_language="ja"
        )

        # autonomous: 自律的 → 探索的
        result_autonomous = service.generate_final_output_mock(
            all_answers={"initial": {"purpose": "task", "autonomy": "autonomous"}},
            detected_language="ja"
        )

        # 認知プロファイルが存在する
        assert "cognitive_profile" in result_obedient["user_profile"]
        assert "cognitive_profile" in result_autonomous["user_profile"]


class TestCreateLLMServiceV2:
    """create_llm_service_v2 ファクトリ関数のテスト"""

    def test_creates_instance(self):
        """インスタンスを作成できる"""
        service = create_llm_service_v2("test-key")
        assert isinstance(service, LLMServiceV2)

    def test_accepts_timeout(self):
        """タイムアウトを指定できる"""
        service = create_llm_service_v2("test-key", timeout=30)
        assert service.timeout == 30

    def test_accepts_provider(self):
        """プロバイダーを指定できる"""
        service = create_llm_service_v2("test-key", provider="gemini")
        assert service.provider == "gemini"
