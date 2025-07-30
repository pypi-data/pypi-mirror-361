"""
Health Monitoring System

This module provides comprehensive health monitoring capabilities for the Stinger
framework, including system status, filter health, error tracking, and performance metrics.
"""

import logging
import threading
import time
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from .api_key_manager import APIKeyManager
from .pipeline import GuardrailPipeline
from .rate_limiter import get_global_rate_limiter

logger = logging.getLogger(__name__)


@dataclass
class HealthEvent:
    """Represents a health event or error."""

    timestamp: float
    event_type: str  # 'error', 'warning', 'info'
    source: str  # 'filter', 'pipeline', 'api', 'rate_limiter'
    message: str
    details: Optional[Dict[str, Any]] = None


@dataclass
class FilterHealth:
    """Health status of a single filter."""

    name: str
    type: str
    enabled: bool
    available: bool
    last_check: float
    error_count: int = 0
    warning_count: int = 0
    total_checks: int = 0
    avg_response_time_ms: float = 0.0
    config: Optional[Dict[str, Any]] = None


@dataclass
class SystemHealth:
    """Overall system health status."""

    timestamp: float
    overall_status: str  # 'healthy', 'degraded', 'unhealthy'
    pipeline_status: Dict[str, Any]
    api_keys_status: Dict[str, bool]
    rate_limiter_status: Dict[str, Any]
    recent_errors: List[HealthEvent]
    performance_metrics: Dict[str, Any]
    uptime_seconds: float


class HealthMonitor:
    """
    Comprehensive health monitoring for the Stinger framework.

    This class provides monitoring capabilities for:
    - Pipeline and filter health
    - API key status
    - Rate limiter status
    - Error tracking and reporting
    - Performance metrics
    """

    def __init__(
        self,
        pipeline: Optional[GuardrailPipeline] = None,
        api_key_manager: Optional[APIKeyManager] = None,
        max_events: int = 100,
    ):
        """
        Initialize the health monitor.

        Args:
            pipeline: Optional pipeline to monitor
            api_key_manager: Optional API key manager to monitor
            max_events: Maximum number of events to keep in memory
        """
        self.pipeline = pipeline
        self.api_key_manager = api_key_manager or APIKeyManager()
        self.rate_limiter = get_global_rate_limiter()

        # Event tracking
        self.events: deque = deque(maxlen=max_events)
        self.start_time = time.time()
        self.lock = threading.Lock()

        # Performance tracking
        self.performance_metrics = {
            "total_requests": 0,
            "blocked_requests": 0,
            "avg_response_time_ms": 0.0,
            "peak_response_time_ms": 0.0,
            "last_request_time": None,
        }

        logger.info("Health monitor initialized")

    def record_event(
        self, event_type: str, source: str, message: str, details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Record a health event.

        Args:
            event_type: Type of event ('error', 'warning', 'info')
            source: Source of the event
            message: Event message
            details: Optional additional details
        """
        event = HealthEvent(
            timestamp=time.time(),
            event_type=event_type,
            source=source,
            message=message,
            details=details,
        )

        with self.lock:
            self.events.append(event)

        logger.debug(f"Health event recorded: {event_type} from {source}: {message}")

    def get_system_health(self) -> SystemHealth:
        """
        Get comprehensive system health status.

        Returns:
            SystemHealth object with complete status information
        """
        now = time.time()

        # Get pipeline status
        pipeline_status = self._get_pipeline_status()

        # Get API key status
        api_keys_status = self._get_api_keys_status()

        # Get rate limiter status
        rate_limiter_status = self._get_rate_limiter_status()

        # Get recent errors
        recent_errors = self._get_recent_errors()

        # Determine overall status
        overall_status = self._determine_overall_status(
            pipeline_status, api_keys_status, rate_limiter_status, recent_errors
        )

        return SystemHealth(
            timestamp=now,
            overall_status=overall_status,
            pipeline_status=pipeline_status,
            api_keys_status=api_keys_status,
            rate_limiter_status=rate_limiter_status,
            recent_errors=recent_errors,
            performance_metrics=self.performance_metrics.copy(),
            uptime_seconds=now - self.start_time,
        )

    def get_filter_status(self) -> List[FilterHealth]:
        """
        Get detailed status of all filters.

        Returns:
            List of FilterHealth objects for each filter
        """
        if not self.pipeline:
            return []

        guardrails = []

        # Get input guardrails
        for guardrail in self.pipeline.input_pipeline:
            filter_health = self._get_filter_health(guardrail)
            guardrails.append(filter_health)

        # Get output guardrails
        for guardrail in self.pipeline.output_pipeline:
            filter_health = self._get_filter_health(guardrail)
            guardrails.append(filter_health)

        return guardrails

    def get_recent_errors(self, limit: int = 10) -> List[HealthEvent]:
        """
        Get recent errors and events.

        Args:
            limit: Maximum number of events to return

        Returns:
            List of recent health events
        """
        with self.lock:
            # Get events from the end of the deque (most recent first)
            recent_events = list(self.events)[-limit:]
            return recent_events[::-1]  # Reverse to show newest first

    def update_performance_metrics(self, response_time_ms: float, blocked: bool) -> None:
        """
        Update performance metrics.

        Args:
            response_time_ms: Response time in milliseconds
            blocked: Whether the request was blocked
        """
        with self.lock:
            self.performance_metrics["total_requests"] += 1
            if blocked:
                self.performance_metrics["blocked_requests"] += 1

            # Update average response time
            total = self.performance_metrics["total_requests"]
            current_avg = self.performance_metrics["avg_response_time_ms"]
            new_avg = ((current_avg * (total - 1)) + response_time_ms) / total
            self.performance_metrics["avg_response_time_ms"] = new_avg

            # Update peak response time
            if response_time_ms > self.performance_metrics["peak_response_time_ms"]:
                self.performance_metrics["peak_response_time_ms"] = response_time_ms

            self.performance_metrics["last_request_time"] = time.time()

    def _get_pipeline_status(self) -> Dict[str, Any]:
        """Get pipeline status information."""
        if not self.pipeline:
            return {"available": False, "error": "No pipeline configured"}

        try:
            status = self.pipeline.get_guardrail_status()
            # Convert TypedDict to regular dict and add available flag
            status_dict = dict(status)
            status_dict["available"] = True
            return status_dict
        except Exception as e:
            from .error_handling import safe_error_message

            safe_msg = safe_error_message(e, "getting pipeline status")
            self.record_event("error", "pipeline", f"Failed: {safe_msg}")
            return {"available": False, "error": safe_msg}

    def _get_api_keys_status(self) -> Dict[str, bool]:
        """Get API key health status."""
        try:
            return self.api_key_manager.health_check()
        except Exception as e:
            from .error_handling import safe_error_message

            safe_msg = safe_error_message(e, "checking API key health")
            self.record_event("error", "api_keys", f"Failed: {safe_msg}")
            return {}

    def _get_rate_limiter_status(self) -> Dict[str, Any]:
        """Get rate limiter status information."""
        try:
            # Get status for a few sample keys
            all_keys = self.rate_limiter.get_all_keys()
            sample_keys = all_keys[:5]  # Limit to first 5 keys

            key_statuses = {}
            for key in sample_keys:
                key_statuses[key] = self.rate_limiter.get_status(key)

            return {
                "available": True,
                "total_tracked_keys": len(all_keys),
                "sample_key_statuses": key_statuses,
                "default_limits": self.rate_limiter.default_limits,
            }
        except Exception as e:
            from .error_handling import safe_error_message

            safe_msg = safe_error_message(e, "getting rate limiter status")
            self.record_event("error", "rate_limiter", f"Failed: {safe_msg}")
            return {"available": False, "error": safe_msg}

    def _get_filter_health(self, guardrail) -> FilterHealth:
        """Get health status for a single filter."""
        try:
            config = guardrail.get_config()

            # Count errors and warnings from recent events
            error_count = 0
            warning_count = 0
            total_checks = 0

            with self.lock:
                for event in self.events:
                    if (
                        event.source == "filter"
                        and event.details
                        and event.details.get("guardrail_name") == guardrail.name
                    ):
                        if event.event_type == "error":
                            error_count += 1
                        elif event.event_type == "warning":
                            warning_count += 1
                        total_checks += 1

            return FilterHealth(
                name=guardrail.name,
                type=guardrail.guardrail_type.value,
                enabled=guardrail.enabled,
                available=guardrail.is_available(),
                last_check=time.time(),
                error_count=error_count,
                warning_count=warning_count,
                total_checks=total_checks,
                config=config,
            )
        except Exception as e:
            from .error_handling import safe_error_message

            safe_msg = safe_error_message(e, f"getting health for filter {guardrail.name}")
            self.record_event("error", "filter", f"Failed: {safe_msg}")
            return FilterHealth(
                name=guardrail.name,
                type="unknown",
                enabled=False,
                available=False,
                last_check=time.time(),
                error_count=1,
                config=None,
            )

    def _get_recent_errors(self) -> List[HealthEvent]:
        """Get recent error events."""
        with self.lock:
            error_events = [event for event in self.events if event.event_type == "error"]
            return error_events[-10:]  # Last 10 errors

    def _determine_overall_status(
        self,
        pipeline_status: Dict[str, Any],
        api_keys_status: Dict[str, bool],
        rate_limiter_status: Dict[str, Any],
        recent_errors: List[HealthEvent],
    ) -> str:
        """Determine overall system health status."""
        # Check for critical failures
        if not pipeline_status.get("available", False):
            return "unhealthy"

        if not rate_limiter_status.get("available", False):
            return "degraded"

        # Check API key status
        if api_keys_status:
            working_keys = sum(1 for status in api_keys_status.values() if status)
            if working_keys == 0:
                return "unhealthy"
            elif working_keys < len(api_keys_status):
                return "degraded"

        # Check for recent errors
        recent_error_count = len(
            [e for e in recent_errors if e.timestamp > time.time() - 300]
        )  # Last 5 minutes
        if recent_error_count > 5:
            return "degraded"

        return "healthy"

    async def run_health_check(self) -> SystemHealth:
        """
        Run a comprehensive health check asynchronously.

        Returns:
            SystemHealth object with current status
        """
        # This could include async operations like API health checks
        return self.get_system_health()


def print_health_status(health: SystemHealth, detailed: bool = False) -> None:
    """
    Print health status in a formatted way.

    Args:
        health: SystemHealth object to print
        detailed: Whether to print detailed information
    """
    print("\n🏥 STINGER HEALTH STATUS")
    print("=" * 60)

    # Overall status
    status_emoji = {"healthy": "✅", "degraded": "⚠️", "unhealthy": "❌"}
    emoji = status_emoji.get(health.overall_status, "❓")
    print(f"{emoji} Overall Status: {health.overall_status.upper()}")
    print(f"📅 Timestamp: {datetime.fromtimestamp(health.timestamp).strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏱️  Uptime: {timedelta(seconds=int(health.uptime_seconds))}")

    if detailed:
        print("\n📊 PERFORMANCE METRICS")
        print("-" * 30)
        metrics = health.performance_metrics
        print(f"Total Requests: {metrics['total_requests']}")
        print(f"Blocked Requests: {metrics['blocked_requests']}")
        print(
            f"Block Rate: {metrics['blocked_requests']/max(metrics['total_requests'], 1)*100:.1f}%"
        )
        print(f"Avg Response Time: {metrics['avg_response_time_ms']:.1f}ms")
        print(f"Peak Response Time: {metrics['peak_response_time_ms']:.1f}ms")

        print("\n🔧 PIPELINE STATUS")
        print("-" * 30)
        pipeline = health.pipeline_status
        if pipeline.get("available"):
            print(f"✅ Pipeline: Available")
            print(f"   Input Guardrails: {len(pipeline.get('input_guardrails', []))}")
            print(f"   Output Guardrails: {len(pipeline.get('output_guardrails', []))}")
            print(f"   Total Enabled: {pipeline.get('total_enabled', 0)}")
            print(f"   Total Disabled: {pipeline.get('total_disabled', 0)}")
        else:
            print(f"❌ Pipeline: {pipeline.get('error', 'Unknown error')}")

        print("\n🔑 API KEY STATUS")
        print("-" * 30)
        for service, status in health.api_keys_status.items():
            status_icon = "✅" if status else "❌"
            print(f"{status_icon} {service}: {'Available' if status else 'Unavailable'}")

        print("\n⚡ RATE LIMITER STATUS")
        print("-" * 30)
        rate_limiter = health.rate_limiter_status
        if rate_limiter.get("available"):
            print(f"✅ Rate Limiter: Available")
            print(f"   Tracked Keys: {rate_limiter.get('total_tracked_keys', 0)}")
        else:
            print(f"❌ Rate Limiter: {rate_limiter.get('error', 'Unknown error')}")

        if health.recent_errors:
            print("\n🚨 RECENT ERRORS")
            print("-" * 30)
            for error in health.recent_errors[-5:]:  # Show last 5 errors
                error_time = datetime.fromtimestamp(error.timestamp).strftime("%H:%M:%S")
                print(f"[{error_time}] {error.source}: {error.message}")

    print("\n" + "=" * 60)
