"""
CloudWatch & Application Metrics Collector.

Phase 5:
  - Custom metrics: request count, 4xx, 5xx, p50/p95 latency, cache hit ratio, token usage, cost.
  - Agent metrics: iterations/request, tool calls/request, refusal rate by terminal reason.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger("ekba.metrics")


@dataclass
class MetricRecord:
    request_count: int = 0
    error_4xx_count: int = 0
    error_5xx_count: int = 0
    total_latency_ms: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    estimated_cost_usd: float = 0.0
    refusal_count: int = 0
    agent_iterations: int = 0
    agent_tool_calls: int = 0


class MetricsCollector:
    def __init__(self) -> None:
        self._metrics = MetricRecord()
        self._per_route_counts: dict[str, int] = {}

    def record_request(
        self,
        route: str,
        status_code: int,
        latency_ms: float,
        input_tokens: int = 0,
        output_tokens: int = 0,
        cost: float = 0.0,
        cache_hit: bool = False,
        is_refusal: bool = False,
        agent_iterations: int = 1,
        agent_tool_calls: int = 1,
    ) -> None:
        self._metrics.request_count += 1
        self._per_route_counts[route] = self._per_route_counts.get(route, 0) + 1

        if 400 <= status_code < 500:
            self._metrics.error_4xx_count += 1
        elif status_code >= 500:
            self._metrics.error_5xx_count += 1

        self._metrics.total_latency_ms += latency_ms
        self._metrics.input_tokens += input_tokens
        self._metrics.output_tokens += output_tokens
        self._metrics.estimated_cost_usd += cost

        if cache_hit:
            self._metrics.cache_hits += 1
        else:
            self._metrics.cache_misses += 1

        if is_refusal:
            self._metrics.refusal_count += 1

        self._metrics.agent_iterations += agent_iterations
        self._metrics.agent_tool_calls += agent_tool_calls

        logger.info(
            f"[METRIC] route={route} status={status_code} latency_ms={latency_ms:.1f} "
            f"tokens={input_tokens}+{output_tokens} cost=${cost:.6f} cache_hit={cache_hit}"
        )

    def get_summary(self) -> dict[str, float | int]:
        total_reqs = max(1, self._metrics.request_count)
        avg_latency = self._metrics.total_latency_ms / total_reqs
        cache_ratio = self._metrics.cache_hits / float(total_reqs)

        return {
            "total_requests": self._metrics.request_count,
            "error_4xx": self._metrics.error_4xx_count,
            "error_5xx": self._metrics.error_5xx_count,
            "avg_latency_ms": round(avg_latency, 2),
            "cache_hit_ratio": round(cache_ratio, 3),
            "total_input_tokens": self._metrics.input_tokens,
            "total_output_tokens": self._metrics.output_tokens,
            "total_cost_usd": round(self._metrics.estimated_cost_usd, 6),
            "total_refusals": self._metrics.refusal_count,
        }


_metrics_singleton: MetricsCollector | None = None


def get_metrics_collector() -> MetricsCollector:
    global _metrics_singleton
    if _metrics_singleton is None:
        _metrics_singleton = MetricsCollector()
    return _metrics_singleton
