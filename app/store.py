"""Redis conversation history; no process-local user state."""

import json

import redis

HISTORY_MAX_MESSAGES = 20
HISTORY_TTL_SECONDS = 86_400


def get_redis_client(redis_url: str):
    if redis_url == "fake://":
        import fakeredis

        return fakeredis.FakeRedis(decode_responses=True)
    return redis.Redis.from_url(redis_url, decode_responses=True)


class ConversationStore:
    def __init__(self, client) -> None:
        self.client = client

    @staticmethod
    def _key(user_id: str) -> str:
        return f"history:{user_id}"

    def ping(self) -> bool:
        try:
            return bool(self.client.ping())
        except Exception:
            return False

    def append(self, user_id: str, role: str, content: str) -> None:
        key = self._key(user_id)
        self.client.rpush(
            key, json.dumps({"role": role, "content": content}, ensure_ascii=False)
        )
        self.client.ltrim(key, -HISTORY_MAX_MESSAGES, -1)
        self.client.expire(key, HISTORY_TTL_SECONDS)

    def get_history(self, user_id: str) -> list[dict]:
        return [json.loads(raw) for raw in self.client.lrange(self._key(user_id), 0, -1)]

    def clear(self, user_id: str) -> None:
        self.client.delete(self._key(user_id))
