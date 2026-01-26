from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
import logging

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging - IMPORTANT: Never log API keys
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="System Prompt Diagnoser API")

# Configure CORS
origins = [
    "http://localhost",
    "http://localhost:5173",
    "http://localhost:5174",
    # Vercel production domains
    "https://*.vercel.app",
]

# Also allow all origins in development mode
if os.getenv("ENV", "development") == "development":
    origins.append("*")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (Vercel preview URLs vary)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class DiagnoseRequest(BaseModel):
    strictness: str  # flexible, strict, creative
    response_length: str  # short, standard, detailed
    tone: str  # formal, casual, technical
    use_case: str  # coding, writing, research, general
    additional_notes: Optional[str] = None


class PromptVariant(BaseModel):
    style: str
    name: str
    prompt: str
    description: str


class DiagnoseResponse(BaseModel):
    recommended_style: str
    variants: list[PromptVariant]
    source: str = "mock"  # "mock" or "llm"


def generate_mock_prompts(request: DiagnoseRequest) -> DiagnoseResponse:
    """Generate mock prompts based on user preferences (fallback when LLM unavailable)."""

    base_traits = []

    # Determine base traits from answers
    if request.strictness == "strict":
        base_traits.append("precise and technically accurate")
    elif request.strictness == "creative":
        base_traits.append("creative and exploratory")
    else:
        base_traits.append("balanced and adaptable")

    if request.tone == "formal":
        base_traits.append("professional language")
    elif request.tone == "casual":
        base_traits.append("conversational and friendly")
    else:
        base_traits.append("technical terminology")

    use_case_context = {
        "coding": "software development and programming tasks",
        "writing": "content creation and writing assistance",
        "research": "research and information synthesis",
        "general": "general-purpose assistance"
    }.get(request.use_case, "general assistance")

    # Generate three variants
    short_prompt = f"""You are a {base_traits[0]} AI assistant for {use_case_context}. Be concise and direct."""

    standard_prompt = f"""You are an AI assistant specialized in {use_case_context}.

Guidelines:
1. Be {base_traits[0]} in your responses.
2. Use {base_traits[1] if len(base_traits) > 1 else 'clear language'}.
3. Focus on the user's specific needs.
4. Ask clarifying questions when needed."""

    strict_prompt = f"""You are an expert AI assistant designed for {use_case_context}.

Core Principles:
1. Maintain {base_traits[0]} standards at all times.
2. Communication style: {base_traits[1] if len(base_traits) > 1 else 'clear and structured'}.
3. Never provide information outside your knowledge domain.
4. Always verify understanding before proceeding with complex tasks.
5. Structure responses with clear sections when appropriate.

Behavioral Guidelines:
- Do not apologize unnecessarily or use filler words.
- Provide actionable, specific guidance.
- When uncertain, explicitly state limitations.
- Request clarification for ambiguous queries."""

    # Determine recommended style
    if request.response_length == "short":
        recommended = "short"
    elif request.strictness == "strict" or request.response_length == "detailed":
        recommended = "strict"
    else:
        recommended = "standard"

    return DiagnoseResponse(
        recommended_style=recommended,
        source="mock",
        variants=[
            PromptVariant(
                style="short",
                name="ショート (Short)",
                prompt=short_prompt,
                description="シンプルで要点を押さえたプロンプト。素早いやり取りに最適。"
            ),
            PromptVariant(
                style="standard",
                name="スタンダード (Standard)",
                prompt=standard_prompt,
                description="バランスの取れた汎用的なプロンプト。日常的な使用に推奨。"
            ),
            PromptVariant(
                style="strict",
                name="ストリクト (Strict)",
                prompt=strict_prompt,
                description="詳細な指示を含む厳格なプロンプト。専門的な作業に最適。"
            )
        ]
    )


async def generate_llm_prompts(request: DiagnoseRequest, api_key: str) -> DiagnoseResponse:
    """Generate prompts using the LangGraph workflow with Gemini LLM (async, parallel)."""
    from workflows.diagnoser import run_diagnosis_async

    result = await run_diagnosis_async(
        strictness=request.strictness,
        response_length=request.response_length,
        tone=request.tone,
        use_case=request.use_case,
        additional_notes=request.additional_notes,
        api_key=api_key
    )

    return DiagnoseResponse(
        recommended_style=result["recommended_style"],
        source=result.get("source", "llm"),
        variants=[
            PromptVariant(**variant)
            for variant in result["variants"]
        ]
    )


def get_api_key(request: Request) -> Optional[str]:
    """
    Get API key from request header or environment variable.
    Priority: X-API-Key header > GEMINI_API_KEY env var

    SECURITY: Never log the API key value.
    """
    header_key = request.headers.get("X-API-Key")
    if header_key and len(header_key) > 0:
        return header_key

    env_key = os.getenv("GEMINI_API_KEY")
    if env_key and len(env_key) > 0:
        return env_key

    return None


def is_llm_available_with_key(api_key: Optional[str]) -> bool:
    """Check if LLM service is available with the given API key."""
    return api_key is not None and len(api_key) > 0


@app.get("/health")
async def health_check():
    env_key_available = bool(os.getenv("GEMINI_API_KEY"))
    return {
        "status": "ok",
        "service": "system-prompt-diagnoser-backend",
        "env_llm_available": env_key_available
    }


@app.get("/")
async def root():
    return {"message": "System Prompt Diagnoser API is running"}


@app.post("/api/diagnose", response_model=DiagnoseResponse)
async def diagnose(request: Request, data: DiagnoseRequest):
    """
    Diagnose user preferences and generate customized system prompts.

    Uses LangGraph workflow with Gemini LLM when API key is provided
    (via X-API-Key header or GEMINI_API_KEY env var),
    otherwise falls back to mock generation.
    """
    api_key = get_api_key(request)

    try:
        if is_llm_available_with_key(api_key):
            logger.info("Using LLM-based generation (parallel execution)")
            return await generate_llm_prompts(data, api_key)
        else:
            logger.info("API key not provided, using mock generation")
            return generate_mock_prompts(data)
    except Exception as e:
        # Log error type for debugging (NOT the API key or full message)
        logger.error(f"Error during diagnosis: {type(e).__name__}: {str(e)[:100]}")
        logger.info("Falling back to mock generation")
        return generate_mock_prompts(data)


@app.get("/api/status")
async def api_status(request: Request):
    """Get the current API status and configuration."""
    api_key = get_api_key(request)
    has_key = is_llm_available_with_key(api_key)

    return {
        "llm_available": has_key,
        "generation_mode": "llm" if has_key else "mock"
    }
