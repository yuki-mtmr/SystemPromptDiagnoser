"""
v2 診断API用 Pydantic スキーマ

動的質問生成を含む新しい診断フロー用のリクエスト/レスポンスモデル
"""
from typing import Literal

from pydantic import BaseModel, Field


class CognitiveProfile(BaseModel):
    """
    認知プロファイル

    ユーザーの思考パターン、学習タイプ、情報構造化の好みを表す
    """

    thinking_pattern: Literal["structural", "fluid", "hybrid"] = Field(
        ..., description="思考パターン（構造型/流動型/混合型）"
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
    use_tables: bool = Field(
        default=False, description="表の使用好み"
    )
    formatting_rules: dict[str, str] = Field(
        default_factory=dict, description="具体的なフォーマットルール（数値制約など）"
    )
    avoid_patterns: list[str] = Field(
        default_factory=list, description="回避すべきパターン"
    )
    persona_summary: str = Field(
        ..., description="ペルソナの一文説明"
    )


class QuestionChoice(BaseModel):
    """選択肢の選択肢"""

    value: str = Field(..., description="選択肢の値")
    label: str = Field(..., description="選択肢のラベル")
    description: str | None = Field(None, description="選択肢の説明")


class Question(BaseModel):
    """質問モデル"""

    id: str = Field(..., description="質問ID")
    question: str = Field(..., description="質問文")
    type: Literal["freeform", "choice", "multi_choice"] = Field(..., description="質問タイプ")
    placeholder: str | None = Field(None, description="プレースホルダー（freeform用）")
    suggestions: list[str] | None = Field(None, description="サジェスト（freeform用）")
    choices: list[QuestionChoice] | None = Field(None, description="選択肢（choice/multi_choice用）")


class InitialAnswers(BaseModel):
    """初期回答（認知特性フィールド拡張）"""

    # 基本フィールド（必須）
    purpose: str = Field(..., description="AIに何をしてもらいたいか（自由記述）")
    autonomy: Literal["obedient", "collaborative", "autonomous"] = Field(
        ..., description="AIの主導権レベル"
    )

    # 認知特性フィールド（オプショナル・後方互換性維持）
    learning_scenario: Literal["overview", "tutorial", "example", "question"] | None = Field(
        default=None, description="学習シナリオ（思考パターン推定用）"
    )
    confusion_scenario: Literal["reread", "example", "simplify", "ask"] | None = Field(
        default=None, description="混乱時のシナリオ（情報処理スタイル推定用）"
    )
    info_load_scenario: Literal["comfortable", "skim", "overwhelmed", "summary"] | None = Field(
        default=None, description="情報量シナリオ（詳細志向度推定用）"
    )
    format_scenario: Literal["structured", "conversational", "code_first", "table"] | None = Field(
        default=None, description="フォーマットシナリオ（情報構造の好み推定用）"
    )
    frustration_scenario: list[str] | None = Field(
        default=None, description="不満シナリオ（回避パターン推定用、複数選択可）"
    )
    ideal_interaction: Literal["mentor", "colleague", "assistant", "teacher"] | None = Field(
        default=None, description="理想のやり取り（コミュニケーショントーン推定用）"
    )


class FollowupAnswer(BaseModel):
    """追加質問への回答"""

    question_id: str = Field(..., description="質問ID")
    answer: str = Field(..., description="回答")


class DiagnoseV2StartRequest(BaseModel):
    """v2診断開始リクエスト"""

    initial_answers: InitialAnswers = Field(..., description="初期回答")
    language: str | None = Field(None, description="希望言語（省略時は自動検出）")


class DiagnoseV2StartResponse(BaseModel):
    """v2診断開始レスポンス"""

    session_id: str = Field(..., description="セッションID")
    phase: Literal["followup", "complete"] = Field(..., description="次のフェーズ")
    followup_questions: list[Question] | None = Field(
        None, description="追加質問（phaseがfollowupの場合）"
    )
    result: "DiagnoseV2Result | None" = Field(
        None, description="診断結果（phaseがcompleteの場合）"
    )


class DiagnoseV2ContinueRequest(BaseModel):
    """v2診断継続リクエスト"""

    session_id: str = Field(..., description="セッションID")
    answers: list[FollowupAnswer] = Field(..., description="追加質問への回答")


class DiagnoseV2ContinueResponse(BaseModel):
    """v2診断継続レスポンス"""

    session_id: str = Field(..., description="セッションID")
    phase: Literal["followup", "complete"] = Field(..., description="次のフェーズ")
    followup_questions: list[Question] | None = Field(
        None, description="追加質問（phaseがfollowupの場合）"
    )
    result: "DiagnoseV2Result | None" = Field(
        None, description="診断結果（phaseがcompleteの場合）"
    )


class UserProfile(BaseModel):
    """ユーザープロファイル"""

    primary_use_case: str = Field(..., description="主な用途")
    autonomy_preference: str = Field(..., description="AIの自律性の好み")
    communication_style: str = Field(..., description="好みのコミュニケーションスタイル")
    key_traits: list[str] = Field(..., description="主要な特性")
    detected_needs: list[str] = Field(..., description="検出されたニーズ")
    cognitive_profile: CognitiveProfile | None = Field(
        default=None, description="認知プロファイル（オプション、後方互換性）"
    )


class PromptVariant(BaseModel):
    """プロンプトバリアント"""

    style: Literal["short", "standard", "strict"] = Field(..., description="スタイル")
    name: str = Field(..., description="スタイル名")
    prompt: str = Field(..., description="システムプロンプト")
    description: str = Field(..., description="説明")


class DiagnoseV2Result(BaseModel):
    """v2診断結果"""

    user_profile: UserProfile = Field(..., description="ユーザープロファイル")
    recommended_style: Literal["short", "standard", "strict"] = Field(
        ..., description="推奨スタイル"
    )
    recommendation_reason: str = Field(..., description="推奨理由")
    variants: list[PromptVariant] = Field(..., description="プロンプトバリアント")
    source: Literal["llm", "mock"] = Field(..., description="生成ソース")


# Forward reference の解決
DiagnoseV2StartResponse.model_rebuild()
DiagnoseV2ContinueResponse.model_rebuild()
