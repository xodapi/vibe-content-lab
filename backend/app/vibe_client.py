import hashlib
import hmac
import json
from typing import Any

import httpx

from .config import settings


class VibeApiError(RuntimeError):
    pass


class VibeClient:
    """Small, explicit adapter. Browser clients never receive the bearer token."""

    def _headers(self, idempotency_key: str | None = None) -> dict[str, str]:
        if not settings.vibe_api_token:
            raise VibeApiError("VIBE_API_TOKEN is not configured")
        headers = {"Authorization": f"Bearer {settings.vibe_api_token}"}
        if idempotency_key:
            headers["X-Idempotency-Key"] = idempotency_key
        return headers

    async def estimate(self, payload: dict[str, Any]) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{settings.vibe_api_base_url}/generate/estimate",
                headers=self._headers(),
                json={**payload, "strict": True},
            )
        self._raise(response)
        return response.json()

    async def generate(self, payload: dict[str, Any], idempotency_key: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{settings.vibe_api_base_url}/generate",
                headers=self._headers(idempotency_key),
                json={**payload, "strict": True},
            )
        self._raise(response)
        return response.json()

    @staticmethod
    def verified_webhook(raw_body: bytes, signature: str | None) -> bool:
        if not settings.vibe_webhook_secret or not signature:
            return False
        expected = hmac.new(
            settings.vibe_webhook_secret.encode(), raw_body, hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected, signature.removeprefix("sha256="))

    @staticmethod
    def _raise(response: httpx.Response) -> None:
        if response.is_success:
            return
        try:
            detail = response.json()
        except json.JSONDecodeError:
            detail = response.text[:500]
        raise VibeApiError(f"Vibe API returned {response.status_code}: {detail}")
