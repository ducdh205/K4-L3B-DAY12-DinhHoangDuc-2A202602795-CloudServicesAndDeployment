"""Redis-backed sliding-window request limiter."""

import time
import uuid

from fastapi import HTTPException, status


class RateLimiter:
    WINDOW_SECONDS = 60

    def __init__(self, client, limit_per_minute: int) -> None:
        self.client = client
        self.limit_per_minute = limit_per_minute

    @staticmethod
    def _key(user_id: str) -> str:
        return f"rate-limit:{user_id}"

    def check(self, user_id: str, now: float | None = None) -> None:
        timestamp = time.time() if now is None else now
        key = self._key(user_id)
        self.client.zremrangebyscore(key, 0, timestamp - self.WINDOW_SECONDS)
        if self.client.zcard(key) >= self.limit_per_minute:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
            )
        self.client.zadd(key, {f"{timestamp}:{uuid.uuid4().hex}": timestamp})
        self.client.expire(key, self.WINDOW_SECONDS)

    def hit_count(self, user_id: str, now: float | None = None) -> int:
        timestamp = time.time() if now is None else now
        key = self._key(user_id)
        self.client.zremrangebyscore(key, 0, timestamp - self.WINDOW_SECONDS)
        return int(self.client.zcard(key))
