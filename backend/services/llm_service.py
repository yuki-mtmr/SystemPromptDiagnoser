from typing import Optional, Literal
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Provider imports
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq


class LLMTimeoutError(Exception):
    """Exception raised when LLM call times out."""
    pass


ProviderType = Literal["groq", "gemini"]


class LLMService:
    """Service for interacting with LLMs via LangChain.

    Supports multiple providers: Groq (default) and Gemini.
    """

    DEFAULT_TIMEOUT = 20  # 20秒
    DEFAULT_PROVIDER: ProviderType = "groq"

    # Model configurations per provider
    MODELS = {
        "groq": "llama-3.3-70b-versatile",
        "gemini": "gemini-2.0-flash",
    }

    def __init__(
        self,
        api_key: str,
        timeout: int = DEFAULT_TIMEOUT,
        provider: ProviderType = DEFAULT_PROVIDER
    ):
        """
        Initialize LLM service with the provided API key.

        Args:
            api_key: API key (Groq or Gemini depending on provider)
            timeout: Timeout in seconds for LLM calls (default: 20)
            provider: LLM provider to use ("groq" or "gemini")
        """
        self.api_key = api_key
        self.timeout = timeout
        self.provider = provider
        self.model_name = self.MODELS.get(provider, self.MODELS["groq"])
        self._llm = None

    @property
    def is_available(self) -> bool:
        """Check if the LLM service is configured and available."""
        return self.api_key is not None and len(self.api_key) > 0

    @property
    def llm(self):
        """Get or create the LLM instance."""
        if self._llm is None:
            if not self.is_available:
                raise ValueError("API key is not configured")

            if self.provider == "groq":
                self._llm = ChatGroq(
                    model=self.model_name,
                    api_key=self.api_key,
                    temperature=0.7,
                    max_tokens=2048
                )
            else:  # gemini
                self._llm = ChatGoogleGenerativeAI(
                    model=self.model_name,
                    google_api_key=self.api_key,
                    temperature=0.7,
                    max_output_tokens=2048
                )
        return self._llm

    def _generate_prompt_internal(
        self,
        strictness: str,
        response_length: str,
        tone: str,
        use_case: str,
        style: str,
        additional_notes: Optional[str] = None
    ) -> str:
        """Internal method to generate prompt (called with timeout wrapper)."""
        style_instructions = {
            "short": "Create a very concise system prompt (2-3 sentences max) that captures the essence of the requirements.",
            "standard": "Create a balanced system prompt with clear guidelines (4-6 bullet points or numbered items).",
            "strict": "Create a comprehensive, detailed system prompt with explicit rules and behavioral guidelines (8-12 points covering all aspects)."
        }

        tone_descriptions = {
            "formal": "professional and business-appropriate",
            "casual": "friendly and conversational",
            "technical": "precise with technical terminology"
        }

        use_case_contexts = {
            "coding": "software development, programming, and technical problem-solving",
            "writing": "content creation, copywriting, and creative writing",
            "research": "information gathering, analysis, and synthesis",
            "general": "general-purpose assistance across various domains"
        }

        strictness_behaviors = {
            "flexible": "adaptable and willing to explore different approaches",
            "strict": "precise, rule-following, and focused on accuracy",
            "creative": "innovative, exploratory, and open to unconventional solutions"
        }

        length_instructions = {
            "short": "Keep responses concise and to the point",
            "standard": "Provide balanced responses with appropriate detail",
            "detailed": "Provide comprehensive, thorough explanations"
        }

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at crafting effective AI system prompts.
Your task is to create a customized system prompt based on user preferences.
Generate ONLY the system prompt text itself, without any explanations or metadata.
Write the prompt in English, as it will be used with AI assistants."""),
            ("human", """Create a system prompt with the following characteristics:

**Style Level**: {style}
{style_instruction}

**User Preferences**:
- Communication Tone: {tone} ({tone_description})
- Primary Use Case: {use_case} ({use_case_context})
- Behavioral Style: {strictness} ({strictness_behavior})
- Response Length Preference: {response_length} ({length_instruction})

{additional_notes_section}

Generate a well-structured system prompt that incorporates all these preferences.
The prompt should be practical, clear, and immediately usable.""")
        ])

        additional_notes_section = ""
        if additional_notes and additional_notes.strip():
            additional_notes_section = f"**Additional User Requirements**:\n{additional_notes}"

        chain = prompt_template | self.llm | StrOutputParser()

        result = chain.invoke({
            "style": style,
            "style_instruction": style_instructions.get(style, style_instructions["standard"]),
            "tone": tone,
            "tone_description": tone_descriptions.get(tone, "clear and professional"),
            "use_case": use_case,
            "use_case_context": use_case_contexts.get(use_case, "general assistance"),
            "strictness": strictness,
            "strictness_behavior": strictness_behaviors.get(strictness, "balanced"),
            "response_length": response_length,
            "length_instruction": length_instructions.get(response_length, "balanced responses"),
            "additional_notes_section": additional_notes_section
        })

        return result.strip()

    def generate_system_prompt(
        self,
        strictness: str,
        response_length: str,
        tone: str,
        use_case: str,
        style: str,
        additional_notes: Optional[str] = None
    ) -> str:
        """
        Generate a customized system prompt based on user preferences.

        Args:
            strictness: User's preferred strictness level (flexible, strict, creative)
            response_length: Preferred response length (short, standard, detailed)
            tone: Communication tone (formal, casual, technical)
            use_case: Primary use case (coding, writing, research, general)
            style: Prompt style to generate (short, standard, strict)
            additional_notes: Optional additional requirements from user

        Returns:
            Generated system prompt string

        Raises:
            LLMTimeoutError: If the LLM call times out
        """
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(
                self._generate_prompt_internal,
                strictness,
                response_length,
                tone,
                use_case,
                style,
                additional_notes
            )

            try:
                return future.result(timeout=self.timeout)
            except FuturesTimeoutError:
                raise LLMTimeoutError(
                    f"LLM呼び出しが{self.timeout}秒でタイムアウトしました。"
                    "サーバーが混雑している可能性があります。"
                )


def create_llm_service(
    api_key: str,
    timeout: int = LLMService.DEFAULT_TIMEOUT,
    provider: ProviderType = LLMService.DEFAULT_PROVIDER
) -> LLMService:
    """
    Create a new LLM service instance with the provided API key.

    This function creates a fresh instance each time to support
    per-request API keys from users.

    Args:
        api_key: API key (Groq or Gemini)
        timeout: Timeout in seconds for LLM calls (default: 20)
        provider: LLM provider ("groq" or "gemini")

    Returns:
        LLMService instance
    """
    return LLMService(api_key, timeout=timeout, provider=provider)
