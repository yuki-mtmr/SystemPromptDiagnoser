"""
Pydantic スキーマ定義
"""

from .diagnose_v2 import (
    DiagnoseV2StartRequest,
    DiagnoseV2StartResponse,
    DiagnoseV2ContinueRequest,
    DiagnoseV2ContinueResponse,
    InitialAnswers,
    FollowupAnswer,
    Question,
    QuestionChoice,
    UserProfile,
    PromptVariant,
)

__all__ = [
    "DiagnoseV2StartRequest",
    "DiagnoseV2StartResponse",
    "DiagnoseV2ContinueRequest",
    "DiagnoseV2ContinueResponse",
    "InitialAnswers",
    "FollowupAnswer",
    "Question",
    "QuestionChoice",
    "UserProfile",
    "PromptVariant",
]
