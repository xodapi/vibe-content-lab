import hashlib
import json
import uuid
from datetime import datetime, timedelta
from typing import Annotated, Any, Literal

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from rag.store import LocalChroma

from .config import settings
from .db import Estimate, Feedback, Generation, SessionLocal, init_db
from .vibe_client import VibeApiError, VibeClient

app = FastAPI(title="Vibe Content Lab", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.lab_public_url, "http://localhost:5173"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


class EstimateInput(BaseModel):
    type: Literal["text", "image", "video", "voice", "music"]
    model: str = Field(min_length=1, max_length=100)
    prompt: str = Field(min_length=3, max_length=20000)
    extra: dict[str, Any] = Field(default_factory=dict)


class FeedbackInput(BaseModel):
    generation_id: str
    score: Literal[-1, 1]
    note: str | None = Field(default=None, max_length=1000)


class SearchInput(BaseModel):
    question: str = Field(min_length=3, max_length=2000)
    limit: int = Field(default=4, ge=1, le=8)


def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


DbSession = Annotated[Session, Depends(db_session)]


def estimate_cost(response: dict[str, Any]) -> float | None:
    for name in ("cost", "estimated_cost", "cost_rub", "total_cost"):
        value = response.get(name)
        if isinstance(value, int | float):
            return float(value)
    return None


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "mode": settings.app_env,
        "vibe_configured": bool(settings.vibe_api_token),
        "openai_configured": bool(settings.openai_api_key),
    }


@app.post("/api/knowledge/search")
def knowledge_search(payload: SearchInput):
    try:
        sources = LocalChroma().search(payload.question, payload.limit)
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    return {"sources": sources}


@app.post("/api/knowledge/answer")
def knowledge_answer(payload: SearchInput):
    try:
        sources = LocalChroma().search(payload.question, payload.limit)
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    if not settings.openai_api_key:
        raise HTTPException(status_code=503, detail="OPENAI_API_KEY is not configured")
    context = "\n\n".join(
        f"[{index + 1}] {item['text']}" for index, item in enumerate(sources)
    )
    answer = OpenAI(api_key=settings.openai_api_key).responses.create(
        model="gpt-4.1-mini",
        input=(
            "Ответь по-русски только на основании публичной документации ниже. "
            "Если источников недостаточно, скажи это. После каждого фактического утверждения "
            "укажи номер источника в квадратных скобках.\n\n"
            f"Вопрос: {payload.question}\n\nИсточники:\n{context}"
        ),
    )
    return {"answer": answer.output_text, "sources": sources}


@app.post("/api/generations/estimate")
async def create_estimate(payload: EstimateInput, db: DbSession):
    request_payload = payload.model_dump(exclude={"extra"}) | payload.extra
    try:
        provider = await VibeClient().estimate(request_payload)
    except VibeApiError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error

    cost = estimate_cost(provider)
    if cost is not None and cost > settings.max_request_budget_rub:
        raise HTTPException(
            status_code=422,
            detail=(
                f"Estimate {cost:.2f} ₽ exceeds Lab limit "
                f"{settings.max_request_budget_rub:.2f} ₽."
            ),
        )

    estimate_id = str(uuid.uuid4())
    record = Estimate(
        id=estimate_id,
        expires_at=datetime.utcnow() + timedelta(seconds=settings.estimate_ttl_seconds),
        payload=request_payload,
        provider_response=provider,
        estimated_cost_rub=cost,
    )
    db.add(record)
    db.commit()
    return {
        "estimate_id": estimate_id,
        "expires_at": record.expires_at,
        "estimated_cost_rub": cost,
        "provider": provider,
        "requires_operator_confirmation": True,
    }


@app.post("/api/generations/{estimate_id}/confirm", status_code=status.HTTP_201_CREATED)
async def confirm_generation(estimate_id: str, db: DbSession):
    estimate = db.get(Estimate, estimate_id)
    if not estimate:
        raise HTTPException(status_code=404, detail="Estimate not found")
    if estimate.status != "awaiting_confirmation":
        raise HTTPException(status_code=409, detail=f"Estimate is {estimate.status}")
    if estimate.expires_at < datetime.utcnow():
        estimate.status = "expired"
        db.commit()
        raise HTTPException(status_code=410, detail="Estimate expired. Request a new estimate.")

    generation_id = str(uuid.uuid4())
    idempotency_key = hashlib.sha256(
        f"{generation_id}:{estimate_id}".encode()
    ).hexdigest()
    try:
        provider = await VibeClient().generate(estimate.payload, idempotency_key)
    except VibeApiError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error

    estimate.status = "submitted"
    record = Generation(
        id=generation_id,
        estimate_id=estimate_id,
        provider_generation_id=str(provider.get("generation_id", "")) or None,
        idempotency_key=idempotency_key,
        status=str(provider.get("status", "submitted")),
        provider_response=provider,
    )
    db.add(record)
    db.commit()
    return {"id": generation_id, "provider": provider}


@app.post("/api/feedback", status_code=status.HTTP_201_CREATED)
def create_feedback(payload: FeedbackInput, db: DbSession):
    if not db.get(Generation, payload.generation_id):
        raise HTTPException(status_code=404, detail="Generation not found")
    db.add(Feedback(**payload.model_dump()))
    db.commit()
    return {"status": "recorded"}


@app.post("/api/webhooks/vibe", status_code=status.HTTP_202_ACCEPTED)
async def vibe_webhook(request: Request, db: DbSession):
    raw = await request.body()
    signature = request.headers.get("X-Vibe-Signature")
    if not VibeClient.verified_webhook(raw, signature):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")
    payload = json.loads(raw)
    provider_id = str(payload.get("generation_id", ""))
    if provider_id:
        generation = (
            db.query(Generation)
            .filter(Generation.provider_generation_id == provider_id)
            .one_or_none()
        )
        if generation:
            generation.status = str(payload.get("status", generation.status))
            generation.provider_response = payload
            db.commit()
    return {"status": "accepted"}
