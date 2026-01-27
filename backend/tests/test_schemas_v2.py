"""
v2 スキーマのテスト
TDD: CognitiveProfile と UserProfile拡張のテスト
"""
import pytest
from pydantic import ValidationError

from schemas.diagnose_v2 import (
    CognitiveProfile,
    UserProfile,
    InitialAnswers,
    Question,
    QuestionChoice,
)


class TestCognitiveProfile:
    """CognitiveProfile モデルのテスト"""

    def test_thinking_pattern_accepts_structural(self):
        """thinking_pattern は 'structural' を受け付ける"""
        profile = CognitiveProfile(
            thinking_pattern="structural",
            learning_type="visual_text",
            detail_orientation="high",
            preferred_structure="hierarchical",
            persona_summary="構造思考型のユーザー",
        )
        assert profile.thinking_pattern == "structural"

    def test_thinking_pattern_accepts_fluid(self):
        """thinking_pattern は 'fluid' を受け付ける"""
        profile = CognitiveProfile(
            thinking_pattern="fluid",
            learning_type="visual_text",
            detail_orientation="medium",
            preferred_structure="flat",
            persona_summary="流動思考型のユーザー",
        )
        assert profile.thinking_pattern == "fluid"

    def test_thinking_pattern_accepts_hybrid(self):
        """thinking_pattern は 'hybrid' を受け付ける"""
        profile = CognitiveProfile(
            thinking_pattern="hybrid",
            learning_type="auditory",
            detail_orientation="low",
            preferred_structure="contextual",
            persona_summary="混合型のユーザー",
        )
        assert profile.thinking_pattern == "hybrid"

    def test_thinking_pattern_rejects_invalid(self):
        """thinking_pattern は無効な値を拒否する"""
        with pytest.raises(ValidationError):
            CognitiveProfile(
                thinking_pattern="invalid",
                learning_type="visual_text",
                detail_orientation="high",
                preferred_structure="hierarchical",
                persona_summary="test",
            )

    def test_learning_type_literal_values(self):
        """learning_type は正しいリテラル値を受け付ける"""
        for lt in ["visual_text", "visual_diagram", "auditory", "kinesthetic"]:
            profile = CognitiveProfile(
                thinking_pattern="structural",
                learning_type=lt,
                detail_orientation="high",
                preferred_structure="hierarchical",
                persona_summary="test",
            )
            assert profile.learning_type == lt

    def test_detail_orientation_literal_values(self):
        """detail_orientation は正しいリテラル値を受け付ける"""
        for do in ["high", "medium", "low"]:
            profile = CognitiveProfile(
                thinking_pattern="structural",
                learning_type="visual_text",
                detail_orientation=do,
                preferred_structure="hierarchical",
                persona_summary="test",
            )
            assert profile.detail_orientation == do

    def test_preferred_structure_literal_values(self):
        """preferred_structure は正しいリテラル値を受け付ける"""
        for ps in ["hierarchical", "flat", "contextual"]:
            profile = CognitiveProfile(
                thinking_pattern="structural",
                learning_type="visual_text",
                detail_orientation="high",
                preferred_structure=ps,
                persona_summary="test",
            )
            assert profile.preferred_structure == ps

    def test_formatting_principles_is_list(self):
        """formatting_principles はリスト型"""
        profile = CognitiveProfile(
            thinking_pattern="structural",
            learning_type="visual_text",
            detail_orientation="high",
            preferred_structure="hierarchical",
            persona_summary="test",
            formatting_principles=[
                "全体構造（マクロ）から詳細（ミクロ）へ順に説明",
                "箇条書き・表・階層構造を活用して整理",
                "網羅的な情報を段階的に提示",
            ],
        )
        assert isinstance(profile.formatting_principles, list)
        assert "全体構造（マクロ）から詳細（ミクロ）へ順に説明" in profile.formatting_principles

    def test_formatting_principles_is_optional_with_default(self):
        """formatting_principles はオプショナルでデフォルトは空リスト"""
        profile = CognitiveProfile(
            thinking_pattern="structural",
            learning_type="visual_text",
            detail_orientation="high",
            preferred_structure="hierarchical",
            persona_summary="test",
        )
        assert profile.formatting_principles == []

    def test_avoid_patterns_is_list(self):
        """avoid_patterns はリスト型"""
        profile = CognitiveProfile(
            thinking_pattern="structural",
            learning_type="visual_text",
            detail_orientation="high",
            preferred_structure="hierarchical",
            persona_summary="test",
            avoid_patterns=["過度な絵文字", "スラング", "曖昧な表現"],
        )
        assert isinstance(profile.avoid_patterns, list)
        assert "過度な絵文字" in profile.avoid_patterns

    def test_avoid_patterns_is_optional_with_default(self):
        """avoid_patterns はオプショナルでデフォルトは空リスト"""
        profile = CognitiveProfile(
            thinking_pattern="structural",
            learning_type="visual_text",
            detail_orientation="high",
            preferred_structure="hierarchical",
            persona_summary="test",
        )
        assert profile.avoid_patterns == []

    def test_use_tables_is_bool(self):
        """use_tables はブール型"""
        profile = CognitiveProfile(
            thinking_pattern="structural",
            learning_type="visual_text",
            detail_orientation="high",
            preferred_structure="hierarchical",
            persona_summary="test",
            use_tables=True,
        )
        assert profile.use_tables is True

    def test_use_tables_is_optional_with_default(self):
        """use_tables はオプショナルでデフォルトはFalse"""
        profile = CognitiveProfile(
            thinking_pattern="structural",
            learning_type="visual_text",
            detail_orientation="high",
            preferred_structure="hierarchical",
            persona_summary="test",
        )
        assert profile.use_tables is False

    def test_persona_summary_is_required(self):
        """persona_summary は必須"""
        with pytest.raises(ValidationError):
            CognitiveProfile(
                thinking_pattern="structural",
                learning_type="visual_text",
                detail_orientation="high",
                preferred_structure="hierarchical",
            )


class TestUserProfileWithCognitive:
    """UserProfile の認知プロファイル拡張テスト"""

    def test_cognitive_profile_is_optional(self):
        """cognitive_profile はオプショナル（後方互換性）"""
        profile = UserProfile(
            primary_use_case="コーディング",
            autonomy_preference="協調的",
            communication_style="技術的",
            key_traits=["詳細志向"],
            detected_needs=["コードレビュー"],
        )
        # cognitive_profile がなくてもエラーにならない
        assert profile.cognitive_profile is None

    def test_user_profile_accepts_cognitive_profile(self):
        """UserProfile は cognitive_profile を受け付ける"""
        cognitive = CognitiveProfile(
            thinking_pattern="structural",
            learning_type="visual_text",
            detail_orientation="high",
            preferred_structure="hierarchical",
            persona_summary="構造思考型の開発者",
            formatting_rules={"heading_length": "10-20トークン"},
            avoid_patterns=["過度な装飾"],
            use_tables=True,
        )
        profile = UserProfile(
            primary_use_case="コーディング",
            autonomy_preference="協調的",
            communication_style="技術的",
            key_traits=["詳細志向"],
            detected_needs=["コードレビュー"],
            cognitive_profile=cognitive,
        )
        assert profile.cognitive_profile is not None
        assert profile.cognitive_profile.thinking_pattern == "structural"
        assert profile.cognitive_profile.use_tables is True

    def test_backward_compatibility_existing_fields_unchanged(self):
        """既存のフィールドは変更なし（後方互換性）"""
        profile = UserProfile(
            primary_use_case="research",
            autonomy_preference="autonomous",
            communication_style="formal",
            key_traits=["analytical", "thorough"],
            detected_needs=["data analysis", "report writing"],
        )
        assert profile.primary_use_case == "research"
        assert profile.autonomy_preference == "autonomous"
        assert len(profile.key_traits) == 2
        assert len(profile.detected_needs) == 2


class TestInitialAnswersExtended:
    """InitialAnswers の認知特性フィールド拡張テスト"""

    def test_backward_compatibility_minimal_fields(self):
        """既存フィールドのみで作成可能（後方互換性）"""
        answers = InitialAnswers(
            purpose="コードレビュー",
            autonomy="collaborative"
        )
        assert answers.purpose == "コードレビュー"
        assert answers.autonomy == "collaborative"

    def test_learning_scenario_is_optional(self):
        """learning_scenario はオプショナル"""
        answers = InitialAnswers(
            purpose="test",
            autonomy="collaborative"
        )
        assert answers.learning_scenario is None

    def test_learning_scenario_accepts_valid_values(self):
        """learning_scenario は有効な値を受け付ける"""
        for value in ["overview", "tutorial", "example", "question"]:
            answers = InitialAnswers(
                purpose="test",
                autonomy="collaborative",
                learning_scenario=value
            )
            assert answers.learning_scenario == value

    def test_confusion_scenario_is_optional(self):
        """confusion_scenario はオプショナル"""
        answers = InitialAnswers(
            purpose="test",
            autonomy="collaborative"
        )
        assert answers.confusion_scenario is None

    def test_confusion_scenario_accepts_valid_values(self):
        """confusion_scenario は有効な値を受け付ける"""
        for value in ["reread", "example", "simplify", "ask"]:
            answers = InitialAnswers(
                purpose="test",
                autonomy="collaborative",
                confusion_scenario=value
            )
            assert answers.confusion_scenario == value

    def test_info_load_scenario_is_optional(self):
        """info_load_scenario はオプショナル"""
        answers = InitialAnswers(
            purpose="test",
            autonomy="collaborative"
        )
        assert answers.info_load_scenario is None

    def test_info_load_scenario_accepts_valid_values(self):
        """info_load_scenario は有効な値を受け付ける"""
        for value in ["comfortable", "skim", "overwhelmed", "summary"]:
            answers = InitialAnswers(
                purpose="test",
                autonomy="collaborative",
                info_load_scenario=value
            )
            assert answers.info_load_scenario == value

    def test_format_scenario_is_optional(self):
        """format_scenario はオプショナル"""
        answers = InitialAnswers(
            purpose="test",
            autonomy="collaborative"
        )
        assert answers.format_scenario is None

    def test_format_scenario_accepts_valid_values(self):
        """format_scenario は有効な値を受け付ける"""
        for value in ["structured", "conversational", "code_first", "table"]:
            answers = InitialAnswers(
                purpose="test",
                autonomy="collaborative",
                format_scenario=value
            )
            assert answers.format_scenario == value

    def test_frustration_scenario_is_optional_list(self):
        """frustration_scenario はオプショナルなリスト"""
        answers = InitialAnswers(
            purpose="test",
            autonomy="collaborative"
        )
        assert answers.frustration_scenario is None

    def test_frustration_scenario_accepts_multiple_values(self):
        """frustration_scenario は複数の値を受け付ける"""
        answers = InitialAnswers(
            purpose="test",
            autonomy="collaborative",
            frustration_scenario=["too_casual", "too_long", "emoji"]
        )
        assert len(answers.frustration_scenario) == 3
        assert "too_casual" in answers.frustration_scenario

    def test_ideal_interaction_is_optional(self):
        """ideal_interaction はオプショナル"""
        answers = InitialAnswers(
            purpose="test",
            autonomy="collaborative"
        )
        assert answers.ideal_interaction is None

    def test_ideal_interaction_accepts_valid_values(self):
        """ideal_interaction は有効な値を受け付ける"""
        for value in ["mentor", "colleague", "assistant", "teacher"]:
            answers = InitialAnswers(
                purpose="test",
                autonomy="collaborative",
                ideal_interaction=value
            )
            assert answers.ideal_interaction == value

    def test_all_cognitive_fields_together(self):
        """全ての認知特性フィールドを同時に設定可能"""
        answers = InitialAnswers(
            purpose="コーディングサポート",
            autonomy="autonomous",
            learning_scenario="overview",
            confusion_scenario="reread",
            info_load_scenario="comfortable",
            format_scenario="structured",
            frustration_scenario=["too_casual", "too_long"],
            ideal_interaction="mentor"
        )
        assert answers.learning_scenario == "overview"
        assert answers.confusion_scenario == "reread"
        assert answers.info_load_scenario == "comfortable"
        assert answers.format_scenario == "structured"
        assert len(answers.frustration_scenario) == 2
        assert answers.ideal_interaction == "mentor"


class TestQuestionTypeMultiChoice:
    """Question.type の multi_choice 対応テスト"""

    def test_question_accepts_multi_choice_type(self):
        """Question は type='multi_choice' を受け付ける"""
        question = Question(
            id="frustration_scenario",
            question="AIの回答で「これは合わない」と感じたのはどんな時でしたか？",
            type="multi_choice",
            choices=[
                QuestionChoice(value="too_casual", label="カジュアルすぎる口調だった"),
                QuestionChoice(value="too_long", label="回答が長すぎた"),
            ]
        )
        assert question.type == "multi_choice"

    def test_question_still_accepts_freeform(self):
        """Question は type='freeform' を引き続き受け付ける"""
        question = Question(
            id="test",
            question="テスト質問",
            type="freeform"
        )
        assert question.type == "freeform"

    def test_question_still_accepts_choice(self):
        """Question は type='choice' を引き続き受け付ける"""
        question = Question(
            id="test",
            question="テスト質問",
            type="choice",
            choices=[QuestionChoice(value="a", label="A")]
        )
        assert question.type == "choice"
