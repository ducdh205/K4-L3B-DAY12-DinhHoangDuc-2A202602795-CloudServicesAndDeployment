"""FastAPI service with health, readiness, and guarded question endpoints."""

from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, Field

from app.auth import require_user
from app.config import Settings
from app.cost_guard import CostGuard
from app.lifecycle import lifecycle
from app.logging_utils import log_event
from app.rate_limiter import RateLimiter
from app.store import ConversationStore, get_redis_client

ESTIMATED_COST_USD = 0.001


class AskRequest(BaseModel):
    question: str = Field(min_length=1)


@asynccontextmanager
async def app_lifespan(_: FastAPI):
    lifecycle.install()
    yield


app = FastAPI(title="Cloud Agent", lifespan=app_lifespan)


def get_store() -> ConversationStore:
    settings = Settings()
    return ConversationStore(get_redis_client(settings.redis_url))


def get_rate_limiter() -> RateLimiter:
    settings = Settings()
    return RateLimiter(get_redis_client(settings.redis_url), settings.rate_limit_per_minute)


def get_cost_guard() -> CostGuard:
    settings = Settings()
    return CostGuard(get_redis_client(settings.redis_url), settings.monthly_budget_usd)


@app.get("/health")
def health():
    if lifecycle.shutting_down:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
    return {"status": "ok"}


@app.get("/ready")
def ready(store: Annotated[ConversationStore, Depends(get_store)]):
    if lifecycle.shutting_down or not store.ping():
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
    return {"status": "ready"}


@app.post("/ask")
def ask(
    request: AskRequest,
    user_id: Annotated[str, Depends(require_user)],
    store: Annotated[ConversationStore, Depends(get_store)],
    limiter: Annotated[RateLimiter, Depends(get_rate_limiter)],
    guard: Annotated[CostGuard, Depends(get_cost_guard)],
):
    if lifecycle.shutting_down:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)

    limiter.check(user_id)
    guard.check(user_id, ESTIMATED_COST_USD)
    history = store.get_history(user_id)
    answer = f"Mock answer: {request.question}"
    tokens = max(1, len(request.question.split()))
    cost_usd = ESTIMATED_COST_USD
    store.append(user_id, "user", request.question)
    store.append(user_id, "assistant", answer)
    guard.record(user_id, cost_usd)
    log_event("ask_completed", user_id=user_id, cost_usd=cost_usd, tokens=tokens)
    return {
        "answer": answer,
        "user_id": user_id,
        "history_length": len(history),
        "cost_usd": cost_usd,
        "tokens": tokens,
    }
