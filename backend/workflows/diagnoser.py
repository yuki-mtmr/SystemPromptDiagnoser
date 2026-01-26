"""
LangGraph workflow for system prompt diagnosis and generation.

This workflow processes user preferences and generates three variants of
system prompts (Short, Standard, Strict) using Gemini LLM.
"""

from typing import TypedDict, Optional, Annotated
from operator import add
from langgraph.graph import StateGraph, END

from services.llm_service import create_llm_service, LLMService
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

    def __init__(self, api_key: str):
        """
        Initialize the workflow with the provided API key.

        Args:
            api_key: Google Gemini API key (passed per-request)
        """
        self.llm_service = create_llm_service(api_key)
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        workflow = StateGraph(DiagnoseState)

        # Add nodes
        workflow.add_node("analyze_preferences", self._analyze_preferences)
        workflow.add_node("generate_short", self._generate_short_prompt)
        workflow.add_node("generate_standard", self._generate_standard_prompt)
        workflow.add_node("generate_strict", self._generate_strict_prompt)
        workflow.add_node("determine_recommendation", self._determine_recommendation)

        # Define edges
        workflow.set_entry_point("analyze_preferences")

        # After analysis, generate all three variants in parallel concept
        # (LangGraph will execute sequentially but we structure as parallel)
        workflow.add_edge("analyze_preferences", "generate_short")
        workflow.add_edge("generate_short", "generate_standard")
        workflow.add_edge("generate_standard", "generate_strict")
        workflow.add_edge("generate_strict", "determine_recommendation")
        workflow.add_edge("determine_recommendation", END)

        return workflow.compile()

    def _analyze_preferences(self, state: DiagnoseState) -> dict:
        """Analyze user preferences and enrich with context."""
        input_data = state["input"]

        return {
            "use_case_context": get_use_case_context(input_data["use_case"]),
            "tone_modifier": get_tone_modifier(input_data["tone"]),
            "strictness_behavior": get_strictness_behavior(input_data["strictness"])
        }

    def _generate_prompt_variant(
        self,
        state: DiagnoseState,
        style: str
    ) -> PromptVariant:
        """Generate a prompt variant using the LLM."""
        input_data = state["input"]
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

    def _generate_short_prompt(self, state: DiagnoseState) -> dict:
        """Generate the short variant."""
        variant = self._generate_prompt_variant(state, "short")
        return {"variants": [variant]}

    def _generate_standard_prompt(self, state: DiagnoseState) -> dict:
        """Generate the standard variant."""
        variant = self._generate_prompt_variant(state, "standard")
        return {"variants": [variant]}

    def _generate_strict_prompt(self, state: DiagnoseState) -> dict:
        """Generate the strict variant."""
        variant = self._generate_prompt_variant(state, "strict")
        return {"variants": [variant]}

    def _determine_recommendation(self, state: DiagnoseState) -> dict:
        """Determine which style to recommend based on preferences."""
        input_data = state["input"]

        # Logic to determine recommended style
        if input_data["response_length"] == "short":
            recommended = "short"
        elif input_data["strictness"] == "strict" or input_data["response_length"] == "detailed":
            recommended = "strict"
        else:
            recommended = "standard"

        return {"recommended_style": recommended}

    def run(self, input_data: DiagnoseInput) -> dict:
        """Run the diagnosis workflow."""
        initial_state: DiagnoseState = {
            "input": input_data,
            "use_case_context": {},
            "tone_modifier": {},
            "strictness_behavior": {},
            "variants": [],
            "recommended_style": "standard",
            "error": None
        }

        result = self.graph.invoke(initial_state)
        return {
            "recommended_style": result["recommended_style"],
            "variants": result["variants"]
        }


# Module-level function for easy import
def run_diagnosis(
    strictness: str,
    response_length: str,
    tone: str,
    use_case: str,
    api_key: str,
    additional_notes: Optional[str] = None
) -> dict:
    """
    Run the diagnosis workflow with the given parameters.

    Args:
        strictness: User's preferred strictness level
        response_length: Preferred response length
        tone: Communication tone
        use_case: Primary use case
        api_key: Google Gemini API key (required)
        additional_notes: Optional additional requirements

    Returns:
        A dict with 'recommended_style' and 'variants' keys.
    """
    workflow = DiagnoserWorkflow(api_key)
    return workflow.run({
        "strictness": strictness,
        "response_length": response_length,
        "tone": tone,
        "use_case": use_case,
        "additional_notes": additional_notes
    })
