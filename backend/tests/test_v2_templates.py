"""
v2 テンプレートのテスト
TDD: 認知特性質問テンプレートのテスト
"""
import pytest

from prompts.v2_templates import (
    INITIAL_QUESTIONS,
    get_initial_questions,
    COGNITIVE_QUESTIONS_STEP2,
    COGNITIVE_QUESTIONS_STEP3,
)


class TestCognitiveQuestionsStep2:
    """ステップ2の認知特性質問テスト（4問）"""

    def test_step2_has_4_questions(self):
        """STEP2には4つの質問がある"""
        for lang in ["ja", "en"]:
            questions = COGNITIVE_QUESTIONS_STEP2[lang]
            assert len(questions) == 4, f"STEP2 {lang} should have 4 questions"

    def test_step2_questions_have_required_fields(self):
        """各質問に必須フィールドがある"""
        required_fields = ["id", "question", "type", "choices"]
        for lang in ["ja", "en"]:
            for q in COGNITIVE_QUESTIONS_STEP2[lang]:
                for field in required_fields:
                    assert field in q, f"Question {q.get('id', 'unknown')} missing {field}"

    def test_step2_question_ids_are_valid(self):
        """質問IDが正しい"""
        expected_ids = ["learning_scenario", "confusion_scenario", "info_load_scenario", "format_scenario"]
        for lang in ["ja", "en"]:
            actual_ids = [q["id"] for q in COGNITIVE_QUESTIONS_STEP2[lang]]
            assert actual_ids == expected_ids, f"STEP2 {lang} question IDs mismatch"

    def test_step2_questions_are_choice_type(self):
        """STEP2の質問はchoiceタイプ"""
        for lang in ["ja", "en"]:
            for q in COGNITIVE_QUESTIONS_STEP2[lang]:
                assert q["type"] == "choice", f"Question {q['id']} should be choice type"

    def test_step2_choices_have_4_options(self):
        """各質問に4つの選択肢がある"""
        for lang in ["ja", "en"]:
            for q in COGNITIVE_QUESTIONS_STEP2[lang]:
                assert len(q["choices"]) == 4, f"Question {q['id']} should have 4 choices"

    def test_step2_choices_have_value_label_description(self):
        """選択肢にvalue, label, descriptionがある"""
        for lang in ["ja", "en"]:
            for q in COGNITIVE_QUESTIONS_STEP2[lang]:
                for choice in q["choices"]:
                    assert "value" in choice
                    assert "label" in choice
                    assert "description" in choice


class TestCognitiveQuestionsStep3:
    """ステップ3の認知特性質問テスト（2問）"""

    def test_step3_has_2_questions(self):
        """STEP3には2つの質問がある"""
        for lang in ["ja", "en"]:
            questions = COGNITIVE_QUESTIONS_STEP3[lang]
            assert len(questions) == 2, f"STEP3 {lang} should have 2 questions"

    def test_step3_questions_have_required_fields(self):
        """各質問に必須フィールドがある"""
        required_fields = ["id", "question", "type", "choices"]
        for lang in ["ja", "en"]:
            for q in COGNITIVE_QUESTIONS_STEP3[lang]:
                for field in required_fields:
                    assert field in q, f"Question {q.get('id', 'unknown')} missing {field}"

    def test_step3_question_ids_are_valid(self):
        """質問IDが正しい"""
        expected_ids = ["frustration_scenario", "ideal_interaction"]
        for lang in ["ja", "en"]:
            actual_ids = [q["id"] for q in COGNITIVE_QUESTIONS_STEP3[lang]]
            assert actual_ids == expected_ids, f"STEP3 {lang} question IDs mismatch"

    def test_step3_frustration_is_multi_choice(self):
        """frustration_scenarioはmulti_choiceタイプ"""
        for lang in ["ja", "en"]:
            frustration_q = next(q for q in COGNITIVE_QUESTIONS_STEP3[lang] if q["id"] == "frustration_scenario")
            assert frustration_q["type"] == "multi_choice"

    def test_step3_ideal_interaction_is_choice(self):
        """ideal_interactionはchoiceタイプ"""
        for lang in ["ja", "en"]:
            ideal_q = next(q for q in COGNITIVE_QUESTIONS_STEP3[lang] if q["id"] == "ideal_interaction")
            assert ideal_q["type"] == "choice"

    def test_step3_frustration_has_6_choices(self):
        """frustration_scenarioには6つの選択肢がある"""
        for lang in ["ja", "en"]:
            frustration_q = next(q for q in COGNITIVE_QUESTIONS_STEP3[lang] if q["id"] == "frustration_scenario")
            assert len(frustration_q["choices"]) == 6

    def test_step3_ideal_interaction_has_4_choices(self):
        """ideal_interactionには4つの選択肢がある"""
        for lang in ["ja", "en"]:
            ideal_q = next(q for q in COGNITIVE_QUESTIONS_STEP3[lang] if q["id"] == "ideal_interaction")
            assert len(ideal_q["choices"]) == 4


class TestInitialQuestionsExisting:
    """既存の初期質問テスト（後方互換性）"""

    def test_initial_questions_still_work(self):
        """既存の初期質問が引き続き動作する"""
        for lang in ["ja", "en"]:
            questions = get_initial_questions(lang)
            assert "purpose" in questions
            assert "autonomy" in questions

    def test_purpose_question_unchanged(self):
        """purpose質問は変更なし"""
        ja_purpose = INITIAL_QUESTIONS["ja"]["purpose"]
        assert ja_purpose["id"] == "purpose"
        assert ja_purpose["type"] == "freeform"

    def test_autonomy_question_unchanged(self):
        """autonomy質問は変更なし"""
        ja_autonomy = INITIAL_QUESTIONS["ja"]["autonomy"]
        assert ja_autonomy["id"] == "autonomy"
        assert ja_autonomy["type"] == "choice"
        assert len(ja_autonomy["choices"]) == 3
