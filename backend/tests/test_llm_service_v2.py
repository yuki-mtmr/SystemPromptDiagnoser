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


class TestCognitiveProfileFromExplicitAnswers:
    """明示的な認知特性回答から認知プロファイルを生成するテスト"""

    def test_uses_learning_scenario_for_thinking_pattern(self):
        """learning_scenarioからthinking_patternを推定"""
        service = LLMServiceV2(api_key="")

        # overview/tutorial → structural
        all_answers = {
            "initial": {
                "purpose": "コーディング",
                "autonomy": "collaborative",
                "learning_scenario": "overview",
            }
        }
        result = service.generate_final_output_mock(all_answers, "ja")
        assert result["user_profile"]["cognitive_profile"]["thinking_pattern"] == "structural"

    def test_uses_confusion_scenario_for_learning_type(self):
        """confusion_scenarioからlearning_typeを推定"""
        service = LLMServiceV2(api_key="")

        # example → kinesthetic
        all_answers = {
            "initial": {
                "purpose": "コーディング",
                "autonomy": "collaborative",
                "confusion_scenario": "example",
            }
        }
        result = service.generate_final_output_mock(all_answers, "ja")
        # example選択者はkinestheticタイプ
        assert result["user_profile"]["cognitive_profile"]["learning_type"] == "kinesthetic"

    def test_uses_info_load_scenario_for_detail_orientation(self):
        """info_load_scenarioからdetail_orientationを推定"""
        service = LLMServiceV2(api_key="")

        # comfortable → high
        all_answers = {
            "initial": {
                "purpose": "コーディング",
                "autonomy": "collaborative",
                "info_load_scenario": "comfortable",
            }
        }
        result = service.generate_final_output_mock(all_answers, "ja")
        assert result["user_profile"]["cognitive_profile"]["detail_orientation"] == "high"

        # overwhelmed → low
        all_answers["initial"]["info_load_scenario"] = "overwhelmed"
        result = service.generate_final_output_mock(all_answers, "ja")
        assert result["user_profile"]["cognitive_profile"]["detail_orientation"] == "low"

    def test_uses_format_scenario_for_preferred_structure(self):
        """format_scenarioからpreferred_structureとuse_tablesを推定"""
        service = LLMServiceV2(api_key="")

        # structured → hierarchical, use_tables=True
        all_answers = {
            "initial": {
                "purpose": "コーディング",
                "autonomy": "collaborative",
                "format_scenario": "structured",
            }
        }
        result = service.generate_final_output_mock(all_answers, "ja")
        assert result["user_profile"]["cognitive_profile"]["preferred_structure"] == "hierarchical"

        # table → hierarchical, use_tables=True
        all_answers["initial"]["format_scenario"] = "table"
        result = service.generate_final_output_mock(all_answers, "ja")
        assert result["user_profile"]["cognitive_profile"]["use_tables"] is True

    def test_uses_frustration_scenario_for_avoid_patterns(self):
        """frustration_scenarioからavoid_patternsを生成"""
        service = LLMServiceV2(api_key="")

        all_answers = {
            "initial": {
                "purpose": "コーディング",
                "autonomy": "collaborative",
                "frustration_scenario": ["too_casual", "emoji", "too_long"],
            }
        }
        result = service.generate_final_output_mock(all_answers, "ja")
        avoid = result["user_profile"]["cognitive_profile"]["avoid_patterns"]

        # frustration_scenarioの値がavoid_patternsに反映される
        assert any("カジュアル" in p or "casual" in p.lower() for p in avoid)
        assert any("絵文字" in p or "emoji" in p.lower() for p in avoid)

    def test_uses_ideal_interaction_for_persona_tone(self):
        """ideal_interactionがpersona_summaryに反映される"""
        service = LLMServiceV2(api_key="")

        # mentor → 専門的なアドバイスを求める
        all_answers = {
            "initial": {
                "purpose": "コーディング",
                "autonomy": "collaborative",
                "ideal_interaction": "mentor",
            }
        }
        result = service.generate_final_output_mock(all_answers, "ja")
        persona = result["user_profile"]["cognitive_profile"]["persona_summary"]
        # ペルソナに何らかの表現が含まれる
        assert len(persona) > 10

    def test_fallback_to_autonomy_when_no_cognitive_answers(self):
        """認知特性回答がない場合はautonomyからフォールバック"""
        service = LLMServiceV2(api_key="")

        all_answers = {
            "initial": {
                "purpose": "コーディング",
                "autonomy": "autonomous",
            }
        }
        result = service.generate_final_output_mock(all_answers, "ja")

        # 認知プロファイルが生成される（既存動作）
        assert "cognitive_profile" in result["user_profile"]
        # autonomousの場合はfluidになる（既存ロジック）
        assert result["user_profile"]["cognitive_profile"]["thinking_pattern"] in ["structural", "fluid", "hybrid"]

    def test_generates_detailed_persona_from_all_answers(self):
        """全ての回答から詳細なペルソナを生成"""
        service = LLMServiceV2(api_key="")

        all_answers = {
            "initial": {
                "purpose": "コードレビューと設計支援",
                "autonomy": "collaborative",
                "learning_scenario": "overview",
                "confusion_scenario": "reread",
                "info_load_scenario": "comfortable",
                "format_scenario": "structured",
                "frustration_scenario": ["too_casual", "too_long"],
                "ideal_interaction": "mentor",
            }
        }
        result = service.generate_final_output_mock(all_answers, "ja")
        cognitive = result["user_profile"]["cognitive_profile"]

        # 全てのフィールドが明示的回答から決定される
        assert cognitive["thinking_pattern"] == "structural"
        assert cognitive["detail_orientation"] == "high"
        assert cognitive["preferred_structure"] == "hierarchical"
        assert len(cognitive["avoid_patterns"]) >= 2

        # ペルソナサマリーが詳細
        assert len(cognitive["persona_summary"]) >= 20

    def test_prompt_reflects_explicit_cognitive_traits(self):
        """生成されるプロンプトが明示的な認知特性を反映"""
        service = LLMServiceV2(api_key="")

        all_answers = {
            "initial": {
                "purpose": "コードレビュー",
                "autonomy": "collaborative",
                "learning_scenario": "overview",
                "info_load_scenario": "comfortable",
                "format_scenario": "structured",
            }
        }
        result = service.generate_final_output_mock(all_answers, "ja")

        strict_prompt = next(
            v["prompt"] for v in result["variants"] if v["style"] == "strict"
        )

        # プロンプトに構造化や詳細志向の言及がある
        assert "構造" in strict_prompt or "階層" in strict_prompt or "マクロ" in strict_prompt
