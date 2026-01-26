"""
LLM分析用プロンプト

ユーザーの認知特性を分析するためのプロンプト定義
ルールベースマッピングではなく、LLMによる真の個別分析を行う
"""
import json
from typing import Any


ANALYSIS_SYSTEM_PROMPT = """あなたは認知心理学と学習スタイル分析の専門家です。

ユーザーの回答を深く分析し、その人固有の認知特性を抽出してください。

重要な原則:
1. テンプレート的な回答を避け、各ユーザーに固有の分析を行う
2. 回答の具体的な内容、言葉遣い、ニュアンスから特性を推測する
3. 表面的なキーワードマッチングではなく、文脈を理解した分析を行う
4. 矛盾する特性がある場合は、より支配的な傾向を判断する

You are an expert in cognitive psychology and learning style analysis.
Analyze the user's responses deeply and extract their unique cognitive traits.
Focus on individualized, specific analysis rather than generic templates."""


PERSONALITY_ANALYSIS_PROMPT = """以下のユーザー回答を分析し、認知特性を抽出してください。

## ユーザー回答
{answers}

{conversation_context}

## 抽出する特性

各特性について、ユーザーの回答から具体的な根拠を示しながら判断してください。

1. **thinking_pattern** (思考パターン):
   - "structural": 全体構造を先に把握してから詳細に進む。概要、フレームワーク、体系を好む。
   - "fluid": 具体例や実践から始めて抽象化する。ハンズオン、試行錯誤を好む。
   - "hybrid": 状況に応じて両方のアプローチを使い分ける。

2. **learning_type** (学習タイプ):
   - "visual_text": テキストベースの説明、文章での理解を好む
   - "visual_diagram": 図解、フローチャート、視覚的表現を好む
   - "auditory": 対話、説明を聞くことで理解する
   - "kinesthetic": 実際に手を動かす、コードを書くことで理解する

3. **detail_orientation** (詳細志向度):
   - "high": 詳細な説明を好む。網羅的な情報、根拠、例外ケースまで知りたい
   - "medium": バランスの取れた情報量。要点と必要な詳細
   - "low": 要点のみ。簡潔さ、素早い理解を優先

4. **preferred_structure** (好む情報構造):
   - "hierarchical": 階層的な構造。見出し、番号付きリスト、明確な区分
   - "flat": フラットな構造。段落ベース、会話調
   - "contextual": 文脈依存。状況に応じて柔軟に

5. **avoid_patterns** (避けるべきパターン):
   ユーザーが不快に感じる、または学習を妨げる可能性のあるコミュニケーションパターンのリスト。
   例: "過度な絵文字", "長すぎる説明", "曖昧な表現", "専門用語の多用"

6. **persona_summary** (ペルソナ説明):
   このユーザーの認知特性を2-3文で説明。
   「私は〜」形式で、ユーザーがシステムプロンプトとして使える形式で。

## 出力形式

以下のJSON形式で出力してください。余計なテキストは含めず、JSONのみを出力:

```json
{{
  "thinking_pattern": "structural" | "fluid" | "hybrid",
  "learning_type": "visual_text" | "visual_diagram" | "auditory" | "kinesthetic",
  "detail_orientation": "high" | "medium" | "low",
  "preferred_structure": "hierarchical" | "flat" | "contextual",
  "use_tables": true | false,
  "avoid_patterns": ["パターン1", "パターン2", ...],
  "persona_summary": "私は〜の学習者です。...",
  "analysis_reasoning": "この判断の根拠: ..."
}}
```

【重要】
- 各ユーザーに固有の分析を行い、テンプレート的な回答は避けてください
- 回答の具体的な内容、言葉遣い、ニュアンスから特性を推測してください
- persona_summaryは検出された言語（日本語/英語）で記述してください
"""


def build_analysis_prompt(
    answers: dict[str, Any],
    conversation_context: str | None = None,
) -> str:
    """
    分析プロンプトを構築

    Args:
        answers: ユーザーの回答（purpose, autonomy など）
        conversation_context: 過去の会話コンテキスト（オプション）

    Returns:
        構築された分析プロンプト
    """
    # 回答をJSON形式で整形
    answers_str = json.dumps(answers, ensure_ascii=False, indent=2)

    # 会話コンテキストのセクションを構築
    if conversation_context and conversation_context.strip():
        context_section = f"""## 過去のAI会話からの追加コンテキスト

以下の会話履歴も分析に活用してください。ユーザーの質問の仕方、好む説明スタイル、
フラストレーションを感じている点などを読み取ってください。

```
{conversation_context}
```
"""
    else:
        context_section = ""

    # プロンプトを構築
    prompt = PERSONALITY_ANALYSIS_PROMPT.format(
        answers=answers_str,
        conversation_context=context_section,
    )

    return prompt
