"""
citation-constellation/app/rate_limiter.py
============================================
Simple in-memory rate limiter for the Gradio UI.
No persistent state — resets on app restart (acceptable for Serve).
"""

import os
import time
from collections import defaultdict


MAX_RUNS_PER_HOUR = int(os.environ.get("RATE_LIMIT_MAX", "10"))
WINDOW_SECONDS = 3600  # 1 hour


class RateLimiter:
    """Per-session rate limiter using sliding window."""

    def __init__(self, max_runs: int = MAX_RUNS_PER_HOUR, window: int = WINDOW_SECONDS):
        self.max_runs = max_runs
        self.window = window
        self._requests: dict[str, list[float]] = defaultdict(list)

    def _clean(self, key: str):
        now = time.time()
        self._requests[key] = [
            t for t in self._requests[key] if now - t < self.window
        ]

    def check(self, session_key: str) -> tuple[bool, str]:
        """Check if a request is allowed. Returns (allowed, message)."""
        self._clean(session_key)
        count = len(self._requests[session_key])
        remaining = self.max_runs - count

        if remaining <= 0:
            oldest = min(self._requests[session_key])
            wait_minutes = int((self.window - (time.time() - oldest)) / 60) + 1
            return False, (
                f"Rate limit reached ({self.max_runs} analyses per hour). "
                f"Please try again in ~{wait_minutes} minute(s)."
            )
        return True, f"{remaining} analysis run(s) remaining this hour."

    def record(self, session_key: str):
        """Record a successful request."""
        self._requests[session_key].append(time.time())

    def remaining(self, session_key: str) -> int:
        self._clean(session_key)
        return max(0, self.max_runs - len(self._requests[session_key]))


# Singleton instance
limiter = RateLimiter()
