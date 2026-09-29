"""API-key authentication for paid endpoints."""

import secrets
from typing import Annotated

from fastapi import Header, HTTPException, status

from app.config import Settings

ANONYMOUS_USER = "anonymous"


def require_user(
    x_api_key: Annotated[str | None, Header()] = None,
    x_user_id: Annotated[str | None, Header()] = None,
) -> str:
    expected = Settings().agent_api_key
    if not x_api_key or not secrets.compare_digest(x_api_key, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
    return x_user_id or ANONYMOUS_USER
