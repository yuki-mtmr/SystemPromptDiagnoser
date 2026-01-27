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

## 【最重要】出力言語ルール
検出された言語: {detected_language}

【絶対遵守】以下の全ての出力は必ず {detected_language} で生成してください：
- user_profile（全フィールド）
- recommendation_reason
- variants内のpromptとdescription

{detected_language}が"ja"の場合：
- 日本語のみで出力すること
- 英語は一切使用禁止（技術用語やスタイル名を除く）
- 自然で読みやすい日本語で記述すること

{detected_language}が"en"の場合：
- 英語のみで出力すること

## 指示
全ての回答を分析し、以下を行ってください：

1. **認知プロファイル分析**: ユーザーの思考パターン、学習タイプ、情報処理の好みを特定
2. **ユーザープロファイル抽出**: ユーザーの特性、好み、ニーズを特定
3. **高度に個人化されたシステムプロンプト生成**: 認知特性を反映した3種類のプロンプトを生成

## ユーザーの全回答
{all_answers}

## 検出された言語（再確認）
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
- 【最重要】全ての出力（user_profile, recommendation_reason, variants）は検出された言語（{detected_language}）で生成してください
- {detected_language}が"ja"の場合、プロンプト本文は必ず日本語で生成すること（英語禁止）
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


# 認知特性質問 - ステップ2（シナリオベース・間接的質問）
COGNITIVE_QUESTIONS_STEP2 = {
    "ja": [
        {
            "id": "learning_scenario",
            "question": "新しいプログラミング言語やツールを学ぶとき、最初に何をしますか？",
            "type": "choice",
            "choices": [
                {
                    "value": "overview",
                    "label": "公式ドキュメントの概要を読む",
                    "description": "全体像や設計思想から入る",
                },
                {
                    "value": "tutorial",
                    "label": "チュートリアルを手を動かしながら進める",
                    "description": "具体例から学ぶ",
                },
                {
                    "value": "example",
                    "label": "既存のコードを読んで真似する",
                    "description": "実例から抽象化する",
                },
                {
                    "value": "question",
                    "label": "解決したい課題から逆引きで調べる",
                    "description": "必要な部分だけ学ぶ",
                },
            ],
        },
        {
            "id": "confusion_scenario",
            "question": "説明を読んでも理解できないとき、どうすることが多いですか？",
            "type": "choice",
            "choices": [
                {
                    "value": "reread",
                    "label": "最初から読み直して全体を整理する",
                    "description": "構造を再把握する",
                },
                {
                    "value": "example",
                    "label": "具体例やコードを探して試す",
                    "description": "手を動かして理解する",
                },
                {
                    "value": "simplify",
                    "label": "もっとシンプルな説明を探す",
                    "description": "抽象度を下げる",
                },
                {
                    "value": "ask",
                    "label": "誰かに質問して対話で理解する",
                    "description": "やり取りで明確にする",
                },
            ],
        },
        {
            "id": "info_load_scenario",
            "question": "長い技術文書やマニュアルを読むとき、どう感じますか？",
            "type": "choice",
            "choices": [
                {
                    "value": "comfortable",
                    "label": "詳しい方が安心する",
                    "description": "網羅的な情報があると理解しやすい",
                },
                {
                    "value": "skim",
                    "label": "目次や見出しを見て必要な部分だけ読む",
                    "description": "効率的に情報を取得したい",
                },
                {
                    "value": "overwhelmed",
                    "label": "情報量が多いと疲れる",
                    "description": "段階的に提示してほしい",
                },
                {
                    "value": "summary",
                    "label": "最初に要約があると助かる",
                    "description": "全体像を先に知りたい",
                },
            ],
        },
        {
            "id": "format_scenario",
            "question": "AIからの回答で「これは分かりやすい」と感じたのはどんな形式でしたか？",
            "type": "choice",
            "choices": [
                {
                    "value": "structured",
                    "label": "見出しと箇条書きで整理された回答",
                    "description": "階層的に構造化された形式",
                },
                {
                    "value": "conversational",
                    "label": "自然な文章で説明された回答",
                    "description": "読み物として理解しやすい",
                },
                {
                    "value": "code_first",
                    "label": "コードが最初にあり、後から解説",
                    "description": "実例先行型",
                },
                {
                    "value": "table",
                    "label": "表や比較でまとめられた回答",
                    "description": "視覚的に整理された形式",
                },
            ],
        },
    ],
    "en": [
        {
            "id": "learning_scenario",
            "question": "When learning a new programming language or tool, what do you do first?",
            "type": "choice",
            "choices": [
                {
                    "value": "overview",
                    "label": "Read the official documentation overview",
                    "description": "Start with the big picture and design philosophy",
                },
                {
                    "value": "tutorial",
                    "label": "Follow a tutorial hands-on",
                    "description": "Learn from concrete examples",
                },
                {
                    "value": "example",
                    "label": "Read existing code and imitate it",
                    "description": "Abstract from real examples",
                },
                {
                    "value": "question",
                    "label": "Research based on a specific problem to solve",
                    "description": "Learn only what's needed",
                },
            ],
        },
        {
            "id": "confusion_scenario",
            "question": "When you read an explanation but don't understand, what do you usually do?",
            "type": "choice",
            "choices": [
                {
                    "value": "reread",
                    "label": "Re-read from the beginning to organize the whole",
                    "description": "Re-grasp the structure",
                },
                {
                    "value": "example",
                    "label": "Search for concrete examples or code to try",
                    "description": "Understand by doing",
                },
                {
                    "value": "simplify",
                    "label": "Look for a simpler explanation",
                    "description": "Lower the abstraction level",
                },
                {
                    "value": "ask",
                    "label": "Ask someone and understand through dialogue",
                    "description": "Clarify through interaction",
                },
            ],
        },
        {
            "id": "info_load_scenario",
            "question": "How do you feel when reading long technical documents or manuals?",
            "type": "choice",
            "choices": [
                {
                    "value": "comfortable",
                    "label": "Detailed is better - feels more secure",
                    "description": "Comprehensive info helps understanding",
                },
                {
                    "value": "skim",
                    "label": "Check TOC and read only needed parts",
                    "description": "Want to get info efficiently",
                },
                {
                    "value": "overwhelmed",
                    "label": "Too much info is tiring",
                    "description": "Prefer step-by-step presentation",
                },
                {
                    "value": "summary",
                    "label": "A summary at the start would help",
                    "description": "Want to know the big picture first",
                },
            ],
        },
        {
            "id": "format_scenario",
            "question": "What format of AI response did you find most understandable?",
            "type": "choice",
            "choices": [
                {
                    "value": "structured",
                    "label": "Response organized with headings and bullet points",
                    "description": "Hierarchically structured format",
                },
                {
                    "value": "conversational",
                    "label": "Response explained in natural prose",
                    "description": "Easier to read as narrative",
                },
                {
                    "value": "code_first",
                    "label": "Code first, then explanation",
                    "description": "Example-first approach",
                },
                {
                    "value": "table",
                    "label": "Response summarized in tables or comparisons",
                    "description": "Visually organized format",
                },
            ],
        },
    ],
}


# 認知特性質問 - ステップ3（好み・回避パターン）
COGNITIVE_QUESTIONS_STEP3 = {
    "ja": [
        {
            "id": "frustration_scenario",
            "question": "AIの回答で「これは合わない」と感じたのはどんな時でしたか？（複数選択可）",
            "type": "multi_choice",
            "choices": [
                {
                    "value": "too_casual",
                    "label": "カジュアルすぎる口調だった",
                    "description": "フレンドリーすぎて専門性を感じなかった",
                },
                {
                    "value": "too_long",
                    "label": "回答が長すぎて要点が分からなかった",
                    "description": "冗長で本質が見えなかった",
                },
                {
                    "value": "too_abstract",
                    "label": "抽象的すぎて具体例がなかった",
                    "description": "実践に結びつかなかった",
                },
                {
                    "value": "too_detailed",
                    "label": "細かすぎて本質が見えなかった",
                    "description": "詳細に埋もれて全体像が掴めなかった",
                },
                {
                    "value": "uncertain",
                    "label": "「〜かもしれません」が多くて不安になった",
                    "description": "自信のない回答が信頼できなかった",
                },
                {
                    "value": "emoji",
                    "label": "絵文字や装飾が多すぎた",
                    "description": "視覚的なノイズが気になった",
                },
            ],
        },
        {
            "id": "ideal_interaction",
            "question": "AIとの理想的なやり取りはどんなイメージですか？",
            "type": "choice",
            "choices": [
                {
                    "value": "mentor",
                    "label": "経験豊富な先輩に相談する感覚",
                    "description": "的確なアドバイスをくれる",
                },
                {
                    "value": "colleague",
                    "label": "同僚と一緒に考える感覚",
                    "description": "対等に議論できる",
                },
                {
                    "value": "assistant",
                    "label": "優秀なアシスタントに指示する感覚",
                    "description": "指示通りに素早く動く",
                },
                {
                    "value": "teacher",
                    "label": "丁寧な先生に教わる感覚",
                    "description": "分かるまで説明してくれる",
                },
            ],
        },
    ],
    "en": [
        {
            "id": "frustration_scenario",
            "question": "When did you feel an AI response didn't work for you? (Select multiple)",
            "type": "multi_choice",
            "choices": [
                {
                    "value": "too_casual",
                    "label": "Tone was too casual",
                    "description": "Too friendly, didn't feel professional",
                },
                {
                    "value": "too_long",
                    "label": "Response was too long to find the point",
                    "description": "Verbose, couldn't see the essence",
                },
                {
                    "value": "too_abstract",
                    "label": "Too abstract without concrete examples",
                    "description": "Couldn't connect to practice",
                },
                {
                    "value": "too_detailed",
                    "label": "Too detailed to see the big picture",
                    "description": "Lost in details, couldn't grasp overall view",
                },
                {
                    "value": "uncertain",
                    "label": "Too many 'might be' or 'perhaps'",
                    "description": "Uncertain answers felt unreliable",
                },
                {
                    "value": "emoji",
                    "label": "Too many emojis or decorations",
                    "description": "Visual noise was distracting",
                },
            ],
        },
        {
            "id": "ideal_interaction",
            "question": "What's your ideal image of interacting with AI?",
            "type": "choice",
            "choices": [
                {
                    "value": "mentor",
                    "label": "Like consulting an experienced senior",
                    "description": "Gives accurate advice",
                },
                {
                    "value": "colleague",
                    "label": "Like thinking together with a colleague",
                    "description": "Can discuss as equals",
                },
                {
                    "value": "assistant",
                    "label": "Like directing a capable assistant",
                    "description": "Moves quickly as instructed",
                },
                {
                    "value": "teacher",
                    "label": "Like learning from a patient teacher",
                    "description": "Explains until you understand",
                },
            ],
        },
    ],
}


def get_cognitive_questions_step2(language: str = "ja") -> list:
    """
    認知特性質問（ステップ2）を取得

    Args:
        language: 言語コード（"ja" または "en"）

    Returns:
        ステップ2の質問リスト
    """
    return COGNITIVE_QUESTIONS_STEP2.get(language, COGNITIVE_QUESTIONS_STEP2["en"])


def get_cognitive_questions_step3(language: str = "ja") -> list:
    """
    認知特性質問（ステップ3）を取得

    Args:
        language: 言語コード（"ja" または "en"）

    Returns:
        ステップ3の質問リスト
    """
    return COGNITIVE_QUESTIONS_STEP3.get(language, COGNITIVE_QUESTIONS_STEP3["en"])
