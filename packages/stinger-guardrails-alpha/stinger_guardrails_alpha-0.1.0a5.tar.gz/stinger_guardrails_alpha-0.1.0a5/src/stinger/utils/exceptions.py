"""
Exception hierarchy for Stinger guardrails framework.

This module provides specific, actionable exceptions with error codes
and context-rich error messages for better developer experience.
"""

from typing import Any, Dict, List, Optional


class GuardrailsError(Exception):
    """Base exception for guardrails framework."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.error_code = error_code or "GENERAL_ERROR"
        self.context = context or {}
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        """Format error message with code and context."""
        msg = f"[{self.error_code}] {self.message}"
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            msg += f" (Context: {context_str})"
        return msg


class ConfigurationError(GuardrailsError):
    """Raised when configuration is invalid."""

    def __init__(
        self, message: str, config_path: Optional[str] = None, field: Optional[str] = None
    ):
        context = {}
        if config_path:
            context["config_path"] = config_path
        if field:
            context["field"] = field
        super().__init__(message, "CONFIG_ERROR", context)


class GuardrailError(GuardrailsError):
    """Raised when a guardrail encounters an error."""

    def __init__(
        self,
        message: str,
        guardrail_name: Optional[str] = None,
        guardrail_type: Optional[str] = None,
    ):
        context = {}
        if guardrail_name:
            context["guardrail_name"] = guardrail_name
        if guardrail_type:
            context["guardrail_type"] = guardrail_type
        super().__init__(message, "GUARDRAIL_ERROR", context)


class PipelineError(GuardrailsError):
    """Raised when pipeline processing fails."""

    def __init__(
        self, message: str, pipeline_stage: Optional[str] = None, input_data: Optional[str] = None
    ):
        context = {}
        if pipeline_stage:
            context["pipeline_stage"] = pipeline_stage
        if input_data:
            context["input_data"] = (
                input_data[:100] + "..." if len(input_data) > 100 else input_data
            )
        super().__init__(message, "PIPELINE_ERROR", context)


class GuardrailNotFoundError(GuardrailsError):
    """Raised when a requested guardrail is not found."""

    def __init__(self, guardrail_name: str, available_guardrails: Optional[List[str]] = None):
        message = f"Guardrail '{guardrail_name}' not found"
        context = {"guardrail_name": guardrail_name}
        if available_guardrails:
            context["available_guardrails"] = str(available_guardrails)
        super().__init__(message, "GUARDRAIL_NOT_FOUND", context)


class InvalidGuardrailTypeError(GuardrailsError):
    """Raised when an invalid guardrail type is specified."""

    def __init__(self, guardrail_type: str, valid_types: Optional[List[str]] = None):
        message = f"Invalid guardrail type '{guardrail_type}'"
        context = {"guardrail_type": guardrail_type}
        if valid_types:
            context["valid_types"] = str(valid_types)
        super().__init__(message, "INVALID_GUARDRAIL_TYPE", context)


class ConfigurationValidationError(GuardrailsError):
    """Raised when configuration validation fails."""

    def __init__(self, message: str, validation_errors: Optional[List[str]] = None):
        context = {}
        if validation_errors:
            context["validation_errors"] = str(validation_errors)
        super().__init__(message, "CONFIG_VALIDATION_ERROR", context)


class GuardrailInitializationError(GuardrailsError):
    """Raised when a guardrail fails to initialize."""

    def __init__(self, message: str, guardrail_name: str, config: Optional[Dict[str, Any]] = None):
        context = {"guardrail_name": guardrail_name}
        if config:
            context["config"] = str(config)
        super().__init__(message, "GUARDRAIL_INIT_ERROR", context)


class PipelineInitializationError(GuardrailsError):
    """Raised when pipeline fails to initialize."""

    def __init__(
        self, message: str, config_path: Optional[str] = None, guardrail_count: Optional[int] = None
    ):
        context = {}
        if config_path:
            context["config_path"] = config_path
        if guardrail_count is not None:
            context["guardrail_count"] = str(guardrail_count)
        super().__init__(message, "PIPELINE_INIT_ERROR", context)


class InputValidationError(GuardrailsError):
    """Raised when input validation fails."""

    def __init__(
        self, message: str, input_type: Optional[str] = None, input_length: Optional[int] = None
    ):
        context = {}
        if input_type:
            context["input_type"] = input_type
        if input_length is not None:
            context["input_length"] = str(input_length)
        super().__init__(message, "INPUT_VALIDATION_ERROR", context)


# Error code constants for programmatic handling
ERROR_CODES = {
    "GENERAL_ERROR": "General framework error",
    "CONFIG_ERROR": "Configuration error",
    "GUARDRAIL_ERROR": "Guardrail processing error",
    "PIPELINE_ERROR": "Pipeline processing error",
    "GUARDRAIL_NOT_FOUND": "Requested guardrail not found",
    "INVALID_GUARDRAIL_TYPE": "Invalid guardrail type specified",
    "CONFIG_VALIDATION_ERROR": "Configuration validation failed",
    "GUARDRAIL_INIT_ERROR": "Guardrail initialization failed",
    "PIPELINE_INIT_ERROR": "Pipeline initialization failed",
    "INPUT_VALIDATION_ERROR": "Input validation failed",
}
