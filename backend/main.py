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


async def generate_llm_prompts(
    request: DiagnoseRequest,
    api_key: str,
    provider: str = "groq"
) -> DiagnoseResponse:
    """Generate prompts using the LangGraph workflow with LLM (async, parallel)."""
    from workflows.diagnoser import run_diagnosis_async

    result = await run_diagnosis_async(
        strictness=request.strictness,
        response_length=request.response_length,
        tone=request.tone,
        use_case=request.use_case,
        additional_notes=request.additional_notes,
        api_key=api_key,
        provider=provider
    )

    return DiagnoseResponse(
        recommended_style=result["recommended_style"],
        source=result.get("source", "llm"),
        variants=[
            PromptVariant(**variant)
            for variant in result["variants"]
        ]
    )


def get_api_key_and_provider(request: Request) -> tuple[Optional[str], str]:
    """
    Get API key and provider from request header or environment variable.
    Priority: X-API-Key header > GROQ_API_KEY env > GEMINI_API_KEY env

    Returns:
        Tuple of (api_key, provider) where provider is "groq" or "gemini"

    SECURITY: Never log the API key value.
    """
    # Check header first (assume Groq by default for new keys)
    header_key = request.headers.get("X-API-Key")
    header_provider = request.headers.get("X-Provider", "groq").lower()
    if header_key and len(header_key) > 0:
        return header_key, header_provider

    # Check GROQ_API_KEY (preferred)
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key and len(groq_key) > 0:
        return groq_key, "groq"

    # Fallback to GEMINI_API_KEY for backward compatibility
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key and len(gemini_key) > 0:
        return gemini_key, "gemini"

    return None, "groq"


def is_llm_available_with_key(api_key: Optional[str]) -> bool:
    """Check if LLM service is available with the given API key."""
    return api_key is not None and len(api_key) > 0


@app.get("/health")
async def health_check():
    groq_key = os.getenv("GROQ_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")
    env_key_available = bool(groq_key) or bool(gemini_key)
    provider = "groq" if groq_key else ("gemini" if gemini_key else None)
    return {
        "status": "ok",
        "service": "system-prompt-diagnoser-backend",
        "env_llm_available": env_key_available,
        "provider": provider
    }


@app.get("/")
async def root():
    return {"message": "System Prompt Diagnoser API is running"}


@app.post("/api/diagnose", response_model=DiagnoseResponse)
async def diagnose(request: Request, data: DiagnoseRequest):
    """
    Diagnose user preferences and generate customized system prompts.

    Uses LangGraph workflow with LLM when API key is provided
    (via X-API-Key header, GROQ_API_KEY or GEMINI_API_KEY env var),
    otherwise falls back to mock generation.
    """
    api_key, provider = get_api_key_and_provider(request)

    try:
        if is_llm_available_with_key(api_key):
            logger.info(f"Using LLM-based generation with {provider} (parallel execution)")
            return await generate_llm_prompts(data, api_key, provider)
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
    api_key, provider = get_api_key_and_provider(request)
    has_key = is_llm_available_with_key(api_key)

    return {
        "llm_available": has_key,
        "generation_mode": "llm" if has_key else "mock",
        "provider": provider if has_key else None
    }


# =============================================================================
# v2 API エンドポイント（動的診断フロー）
# =============================================================================

from schemas.diagnose_v2 import (
    DiagnoseV2StartRequest,
    DiagnoseV2StartResponse,
    DiagnoseV2ContinueRequest,
    DiagnoseV2ContinueResponse,
    DiagnoseV2Result,
    Question,
    QuestionChoice,
    UserProfile,
    CognitiveProfile,
    PromptVariant as PromptVariantV2,
)
from services.session_service import (
    get_session_service,
    SessionNotFoundError,
    SessionExpiredError,
)
from services.llm_service_v2 import create_llm_service_v2, LLMTimeoutError


@app.post("/api/v2/diagnose/start", response_model=DiagnoseV2StartResponse)
async def diagnose_v2_start(request: Request, data: DiagnoseV2StartRequest):
    """
    v2診断を開始する。

    初期回答を受け取り、セッションを作成し、動的質問を生成する。
    LLMが利用可能な場合はLLMで質問を生成、そうでなければモックを使用。
    """
    api_key, provider = get_api_key_and_provider(request)
    session_service = get_session_service()

    # セッション作成
    session_id = session_service.create_session()

    # 初期回答をセッションに保存
    session_service.update_session(session_id, {
        "phase": 1,
        "initial_answers": {
            "purpose": data.initial_answers.purpose,
            "autonomy": data.initial_answers.autonomy,
        },
        "followup_answers": [],
        "followup_count": 0,
    })

    try:
        if is_llm_available_with_key(api_key):
            logger.info(f"v2 診断開始: LLM使用 ({provider})")
            llm_service = create_llm_service_v2(api_key, provider=provider)
            result = llm_service.generate_followup_questions(data.initial_answers)
        else:
            logger.info("v2 診断開始: モック使用")
            llm_service = create_llm_service_v2("")
            result = llm_service.generate_followup_questions_mock(data.initial_answers)

        # 言語とフォローアップ質問をセッションに保存
        session_service.update_session(session_id, {
            "detected_language": result.get("detected_language", "en"),
            "analysis_notes": result.get("analysis_notes", ""),
        })

        followup_questions = result.get("followup_questions", [])

        # フォローアップ質問がない場合、最終出力を生成
        if not followup_questions:
            return await _generate_final_result(
                session_id, session_service, api_key, provider
            )

        # フォローアップ質問をQuestion形式に変換
        questions = _convert_to_questions(followup_questions)

        return DiagnoseV2StartResponse(
            session_id=session_id,
            phase="followup",
            followup_questions=questions,
            result=None,
        )

    except Exception as e:
        logger.error(f"v2 診断開始エラー: {type(e).__name__}: {str(e)[:100]}")
        # エラー時はモックでフォールバック
        llm_service = create_llm_service_v2("")
        result = llm_service.generate_followup_questions_mock(data.initial_answers)

        session_service.update_session(session_id, {
            "detected_language": result.get("detected_language", "en"),
        })

        followup_questions = result.get("followup_questions", [])
        if not followup_questions:
            return await _generate_final_result(
                session_id, session_service, api_key, provider
            )

        return DiagnoseV2StartResponse(
            session_id=session_id,
            phase="followup",
            followup_questions=_convert_to_questions(followup_questions),
            result=None,
        )


@app.post("/api/v2/diagnose/continue", response_model=DiagnoseV2ContinueResponse)
async def diagnose_v2_continue(request: Request, data: DiagnoseV2ContinueRequest):
    """
    v2診断を継続する。

    追加の回答を受け取り、さらに質問が必要か判断する。
    必要なければ最終結果を生成して返す。
    """
    api_key, provider = get_api_key_and_provider(request)
    session_service = get_session_service()

    try:
        session = session_service.get_session(data.session_id)
    except SessionNotFoundError:
        raise HTTPException(status_code=404, detail="セッションが見つかりません")
    except SessionExpiredError:
        raise HTTPException(status_code=404, detail="セッションの有効期限が切れています")

    # 回答をセッションに保存
    current_followup_answers = session.data.get("followup_answers", [])
    for answer in data.answers:
        current_followup_answers.append({
            "question_id": answer.question_id,
            "answer": answer.answer,
        })

    followup_count = session.data.get("followup_count", 0) + 1

    session_service.update_session(data.session_id, {
        "followup_answers": current_followup_answers,
        "followup_count": followup_count,
    })

    # 最大2回のフォローアップ後は最終結果を生成
    if followup_count >= 2:
        return await _generate_final_result(
            data.session_id, session_service, api_key, provider
        )

    # LLMで追加質問が必要か判断（今回はシンプルに最終結果へ）
    # 将来的にはLLMで追加質問を生成することも可能
    return await _generate_final_result(
        data.session_id, session_service, api_key, provider
    )


async def _generate_final_result(
    session_id: str,
    session_service,
    api_key: Optional[str],
    provider: str,
) -> DiagnoseV2StartResponse | DiagnoseV2ContinueResponse:
    """最終結果を生成する内部関数"""
    session = session_service.get_session(session_id)
    session_data = session.data

    all_answers = {
        "initial": session_data.get("initial_answers", {}),
        "followup": session_data.get("followup_answers", []),
    }
    detected_language = session_data.get("detected_language", "en")

    try:
        if is_llm_available_with_key(api_key):
            logger.info(f"v2 最終結果生成: LLM使用 ({provider})")
            llm_service = create_llm_service_v2(api_key, provider=provider)
            result = llm_service.generate_final_output(all_answers, detected_language)
            source = "llm"
        else:
            logger.info("v2 最終結果生成: モック使用")
            llm_service = create_llm_service_v2("")
            result = llm_service.generate_final_output_mock(all_answers, detected_language)
            source = "mock"
    except Exception as e:
        logger.error(f"v2 最終結果生成エラー: {type(e).__name__}: {str(e)[:100]}")
        llm_service = create_llm_service_v2("")
        result = llm_service.generate_final_output_mock(all_answers, detected_language)
        source = "mock"

    # セッションを更新
    session_service.update_session(session_id, {"phase": "complete"})

    # 認知プロファイルを構築（存在する場合）
    cognitive_profile = None
    if "cognitive_profile" in result["user_profile"] and result["user_profile"]["cognitive_profile"]:
        cp = result["user_profile"]["cognitive_profile"]
        cognitive_profile = CognitiveProfile(
            thinking_pattern=cp["thinking_pattern"],
            learning_type=cp["learning_type"],
            detail_orientation=cp["detail_orientation"],
            preferred_structure=cp["preferred_structure"],
            use_tables=cp.get("use_tables", False),
            formatting_rules=cp.get("formatting_rules", {}),
            avoid_patterns=cp.get("avoid_patterns", []),
            persona_summary=cp["persona_summary"],
        )

    # 結果を構築
    diagnose_result = DiagnoseV2Result(
        user_profile=UserProfile(
            primary_use_case=result["user_profile"]["primary_use_case"],
            autonomy_preference=result["user_profile"]["autonomy_preference"],
            communication_style=result["user_profile"]["communication_style"],
            key_traits=result["user_profile"]["key_traits"],
            detected_needs=result["user_profile"]["detected_needs"],
            cognitive_profile=cognitive_profile,
        ),
        recommended_style=result["recommended_style"],
        recommendation_reason=result["recommendation_reason"],
        variants=[
            PromptVariantV2(
                style=v["style"],
                name=v["name"],
                prompt=v["prompt"],
                description=v["description"],
            )
            for v in result["variants"]
        ],
        source=source,
    )

    # レスポンスクラスを判断（startから呼ばれたかcontinueから呼ばれたか）
    return DiagnoseV2ContinueResponse(
        session_id=session_id,
        phase="complete",
        followup_questions=None,
        result=diagnose_result,
    )


def _convert_to_questions(followup_questions: list[dict]) -> list[Question]:
    """フォローアップ質問をQuestion形式に変換"""
    questions = []
    for q in followup_questions:
        choices = None
        if q.get("type") == "choice" and q.get("choices"):
            choices = [
                QuestionChoice(
                    value=c.get("value", c.get("label", "")),
                    label=c.get("label", ""),
                    description=c.get("description"),
                )
                for c in q["choices"]
            ]

        questions.append(Question(
            id=q["id"],
            question=q["question"],
            type=q.get("type", "freeform"),
            placeholder=q.get("placeholder"),
            suggestions=q.get("suggestions"),
            choices=choices,
        ))

    return questions
