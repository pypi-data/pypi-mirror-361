"""
Input Validation Limits

Provides comprehensive input validation to prevent resource exhaustion attacks
and ensure system stability under high load.
"""

import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Optional psutil import for system monitoring
try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    psutil = None
    PSUTIL_AVAILABLE = False


class ValidationError(Exception):
    """Raised when input validation fails."""


class ResourceExhaustionError(ValidationError):
    """Raised when resource limits would be exceeded."""


@dataclass
class ValidationLimits:
    """Global validation limits for input processing."""

    # Content size limits
    MAX_INPUT_LENGTH: int = 100 * 1024  # 100KB
    MAX_PROMPT_LENGTH: int = 50 * 1024  # 50KB
    MAX_RESPONSE_LENGTH: int = 50 * 1024  # 50KB

    # Conversation limits
    MAX_CONVERSATION_TURNS: int = 50
    MAX_CONVERSATION_MEMORY_MB: int = 100
    MAX_CONVERSATION_AGE_HOURS: int = 24

    # System resource limits
    MAX_MEMORY_USAGE_MB: int = 500
    MAX_CPU_USAGE_PERCENT: float = 80.0
    MAX_CONCURRENT_REQUESTS: int = 100

    # Filter-specific limits
    MAX_FILTER_PROCESSING_TIME_MS: int = 5000  # 5 seconds
    MAX_FILTERS_PER_PIPELINE: int = 20
    MAX_PIPELINE_DEPTH: int = 10

    # File and configuration limits
    MAX_CONFIG_FILE_SIZE_KB: int = 1024  # 1MB
    MAX_KEYWORD_LIST_SIZE: int = 10000
    MAX_REGEX_PATTERNS: int = 100

    # Rate limiting related
    MAX_REQUESTS_PER_MINUTE: int = 1000
    MAX_REQUESTS_PER_HOUR: int = 10000

    def __post_init__(self):
        """Validate that limits are reasonable."""
        if self.MAX_INPUT_LENGTH <= 0:
            raise ValueError("MAX_INPUT_LENGTH must be positive")
        if self.MAX_CONVERSATION_TURNS <= 0:
            raise ValueError("MAX_CONVERSATION_TURNS must be positive")
        if self.MAX_MEMORY_USAGE_MB <= 0:
            raise ValueError("MAX_MEMORY_USAGE_MB must be positive")


class InputValidator:
    """Comprehensive input validation with resource protection."""

    def __init__(self, limits: Optional[ValidationLimits] = None):
        self.limits = limits or ValidationLimits()
        self._request_count = 0
        self._start_time = time.time()
        self._memory_baseline = self._get_memory_usage()

    def validate_input_content(self, content: str, content_type: str = "input") -> None:
        """
        Validate input content size and format.

        Args:
            content: Content to validate
            content_type: Type of content for error messages

        Raises:
            ValidationError: If content violates limits
        """
        if not isinstance(content, str):
            raise ValidationError(f"{content_type} must be a string")

        content_length = len(content.encode("utf-8"))

        if content_type == "prompt" and content_length > self.limits.MAX_PROMPT_LENGTH:
            raise ValidationError(
                f"Prompt too large: {content_length} bytes > {self.limits.MAX_PROMPT_LENGTH} bytes"
            )
        elif content_type == "response" and content_length > self.limits.MAX_RESPONSE_LENGTH:
            raise ValidationError(
                f"Response too large: {content_length} bytes > {self.limits.MAX_RESPONSE_LENGTH} bytes"
            )
        elif content_length > self.limits.MAX_INPUT_LENGTH:
            raise ValidationError(
                f"Input too large: {content_length} bytes > {self.limits.MAX_INPUT_LENGTH} bytes"
            )

        # Check for potentially malicious patterns
        self._validate_content_safety(content, content_type)

    def validate_conversation_limits(self, conversation_data: Dict[str, Any]) -> None:
        """
        Validate conversation against limits.

        Args:
            conversation_data: Conversation data with turns, memory usage, etc.

        Raises:
            ValidationError: If conversation violates limits
        """
        # Check turn count
        turn_count = conversation_data.get("turn_count", 0)
        if turn_count > self.limits.MAX_CONVERSATION_TURNS:
            raise ValidationError(
                f"Too many conversation turns: {turn_count} > {self.limits.MAX_CONVERSATION_TURNS}"
            )

        # Check memory usage
        memory_mb = conversation_data.get("memory_usage_mb", 0)
        if memory_mb > self.limits.MAX_CONVERSATION_MEMORY_MB:
            raise ValidationError(
                f"Conversation memory too large: {memory_mb}MB > {self.limits.MAX_CONVERSATION_MEMORY_MB}MB"
            )

        # Check conversation age
        created_time = conversation_data.get("created_time", time.time())
        age_hours = (time.time() - created_time) / 3600
        if age_hours > self.limits.MAX_CONVERSATION_AGE_HOURS:
            raise ValidationError(
                f"Conversation too old: {age_hours:.1f}h > {self.limits.MAX_CONVERSATION_AGE_HOURS}h"
            )

    def validate_system_resources(self) -> None:
        """
        Validate current system resource usage.

        Raises:
            ResourceExhaustionError: If system resources are exhausted
        """
        # Check memory usage
        current_memory = self._get_memory_usage()
        memory_used_mb = (current_memory - self._memory_baseline) / (1024 * 1024)

        if memory_used_mb > self.limits.MAX_MEMORY_USAGE_MB:
            raise ResourceExhaustionError(
                f"Memory usage too high: {memory_used_mb:.1f}MB > {self.limits.MAX_MEMORY_USAGE_MB}MB"
            )

        # Check CPU usage (if psutil available)
        if PSUTIL_AVAILABLE:
            try:
                cpu_percent = psutil.cpu_percent(interval=0.1)
                if cpu_percent > self.limits.MAX_CPU_USAGE_PERCENT:
                    raise ResourceExhaustionError(
                        f"CPU usage too high: {cpu_percent:.1f}% > {self.limits.MAX_CPU_USAGE_PERCENT}%"
                    )
            except Exception:
                # If psutil fails, skip CPU check
                pass

    def validate_pipeline_configuration(self, pipeline_config: Dict[str, Any]) -> None:
        """
        Validate pipeline configuration limits.

        Args:
            pipeline_config: Pipeline configuration data

        Raises:
            ValidationError: If pipeline configuration violates limits
        """
        # Check number of filters
        guardrails = pipeline_config.get("guardrails", [])
        if len(guardrails) > self.limits.MAX_FILTERS_PER_PIPELINE:
            raise ValidationError(
                f"Too many guardrails: {len(guardrails)} > {self.limits.MAX_FILTERS_PER_PIPELINE}"
            )

        # Check for regex pattern limits
        regex_count = 0
        for guardrail_config in guardrails:
            if guardrail_config.get("type") == "regex":
                patterns = guardrail_config.get("patterns", [])
                regex_count += len(patterns)

        if regex_count > self.limits.MAX_REGEX_PATTERNS:
            raise ValidationError(
                f"Too many regex patterns: {regex_count} > {self.limits.MAX_REGEX_PATTERNS}"
            )

    def validate_file_upload(self, file_path: Union[str, Path], file_type: str = "config") -> None:
        """
        Validate uploaded file size and type.

        Args:
            file_path: Path to file to validate
            file_type: Type of file for error messages

        Raises:
            ValidationError: If file violates limits
        """
        path = Path(file_path)

        if not path.exists():
            raise ValidationError(f"{file_type} file not found: {path}")

        # Check file size
        file_size_kb = path.stat().st_size / 1024
        if file_size_kb > self.limits.MAX_CONFIG_FILE_SIZE_KB:
            raise ValidationError(
                f"{file_type} file too large: {file_size_kb:.1f}KB > {self.limits.MAX_CONFIG_FILE_SIZE_KB}KB"
            )

        # Basic file type validation
        if file_type == "config" and path.suffix not in [".yaml", ".yml", ".json"]:
            raise ValidationError(f"Invalid config file type: {path.suffix}")

    def validate_keyword_list(self, keywords: List[str]) -> None:
        """
        Validate keyword list size and content.

        Args:
            keywords: List of keywords to validate

        Raises:
            ValidationError: If keyword list violates limits
        """
        if len(keywords) > self.limits.MAX_KEYWORD_LIST_SIZE:
            raise ValidationError(
                f"Too many keywords: {len(keywords)} > {self.limits.MAX_KEYWORD_LIST_SIZE}"
            )

        # Check individual keyword lengths
        for i, keyword in enumerate(keywords):
            if len(keyword) > 1000:  # Reasonable individual keyword limit
                raise ValidationError(f"Keyword {i} too long: {len(keyword)} > 1000 characters")

    def validate_request_rate(self) -> None:
        """
        Validate request rate limits.

        Raises:
            ResourceExhaustionError: If rate limits exceeded
        """
        self._request_count += 1
        current_time = time.time()
        elapsed_minutes = (current_time - self._start_time) / 60

        if elapsed_minutes > 0:
            requests_per_minute = self._request_count / elapsed_minutes
            if requests_per_minute > self.limits.MAX_REQUESTS_PER_MINUTE:
                raise ResourceExhaustionError(
                    f"Request rate too high: {requests_per_minute:.1f}/min > {self.limits.MAX_REQUESTS_PER_MINUTE}/min"
                )

    def _validate_content_safety(self, content: str, content_type: str) -> None:
        """
        Check content for potentially malicious patterns.

        Args:
            content: Content to check
            content_type: Type of content

        Raises:
            ValidationError: If malicious patterns detected
        """
        # Check for extremely long lines (potential DoS)
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if len(line) > 10000:  # 10KB per line limit
                raise ValidationError(
                    f"{content_type} line {i} too long: {len(line)} > 10000 characters"
                )

        # Check for excessive repetition (potential memory bomb)
        if self._has_excessive_repetition(content):
            raise ValidationError(f"{content_type} contains excessive repetition")

        # Check for null bytes (potential file inclusion attacks)
        if "\x00" in content:
            raise ValidationError(f"{content_type} contains null bytes")

    def _has_excessive_repetition(self, content: str, threshold: float = 0.8) -> bool:
        """
        Check if content has excessive character repetition.

        Args:
            content: Content to analyze
            threshold: Repetition threshold (0.8 = 80% same character)

        Returns:
            True if excessive repetition detected
        """
        if len(content) < 100:  # Skip check for short content
            return False

        # Count character frequencies
        char_counts = {}
        for char in content:
            char_counts[char] = char_counts.get(char, 0) + 1

        # Check if any character dominates
        max_count = max(char_counts.values())
        repetition_ratio = max_count / len(content)

        return repetition_ratio > threshold

    def _get_memory_usage(self) -> int:
        """Get current process memory usage in bytes."""
        if PSUTIL_AVAILABLE:
            try:
                process = psutil.Process(os.getpid())
                return process.memory_info().rss
            except Exception:
                # Fallback if psutil fails
                return 0
        else:
            # Fallback if psutil unavailable
            return 0

    def reset_counters(self) -> None:
        """Reset rate limiting and resource counters."""
        self._request_count = 0
        self._start_time = time.time()
        self._memory_baseline = self._get_memory_usage()

    def get_current_usage(self) -> Dict[str, Any]:
        """
        Get current resource usage statistics.

        Returns:
            Dictionary with current usage information
        """
        current_time = time.time()
        elapsed_minutes = (current_time - self._start_time) / 60

        usage = {
            "request_count": self._request_count,
            "requests_per_minute": self._request_count / max(elapsed_minutes, 0.1),
            "memory_usage_mb": (self._get_memory_usage() - self._memory_baseline) / (1024 * 1024),
            "uptime_minutes": elapsed_minutes,
        }

        if PSUTIL_AVAILABLE:
            try:
                usage["cpu_percent"] = psutil.cpu_percent(interval=0)
            except Exception:
                usage["cpu_percent"] = 0
        else:
            usage["cpu_percent"] = 0

        return usage


# Global validator instance
_validator = None


def get_validator() -> InputValidator:
    """Get or create the global input validator instance."""
    global _validator
    if _validator is None:
        _validator = InputValidator()
    return _validator


def validate_input_content(content: str, content_type: str = "input") -> None:
    """Convenience function for input content validation."""
    get_validator().validate_input_content(content, content_type)


def validate_conversation_limits(conversation_data: Dict[str, Any]) -> None:
    """Convenience function for conversation validation."""
    get_validator().validate_conversation_limits(conversation_data)


def validate_system_resources() -> None:
    """Convenience function for system resource validation."""
    get_validator().validate_system_resources()


def validate_pipeline_configuration(pipeline_config: Dict[str, Any]) -> None:
    """Convenience function for pipeline configuration validation."""
    get_validator().validate_pipeline_configuration(pipeline_config)


def reset_validation_counters() -> None:
    """Convenience function to reset validation counters."""
    get_validator().reset_counters()
