"""
Universal Guardrail Interface System

This module provides the core interface for all guardrails to ensure pluggability
and consistent behavior across different implementations.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional

from .config_validator import ConfigValidator, ValidationRule
from .input_validation import ValidationError, validate_input_content

if TYPE_CHECKING:
    from .conversation import Conversation


class GuardrailType(Enum):
    """Types of guardrails available in the system."""

    CONTENT_MODERATION = "content_moderation"
    PROMPT_INJECTION = "prompt_injection"
    KEYWORD_BLOCK = "keyword_block"
    KEYWORD_LIST = "keyword_list"
    REGEX_FILTER = "regex_filter"
    LENGTH_FILTER = "length_filter"
    URL_FILTER = "url_filter"
    PASS_THROUGH = "pass_through"
    TOPIC_FILTER = "topic_filter"
    PII_DETECTION = "pii_detection"
    TOXICITY_DETECTION = "toxicity_detection"
    CODE_GENERATION = "code_generation"
    SIMPLE_PII_DETECTION = "simple_pii_detection"
    AI_PII_DETECTION = "ai_pii_detection"
    SIMPLE_TOXICITY_DETECTION = "simple_toxicity_detection"
    AI_TOXICITY_DETECTION = "ai_toxicity_detection"
    SIMPLE_CODE_GENERATION = "simple_code_generation"
    AI_CODE_GENERATION = "ai_code_generation"


@dataclass
class GuardrailResult:
    """Standardized result format for all guardrails."""

    blocked: bool
    confidence: float  # 0.0 to 1.0
    reason: str
    details: Dict[str, Any]
    guardrail_name: str
    guardrail_type: GuardrailType
    risk_level: Optional[str] = None  # "low", "medium", "high", "critical"
    indicators: Optional[List[str]] = None  # Array of evidence strings

    def get_action(self, config: Optional[Dict[str, Any]] = None) -> str:
        """Convert boolean blocked result to action string.

        Args:
            config: Optional configuration dict containing 'action' field

        Returns:
            Action string: 'block', 'warn', 'allow', etc.
        """
        if not self.blocked:
            return "allow"

        # If blocked, use configured action or default to 'block'
        if config and "action" in config:
            return config["action"]

        # Default action for blocked content
        return "block"


class GuardrailInterface(ABC):
    """Universal interface for all guardrails to ensure pluggability."""

    def __init__(self, name: str, guardrail_type: GuardrailType, config: Dict[str, Any]):
        """Initialize guardrail with name, type, and configuration.

        Args:
            name: Name of the guardrail instance
            guardrail_type: Type of guardrail
            config: Configuration dictionary

        Raises:
            ValueError: If configuration validation fails
        """
        # Validate configuration before initialization
        self._validate_config(config)

        # Initialize core attributes
        self.name = name
        self.guardrail_type = guardrail_type
        self.enabled = config.get("enabled", True)

    @abstractmethod
    async def analyze(
        self, content: str, conversation: Optional["Conversation"] = None
    ) -> GuardrailResult:
        """Analyze content and return standardized result.

        Args:
            content: The content to analyze
            conversation: Optional conversation context for multi-turn analysis

        Returns:
            GuardrailResult with analysis details
        """

    async def analyze_safe(self, content: str) -> GuardrailResult:
        """Analyze content with input validation and error handling."""
        try:
            # Validate input content before processing
            validate_input_content(content, "guardrail_input")

            # Proceed with analysis if validation passes
            return await self.analyze(content)

        except ValidationError as e:
            # Handle validation errors
            from .error_handling import safe_error_message

            safe_msg = safe_error_message(e, f"input validation in {self.name}")

            return GuardrailResult(
                blocked=True,  # Always block on validation errors
                confidence=1.0,
                reason=f"Input validation failed: {safe_msg}",
                details={"validation_error": str(e)},
                guardrail_name=self.name,
                guardrail_type=self.guardrail_type,
                risk_level="high",
            )
        except Exception as e:
            # Handle other unexpected errors
            from .error_handling import safe_error_message

            safe_msg = safe_error_message(e, f"guardrail execution in {self.name}")

            return GuardrailResult(
                blocked=True,  # Conservative approach - block on errors
                confidence=0.0,
                reason=f"Guardrail error: {safe_msg}",
                details={"execution_error": str(e)},
                guardrail_name=self.name,
                guardrail_type=self.guardrail_type,
                risk_level="medium",
            )

    def get_name(self) -> str:
        """Return the name/identifier of this guardrail."""
        return self.name

    def get_type(self) -> GuardrailType:
        """Return the type of this guardrail."""
        return self.guardrail_type

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this guardrail is available/healthy."""

    def is_enabled(self) -> bool:
        """Check if this guardrail is enabled."""
        return self.enabled

    def enable(self) -> None:
        """Enable this guardrail."""
        self.enabled = True

    def disable(self) -> None:
        """Disable this guardrail."""
        self.enabled = False

    @abstractmethod
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration of this guardrail."""

    @abstractmethod
    def get_validation_rules(self) -> List[ValidationRule]:
        """Get the validation rules for this guardrail.

        Returns:
            List of ValidationRule objects defining the validation schema
        """

    def get_config_validator(self) -> ConfigValidator:
        """Get the configuration validator for this guardrail.

        Can be overridden by subclasses that need custom validator logic.

        Returns:
            ConfigValidator instance
        """
        return ConfigValidator(self.get_validation_rules())

    def _validate_config(self, config: Dict[str, Any]):
        """Validate the configuration using the centralized validator.

        Args:
            config: Configuration dictionary to validate

        Raises:
            ValueError: If configuration is invalid
        """
        validator = self.get_config_validator()
        validator.validate_with_exception(config)

    @abstractmethod
    def update_config(self, config: Dict[str, Any]) -> bool:
        """Update configuration of this guardrail."""


class GuardrailRegistry:
    """Registry for managing guardrail implementations."""

    def __init__(self):
        """Initialize the guardrail registry."""
        self._guardrails: Dict[str, GuardrailInterface] = {}
        self._factories: Dict[
            GuardrailType, Callable[[str, Dict[str, Any]], Optional[GuardrailInterface]]
        ] = {}

    def register_guardrail(self, guardrail: GuardrailInterface) -> None:
        """Register a guardrail instance."""
        self._guardrails[guardrail.get_name()] = guardrail

    def unregister_guardrail(self, name: str) -> bool:
        """Unregister a guardrail by name."""
        if name in self._guardrails:
            del self._guardrails[name]
            return True
        return False

    def get_guardrail(self, name: str) -> Optional[GuardrailInterface]:
        """Get a guardrail by name."""
        return self._guardrails.get(name)

    def get_all_guardrails(self) -> Dict[str, GuardrailInterface]:
        """Get all registered guardrails."""
        return self._guardrails.copy()

    def get_guardrails_by_type(self, guardrail_type: GuardrailType) -> List[GuardrailInterface]:
        """Get all guardrails of a specific type."""
        return [
            guardrail
            for guardrail in self._guardrails.values()
            if guardrail.get_type() == guardrail_type
        ]

    def register_factory(
        self,
        guardrail_type: GuardrailType,
        factory_func: Callable[[str, Dict[str, Any]], Optional[GuardrailInterface]],
    ) -> None:
        """Register a factory function for creating guardrails of a specific type."""
        self._factories[guardrail_type] = factory_func

    def create_guardrail(
        self, guardrail_type: GuardrailType, name: str, config: Dict[str, Any]
    ) -> Optional[GuardrailInterface]:
        """Create a new guardrail instance using the registered factory."""
        if guardrail_type in self._factories:
            try:
                return self._factories[guardrail_type](name, config)
            except Exception as e:
                logger = logging.getLogger(__name__)
                logger.error(
                    f"Factory failed to create guardrail '{name}' of type '{guardrail_type}': {e}"
                )
                # Re-raise the exception instead of returning None for better error handling
                raise
        return None

    def clear(self) -> None:
        """Clear all registered guardrails and factories."""
        self._guardrails.clear()
        self._factories.clear()


class GuardrailFactory:
    """Factory for creating guardrail instances."""

    def __init__(self, registry: GuardrailRegistry):
        """Initialize the factory with a registry."""
        self.registry = registry

    def create_from_config(self, config: Dict[str, Any]) -> Optional[GuardrailInterface]:
        """Create a guardrail from configuration dictionary."""
        from ..utils.exceptions import ConfigurationError, InvalidGuardrailTypeError

        name = config.get("name")
        guardrail_type_str = config.get("type")

        if not name or not guardrail_type_str:
            raise ConfigurationError(
                "Guardrail configuration must include 'name' and 'type' fields"
            )

        try:
            guardrail_type = GuardrailType(guardrail_type_str)
        except ValueError:
            valid_types = [t.value for t in GuardrailType]
            raise InvalidGuardrailTypeError(guardrail_type_str, valid_types)

        return self.registry.create_guardrail(guardrail_type, name, config)

    def create_multiple_from_configs(
        self, configs: List[Dict[str, Any]]
    ) -> List[GuardrailInterface]:
        """Create multiple guardrails from configuration list."""
        guardrails = []
        for config in configs:
            guardrail = self.create_from_config(config)
            if guardrail:
                guardrails.append(guardrail)
        return guardrails
