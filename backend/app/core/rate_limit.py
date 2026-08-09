"""
Token-Bucket Rate Limiter Module.

Task 1.10:
  - Token bucket algorithm enforcing per-principal or per-IP rate limits.
  - Supports Redis client with an in-memory fallback.
  - Returns Retry-After duration on HTTP 429.
"""

from __future__ import annotations

import time

from .errors import RateLimitExceededError


class TokenBucket:
    def __init__(self, capacity: int, refill_rate_per_sec: float) -> None:
        self.capacity = float(capacity)
        self.tokens = float(capacity)
        self.refill_rate = refill_rate_per_sec
        self.last_refill = time.time()

    def consume(self, num_tokens: float = 1.0) -> tuple[bool, int]:
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now

        if self.tokens >= num_tokens:
            self.tokens -= num_tokens
            return True, 0

        needed = num_tokens - self.tokens
        retry_after = int(needed / self.refill_rate) + 1
        return False, retry_after


class InMemoryRateLimiter:
    def __init__(self) -> None:
        self._buckets: dict[str, TokenBucket] = {}

    def check_rate_limit(
        self,
        key: str,
        limit: int = 60,
        window_sec: int = 60,
    ) -> None:
        refill_rate = limit / float(window_sec)
        if key not in self._buckets:
            self._buckets[key] = TokenBucket(capacity=limit, refill_rate_per_sec=refill_rate)

        bucket = self._buckets[key]
        allowed, retry_after = bucket.consume(1.0)
        if not allowed:
            raise RateLimitExceededError(
                message=f"Rate limit of {limit} requests per {window_sec}s exceeded",
                retry_after_sec=retry_after,
            )


_rate_limiter = InMemoryRateLimiter()


def get_rate_limiter() -> InMemoryRateLimiter:
    return _rate_limiter
