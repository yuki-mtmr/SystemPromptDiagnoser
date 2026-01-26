"""
LangGraph workflow for system prompt diagnosis and generation.

This workflow processes user preferences and generates three variants of
system prompts (Short, Standard, Strict) using Gemini LLM.

Supports both synchronous and asynchronous execution with parallel LLM calls.
"""

import asyncio
from typing import TypedDict, Optional, Annotated
from operator import add
from concurrent.futures import ThreadPoolExecutor
from langgraph.graph import StateGraph, END

from services.llm_service import create_llm_service, LLMService, ProviderType
from prompts.templates import (
    PROMPT_TEMPLATES,
    get_use_case_context,
    get_tone_modifier,
    get_strictness_behavior
)


class DiagnoseInput(TypedDict):
    """Input state for the diagnosis workflow."""
    strictness: str
    response_length: str
    tone: str
    use_case: str
    additional_notes: Optional[str]


class PromptVariant(TypedDict):
    """A generated prompt variant."""
    style: str
    name: str
    prompt: str
    description: str


class DiagnoseState(TypedDict):
    """State for the diagnosis workflow."""
    # Input
    input: DiagnoseInput

    # Intermediate
    use_case_context: dict
    tone_modifier: dict
    strictness_behavior: dict

    # Output
    variants: Annotated[list[PromptVariant], add]
    recommended_style: str
    error: Optional[str]


class DiagnoserWorkflow:
    """LangGraph workflow for generating customized system prompts."""

    def __init__(self, api_key: str, provider: ProviderType = "groq"):
        """
        Initialize the workflow with the provided API key.

        Args:
            api_key: API key (Groq or Gemini depending on provider)
            provider: LLM provider to use ("groq" or "gemini")
        """
        self.api_key = api_key
        self.provider = provider
        self.llm_service = create_llm_service(api_key, provider=provider)
        self._use_llm = True  # Track if LLM was used

    def _generate_prompt_variant(
        self,
        input_data: DiagnoseInput,
        style: str
    ) -> PromptVariant:
        """Generate a prompt variant using the LLM."""
        template = PROMPT_TEMPLATES[style]

        try:
            prompt = self.llm_service.generate_system_prompt(
                strictness=input_data["strictness"],
                response_length=input_data["response_length"],
                tone=input_data["tone"],
                use_case=input_data["use_case"],
                style=style,
                additional_notes=input_data.get("additional_notes")
            )
        except Exception as e:
            # Fallback to a basic prompt on error
            import logging
            logging.getLogger(__name__).error(f"LLM call failed for style '{style}': {type(e).__name__}: {str(e)[:100]}")
            self._use_llm = False
            prompt = self._generate_fallback_prompt(input_data, style)

        return PromptVariant(
            style=style,
            name=template["name_ja"],
            prompt=prompt,
            description=template["description_ja"]
        )

    def _generate_fallback_prompt(
        self,
        input_data: DiagnoseInput,
        style: str
    ) -> str:
        """Generate a fallback prompt when LLM is unavailable."""
        use_case_context = get_use_case_context(input_data["use_case"])
        tone_modifier = get_tone_modifier(input_data["tone"])
        strictness_behavior = get_strictness_behavior(input_data["strictness"])

        context = use_case_context["context"]
        tone_desc = tone_modifier["description"]
        behavior = strictness_behavior["description"]

        if style == "short":
            return f"You are a {behavior} AI assistant for {context}. Be {tone_desc} and direct."

        elif style == "standard":
            guidelines = use_case_context["additional_guidance"]
            tone_guidelines = tone_modifier["guidelines"]

            return f"""You are an AI assistant specialized in {context}.

Communication Style: {tone_desc}

Guidelines:
1. Be {behavior} in your approach.
2. {guidelines[0]}
3. {tone_guidelines[0]}
4. Ask clarifying questions when needed."""

        else:  # strict
            guidelines = use_case_context["additional_guidance"]
            tone_guidelines = tone_modifier["guidelines"]
            strictness_guidelines = strictness_behavior["guidelines"]

            return f"""You are an expert AI assistant designed for {context}.

Core Principles:
1. Maintain a {behavior} approach at all times.
2. Communication style: {tone_desc}.
3. {tone_guidelines[0]}
4. {tone_guidelines[1]}

Domain Guidelines:
5. {guidelines[0]}
6. {guidelines[1]}
7. {guidelines[2]}

Behavioral Rules:
8. {strictness_guidelines[0]}
9. {strictness_guidelines[1]}
10. Do not provide information outside your knowledge domain.
11. Request clarification for ambiguous queries.
12. Structure responses clearly when appropriate."""

    def _determine_recommendation(self, input_data: DiagnoseInput) -> str:
        """Determine which style to recommend based on preferences."""
        if input_data["response_length"] == "short":
            return "short"
        elif input_data["strictness"] == "strict" or input_data["response_length"] == "detailed":
            return "strict"
        else:
            return "standard"

    def run(self, input_data: DiagnoseInput) -> dict:
        """
        Run the diagnosis workflow synchronously.
        Uses ThreadPoolExecutor for parallel LLM calls.
        """
        self._use_llm = True
        styles = ["short", "standard", "strict"]

        # 並列でLLM呼び出しを実行
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(self._generate_prompt_variant, input_data, style)
                for style in styles
            ]
            variants = [f.result() for f in futures]

        recommended_style = self._determine_recommendation(input_data)

        return {
            "recommended_style": recommended_style,
            "variants": variants,
            "source": "llm" if self._use_llm else "mock"
        }

    async def run_async(self, input_data: DiagnoseInput) -> dict:
        """
        Run the diagnosis workflow asynchronously.
        Uses asyncio for parallel LLM calls.
        """
        self._use_llm = True
        styles = ["short", "standard", "strict"]

        loop = asyncio.get_event_loop()

        # 並列でLLM呼び出しを実行（asyncioで同期関数をラップ）
        async def generate_variant_async(style: str) -> PromptVariant:
            return await loop.run_in_executor(
                None,
                self._generate_prompt_variant,
                input_data,
                style
            )

        # 3つのプロンプト生成を並列実行
        variants = await asyncio.gather(
            *[generate_variant_async(style) for style in styles]
        )

        recommended_style = self._determine_recommendation(input_data)

        return {
            "recommended_style": recommended_style,
            "variants": list(variants),
            "source": "llm" if self._use_llm else "mock"
        }


# Module-level function for easy import (synchronous)
def run_diagnosis(
    strictness: str,
    response_length: str,
    tone: str,
    use_case: str,
    api_key: str,
    additional_notes: Optional[str] = None,
    provider: ProviderType = "groq"
) -> dict:
    """
    Run the diagnosis workflow with the given parameters (synchronous).

    Args:
        strictness: User's preferred strictness level
        response_length: Preferred response length
        tone: Communication tone
        use_case: Primary use case
        api_key: API key (Groq or Gemini)
        additional_notes: Optional additional requirements
        provider: LLM provider ("groq" or "gemini")

    Returns:
        A dict with 'recommended_style', 'variants', and 'source' keys.
    """
    workflow = DiagnoserWorkflow(api_key, provider=provider)
    return workflow.run({
        "strictness": strictness,
        "response_length": response_length,
        "tone": tone,
        "use_case": use_case,
        "additional_notes": additional_notes
    })


# Module-level function for easy import (asynchronous)
async def run_diagnosis_async(
    strictness: str,
    response_length: str,
    tone: str,
    use_case: str,
    api_key: str,
    additional_notes: Optional[str] = None,
    provider: ProviderType = "groq"
) -> dict:
    """
    Run the diagnosis workflow with the given parameters (asynchronous).

    This version runs LLM calls in parallel for better performance.

    Args:
        strictness: User's preferred strictness level
        response_length: Preferred response length
        tone: Communication tone
        use_case: Primary use case
        api_key: API key (Groq or Gemini)
        additional_notes: Optional additional requirements
        provider: LLM provider ("groq" or "gemini")

    Returns:
        A dict with 'recommended_style', 'variants', and 'source' keys.
    """
    workflow = DiagnoserWorkflow(api_key, provider=provider)
    return await workflow.run_async({
        "strictness": strictness,
        "response_length": response_length,
        "tone": tone,
        "use_case": use_case,
        "additional_notes": additional_notes
    })
