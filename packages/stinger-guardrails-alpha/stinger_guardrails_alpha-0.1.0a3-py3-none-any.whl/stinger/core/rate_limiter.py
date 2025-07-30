"""
Global Rate Limiting System

This module provides global rate limiting capabilities that build on the existing
conversation rate limiting system. It supports rate limiting per API key, user ID,
or any other identifier across the entire application.
"""

import logging
import threading
import time
from typing import Any, Dict, List, Optional, Union

import yaml

logger = logging.getLogger(__name__)


class RateLimitTracker:
    """Tracks rate limit data for a specific key."""

    def __init__(self, key: str):
        self.key = key
        self.requests: List[float] = []  # Timestamps of requests
        self.lock = threading.Lock()

    def add_request(self, timestamp: Optional[float] = None) -> None:
        """Add a request timestamp."""
        if timestamp is None:
            timestamp = time.time()

        with self.lock:
            self.requests.append(timestamp)

    def check_limit(self, limit: int, window_seconds: int) -> bool:
        """
        Check if the rate limit is exceeded.

        Args:
            limit: Maximum number of requests allowed
            window_seconds: Time window in seconds

        Returns:
            True if limit is exceeded, False otherwise
        """
        now = time.time()
        cutoff = now - window_seconds

        with self.lock:
            # Remove old requests outside the window
            self.requests = [req for req in self.requests if req > cutoff]

            # Check if we're over the limit (strictly greater than)
            return len(self.requests) > limit

    def get_current_count(self, window_seconds: int) -> int:
        """Get current request count within the window."""
        now = time.time()
        cutoff = now - window_seconds

        with self.lock:
            # Remove old requests and return count
            self.requests = [req for req in self.requests if req > cutoff]
            return len(self.requests)

    def get_remaining_requests(self, limit: int, window_seconds: int) -> int:
        """Get remaining requests allowed within the window."""
        current = self.get_current_count(window_seconds)
        return max(0, limit - current)

    def get_reset_time(self, window_seconds: int) -> float:
        """Get the time when the rate limit will reset."""
        if not self.requests:
            return time.time()

        with self.lock:
            oldest_request = min(self.requests)
            return oldest_request + window_seconds

    def cleanup_old_entries(self, max_age_seconds: int) -> None:
        """Remove requests older than max_age_seconds."""
        now = time.time()
        cutoff = now - max_age_seconds

        with self.lock:
            self.requests = [req for req in self.requests if req > cutoff]


class GlobalRateLimiter:
    """
    Global rate limiter for API keys, users, and other identifiers.

    This class provides rate limiting capabilities that work across the entire
    application, building on the existing conversation rate limiting system.
    """

    def __init__(
        self,
        backend: str = "memory",
        cleanup_interval: int = 3600,
        config: Optional[dict] = None,
        config_path: Optional[str] = None,
    ):
        """
        Initialize the global rate limiter.

        Args:
            backend: Rate limiting backend ("memory" for now, future: "redis", "database")
            cleanup_interval: How often to clean up old entries (seconds)
            config: Optional config dict
            config_path: Optional path to YAML config file
        """
        self.backend = backend
        self.cleanup_interval = cleanup_interval
        self.trackers: Dict[str, RateLimitTracker] = {}
        self.lock = threading.Lock()
        self.last_cleanup = time.time()

        # Load config
        if config is not None:
            self.config = config
        elif config_path is not None:
            with open(config_path, "r") as f:
                self.config = yaml.safe_load(f)
        else:
            self.config = {}

        # Default rate limits (can be overridden per key)
        self.default_limits = self.config.get(
            "default_limits",
            {"requests_per_minute": 60, "requests_per_hour": 1000, "requests_per_day": 10000},
        )

        logger.info(f"Initialized global rate limiter with {backend} backend")

    @property
    def max_requests_per_minute(self):
        return self.default_limits.get("requests_per_minute", 60)

    @property
    def max_requests_per_hour(self):
        return self.default_limits.get("requests_per_hour", 1000)

    def _check_limits(self, api_key: str, max_per_minute: int, max_per_hour: int) -> dict:
        """
        Check the actual limits for the given key.
        Returns a dict with 'exceeded', 'remaining', 'limit', 'reason', and 'current'.
        """
        tracker = self._get_tracker(api_key)
        time.time()
        minute_window = 60
        hour_window = 3600
        minute_count = tracker.get_current_count(minute_window)
        hour_count = tracker.get_current_count(hour_window)
        exceeded = False
        reason = ""
        if minute_count >= max_per_minute:
            exceeded = True
            reason = f"Exceeded per-minute limit: {minute_count}/{max_per_minute}"
        elif hour_count >= max_per_hour:
            exceeded = True
            reason = f"Exceeded per-hour limit: {hour_count}/{max_per_hour}"
        return {
            "exceeded": exceeded,
            "current": {"minute": minute_count, "hour": hour_count},
            "remaining": {
                "minute": max(0, max_per_minute - minute_count),
                "hour": max(0, max_per_hour - hour_count),
            },
            "limit": {"minute": max_per_minute, "hour": max_per_hour},
            "reason": reason,
        }

    def check_rate_limit(
        self,
        api_key: str,
        role_or_limits: Optional[Union[str, Dict[str, int]]] = None,
        *,
        role: Optional[str] = None,
    ) -> dict:
        """
        Check if the API key has exceeded the rate limit, considering role-based overrides.
        Args:
            api_key: The API key to check
            role_or_limits: Optional user role for overrides, or custom limits dict
            role: Optional user role for overrides (keyword-only argument)
        Returns:
            dict with 'exceeded' (bool), 'key', 'exceeded_limits', 'remaining', 'limit', 'reason', and 'details'
        """
        # Handle keyword role argument
        if role is not None:
            role_or_limits = role

        # Handle custom limits dict (for backward compatibility)
        if isinstance(role_or_limits, dict):
            # Use custom limits directly
            custom_limits = role_or_limits
            max_per_minute = custom_limits.get("requests_per_minute", self.max_requests_per_minute)
            max_per_hour = custom_limits.get("requests_per_hour", self.max_requests_per_hour)

            # Convert to int, handling None values
            max_per_minute = (
                int(max_per_minute) if max_per_minute is not None else self.max_requests_per_minute
            )
            max_per_hour = (
                int(max_per_hour) if max_per_hour is not None else self.max_requests_per_hour
            )

            # Handle zero limits - should be exceeded immediately
            if max_per_minute == 0 or max_per_hour == 0:
                return {
                    "exceeded": True,
                    "key": api_key,
                    "exceeded_limits": (
                        ["requests_per_minute"] if max_per_minute == 0 else ["requests_per_hour"]
                    ),
                    "remaining": {"minute": 0, "hour": 0},
                    "limit": {"minute": max_per_minute, "hour": max_per_hour},
                    "reason": "Zero rate limit configured",
                    "details": {
                        "requests_per_minute": {
                            "current": 0,
                            "remaining": 0,
                            "limit": max_per_minute,
                        },
                        "requests_per_hour": {"current": 0, "remaining": 0, "limit": max_per_hour},
                        "requests_per_day": {"current": 0, "remaining": 10000, "limit": 10000},
                    },
                }
        else:
            # Handle role-based overrides
            role = role_or_limits
            role_overrides = self.config.get("role_overrides", {})
            role_config = role_overrides.get(role) if role else None

            # If role is exempt, always allow
            if role_config and role_config.get("exempt", False):
                return {
                    "exceeded": False,
                    "key": api_key,
                    "exceeded_limits": [],
                    "remaining": float("inf"),
                    "limit": float("inf"),
                    "reason": f"Role {role} is exempt",
                    "details": {},
                }

            # Use custom limits for the role if specified
            max_per_minute = (
                role_config.get("max_requests_per_minute")
                if role_config
                else self.max_requests_per_minute
            )
            max_per_hour = (
                role_config.get("max_requests_per_hour")
                if role_config
                else self.max_requests_per_hour
            )

        # Check limits
        result = self._check_limits(api_key, max_per_minute, max_per_hour)

        # Build the expected response format
        response = {
            "exceeded": result["exceeded"],
            "key": api_key,
            "exceeded_limits": [],
            "remaining": result["remaining"],
            "limit": result["limit"],
            "reason": result["reason"],
            "details": {
                "requests_per_minute": {
                    "current": result["current"]["minute"],
                    "remaining": result["remaining"]["minute"],
                    "limit": result["limit"]["minute"],
                },
                "requests_per_hour": {
                    "current": result["current"]["hour"],
                    "remaining": result["remaining"]["hour"],
                    "limit": result["limit"]["hour"],
                },
                "requests_per_day": {
                    "current": 0,  # Not implemented yet
                    "remaining": 10000,  # Default
                    "limit": 10000,
                },
            },
        }

        # Add exceeded limits if any
        if result["exceeded"]:
            if result["remaining"]["minute"] == 0:
                response["exceeded_limits"].append("requests_per_minute")
            if result["remaining"]["hour"] == 0:
                response["exceeded_limits"].append("requests_per_hour")

        return response

    def record_request(self, key: str, timestamp: Optional[float] = None) -> None:
        """
        Record a request for rate limiting.

        Args:
            key: The key to record the request for
            timestamp: Optional timestamp (uses current time if None)
        """
        tracker = self._get_tracker(key)
        tracker.add_request(timestamp)

        logger.debug(f"Recorded request for key {key}")

    def get_status(self, key: str, limits: Optional[Dict[str, int]] = None) -> Dict[str, Any]:
        """
        Get current rate limit status for a key without recording a request.

        Args:
            key: The key to check
            limits: Rate limits to check (overrides defaults)

        Returns:
            Dict with current status
        """
        if limits is None:
            limits = self.default_limits

        if not limits:
            return {"key": key, "details": {}}

        tracker = self._get_tracker(key)
        details = {}

        for limit_name, limit_value in limits.items():
            window_seconds = self._get_window_seconds(limit_name)
            if window_seconds is None:
                continue

            details[limit_name] = {
                "limit": limit_value,
                "current": tracker.get_current_count(window_seconds),
                "remaining": tracker.get_remaining_requests(limit_value, window_seconds),
                "reset_time": tracker.get_reset_time(window_seconds),
            }

        return {"key": key, "details": details}

    def reset_limits(self, key: str) -> None:
        """
        Reset rate limits for a key.

        Args:
            key: The key to reset
        """
        with self.lock:
            if key in self.trackers:
                del self.trackers[key]
                logger.info(f"Reset rate limits for key {key}")

    def set_default_limits(self, limits: Dict[str, int]) -> None:
        """
        Set default rate limits.

        Args:
            limits: New default limits
        """
        self.default_limits.update(limits)
        logger.info(f"Updated default rate limits: {limits}")

    def get_all_keys(self) -> List[str]:
        """Get all tracked keys."""
        with self.lock:
            return list(self.trackers.keys())

    def _get_tracker(self, key: str) -> RateLimitTracker:
        """Get or create a tracker for the given key."""
        with self.lock:
            if key not in self.trackers:
                self.trackers[key] = RateLimitTracker(key)
            return self.trackers[key]

    def _get_window_seconds(self, limit_name: str) -> Optional[int]:
        """Get window size in seconds for a limit name."""
        window_mapping = {
            "requests_per_minute": 60,
            "requests_per_hour": 3600,
            "requests_per_day": 86400,
            "requests_per_second": 1,
            "requests_per_week": 604800,
        }
        return window_mapping.get(limit_name)

    def _cleanup_if_needed(self) -> None:
        """Clean up old entries if cleanup interval has passed."""
        now = time.time()
        if now - self.last_cleanup > self.cleanup_interval:
            self._cleanup_old_entries()
            self.last_cleanup = now

    def _cleanup_old_entries(self) -> None:
        """Clean up old entries from all trackers."""
        if not self.default_limits:
            return

        # Use the minimum window from configured limits for cleanup
        window_seconds_list = [
            self._get_window_seconds(limit) for limit in self.default_limits.keys()
        ]
        valid_seconds = [seconds for seconds in window_seconds_list if seconds is not None]

        if not valid_seconds:
            return

        max_age = min(valid_seconds)  # Use minimum window for cleanup

        with self.lock:
            for tracker in self.trackers.values():
                tracker.cleanup_old_entries(max_age)

        logger.debug("Cleaned up old rate limit entries")


# Global instance for easy access
_global_rate_limiter: Optional[GlobalRateLimiter] = None


def get_global_rate_limiter() -> GlobalRateLimiter:
    """Get the global rate limiter instance."""
    global _global_rate_limiter
    if _global_rate_limiter is None:
        _global_rate_limiter = GlobalRateLimiter()
    return _global_rate_limiter


def set_global_rate_limiter(limiter: GlobalRateLimiter) -> None:
    """Set the global rate limiter instance."""
    global _global_rate_limiter
    _global_rate_limiter = limiter
