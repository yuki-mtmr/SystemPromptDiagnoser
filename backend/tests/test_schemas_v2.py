"""
v2 スキーマのテスト
TDD: CognitiveProfile と UserProfile拡張のテスト
"""
import pytest
from pydantic import ValidationError

from schemas.diagnose_v2 import (
    CognitiveProfile,
    UserProfile,
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

    def test_formatting_rules_is_dict(self):
        """formatting_rules は辞書型"""
        profile = CognitiveProfile(
            thinking_pattern="structural",
            learning_type="visual_text",
            detail_orientation="high",
            preferred_structure="hierarchical",
            persona_summary="test",
            formatting_rules={
                "paragraph_length": "80-120語",
                "heading_length": "10-20トークン",
                "list_items": "3-7項目",
            },
        )
        assert isinstance(profile.formatting_rules, dict)
        assert profile.formatting_rules["paragraph_length"] == "80-120語"

    def test_formatting_rules_is_optional_with_default(self):
        """formatting_rules はオプショナルでデフォルトは空辞書"""
        profile = CognitiveProfile(
            thinking_pattern="structural",
            learning_type="visual_text",
            detail_orientation="high",
            preferred_structure="hierarchical",
            persona_summary="test",
        )
        assert profile.formatting_rules == {}

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
