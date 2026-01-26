"""
Prompt templates for system prompt generation.

These templates define the structure and style for each prompt variant:
- Short: Minimal, essential guidance only
- Standard: Balanced coverage with key guidelines
- Strict: Comprehensive rules and detailed instructions
"""

from typing import TypedDict


class PromptTemplate(TypedDict):
    style: str
    name: str
    name_ja: str
    description: str
    description_ja: str
    generation_instruction: str


PROMPT_TEMPLATES: dict[str, PromptTemplate] = {
    "short": {
        "style": "short",
        "name": "Short",
        "name_ja": "ショート (Short)",
        "description": "Minimal prompt with essential guidance only. Best for quick interactions.",
        "description_ja": "シンプルで要点を押さえたプロンプト。素早いやり取りに最適。",
        "generation_instruction": """Generate a SHORT system prompt (2-3 sentences maximum).
Focus only on the most essential characteristics:
- Define the AI's primary role in one sentence
- Add one key behavioral guideline
Keep it minimal and impactful."""
    },
    "standard": {
        "style": "standard",
        "name": "Standard",
        "name_ja": "スタンダード (Standard)",
        "description": "Balanced prompt with clear guidelines. Recommended for everyday use.",
        "description_ja": "バランスの取れた汎用的なプロンプト。日常的な使用に推奨。",
        "generation_instruction": """Generate a STANDARD system prompt (4-6 bullet points or numbered items).
Include a balanced coverage of:
- Role definition
- Communication style
- Key behavioral guidelines
- Response approach
Format with clear sections or numbered list."""
    },
    "strict": {
        "style": "strict",
        "name": "Strict",
        "name_ja": "ストリクト (Strict)",
        "description": "Comprehensive prompt with detailed rules. Best for professional or specialized tasks.",
        "description_ja": "詳細な指示を含む厳格なプロンプト。専門的な作業に最適。",
        "generation_instruction": """Generate a STRICT, comprehensive system prompt (8-12 points).
Cover all aspects thoroughly:
- Core identity and role
- Communication principles
- Behavioral rules
- Response formatting guidelines
- Handling uncertainty and edge cases
- Prohibited behaviors
Use clear sections with headers."""
    }
}


# Use case specific context additions
USE_CASE_CONTEXTS = {
    "coding": {
        "context": "software development and programming",
        "additional_guidance": [
            "Provide code examples when helpful",
            "Explain technical concepts clearly",
            "Follow best practices and conventions",
            "Consider security and performance"
        ]
    },
    "writing": {
        "context": "content creation and writing assistance",
        "additional_guidance": [
            "Focus on clarity and engagement",
            "Match the requested style and tone",
            "Offer constructive suggestions",
            "Maintain consistent voice"
        ]
    },
    "research": {
        "context": "research and information synthesis",
        "additional_guidance": [
            "Cite sources when possible",
            "Distinguish facts from interpretations",
            "Present multiple perspectives",
            "Acknowledge limitations in knowledge"
        ]
    },
    "general": {
        "context": "general-purpose assistance",
        "additional_guidance": [
            "Be versatile and adaptive",
            "Ask clarifying questions when needed",
            "Provide balanced, helpful responses",
            "Match the user's communication style"
        ]
    }
}


# Tone modifiers
TONE_MODIFIERS = {
    "formal": {
        "description": "professional and business-appropriate",
        "guidelines": [
            "Use formal language and structure",
            "Avoid colloquialisms and casual expressions",
            "Maintain a respectful, professional tone"
        ]
    },
    "casual": {
        "description": "friendly and conversational",
        "guidelines": [
            "Use a warm, approachable tone",
            "Feel free to use contractions and casual language",
            "Be personable while staying helpful"
        ]
    },
    "technical": {
        "description": "precise with technical terminology",
        "guidelines": [
            "Use accurate technical terminology",
            "Be precise and detailed in explanations",
            "Assume familiarity with domain concepts"
        ]
    }
}


# Strictness behaviors
STRICTNESS_BEHAVIORS = {
    "flexible": {
        "description": "adaptable and open to different approaches",
        "guidelines": [
            "Be willing to explore alternatives",
            "Adapt to user preferences",
            "Offer multiple options when appropriate"
        ]
    },
    "strict": {
        "description": "rule-following and focused on accuracy",
        "guidelines": [
            "Prioritize accuracy over creativity",
            "Follow established conventions",
            "Verify information before providing"
        ]
    },
    "creative": {
        "description": "innovative and exploratory",
        "guidelines": [
            "Offer creative and unconventional ideas",
            "Think outside the box",
            "Encourage experimentation"
        ]
    }
}


def get_prompt_template(style: str) -> PromptTemplate:
    """Get the prompt template for a given style."""
    return PROMPT_TEMPLATES.get(style, PROMPT_TEMPLATES["standard"])


def get_use_case_context(use_case: str) -> dict:
    """Get the use case context information."""
    return USE_CASE_CONTEXTS.get(use_case, USE_CASE_CONTEXTS["general"])


def get_tone_modifier(tone: str) -> dict:
    """Get the tone modifier information."""
    return TONE_MODIFIERS.get(tone, TONE_MODIFIERS["formal"])


def get_strictness_behavior(strictness: str) -> dict:
    """Get the strictness behavior information."""
    return STRICTNESS_BEHAVIORS.get(strictness, STRICTNESS_BEHAVIORS["flexible"])
