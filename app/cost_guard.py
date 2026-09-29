"""Per-user monthly LLM spending guard backed by Redis."""

from datetime import datetime, timezone

from fastapi import HTTPException, status


class CostGuard:
    def __init__(self, client, monthly_budget_usd: float) -> None:
        self.client = client
        self.monthly_budget_usd = monthly_budget_usd

    @staticmethod
    def _key(user_id: str) -> str:
        month = datetime.now(timezone.utc).strftime("%Y-%m")
        return f"cost:{month}:{user_id}"

    def spent(self, user_id: str) -> float:
        value = self.client.get(self._key(user_id))
        return float(value) if value is not None else 0.0

    def check(self, user_id: str, estimated_cost: float) -> None:
        if self.spent(user_id) + estimated_cost > self.monthly_budget_usd:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Monthly budget exceeded",
            )

    def record(self, user_id: str, cost_usd: float) -> None:
        self.client.incrbyfloat(self._key(user_id), cost_usd)
