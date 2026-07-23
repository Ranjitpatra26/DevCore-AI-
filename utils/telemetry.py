"""
Telemetry & Response Caching Module for DevCore AI Operating System.
Provides lightweight operational metrics (latency, prompt tokens, cache hits) and response caching.
"""

import hashlib
import time
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("ai_software_company.telemetry")

class TelemetryCollector:
    """Lightweight in-memory telemetry metrics tracker."""
    def __init__(self):
        self._metrics = {
            "total_requests": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "failures": 0,
            "total_latency_s": 0.0,
            "total_prompt_chars": 0,
            "total_response_chars": 0
        }

    def record_request(self, latency_s: float, prompt_chars: int, response_chars: int, from_cache: bool = False, failed: bool = False):
        self._metrics["total_requests"] += 1
        if from_cache:
            self._metrics["cache_hits"] += 1
        else:
            self._metrics["cache_misses"] += 1

        if failed:
            self._metrics["failures"] += 1

        self._metrics["total_latency_s"] += latency_s
        self._metrics["total_prompt_chars"] += prompt_chars
        self._metrics["total_response_chars"] += response_chars

    def get_summary(self) -> Dict[str, Any]:
        reqs = self._metrics["total_requests"]
        avg_latency = (self._metrics["total_latency_s"] / reqs) if reqs > 0 else 0.0
        hit_rate = (self._metrics["cache_hits"] / reqs * 100) if reqs > 0 else 0.0
        return {
            "total_requests": reqs,
            "cache_hit_rate_pct": round(hit_rate, 2),
            "failures": self._metrics["failures"],
            "avg_latency_s": round(avg_latency, 3),
            "total_prompt_chars": self._metrics["total_prompt_chars"],
            "total_response_chars": self._metrics["total_response_chars"]
        }

# Global Singleton Telemetry Tracker
telemetry = TelemetryCollector()

class ResponseCache:
    """In-memory LRU response cache for prompt requests."""
    def __init__(self, maxsize: int = 128):
        self.maxsize = maxsize
        self._cache: Dict[str, Dict[str, Any]] = {}

    def _compute_key(self, project_id: str, category: str, mode: str, module: str, prompt_text: str) -> str:
        raw_key = f"{project_id}:{category}:{mode}:{module}:{prompt_text}"
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    def get(self, project_id: str, category: str, mode: str, module: str, prompt_text: str) -> Optional[str]:
        key = self._compute_key(project_id, category, mode, module, prompt_text)
        item = self._cache.get(key)
        if item:
            logger.info(f"Cache HIT for key: {key[:8]}")
            return item.get("response")
        return None

    def set(self, project_id: str, category: str, mode: str, module: str, prompt_text: str, response: str):
        if len(self._cache) >= self.maxsize:
            # Evict oldest entry
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
        
        key = self._compute_key(project_id, category, mode, module, prompt_text)
        self._cache[key] = {
            "response": response,
            "timestamp": time.time()
        }
        logger.info(f"Cached response for key: {key[:8]}")

    def clear(self):
        self._cache.clear()

# Global Singleton Response Cache
response_cache = ResponseCache()
