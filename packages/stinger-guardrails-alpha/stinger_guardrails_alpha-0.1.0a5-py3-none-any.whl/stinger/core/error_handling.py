"""
Production Error Handler

Provides secure error handling for production environments by sanitizing
error messages and preventing information disclosure.
"""

import logging
import os
import re
import uuid
from pathlib import Path
from typing import Any, Dict, Optional


class SecurityError(Exception):
    """Raised when a security constraint is violated."""


class ProductionErrorHandler:
    """Handles error messages securely for production environments."""

    def __init__(self):
        self._is_production = self._detect_production_environment()
        self._error_registry: Dict[str, str] = {}
        self.logger = logging.getLogger(__name__)

    def _detect_production_environment(self) -> bool:
        """
        Detect if we're running in a production environment.

        Returns:
            True if production environment detected, False otherwise
        """
        # Check common production environment variables
        prod_indicators = [
            os.getenv("ENVIRONMENT") in ["production", "prod"],
            os.getenv("ENV") in ["production", "prod"],
            os.getenv("STAGE") in ["production", "prod"],
            os.getenv("DEPLOYMENT_ENV") in ["production", "prod"],
            os.getenv("PYTHON_ENV") in ["production", "prod"],
            # Heroku, AWS, Azure, GCP indicators
            bool(os.getenv("DYNO")),
            bool(os.getenv("AWS_EXECUTION_ENV")),
            bool(os.getenv("WEBSITE_SITE_NAME")),
            bool(os.getenv("GOOGLE_CLOUD_PROJECT")),
            # Docker production indicators
            os.getenv("DOCKER_ENV") == "production",
            # No development indicators present
            not bool(os.getenv("DEBUG")),
            not bool(os.getenv("DEVELOPMENT")),
        ]

        # If any strong production indicators are present, assume production
        strong_indicators = prod_indicators[:9]  # First 9 are explicit production flags
        if any(strong_indicators):
            return True

        # If we're in a containerized environment without dev flags, assume production
        if bool(os.getenv("CONTAINER")) and not any(
            [os.getenv("DEBUG"), os.getenv("DEVELOPMENT"), os.getenv("DEV_MODE")]
        ):
            return True

        # Default to development if unclear
        return False

    def safe_error_message(
        self, error: Exception, context: str = "operation", include_type: bool = False
    ) -> str:
        """
        Generate a safe error message for the current environment.

        Args:
            error: The original exception
            context: Context description for the error
            include_type: Whether to include error type in production

        Returns:
            Safe error message string
        """
        if not self._is_production:
            # Development: show full error details
            return f"{context} failed: {str(error)}"

        # Production: sanitize error message
        error_id = self._generate_error_id()
        safe_message = f"{context} failed"

        if include_type:
            safe_message += f" ({type(error).__name__})"

        safe_message += f" [Error ID: {error_id}]"

        # Log full error details for debugging
        self._log_error_details(error_id, error, context)

        return safe_message

    def sanitize_path(self, path_str: str) -> str:
        """
        Sanitize file paths for safe display in error messages.

        Args:
            path_str: File path string to sanitize

        Returns:
            Sanitized path string
        """
        if not self._is_production:
            return path_str

        # Handle different path separators manually for cross-platform compatibility
        if "\\" in path_str:
            # Windows-style path
            return path_str.split("\\")[-1]
        elif "/" in path_str:
            # Unix-style path
            return path_str.split("/")[-1]
        else:
            # Try using pathlib as fallback
            try:
                path = Path(path_str)
                return path.name
            except Exception:
                # If no separators and pathlib fails, assume it's just a filename
                return path_str

    def sanitize_error_details(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize error details dictionary for safe display.

        Args:
            details: Dictionary containing error details

        Returns:
            Sanitized details dictionary
        """
        if not self._is_production:
            return details

        sanitized = {}

        for key, value in details.items():
            if key in ["error_id", "timestamp", "context"]:
                # Safe keys to include
                sanitized[key] = value
            elif key == "error" and isinstance(value, str):
                # Sanitize error messages
                sanitized[key] = self._sanitize_error_string(value)
            elif "path" in key.lower() and isinstance(value, str):
                # Sanitize path information
                sanitized[key] = self.sanitize_path(value)
            elif key in ["stack_trace", "api_key", "password", "secret", "token"]:
                # Completely redact sensitive keys
                sanitized[key] = "[redacted]"
            elif isinstance(value, str):
                # For other string values, apply basic sanitization
                sanitized[key] = self._sanitize_error_string(value)
            else:
                # For other keys, include generic placeholder
                sanitized[key] = "[redacted]"

        return sanitized

    def _generate_error_id(self) -> str:
        """Generate a unique error ID for tracking."""
        return str(uuid.uuid4())[:8]

    def _sanitize_error_string(self, error_str: str) -> str:
        """
        Sanitize individual error strings.

        Args:
            error_str: Error string to sanitize

        Returns:
            Sanitized error string
        """
        # Remove stack trace information first (before generic path removal)
        error_str = re.sub(r'File "[^"]+", line \d+', r"File [path], line [number]", error_str)

        # Remove remaining file paths
        error_str = re.sub(r"/[^\s]+", "[path]", error_str)
        error_str = re.sub(r"[A-Z]:\\[^\s]+", "[path]", error_str)

        # Remove sensitive patterns
        sensitive_patterns = [
            r'api[_-]?key[s]?["\']?\s*[:=]\s*["\']?[^"\s]+',
            r'password["\']?\s*[:=]\s*["\']?[^"\s]+',
            r'secret["\']?\s*[:=]\s*["\']?[^"\s]+',
            r'token["\']?\s*[:=]\s*["\']?[^"\s]+',
            r"secret\s+\w+",  # "secret data", "secret key", etc.
            r"\w*secret\w*",  # anything with "secret" in it
            r"sk-[a-zA-Z0-9]+",  # OpenAI-style API keys
        ]

        for pattern in sensitive_patterns:
            error_str = re.sub(pattern, "[redacted]", error_str, flags=re.IGNORECASE)

        return error_str

    def _log_error_details(self, error_id: str, error: Exception, context: str):
        """
        Log full error details for debugging while keeping them out of user-facing messages.

        Args:
            error_id: Unique error identifier
            error: Original exception
            context: Error context
        """
        self.logger.error(
            f"Error ID {error_id}: {context} failed with {type(error).__name__}: {str(error)}",
            exc_info=True,
            extra={
                "error_id": error_id,
                "context": context,
                "error_type": type(error).__name__,
                "is_production": self._is_production,
            },
        )

        # Store in registry for later lookup if needed
        self._error_registry[error_id] = str(error)

    def is_production(self) -> bool:
        """Return whether we're in production mode."""
        return self._is_production

    def get_error_by_id(self, error_id: str) -> Optional[str]:
        """
        Get full error details by error ID (for authorized debugging).

        Args:
            error_id: Error ID to lookup

        Returns:
            Full error message if found, None otherwise
        """
        return self._error_registry.get(error_id)


# Global instance for easy access
_error_handler = None


def _get_handler() -> ProductionErrorHandler:
    """Get or create the global error handler instance."""
    global _error_handler
    if _error_handler is None:
        _error_handler = ProductionErrorHandler()
    return _error_handler


def safe_error_message(
    error: Exception, context: str = "operation", include_type: bool = False
) -> str:
    """Convenience function for safe error message generation."""
    return _get_handler().safe_error_message(error, context, include_type)


def sanitize_path(path_str: str) -> str:
    """Convenience function for path sanitization."""
    return _get_handler().sanitize_path(path_str)


def sanitize_error_details(details: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function for error details sanitization."""
    return _get_handler().sanitize_error_details(details)


def is_production() -> bool:
    """Convenience function to check production environment."""
    return _get_handler().is_production()
