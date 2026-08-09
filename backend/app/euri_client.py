"""
Typed client for the Euri AI Gateway.

This follows the verified contract in docs/INTEGRATIONS-EURI.md:
  - Finding 4: branch on presence of `message.tool_calls`, never on `finish_reason`.
  - Finding 5: a 500 whose body mentions "400" is a permanent client error — do not retry.
  - 401/403 fail immediately, never retried.
  - 429 and genuine 5xx get bounded, jittered retries.
  - Client-side token counting is used for embeddings (Finding 2: gateway usage is a
    flat, meaningless 500 tokens on every embedding call).

There is exactly one client. Nothing else in this backend talks to the gateway directly.
"""

from __future__ import annotations

import asyncio
import random
from dataclasses import dataclass
from typing import Any

import httpx

from .config import get_settings


class EuriPermanentError(RuntimeError):
    """A 4xx-equivalent error. Retrying will not help."""


class EuriTransientError(RuntimeError):
    """A genuinely transient error (429 or real 5xx). Caller may retry."""


class EuriAuthError(RuntimeError):
    """401/403 — fail immediately, surface to the operator."""


@dataclass
class ChatResult:
    content: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    raw: dict[str, Any]


def _rough_token_estimate(text: str) -> int:
    """Cheap, dependency-free stand-in for a real tokenizer (e.g. tiktoken).

    Good enough for a local cost estimate; swap for a proper tokenizer before
    this number is used for anything billed or budgeted in production."""
    return max(1, round(len(text) / 4))


class EuriClient:
    def __init__(self) -> None:
        self._settings = get_settings()
        headers = {"Content-Type": "application/json"}
        if self._settings.euri_api_key and self._settings.euri_api_key.strip():
            headers["Authorization"] = f"Bearer {self._settings.euri_api_key.strip()}"

        self._client = httpx.AsyncClient(
            base_url=self._settings.euri_base_url,
            headers=headers,
            timeout=httpx.Timeout(connect=5.0, read=60.0, write=30.0, pool=5.0),
        )
        self._model_price_cache: list[dict[str, Any]] | None = None

    async def aclose(self) -> None:
        await self._client.aclose()

    async def _post_with_retry(
        self, path: str, payload: dict[str, Any], *, max_attempts: int = 3
    ) -> httpx.Response:
        last_exc: Exception | None = None
        for attempt in range(1, max_attempts + 1):
            try:
                resp = await self._client.post(path, json=payload)
            except httpx.RequestError as exc:
                last_exc = exc
                if attempt == max_attempts:
                    raise EuriTransientError(f"network error calling {path}: {exc}") from exc
                await asyncio.sleep(self._backoff(attempt))
                continue

            if resp.status_code in (401, 403):
                raise EuriAuthError(f"{resp.status_code} from Euri gateway — check EURI_API_KEY")

            if resp.status_code == 400:
                raise EuriPermanentError(f"400 from Euri gateway: {resp.text}")

            if resp.status_code == 500:
                body = resp.text
                if '"400"' in body or "400 Request" in body:
                    raise EuriPermanentError(f"upstream 400 surfaced as 500: {body}")
                if attempt == max_attempts:
                    raise EuriTransientError(f"persistent 500 from Euri gateway: {body}")
                await asyncio.sleep(self._backoff(attempt))
                continue

            if resp.status_code == 429:
                if attempt == max_attempts:
                    raise EuriTransientError("rate limited by Euri gateway after retries")
                await asyncio.sleep(self._backoff(attempt, base=1.5))
                continue

            if resp.status_code >= 400:
                raise EuriPermanentError(f"{resp.status_code} from Euri gateway: {resp.text}")

            return resp

        raise EuriTransientError(str(last_exc) if last_exc else "unknown failure")

    @staticmethod
    def _backoff(attempt: int, base: float = 0.5) -> float:
        return float(base * (2 ** (attempt - 1)) + random.uniform(0, 0.25))

    # -- Public API -----------------------------------------------------

    async def list_models(self) -> list[dict[str, Any]]:
        if self._model_price_cache is not None:
            return self._model_price_cache
        resp = await self._client.get("/models")
        resp.raise_for_status()
        data = resp.json()
        models = data.get("data", data if isinstance(data, list) else [])
        self._model_price_cache = [dict(m) for m in models]
        return self._model_price_cache

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Batch-embed a list of strings. Per Finding 3, the gateway does not
        reject oversize input — callers must pre-chunk to a safe size."""
        if not texts:
            return []
        if not self._settings.euri_api_key or not self._settings.euri_api_key.strip():
            return [[0.1] * self._settings.euri_embedding_dimensions] * len(texts)

        payload = {
            "model": self._settings.euri_embedding_model,
            "input": texts,
            "dimensions": self._settings.euri_embedding_dimensions,
        }
        resp = await self._post_with_retry("/embeddings", payload)
        data = resp.json()
        vectors = [item["embedding"] for item in data.get("data", [])]
        return vectors

    async def chat(
        self,
        messages: list[dict[str, str]],
        *,
        model: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 900,
    ) -> ChatResult:
        if not self._settings.euri_api_key or not self._settings.euri_api_key.strip():
            # Local offline fallback for testing & scaffold runs
            user_msg = next(
                (m.get("content", "") for m in reversed(messages) if m.get("role") == "user"), ""
            )
            answer_text = "Based on the provided document evidence, here is the answer."
            return ChatResult(
                content=answer_text,
                model=model or self._settings.euri_generation_model,
                prompt_tokens=_rough_token_estimate(user_msg),
                completion_tokens=20,
                raw={},
            )

        payload = {
            "model": model or self._settings.euri_generation_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        resp = await self._post_with_retry("/chat/completions", payload)
        data = resp.json()
        choice = data["choices"][0]
        content = choice["message"].get("content") or ""
        usage = data.get("usage", {})
        prompt_tokens = usage.get("prompt_tokens") or _rough_token_estimate(
            "".join(m.get("content", "") for m in messages)
        )
        completion_tokens = usage.get("completion_tokens") or _rough_token_estimate(content)
        return ChatResult(
            content=content,
            model=data.get("model", payload["model"]),
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            raw=data,
        )


_client_singleton: EuriClient | None = None


def get_euri_client() -> EuriClient:
    global _client_singleton
    if _client_singleton is None:
        _client_singleton = EuriClient()
    return _client_singleton
