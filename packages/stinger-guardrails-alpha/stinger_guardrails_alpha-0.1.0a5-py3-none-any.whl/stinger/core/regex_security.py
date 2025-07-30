"""
Regex Security Validator

Prevents Regular Expression Denial of Service (ReDoS) attacks by validating
regex patterns for dangerous constructs and enforcing complexity limits.
"""

import re
import threading
import time
from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass
class RegexSecurityConfig:
    """Configuration for regex security validation."""

    MAX_PATTERN_LENGTH: int = 1000
    MAX_REGEX_COMPLEXITY: int = 200  # Increased to accommodate legitimate complex patterns
    MAX_COMPILE_TIME_MS: int = 100
    MAX_EXECUTION_TIME_MS: int = 50
    DANGEROUS_PATTERNS: List[str] = None

    def __post_init__(self):
        if self.DANGEROUS_PATTERNS is None:
            # Known dangerous regex patterns that can cause ReDoS
            self.DANGEROUS_PATTERNS = [
                r"\(\w\+\)\+",  # (a+)+ - nested quantifiers
                r"\(\w\*\)\*",  # (a*)* - nested quantifiers
                r"\(\.\+\)\+",  # (.+)+ - nested quantifiers with wildcard
                r"\(\.\*\)\*",  # (.*)* - nested quantifiers with wildcard
                r"\w\+\*",  # a+* - conflicting quantifiers
                r"\w\*\+",  # a*+ - conflicting quantifiers
                r"\(\?\:\w\+\)\+\w\+",  # (?:a+)+a+ - nested quantifiers with suffix
                r"\(\w\|\w\)\+\w",  # (a|a)+a - alternation with overlap
                r"\(\w\+\)\?\w\+",  # (a+)?a+ - optional with required
            ]


class SecurityError(Exception):
    """Raised when a security constraint is violated."""


class RegexSecurityValidator:
    """Validates regex patterns for security vulnerabilities."""

    def __init__(self, config: Optional[RegexSecurityConfig] = None):
        self.config = config or RegexSecurityConfig()

    def validate_pattern(self, pattern: str) -> Tuple[bool, str]:
        """
        Validate a regex pattern for security issues.

        Args:
            pattern: The regex pattern to validate

        Returns:
            Tuple of (is_safe, reason_if_unsafe)

        Raises:
            SecurityError: If pattern violates security constraints
        """
        # Check pattern length
        if len(pattern) > self.config.MAX_PATTERN_LENGTH:
            return False, f"Pattern too long: {len(pattern)} > {self.config.MAX_PATTERN_LENGTH}"

        # Check for dangerous patterns
        dangerous_reason = self._check_dangerous_patterns(pattern)
        if dangerous_reason:
            return False, dangerous_reason

        # Check complexity
        complexity = self._calculate_complexity(pattern)
        if complexity > self.config.MAX_REGEX_COMPLEXITY:
            return False, f"Pattern too complex: {complexity} > {self.config.MAX_REGEX_COMPLEXITY}"

        # Check compilation time
        compile_time = self._measure_compile_time(pattern)
        if compile_time > self.config.MAX_COMPILE_TIME_MS:
            return (
                False,
                f"Compilation too slow: {compile_time}ms > {self.config.MAX_COMPILE_TIME_MS}ms",
            )

        return True, "Pattern is safe"

    def safe_compile(self, pattern: str, flags: int = 0) -> re.Pattern:
        """
        Safely compile a regex pattern with security validation.

        Args:
            pattern: The regex pattern to compile
            flags: Regex flags

        Returns:
            Compiled regex pattern

        Raises:
            SecurityError: If pattern is unsafe
        """
        is_safe, reason = self.validate_pattern(pattern)
        if not is_safe:
            raise SecurityError(f"Unsafe regex pattern: {reason}")

        try:
            start_time = time.perf_counter()
            compiled = re.compile(pattern, flags)
            compile_time = (time.perf_counter() - start_time) * 1000

            if compile_time > self.config.MAX_COMPILE_TIME_MS:
                raise SecurityError(f"Regex compilation too slow: {compile_time:.1f}ms")

            return compiled
        except re.error as e:
            raise SecurityError(f"Invalid regex pattern: {e}")

    def safe_search(
        self, compiled_pattern: re.Pattern, text: str, timeout_ms: Optional[int] = None
    ) -> Optional[re.Match]:
        """
        Safely execute a regex search with timeout protection.

        Args:
            compiled_pattern: Pre-compiled regex pattern
            text: Text to search
            timeout_ms: Optional timeout in milliseconds (defaults to config)

        Returns:
            Match object or None

        Raises:
            SecurityError: If execution times out
        """
        timeout = timeout_ms or self.config.MAX_EXECUTION_TIME_MS
        result = [None]
        exception = [None]

        def search_worker():
            try:
                result[0] = compiled_pattern.search(text)
            except Exception as e:
                exception[0] = e

        thread = threading.Thread(target=search_worker)
        thread.daemon = True
        thread.start()
        thread.join(timeout / 1000.0)

        if thread.is_alive():
            # Thread is still running - timeout occurred
            raise SecurityError(f"Regex execution timeout: >{timeout}ms")

        if exception[0]:
            raise SecurityError(f"Regex execution error: {exception[0]}")

        return result[0]

    def _check_dangerous_patterns(self, pattern: str) -> Optional[str]:
        """Check if pattern contains known dangerous constructs."""
        for dangerous in self.config.DANGEROUS_PATTERNS:
            if re.search(dangerous, pattern):
                return f"Contains dangerous pattern: {dangerous}"

        # Additional manual checks for actual nested quantifiers
        if "(" in pattern and "+" in pattern and ")" in pattern:
            # Look for truly dangerous nested quantifiers: (a+)+ or (a*)*
            if re.search(r"\([^)]*[*+][^)]*\)[*+]", pattern):
                return "Dangerous nested quantifiers detected"

        # Check for alternation overlap (a|a)
        if re.search(r"\([^)]*\|[^)]*\)", pattern):
            # Simple check for duplicate alternatives
            if "|a)" in pattern and "(a|" in pattern:
                return "Alternation with overlap detected"

        return None

    def _calculate_complexity(self, pattern: str) -> int:
        """Calculate approximate complexity score for a regex pattern."""
        complexity = 0

        # Basic character count
        complexity += len(pattern)

        # Quantifier penalties
        complexity += pattern.count("+") * 5  # + quantifier
        complexity += pattern.count("*") * 5  # * quantifier
        complexity += pattern.count("?") * 2  # ? quantifier
        complexity += pattern.count("{") * 3  # {n,m} quantifiers

        # Group penalties
        complexity += pattern.count("(") * 3  # Groups
        complexity += pattern.count("(?:") * 2  # Non-capturing groups
        complexity += pattern.count("(?=") * 5  # Lookaheads
        complexity += pattern.count("(?<=") * 5  # Lookbehinds

        # Character class penalties
        complexity += pattern.count("[") * 2  # Character classes
        complexity += pattern.count(".") * 3  # Wildcard

        # Alternation penalties
        complexity += pattern.count("|") * 4  # Alternation

        return complexity

    def _measure_compile_time(self, pattern: str) -> float:
        """Measure regex compilation time in milliseconds."""
        start_time = time.perf_counter()
        try:
            re.compile(pattern)
        except re.error:
            # Pattern is invalid, but we still measured compile time
            pass
        end_time = time.perf_counter()
        return (end_time - start_time) * 1000

    def get_safe_pattern_suggestions(self, unsafe_pattern: str) -> List[str]:
        """Suggest safer alternatives for unsafe patterns."""
        suggestions = []

        # Replace nested quantifiers
        if re.search(r"\(\w\+\)\+", unsafe_pattern):
            suggestions.append("Replace (a+)+ with a+ or use possessive quantifiers")

        if re.search(r"\(\w\*\)\*", unsafe_pattern):
            suggestions.append("Replace (a*)* with a* - redundant quantifiers")

        # Replace overly broad patterns
        if ".+" in unsafe_pattern:
            suggestions.append("Replace .+ with more specific character classes like [a-zA-Z0-9]+")

        if ".*" in unsafe_pattern:
            suggestions.append("Replace .* with more specific patterns or use non-greedy .*?")

        # Suggest anchoring
        if not unsafe_pattern.startswith("^") and not unsafe_pattern.endswith("$"):
            suggestions.append("Consider anchoring with ^ and $ to prevent backtracking")

        return suggestions


# Global validator instance
_default_validator = RegexSecurityValidator()


def validate_regex_pattern(pattern: str) -> Tuple[bool, str]:
    """Convenience function to validate a regex pattern."""
    return _default_validator.validate_pattern(pattern)


def safe_compile_regex(pattern: str, flags: int = 0) -> re.Pattern:
    """Convenience function to safely compile a regex pattern."""
    return _default_validator.safe_compile(pattern, flags)


def safe_regex_search(compiled_pattern: re.Pattern, text: str) -> Optional[re.Match]:
    """Convenience function to safely execute a regex search."""
    return _default_validator.safe_search(compiled_pattern, text)
