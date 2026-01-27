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
        明示的な認知特性回答がある場合はそれを優先、なければautonomyから推定

        Args:
            all_answers: 全ての回答
            detected_language: 検出された言語

        Returns:
            モック生成された結果
        """
        initial = all_answers.get("initial", {})
        purpose = initial.get("purpose", "general assistance")
        autonomy = initial.get("autonomy", "collaborative")

        # 認知プロファイルを構築（明示的回答を優先）
        cognitive_profile = self._build_cognitive_profile(initial, autonomy, detected_language)

        # 推奨スタイルを決定（detail_orientationに基づく）
        recommended_style = self._determine_recommended_style(cognitive_profile, autonomy)

        if detected_language == "ja":
            return self._generate_mock_ja(purpose, autonomy, recommended_style, cognitive_profile)
        else:
            return self._generate_mock_en(purpose, autonomy, recommended_style, cognitive_profile)

    def _build_cognitive_profile(
        self,
        initial: dict[str, Any],
        autonomy: str,
        detected_language: str,
    ) -> dict[str, Any]:
        """
        認知プロファイルを構築

        明示的な回答がある場合はそれを使用、なければautonomyから推定
        """
        # 基本プロファイル（autonomyベースのデフォルト）
        base_profiles = {
            "obedient": {
                "thinking_pattern": "structural",
                "learning_type": "visual_text",
                "detail_orientation": "high",
                "preferred_structure": "hierarchical",
                "use_tables": True,
            },
            "collaborative": {
                "thinking_pattern": "hybrid",
                "learning_type": "visual_text",
                "detail_orientation": "medium",
                "preferred_structure": "contextual",
                "use_tables": True,
            },
            "autonomous": {
                "thinking_pattern": "fluid",
                "learning_type": "kinesthetic",
                "detail_orientation": "low",
                "preferred_structure": "flat",
                "use_tables": False,
            },
        }
        base = base_profiles.get(autonomy, base_profiles["collaborative"])

        # learning_scenario → thinking_pattern
        learning_scenario = initial.get("learning_scenario")
        if learning_scenario:
            thinking_map = {
                "overview": "structural",
                "tutorial": "structural",
                "example": "fluid",
                "question": "fluid",
            }
            base["thinking_pattern"] = thinking_map.get(learning_scenario, base["thinking_pattern"])

        # confusion_scenario → learning_type
        confusion_scenario = initial.get("confusion_scenario")
        if confusion_scenario:
            learning_map = {
                "reread": "visual_text",
                "example": "kinesthetic",
                "simplify": "visual_text",
                "ask": "auditory",
            }
            base["learning_type"] = learning_map.get(confusion_scenario, base["learning_type"])

        # info_load_scenario → detail_orientation
        info_load = initial.get("info_load_scenario")
        if info_load:
            detail_map = {
                "comfortable": "high",
                "skim": "medium",
                "overwhelmed": "low",
                "summary": "medium",
            }
            base["detail_orientation"] = detail_map.get(info_load, base["detail_orientation"])

        # format_scenario → preferred_structure, use_tables
        format_scenario = initial.get("format_scenario")
        if format_scenario:
            structure_map = {
                "structured": "hierarchical",
                "conversational": "contextual",
                "code_first": "flat",
                "table": "hierarchical",
            }
            base["preferred_structure"] = structure_map.get(format_scenario, base["preferred_structure"])
            base["use_tables"] = format_scenario in ["structured", "table"]

        # frustration_scenario → avoid_patterns
        frustration = initial.get("frustration_scenario", [])
        avoid_patterns = self._build_avoid_patterns(frustration, detected_language)
        if not avoid_patterns:
            # デフォルトのavoid_patterns
            avoid_patterns = self._get_default_avoid_patterns(autonomy, detected_language)

        # ideal_interaction → コミュニケーショントーン（persona_summaryに反映）
        ideal_interaction = initial.get("ideal_interaction")

        # persona_summary生成
        persona_summary = self._generate_persona_summary(
            base, ideal_interaction, detected_language
        )

        # formatting_principles（認知特性に基づく原則リスト）
        profile_for_principles = {
            "thinking_pattern": base["thinking_pattern"],
            "learning_type": base["learning_type"],
            "detail_orientation": base["detail_orientation"],
            "preferred_structure": base["preferred_structure"],
        }
        formatting_principles = self._get_formatting_principles(
            profile_for_principles, detected_language
        )

        return {
            "thinking_pattern": base["thinking_pattern"],
            "learning_type": base["learning_type"],
            "detail_orientation": base["detail_orientation"],
            "preferred_structure": base["preferred_structure"],
            "use_tables": base["use_tables"],
            "formatting_principles": formatting_principles,
            "avoid_patterns": avoid_patterns,
            "persona_summary": persona_summary,
        }

    def _build_avoid_patterns(
        self,
        frustration: list[str],
        detected_language: str,
    ) -> list[str]:
        """frustration_scenarioからavoid_patternsを生成"""
        if not frustration:
            return []

        patterns_ja = {
            "too_casual": "カジュアルすぎる口調",
            "too_long": "長すぎる回答",
            "too_abstract": "抽象的すぎる説明",
            "too_detailed": "細かすぎる説明",
            "uncertain": "曖昧な「〜かもしれません」表現",
            "emoji": "絵文字や過度な装飾",
        }
        patterns_en = {
            "too_casual": "overly casual tone",
            "too_long": "excessively long responses",
            "too_abstract": "overly abstract explanations",
            "too_detailed": "overly detailed explanations",
            "uncertain": "uncertain 'might be' expressions",
            "emoji": "emojis and excessive decorations",
        }
        patterns = patterns_ja if detected_language == "ja" else patterns_en

        return [patterns[f] for f in frustration if f in patterns]

    def _get_default_avoid_patterns(
        self,
        autonomy: str,
        detected_language: str,
    ) -> list[str]:
        """デフォルトのavoid_patternsを取得"""
        defaults = {
            "obedient": {
                "ja": ["曖昧な表現", "過度な装飾", "推測的な回答"],
                "en": ["vague expressions", "excessive decorations", "speculative answers"],
            },
            "collaborative": {
                "ja": ["過度な専門用語", "長すぎる説明"],
                "en": ["excessive jargon", "overly long explanations"],
            },
            "autonomous": {
                "ja": ["過度な説明", "細かすぎる指示", "冗長な表現"],
                "en": ["excessive explanations", "overly detailed instructions", "verbose expressions"],
            },
        }
        return defaults.get(autonomy, defaults["collaborative"]).get(
            detected_language, defaults["collaborative"]["en"]
        )

    def _get_formatting_principles(
        self,
        profile: dict[str, Any],
        detected_language: str,
    ) -> list[str]:
        """認知特性から原則ベースのガイドラインを生成"""
        thinking = profile.get("thinking_pattern", "hybrid")
        detail = profile.get("detail_orientation", "medium")
        structure = profile.get("preferred_structure", "hierarchical")
        learning = profile.get("learning_type", "visual_text")

        if detected_language == "ja":
            return self._get_formatting_principles_ja(thinking, detail, structure, learning)
        else:
            return self._get_formatting_principles_en(thinking, detail, structure, learning)

    def _get_formatting_principles_ja(
        self,
        thinking: str,
        detail: str,
        structure: str,
        learning: str,
    ) -> list[str]:
        """日本語の原則リストを生成"""
        principles = []

        # 思考パターンに基づく原則
        if thinking == "structural":
            principles.append("全体構造（マクロ）から詳細（ミクロ）へ順に説明")
            principles.append("階層構造・関係性・位置づけを明確にする")
        elif thinking == "fluid":
            principles.append("文脈と流れを重視し、自然な説明順序で展開")
            principles.append("具体例から一般化へ帰納的に説明")
        else:  # hybrid
            principles.append("状況に応じて全体像と具体例を使い分ける")

        # 詳細志向に基づく原則
        if detail == "high":
            principles.append("網羅的な情報を段階的に提示")
            principles.append("長文では適宜小結論を挟む")
        elif detail == "low":
            principles.append("核心的情報に絞り、簡潔に")
            principles.append("詳細は追加質問を待って展開")
        else:  # medium
            principles.append("バランスの取れた情報量で要点を明確に")

        # 構造の好みに基づく原則
        if structure == "hierarchical":
            principles.append("箇条書き・表・階層構造を活用して整理")
        elif structure == "flat":
            principles.append("フラットな箇条書きでシンプルに")
        else:  # contextual
            principles.append("文脈に応じた柔軟な構造で")

        # 学習タイプに基づく原則
        if learning == "kinesthetic":
            principles.append("実践的な例やハンズオンを優先")
        elif learning == "visual_diagram":
            principles.append("図表やフローで視覚的に表現")

        return principles

    def _get_formatting_principles_en(
        self,
        thinking: str,
        detail: str,
        structure: str,
        learning: str,
    ) -> list[str]:
        """英語の原則リストを生成"""
        principles = []

        # Thinking pattern principles
        if thinking == "structural":
            principles.append("Explain from overall structure (macro) to details (micro)")
            principles.append("Clarify hierarchies, relationships, and positioning")
        elif thinking == "fluid":
            principles.append("Prioritize context and flow with natural explanation order")
            principles.append("Explain inductively from examples to generalizations")
        else:  # hybrid
            principles.append("Flexibly use both overview and concrete examples")

        # Detail orientation principles
        if detail == "high":
            principles.append("Present comprehensive information progressively")
            principles.append("Include interim conclusions in long responses")
        elif detail == "low":
            principles.append("Focus on core information, keep it concise")
            principles.append("Expand details only when asked")
        else:  # medium
            principles.append("Provide balanced information with clear key points")

        # Structure preference principles
        if structure == "hierarchical":
            principles.append("Use bullet points, tables, and hierarchical structures")
        elif structure == "flat":
            principles.append("Use flat bullet points for simplicity")
        else:  # contextual
            principles.append("Adapt structure flexibly to context")

        # Learning type principles
        if learning == "kinesthetic":
            principles.append("Prioritize practical examples and hands-on content")
        elif learning == "visual_diagram":
            principles.append("Express visually with diagrams and flowcharts")

        return principles

    def _generate_persona_summary(
        self,
        profile: dict[str, Any],
        ideal_interaction: str | None,
        detected_language: str,
    ) -> str:
        """認知特性からペルソナサマリーを生成"""
        thinking = profile["thinking_pattern"]
        detail = profile["detail_orientation"]
        structure = profile["preferred_structure"]

        # 思考パターンの説明
        thinking_desc = {
            "ja": {
                "structural": "全体構造を先に把握してから詳細に進む構造型思考",
                "fluid": "具体例から始めて抽象化する流動型思考",
                "hybrid": "状況に応じて構造的/流動的アプローチを使い分ける混合型思考",
            },
            "en": {
                "structural": "structural thinking that grasps the overall structure first",
                "fluid": "fluid thinking that starts from examples and abstracts",
                "hybrid": "hybrid thinking that adapts approach to the situation",
            },
        }

        # 詳細志向の説明
        detail_desc = {
            "ja": {
                "high": "詳細な説明を好む",
                "medium": "バランスの取れた情報量を好む",
                "low": "要点を素早く把握したい",
            },
            "en": {
                "high": "prefers detailed explanations",
                "medium": "prefers balanced information",
                "low": "wants to quickly grasp key points",
            },
        }

        # 対話スタイルの説明
        interaction_desc = {
            "ja": {
                "mentor": "専門的なアドバイスを求める",
                "colleague": "対等な議論を好む",
                "assistant": "的確な指示への対応を求める",
                "teacher": "丁寧な説明を求める",
            },
            "en": {
                "mentor": "seeks expert advice",
                "colleague": "prefers equal discussion",
                "assistant": "expects prompt response to instructions",
                "teacher": "seeks patient explanations",
            },
        }

        lang = detected_language if detected_language in ["ja", "en"] else "en"

        parts = [
            thinking_desc[lang].get(thinking, thinking_desc[lang]["hybrid"]),
            detail_desc[lang].get(detail, detail_desc[lang]["medium"]),
        ]

        if ideal_interaction and ideal_interaction in interaction_desc[lang]:
            parts.append(interaction_desc[lang][ideal_interaction])

        if lang == "ja":
            return f"私は{parts[0]}の学習者です。{parts[1]}タイプで、" + (
                f"{parts[2]}傾向があります。" if len(parts) > 2 else "。"
            )
        else:
            return f"I am a learner with {parts[0]}. I {parts[1]}" + (
                f" and {parts[2]}." if len(parts) > 2 else "."
            )

    def _determine_recommended_style(
        self,
        cognitive_profile: dict[str, Any],
        autonomy: str,
    ) -> str:
        """認知プロファイルから推奨スタイルを決定"""
        detail = cognitive_profile["detail_orientation"]

        if detail == "high":
            return "strict"
        elif detail == "low":
            return "short"
        else:
            return "standard"

    def _get_tone_guidance_ja(self, autonomy: str) -> str:
        """自律性の好みに基づいてトーンガイダンスを生成（日本語）"""
        tones = {
            "obedient": "指示に忠実で的確なアシスタントとして対応。専門的かつ丁寧に。",
            "collaborative": "対等なパートナーとして一緒に考える姿勢。提案や代替案を積極的に。",
            "autonomous": "専門家として自律的に判断し、積極的に提案。簡潔で効率的なやり取りを。",
        }
        return tones.get(autonomy, tones["collaborative"])

    def _get_tone_guidance_en(self, autonomy: str) -> str:
        """自律性の好みに基づいてトーンガイダンスを生成（英語）"""
        tones = {
            "obedient": "Respond as a precise and reliable assistant. Professional and thorough.",
            "collaborative": "Act as an equal partner, thinking together. Actively offer suggestions and alternatives.",
            "autonomous": "Make autonomous decisions as an expert. Keep interactions concise and efficient.",
        }
        return tones.get(autonomy, tones["collaborative"])

    def _generate_mock_ja(
        self,
        purpose: str,
        autonomy: str,
        recommended_style: str,
        cognitive_profile: dict,
    ) -> dict[str, Any]:
        """日本語モック生成（原則ベース）"""
        persona = cognitive_profile["persona_summary"]
        avoid = "、".join(cognitive_profile["avoid_patterns"])
        principles = cognitive_profile["formatting_principles"]

        # 原則リストをフォーマット
        principles_short = "\n".join(f"- {p}" for p in principles[:3])
        principles_standard = "\n".join(f"- {p}" for p in principles[:5])
        principles_full = "\n".join(f"- {p}" for p in principles)

        # トーンガイダンスを生成
        tone = self._get_tone_guidance_ja(autonomy)

        short_prompt = f"""{persona}

## 回答の原則
{principles_short}
- {avoid}は避ける"""

        standard_prompt = f"""{persona}
以下の原則で{purpose}をサポートしてください。

## 回答の原則
{principles_standard}

## トーン
{tone}

## 回避事項
{avoid}は避けてください。"""

        strict_prompt = f"""{persona}

## 回答の原則
{principles_full}

## 認知特性
- 思考パターン: {cognitive_profile["thinking_pattern"]}型
- 学習タイプ: {cognitive_profile["learning_type"]}
- 詳細志向度: {cognitive_profile["detail_orientation"]}
- 情報構造: {cognitive_profile["preferred_structure"]}構造を好む

## トーン・インタラクション
{tone}

## 回答形式の指針
- 冒頭で結論・要点を述べる
- 根拠・詳細を段階的に展開
- 具体例は実践的なものを選ぶ
- コードを含む場合は適宜コメントを付与

## 回避すべきパターン
以下は私の認知特性に合わないため、避けてください：
- {avoid}

## 品質基準
- 正確性: 不確実な情報には明示的に注記
- 構造化: 視覚的に読み取りやすいフォーマット
- 実践性: すぐに適用可能な具体例"""

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
                    "description": "ペルソナ宣言と核心的な原則のみを含む簡潔なプロンプト",
                },
                {
                    "style": "standard",
                    "name": "スタンダード (Standard)",
                    "prompt": standard_prompt,
                    "description": "認知特性に基づく原則とトーン指針を含むバランスの取れたプロンプト",
                },
                {
                    "style": "strict",
                    "name": "ストリクト (Strict)",
                    "prompt": strict_prompt,
                    "description": "完全な認知プロファイルと詳細な原則・品質基準を含むプロンプト",
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
        """英語モック生成（原則ベース）"""
        persona = cognitive_profile["persona_summary"]
        avoid = ", ".join(cognitive_profile["avoid_patterns"])
        principles = cognitive_profile["formatting_principles"]

        # Format principle lists
        principles_short = "\n".join(f"- {p}" for p in principles[:3])
        principles_standard = "\n".join(f"- {p}" for p in principles[:5])
        principles_full = "\n".join(f"- {p}" for p in principles)

        # Generate tone guidance
        tone = self._get_tone_guidance_en(autonomy)

        short_prompt = f"""{persona}

## Response Principles
{principles_short}
- Avoid: {avoid}"""

        standard_prompt = f"""{persona}
Please support me with {purpose} following these principles.

## Response Principles
{principles_standard}

## Tone
{tone}

## Avoid
Please avoid: {avoid}"""

        strict_prompt = f"""{persona}

## Response Principles
{principles_full}

## Cognitive Traits
- Thinking pattern: {cognitive_profile["thinking_pattern"]} type
- Learning type: {cognitive_profile["learning_type"]}
- Detail orientation: {cognitive_profile["detail_orientation"]}
- Preferred structure: {cognitive_profile["preferred_structure"]}

## Tone & Interaction
{tone}

## Response Guidelines
- State conclusions and key points at the beginning
- Expand supporting details progressively
- Choose practical, applicable examples
- Include comments when providing code

## Patterns to Avoid
The following don't match my cognitive style, please avoid:
- {avoid}

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
                    "description": "Concise prompt with persona and core principles only",
                },
                {
                    "style": "standard",
                    "name": "Standard",
                    "prompt": standard_prompt,
                    "description": "Balanced prompt with cognitive-based principles and tone guidance",
                },
                {
                    "style": "strict",
                    "name": "Strict",
                    "prompt": strict_prompt,
                    "description": "Complete prompt with full cognitive profile and detailed principles",
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
