"""
v2 LLM サービス

動的質問生成と特性抽出・プロンプト生成のためのLLMサービス
"""
import json
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FuturesTimeoutError
from typing import Any, Literal

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq

from prompts.v2_templates import (
    LANGUAGE_DETECTION_AND_QUESTION_GENERATION,
    PROFILE_EXTRACTION_AND_PROMPT_GENERATION,
)
from schemas.diagnose_v2 import InitialAnswers


class LLMTimeoutError(Exception):
    """LLM呼び出しがタイムアウトした場合のエラー"""

    pass


ProviderType = Literal["groq", "gemini"]


class LLMServiceV2:
    """
    v2 LLMサービス

    動的質問生成と最終出力生成のためのLLM統合サービス
    """

    DEFAULT_TIMEOUT = 20
    DEFAULT_PROVIDER: ProviderType = "groq"

    MODELS = {
        "groq": "llama-3.3-70b-versatile",
        "gemini": "gemini-2.0-flash",
    }

    def __init__(
        self,
        api_key: str,
        timeout: int = DEFAULT_TIMEOUT,
        provider: ProviderType = DEFAULT_PROVIDER,
    ):
        """
        v2 LLMサービスを初期化

        Args:
            api_key: APIキー
            timeout: タイムアウト秒数
            provider: LLMプロバイダー
        """
        self.api_key = api_key
        self.timeout = timeout
        self.provider = provider
        self.model_name = self.MODELS.get(provider, self.MODELS["groq"])
        self._llm = None

    @property
    def is_available(self) -> bool:
        """LLMサービスが利用可能かどうか"""
        return bool(self.api_key)

    @property
    def llm(self):
        """LLMインスタンスを取得（遅延初期化）"""
        if self._llm is None:
            if not self.is_available:
                raise ValueError("APIキーが設定されていません")

            if self.provider == "groq":
                self._llm = ChatGroq(
                    model=self.model_name,
                    api_key=self.api_key,
                    temperature=0.7,
                    max_tokens=2048,
                )
            else:
                self._llm = ChatGoogleGenerativeAI(
                    model=self.model_name,
                    google_api_key=self.api_key,
                    temperature=0.7,
                    max_output_tokens=2048,
                )
        return self._llm

    def _call_llm_internal(self, prompt_template: str, variables: dict) -> str:
        """LLMを内部的に呼び出す（タイムアウトなし）"""
        chat_prompt = ChatPromptTemplate.from_messages(
            [("system", "You are a helpful assistant that outputs valid JSON only."),
             ("human", prompt_template)]
        )
        chain = chat_prompt | self.llm | StrOutputParser()
        result = chain.invoke(variables)
        return result.strip()

    def _call_llm(self, prompt_template: str, variables: dict) -> str:
        """LLMを呼び出す（タイムアウト付き）"""
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(self._call_llm_internal, prompt_template, variables)

            try:
                return future.result(timeout=self.timeout)
            except FuturesTimeoutError:
                raise LLMTimeoutError(
                    f"LLM呼び出しが{self.timeout}秒でタイムアウトしました"
                )

    def _parse_json_response(self, response: str) -> dict:
        """JSONレスポンスをパース"""
        # JSONブロックを抽出（マークダウンコードブロックに対応）
        if "```json" in response:
            start = response.find("```json") + 7
            end = response.find("```", start)
            response = response[start:end].strip()
        elif "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            response = response[start:end].strip()

        return json.loads(response)

    def generate_followup_questions(
        self, initial_answers: InitialAnswers
    ) -> dict[str, Any]:
        """
        動的質問を生成

        Args:
            initial_answers: 初期回答

        Returns:
            検出された言語、動的質問、分析ノートを含む辞書
        """
        user_answers = {
            "purpose": initial_answers.purpose,
            "autonomy": initial_answers.autonomy,
        }

        response = self._call_llm(
            LANGUAGE_DETECTION_AND_QUESTION_GENERATION,
            {"user_answers": json.dumps(user_answers, ensure_ascii=False)},
        )

        return self._parse_json_response(response)

    def generate_followup_questions_mock(
        self, initial_answers: InitialAnswers
    ) -> dict[str, Any]:
        """
        動的質問のモック生成（LLM未使用時）

        Args:
            initial_answers: 初期回答

        Returns:
            モック生成された結果
        """
        # 言語検出（簡易）
        purpose = initial_answers.purpose
        has_japanese = any(
            "\u3040" <= char <= "\u309f" or  # ひらがな
            "\u30a0" <= char <= "\u30ff" or  # カタカナ
            "\u4e00" <= char <= "\u9fff"  # 漢字
            for char in purpose
        )
        detected_language = "ja" if has_japanese else "en"

        # 自律性に基づいて追加質問を決定
        followup_questions = []
        if initial_answers.autonomy == "collaborative":
            if detected_language == "ja":
                followup_questions = [
                    {
                        "id": "fq1",
                        "question": "どのような形式でフィードバックを受け取りたいですか？",
                        "type": "choice",
                        "choices": [
                            {"value": "detailed", "label": "詳細な説明付き"},
                            {"value": "brief", "label": "簡潔なポイントのみ"},
                            {"value": "mixed", "label": "状況に応じて"},
                        ],
                    }
                ]
            else:
                followup_questions = [
                    {
                        "id": "fq1",
                        "question": "How would you like to receive feedback?",
                        "type": "choice",
                        "choices": [
                            {"value": "detailed", "label": "Detailed explanations"},
                            {"value": "brief", "label": "Brief points only"},
                            {"value": "mixed", "label": "Depends on situation"},
                        ],
                    }
                ]

        return {
            "detected_language": detected_language,
            "followup_questions": followup_questions,
            "analysis_notes": f"Mock analysis: purpose={purpose[:50]}...",
        }

    def generate_final_output(
        self,
        all_answers: dict[str, Any],
        detected_language: str,
    ) -> dict[str, Any]:
        """
        最終出力を生成（ユーザープロファイル + 3種プロンプト）

        Args:
            all_answers: 全ての回答
            detected_language: 検出された言語

        Returns:
            ユーザープロファイル、推奨スタイル、3種のプロンプトを含む辞書
        """
        response = self._call_llm(
            PROFILE_EXTRACTION_AND_PROMPT_GENERATION,
            {
                "all_answers": json.dumps(all_answers, ensure_ascii=False),
                "detected_language": detected_language,
            },
        )

        return self._parse_json_response(response)

    def generate_final_output_mock(
        self,
        all_answers: dict[str, Any],
        detected_language: str,
    ) -> dict[str, Any]:
        """
        最終出力のモック生成（LLM未使用時）

        認知プロファイルと個人化されたプロンプトを生成

        Args:
            all_answers: 全ての回答
            detected_language: 検出された言語

        Returns:
            モック生成された結果
        """
        initial = all_answers.get("initial", {})
        purpose = initial.get("purpose", "general assistance")
        autonomy = initial.get("autonomy", "collaborative")

        # 自律性に基づいて認知プロファイルと推奨スタイルを決定
        cognitive_profiles = {
            "obedient": {
                "thinking_pattern": "structural",
                "learning_type": "visual_text",
                "detail_orientation": "high",
                "preferred_structure": "hierarchical",
                "use_tables": True,
                "formatting_rules": {
                    "paragraph_length": "80-120語/段落",
                    "heading_length": "10-20トークン",
                    "list_items": "3-7項目",
                },
                "avoid_patterns": ["曖昧な表現", "過度な装飾", "推測的な回答"],
                "persona_summary_ja": "明確な指示と構造化された情報を好む、静的構造思考型の学習者です",
                "persona_summary_en": "I am a structured thinker who prefers clear instructions and well-organized information",
            },
            "collaborative": {
                "thinking_pattern": "hybrid",
                "learning_type": "visual_text",
                "detail_orientation": "medium",
                "preferred_structure": "contextual",
                "use_tables": True,
                "formatting_rules": {
                    "paragraph_length": "60-100語/段落",
                    "heading_length": "10-15トークン",
                    "list_items": "3-5項目",
                },
                "avoid_patterns": ["過度な専門用語", "長すぎる説明"],
                "persona_summary_ja": "対話を通じて理解を深める、協調型の学習者です",
                "persona_summary_en": "I am a collaborative learner who deepens understanding through dialogue",
            },
            "autonomous": {
                "thinking_pattern": "fluid",
                "learning_type": "kinesthetic",
                "detail_orientation": "low",
                "preferred_structure": "flat",
                "use_tables": False,
                "formatting_rules": {
                    "paragraph_length": "40-80語/段落",
                    "heading_length": "5-10トークン",
                    "list_items": "2-4項目",
                },
                "avoid_patterns": ["過度な説明", "細かすぎる指示", "冗長な表現"],
                "persona_summary_ja": "自律的に探索し、要点を素早く把握する探索型の学習者です",
                "persona_summary_en": "I am an exploratory learner who autonomously navigates and quickly grasps key points",
            },
        }

        style_map = {
            "obedient": "short",
            "collaborative": "standard",
            "autonomous": "strict",
        }
        recommended_style = style_map.get(autonomy, "standard")

        profile_data = cognitive_profiles.get(autonomy, cognitive_profiles["collaborative"])
        persona_key = "persona_summary_ja" if detected_language == "ja" else "persona_summary_en"

        cognitive_profile = {
            "thinking_pattern": profile_data["thinking_pattern"],
            "learning_type": profile_data["learning_type"],
            "detail_orientation": profile_data["detail_orientation"],
            "preferred_structure": profile_data["preferred_structure"],
            "use_tables": profile_data["use_tables"],
            "formatting_rules": profile_data["formatting_rules"],
            "avoid_patterns": profile_data["avoid_patterns"],
            "persona_summary": profile_data[persona_key],
        }

        if detected_language == "ja":
            return self._generate_mock_ja(purpose, autonomy, recommended_style, cognitive_profile)
        else:
            return self._generate_mock_en(purpose, autonomy, recommended_style, cognitive_profile)

    def _generate_mock_ja(
        self,
        purpose: str,
        autonomy: str,
        recommended_style: str,
        cognitive_profile: dict,
    ) -> dict[str, Any]:
        """日本語モック生成"""
        persona = cognitive_profile["persona_summary"]
        avoid = "、".join(cognitive_profile["avoid_patterns"])
        rules = cognitive_profile["formatting_rules"]

        short_prompt = f"""私は{persona}。

## 基本方針
- {purpose}に関する質問に簡潔に回答
- 要点を3つ以内にまとめる
- {avoid}は避ける"""

        standard_prompt = f"""私は{persona}。
以下の原則で{purpose}をサポートしてください。

## 情報構造化
| 要素 | ルール |
|------|--------|
| 段落 | {rules.get("paragraph_length", "80-120語")} |
| 見出し | {rules.get("heading_length", "10-20トークン")} |
| 箇条書き | {rules.get("list_items", "3-7項目")} |

## 認知特性
- 思考パターン: {cognitive_profile["thinking_pattern"]}
- 詳細志向: {cognitive_profile["detail_orientation"]}

## 回避事項
{avoid}は避けてください。"""

        strict_prompt = f"""私は{persona}。
全体構造の整合性が取れたときに理解が成立する学習者として、以下のフォーマットで{purpose}に関する情報を構造化してください。

## 情報構造化の原則
| 要素 | ルール |
|------|--------|
| 階層構造 | マクロ→メソ→ミクロの3層 |
| 見出し | {rules.get("heading_length", "10-20トークン")}、「〜について」禁止 |
| 段落 | {rules.get("paragraph_length", "80-120語")} |
| 箇条書き | {rules.get("list_items", "3-7項目")}、論理順 |

## 認知特性
- 思考パターン: {cognitive_profile["thinking_pattern"]}型
- 学習タイプ: {cognitive_profile["learning_type"]}
- 詳細志向度: {cognitive_profile["detail_orientation"]}
- 情報構造: {cognitive_profile["preferred_structure"]}構造を好む

## 回答形式の要件
1. 冒頭で結論・要点を述べる
2. 根拠・詳細を階層的に展開
3. 具体例は実践的なものを選ぶ
4. コードを含む場合はコメントを付与

## 回避すべきパターン
以下は私の認知特性に合わないため、避けてください：
- {avoid}
- 過度な絵文字・装飾
- 曖昧な「〜かもしれません」表現

## 品質基準
- 正確性: 不確実な情報には明示的に注記
- 構造化: 視覚的に読み取りやすいフォーマット
- 実践性: 即座に適用可能な具体例"""

        return {
            "user_profile": {
                "primary_use_case": purpose[:50],
                "autonomy_preference": autonomy,
                "communication_style": "技術的・構造的",
                "key_traits": ["構造思考", "効率重視", "詳細志向"],
                "detected_needs": [purpose, "構造化された情報"],
                "cognitive_profile": cognitive_profile,
            },
            "recommended_style": recommended_style,
            "recommendation_reason": f"あなたの認知特性（{cognitive_profile['thinking_pattern']}型思考）に基づいて推奨しています",
            "variants": [
                {
                    "style": "short",
                    "name": "ショート (Short)",
                    "prompt": short_prompt,
                    "description": "ペルソナ宣言と最小限のルールを含む簡潔なプロンプト",
                },
                {
                    "style": "standard",
                    "name": "スタンダード (Standard)",
                    "prompt": standard_prompt,
                    "description": "認知特性とフォーマットルールを含むバランスの取れたプロンプト",
                },
                {
                    "style": "strict",
                    "name": "ストリクト (Strict)",
                    "prompt": strict_prompt,
                    "description": "完全な認知プロファイルと詳細な構造化ルールを含むプロンプト",
                },
            ],
        }

    def _generate_mock_en(
        self,
        purpose: str,
        autonomy: str,
        recommended_style: str,
        cognitive_profile: dict,
    ) -> dict[str, Any]:
        """英語モック生成"""
        persona = cognitive_profile["persona_summary"]
        avoid = ", ".join(cognitive_profile["avoid_patterns"])
        rules = cognitive_profile["formatting_rules"]

        short_prompt = f"""I am {persona.lower()}.

## Core Principles
- Respond concisely to questions about {purpose}
- Summarize key points in 3 or fewer items
- Avoid: {avoid}"""

        standard_prompt = f"""I am {persona.lower()}.
Please support me with {purpose} following these principles.

## Information Structuring
| Element | Rule |
|---------|------|
| Paragraph | {rules.get("paragraph_length", "80-120 words")} |
| Heading | {rules.get("heading_length", "10-20 tokens")} |
| Lists | {rules.get("list_items", "3-7 items")} |

## Cognitive Traits
- Thinking pattern: {cognitive_profile["thinking_pattern"]}
- Detail orientation: {cognitive_profile["detail_orientation"]}

## Avoid
Please avoid: {avoid}"""

        strict_prompt = f"""I am {persona.lower()}.
As a learner who achieves understanding when the overall structure is coherent, please structure information about {purpose} using the following format.

## Information Structuring Principles
| Element | Rule |
|---------|------|
| Hierarchy | 3 layers: macro → meso → micro |
| Headings | {rules.get("heading_length", "10-20 tokens")}, avoid "About..." |
| Paragraphs | {rules.get("paragraph_length", "80-120 words")} |
| Lists | {rules.get("list_items", "3-7 items")}, logical order |

## Cognitive Traits
- Thinking pattern: {cognitive_profile["thinking_pattern"]} type
- Learning type: {cognitive_profile["learning_type"]}
- Detail orientation: {cognitive_profile["detail_orientation"]}
- Preferred structure: {cognitive_profile["preferred_structure"]}

## Response Format Requirements
1. State conclusions/key points at the beginning
2. Expand supporting details hierarchically
3. Choose practical, applicable examples
4. Include comments when providing code

## Patterns to Avoid
The following don't match my cognitive style, please avoid:
- {avoid}
- Excessive emojis or decorations
- Vague expressions like "might be" or "perhaps"

## Quality Standards
- Accuracy: Explicitly note uncertain information
- Structure: Visually scannable formatting
- Practicality: Immediately applicable examples"""

        return {
            "user_profile": {
                "primary_use_case": purpose[:50],
                "autonomy_preference": autonomy,
                "communication_style": "technical and structured",
                "key_traits": ["structured thinking", "efficiency-focused", "detail-oriented"],
                "detected_needs": [purpose, "structured information"],
                "cognitive_profile": cognitive_profile,
            },
            "recommended_style": recommended_style,
            "recommendation_reason": f"Recommended based on your cognitive traits ({cognitive_profile['thinking_pattern']} thinking pattern)",
            "variants": [
                {
                    "style": "short",
                    "name": "Short",
                    "prompt": short_prompt,
                    "description": "Concise prompt with persona declaration and minimal rules",
                },
                {
                    "style": "standard",
                    "name": "Standard",
                    "prompt": standard_prompt,
                    "description": "Balanced prompt with cognitive traits and formatting rules",
                },
                {
                    "style": "strict",
                    "name": "Strict",
                    "prompt": strict_prompt,
                    "description": "Complete prompt with full cognitive profile and detailed structuring rules",
                },
            ],
        }


def create_llm_service_v2(
    api_key: str,
    timeout: int = LLMServiceV2.DEFAULT_TIMEOUT,
    provider: ProviderType = LLMServiceV2.DEFAULT_PROVIDER,
) -> LLMServiceV2:
    """
    v2 LLMサービスインスタンスを作成

    Args:
        api_key: APIキー
        timeout: タイムアウト秒数
        provider: LLMプロバイダー

    Returns:
        LLMServiceV2 インスタンス
    """
    return LLMServiceV2(api_key, timeout=timeout, provider=provider)
