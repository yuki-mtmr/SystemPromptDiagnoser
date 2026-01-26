"""
v2 診断フロー用プロンプトテンプレート

動的質問生成と特性抽出・プロンプト生成のためのテンプレート
"""

# 言語検出と動的質問生成用プロンプト
LANGUAGE_DETECTION_AND_QUESTION_GENERATION = """あなたはユーザーのAI利用ニーズを深く理解するための質問を生成するアシスタントです。

## 指示
ユーザーの回答を分析し、以下の2つを行ってください：

1. **言語検出**: ユーザーが主に使用している言語を検出してください（日本語、英語、その他）
2. **深掘り質問生成**: ユーザーの回答から、まだ明確でない点や深掘りすべき点を特定し、1-2個の追加質問を生成してください

## ユーザーの回答
{user_answers}

## 出力形式（JSON）
{{
  "detected_language": "ja" または "en",
  "followup_questions": [
    {{
      "id": "fq1",
      "question": "質問文（ユーザーの言語で）",
      "type": "freeform" または "choice",
      "choices": ["選択肢1", "選択肢2", "選択肢3"] // typeがchoiceの場合のみ
    }}
  ],
  "analysis_notes": "ユーザーの回答から読み取れた特性（内部メモ用）"
}}

## 注意事項
- 質問は必ずユーザーが使用した言語で生成してください
- 質問は具体的で答えやすいものにしてください
- 深掘りが不要と判断した場合は、空の配列を返してください
- 分析ノートは後続の処理で活用されます
"""

# プロファイル抽出とシステムプロンプト生成用プロンプト
PROFILE_EXTRACTION_AND_PROMPT_GENERATION = """あなたはユーザーの認知特性を深く分析し、高度に個人化されたAIシステムプロンプトを生成する専門家です。

## 指示
全ての回答を分析し、以下を行ってください：

1. **認知プロファイル分析**: ユーザーの思考パターン、学習タイプ、情報処理の好みを特定
2. **ユーザープロファイル抽出**: ユーザーの特性、好み、ニーズを特定
3. **高度に個人化されたシステムプロンプト生成**: 認知特性を反映した3種類のプロンプトを生成

## ユーザーの全回答
{all_answers}

## 検出された言語
{detected_language}

## 出力形式（JSON）
{{
  "user_profile": {{
    "primary_use_case": "主な用途（コーディング、文章作成、リサーチ、一般質問など）",
    "autonomy_preference": "AIの自律性の好み（指示に忠実、協調的、自律的）",
    "communication_style": "好みのコミュニケーションスタイル",
    "key_traits": ["特性1", "特性2", "特性3"],
    "detected_needs": ["ニーズ1", "ニーズ2"],
    "cognitive_profile": {{
      "thinking_pattern": "structural" または "fluid" または "hybrid",
      "learning_type": "visual_text" または "visual_diagram" または "auditory" または "kinesthetic",
      "detail_orientation": "high" または "medium" または "low",
      "preferred_structure": "hierarchical" または "flat" または "contextual",
      "use_tables": true または false,
      "formatting_rules": {{
        "paragraph_length": "80-120語/段落",
        "heading_length": "10-20トークン",
        "list_items": "3-7項目"
      }},
      "avoid_patterns": ["過度な絵文字", "スラング", "曖昧な表現"],
      "persona_summary": "ユーザーの認知特性を一文で表現（例：全体構造の整合性が取れたときに理解が成立する、静的構造思考型の学習者です）"
    }}
  }},
  "recommended_style": "short" または "standard" または "strict",
  "recommendation_reason": "推奨理由（ユーザーの言語で）",
  "variants": [
    {{
      "style": "short",
      "name": "ショート (Short)",
      "prompt": "生成されたシステムプロンプト（ユーザーの言語で）",
      "description": "このスタイルの説明（ユーザーの言語で）"
    }},
    {{
      "style": "standard",
      "name": "スタンダード (Standard)",
      "prompt": "生成されたシステムプロンプト（ユーザーの言語で）",
      "description": "このスタイルの説明（ユーザーの言語で）"
    }},
    {{
      "style": "strict",
      "name": "ストリクト (Strict)",
      "prompt": "生成されたシステムプロンプト（ユーザーの言語で）",
      "description": "このスタイルの説明（ユーザーの言語で）"
    }}
  ]
}}

## 認知プロファイル分析ガイドライン

### thinking_pattern（思考パターン）
- **structural**: 全体構造を先に把握し、体系的に理解する。マクロ→ミクロの順で情報を好む
- **fluid**: 具体例から始めて抽象化する。ストーリー性を重視
- **hybrid**: 状況に応じて両方のアプローチを使い分ける

### learning_type（学習タイプ）
- **visual_text**: テキストの視覚的読み込みを好む。コードブロック、箇条書きを重視
- **visual_diagram**: 図表、フローチャート、マインドマップを好む
- **auditory**: 説明的な文章、対話形式を好む
- **kinesthetic**: ハンズオン、実践的な例を好む

### detail_orientation（詳細志向度）
- **high**: 詳細な説明、エッジケース、注釈を求める
- **medium**: バランスの取れた詳細度
- **low**: 要点のみ、シンプルな回答を好む

### preferred_structure（情報構造の好み）
- **hierarchical**: マクロ→メソ→ミクロの3層構造
- **flat**: フラットな箇条書き
- **contextual**: 文脈に応じた柔軟な構造

## プロンプト生成ガイドライン

### 共通原則（全スタイル必須）
1. **ペルソナ宣言**を冒頭に含める（例：「私は〇〇型の学習者です。」）
2. **情報構造化ルール**を表形式で示す（use_tables=trueの場合）
3. **認知特性**を箇条書きで明記
4. **回避パターン**を明確に指示

### Short スタイル（200-350文字）
- ペルソナ宣言 + 3つの核心的ルール
- 最重要な認知特性のみ

### Standard スタイル（400-600文字）
- ペルソナ宣言 + 情報構造化ルール表 + 認知特性
- フォーマットルールを具体的数値で指定

### Strict スタイル（800-1200文字）
- 完全なペルソナ宣言
- 詳細な情報構造化ルール表（要素、ルール列）
- 認知特性の詳細説明
- 回避パターンの完全なリスト
- 具体的なフォーマット数値制約

## 生成されるプロンプトの品質基準

良いプロンプト例（strictスタイル）:
```
私は全体構造の整合性が取れたときに理解が成立する、静的構造思考型の学習者です。
以下のフォーマットで情報を構造化してください：

## 情報構造化の原則
| 要素 | ルール |
|------|--------|
| 階層構造 | マクロ→メソ→ミクロの3層 |
| 見出し | 10-20トークン、「〜について」禁止 |
| 段落 | 80-120語/段落 |
| 箇条書き | 3-7項目、論理順 |

## 認知特性
- テキストの視覚的読み込みタイプ
- 「構造型・自律先行性・探索思考」という三要素
- 感覚過敏があり、過度な絵文字・装飾・スラングは避けてください
```

悪いプロンプト例（避けるべき）:
```
あなたはコーディングのサポートをサポートするAIアシスタントです。
- ユーザーの質問に的確に回答してください
- 必要に応じて追加の情報を提供してください
```

## 注意事項
- 全ての出力はユーザーが使用した言語で生成してください
- プロンプトはユーザーの認知特性を深く反映させてください
- 汎用的・表面的なプロンプトは絶対に生成しないでください
- recommended_style はユーザーの詳細志向度と自律性の好みから判断してください
"""

# システムプロンプトのスタイル名（多言語対応）
STYLE_NAMES = {
    "ja": {
        "short": "ショート (Short)",
        "standard": "スタンダード (Standard)",
        "strict": "ストリクト (Strict)",
    },
    "en": {
        "short": "Short",
        "standard": "Standard",
        "strict": "Strict",
    },
}

# 初期質問（固定）
INITIAL_QUESTIONS = {
    "ja": {
        "purpose": {
            "id": "purpose",
            "question": "AIに何をしてもらいたいですか？",
            "type": "freeform",
            "placeholder": "例: コードレビュー、文章の校正、アイデア出し...",
            "suggestions": [
                "コーディングのサポート",
                "文章作成・編集",
                "情報のリサーチ",
                "アイデアのブレインストーミング",
                "学習・教育サポート",
            ],
        },
        "autonomy": {
            "id": "autonomy",
            "question": "AIにどの程度主導権を持ってほしいですか？",
            "type": "choice",
            "choices": [
                {
                    "value": "obedient",
                    "label": "指示に忠実",
                    "description": "私の指示通りに動いてほしい",
                },
                {
                    "value": "collaborative",
                    "label": "一緒に考える",
                    "description": "提案しながら一緒に進めてほしい",
                },
                {
                    "value": "autonomous",
                    "label": "自律的",
                    "description": "自分で判断して積極的に動いてほしい",
                },
            ],
        },
    },
    "en": {
        "purpose": {
            "id": "purpose",
            "question": "What would you like AI to help you with?",
            "type": "freeform",
            "placeholder": "e.g., code review, proofreading, brainstorming...",
            "suggestions": [
                "Coding support",
                "Writing & editing",
                "Research",
                "Brainstorming ideas",
                "Learning & education",
            ],
        },
        "autonomy": {
            "id": "autonomy",
            "question": "How much autonomy would you like the AI to have?",
            "type": "choice",
            "choices": [
                {
                    "value": "obedient",
                    "label": "Follow instructions",
                    "description": "I want it to follow my instructions exactly",
                },
                {
                    "value": "collaborative",
                    "label": "Collaborate",
                    "description": "I want it to make suggestions and work together",
                },
                {
                    "value": "autonomous",
                    "label": "Autonomous",
                    "description": "I want it to make decisions and act proactively",
                },
            ],
        },
    },
}


def get_initial_questions(language: str = "ja") -> dict:
    """
    初期質問を取得

    Args:
        language: 言語コード（"ja" または "en"）

    Returns:
        初期質問の辞書
    """
    return INITIAL_QUESTIONS.get(language, INITIAL_QUESTIONS["en"])


def get_style_name(style: str, language: str = "ja") -> str:
    """
    スタイル名を取得

    Args:
        style: スタイル（"short", "standard", "strict"）
        language: 言語コード

    Returns:
        ローカライズされたスタイル名
    """
    names = STYLE_NAMES.get(language, STYLE_NAMES["en"])
    return names.get(style, style)
