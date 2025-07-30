"""
Base AI Guardrail (Updated)

This module provides a base class for all AI-powered guardrails, consolidating
common initialization, API interaction, fallback logic, and configuration management.
"""

import json
import logging
from abc import abstractmethod
from typing import Any, Dict, List, Optional, Tuple

from ..core.api_key_manager import get_openai_key
from ..core.config_validator import AI_GUARDRAIL_RULES, ValidationRule
from ..core.conversation import Conversation
from ..core.guardrail_interface import GuardrailInterface, GuardrailResult, GuardrailType
from ..core.model_config import ModelFactory

logger = logging.getLogger(__name__)


class BaseAIGuardrail(GuardrailInterface):
    """Base class for AI-powered guardrails with common functionality."""

    def __init__(
        self,
        name: str,
        guardrail_type: GuardrailType,
        config: Dict[str, Any],
        default_confidence_threshold: float = 0.7,
        default_on_error: str = "allow",
    ):
        """
        Initialize the base AI guardrail.

        Args:
            name: Name of the guardrail instance
            guardrail_type: Type of guardrail (PII, toxicity, etc.)
            config: Configuration dictionary
            default_confidence_threshold: Default confidence threshold for this guardrail type
            default_on_error: Default error handling behavior
        """
        super().__init__(name, guardrail_type, config)

        # Handle nested config structure from pipeline configuration
        nested_config = config.get("config", {})

        # Configuration
        self.confidence_threshold = nested_config.get(
            "confidence_threshold", config.get("confidence_threshold", default_confidence_threshold)
        )
        self.on_error = config.get("on_error", default_on_error)

        # Use centralized API key manager instead of config
        self.api_key = get_openai_key()

        # Use centralized model factory
        self.model_factory = ModelFactory()
        self.model_provider = None

        detection_type = self._get_detection_type()

        if self.api_key:
            try:
                self.model_provider = self.model_factory.create_model_provider(
                    detection_type, self.api_key
                )
                logger.info(f"Initialized AI {detection_type} guardrail with centralized API key")
            except Exception as e:
                logger.error(f"Failed to create model provider for {detection_type}: {e}")
        else:
            logger.warning(f"No OpenAI API key available for AI {detection_type} guardrail")

    def _get_detection_type(self) -> str:
        """Get the detection type string for model factory."""
        type_mapping = {
            GuardrailType.PII_DETECTION: "pii_detection",
            GuardrailType.TOXICITY_DETECTION: "toxicity_detection",
            GuardrailType.CODE_GENERATION: "code_generation",
        }
        return type_mapping.get(self.guardrail_type, "general_detection")

    @abstractmethod
    def get_analysis_prompt(self) -> str:
        """Get the prompt template for AI analysis. Must be implemented by subclasses."""

    @abstractmethod
    def parse_ai_response(self, data: Dict[str, Any]) -> Tuple[bool, list, float]:
        """
        Parse the AI response into detected, categories, and confidence.

        Args:
            data: Parsed JSON response from AI

        Returns:
            Tuple of (detected, categories_list, confidence)
        """

    @abstractmethod
    def get_categories_field_name(self) -> str:
        """Get the name of the categories field for this guardrail type."""

    def get_validation_rules(self) -> List[ValidationRule]:
        """Get validation rules for AI guardrails."""
        return AI_GUARDRAIL_RULES

    async def analyze(
        self, content: str, conversation: Optional["Conversation"] = None
    ) -> GuardrailResult:
        """Analyze content using AI with centralized model configuration."""
        if not self.enabled:
            detection_type = self._get_detection_type().replace("_", " ")
            return GuardrailResult(
                blocked=False,
                confidence=0.0,
                reason=f"AI {detection_type} guardrail disabled",
                details={"method": "ai", "enabled": False},
                guardrail_name=self.name,
                guardrail_type=self.guardrail_type,
            )

        if not self.model_provider:
            detection_type = self._get_detection_type().replace("_", " ")
            return await self._handle_ai_failure(content, "No API key configured")

        try:
            # Use centralized model provider
            prompt = self.get_analysis_prompt()
            response_content = await self.model_provider.generate_response(
                prompt.format(content=content)
            )

            if response_content:
                try:
                    data = json.loads(response_content.strip())

                    # Parse response using subclass implementation
                    detected, categories, confidence = self.parse_ai_response(data)

                    blocked = detected and confidence >= self.confidence_threshold

                    # Build reason message
                    detection_type = self._get_detection_type().replace("_", " ")
                    categories_str = ", ".join(categories) if categories else "none"

                    return GuardrailResult(
                        blocked=blocked,
                        confidence=confidence,
                        reason=(
                            f"{detection_type.replace('_', ' ').title()} detected (AI): {categories_str}"
                            if detected
                            else f"No {detection_type.replace('_', ' ')} detected (AI)"
                        ),
                        details={
                            f"detected_{self.get_categories_field_name()}": categories,
                            "confidence": confidence,
                            "method": "ai",
                            "model": self.model_provider.get_model_name(),
                        },
                        guardrail_name=self.name,
                        guardrail_type=self.guardrail_type,
                    )
                except json.JSONDecodeError as e:
                    logger.warning(f"Invalid JSON response from AI model: {e}")
                    return await self._handle_ai_failure(
                        content, "Invalid JSON response from AI model"
                    )
            else:
                return await self._handle_ai_failure(content, "Empty response from AI model")

        except Exception as e:
            logger.error(f"AI {self._get_detection_type()} error: {e}")
            return await self._handle_ai_failure(content, str(e))

    async def _handle_ai_failure(
        self, content: str, error: str = "AI analysis failed"
    ) -> GuardrailResult:
        """Handle AI failure based on on_error configuration. No automatic fallbacks."""
        detection_type = self._get_detection_type().replace("_", " ")

        if self.on_error == "block":
            # Fail hard - block content when AI fails
            return GuardrailResult(
                blocked=True,
                confidence=0.0,
                reason=f"⚠️ AI {detection_type} unavailable - blocking for safety: {error}",
                details={
                    "error": error,
                    "method": "ai_failed",
                    "on_error": "block",
                    "ai_required": True,
                },
                guardrail_name=self.name,
                guardrail_type=self.guardrail_type,
            )

        elif self.on_error == "warn":
            # Allow but with prominent warning - NO automatic fallback
            logger.warning(f"AI {detection_type} failed: {error}")
            return GuardrailResult(
                blocked=False,
                confidence=0.0,
                reason=f"⚠️ WARNING: AI {detection_type} unavailable - {error}. Consider using non-AI alternative if appropriate.",
                details={
                    "error": error,
                    "method": "ai_failed",
                    "on_error": "warn",
                    "ai_required": True,
                    "alternative_available": f"simple_{self._get_detection_type()}",
                },
                guardrail_name=self.name,
                guardrail_type=self.guardrail_type,
            )

        else:  # on_error == 'allow'
            # Allow content but log the failure
            logger.info(f"AI {detection_type} failed but on_error='allow': {error}")
            return GuardrailResult(
                blocked=False,
                confidence=0.0,
                reason=f"AI {detection_type} unavailable (allowing due to configuration): {error}",
                details={
                    "error": error,
                    "method": "ai_failed",
                    "on_error": "allow",
                    "ai_required": True,
                },
                guardrail_name=self.name,
                guardrail_type=self.guardrail_type,
            )

    def is_available(self) -> bool:
        """Check if this guardrail is available."""
        return self.enabled and self.model_provider is not None

    def get_config(self) -> Dict[str, Any]:
        """Get current configuration of this guardrail."""
        return {
            "enabled": self.enabled,
            "api_key": "***" if self.api_key else None,
            "confidence_threshold": self.confidence_threshold,
            "on_error": self.on_error,
            "model": self.model_provider.get_model_name() if self.model_provider else None,
        }

    def update_config(self, config: Dict[str, Any]) -> bool:
        """Update configuration of this guardrail."""
        try:
            if "enabled" in config:
                self.enabled = config["enabled"]
            if "confidence_threshold" in config:
                self.confidence_threshold = config["confidence_threshold"]
            if "on_error" in config:
                self.on_error = config["on_error"]
            return True
        except Exception as e:
            detection_type = self._get_detection_type().replace("_", " ")
            logger.error(f"Failed to update AI {detection_type} guardrail config: {e}")
            return False
