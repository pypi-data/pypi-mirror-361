"""
Content Moderation Filter

This filter uses OpenAI's content moderation API to detect and block inappropriate content.
"""

import logging
from typing import Any, Dict, List, Optional

from ..adapters.openai_adapter import OpenAIAdapter
from ..core.api_key_manager import APIKeyManager
from ..core.config_validator import AI_GUARDRAIL_RULES, ValidationRule
from ..core.conversation import Conversation
from ..core.guardrail_interface import GuardrailInterface, GuardrailResult, GuardrailType

logger = logging.getLogger(__name__)


class ContentModerationGuardrail(GuardrailInterface):
    """Content moderation filter using OpenAI API."""

    def __init__(self, name: str, config: Dict[str, Any]):
        """Initialize the content moderation filter."""
        super().__init__(name, GuardrailType.CONTENT_MODERATION, config)

        # Handle nested config structure from pipeline configuration
        nested_config = config.get("config", {})

        # Configuration
        self.confidence_threshold = nested_config.get(
            "confidence_threshold", config.get("confidence_threshold", 0.7)
        )
        self.block_categories = nested_config.get(
            "block_categories",
            config.get(
                "block_categories", ["hate", "harassment", "self_harm", "sexual", "violence"]
            ),
        )
        self.warn_categories = nested_config.get(
            "warn_categories", config.get("warn_categories", [])
        )
        self.on_error = config.get("on_error", "allow")  # 'allow', 'block', 'warn'

        # API setup
        self.api_key_manager = APIKeyManager()
        self.openai_adapter: Optional[OpenAIAdapter] = None
        self._initialize_adapter()

    def get_validation_rules(self) -> List[ValidationRule]:
        """Get validation rules for content moderation guardrail."""
        return AI_GUARDRAIL_RULES

    def _initialize_adapter(self) -> None:
        """Initialize the OpenAI adapter."""
        try:
            api_key = self.api_key_manager.get_openai_key()
            if api_key:
                self.openai_adapter = OpenAIAdapter(api_key)
                logger.info(f"Initialized OpenAI adapter for {self.name}")
            else:
                logger.warning(f"No OpenAI API key found for {self.name}")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI adapter for {self.name}: {e}")

    async def analyze(
        self, content: str, conversation: Optional["Conversation"] = None
    ) -> GuardrailResult:
        """Analyze content using OpenAI moderation API."""
        if not self.is_enabled():
            return GuardrailResult(
                blocked=False,
                confidence=0.0,
                reason="Filter disabled",
                details={},
                guardrail_name=self.name,
                guardrail_type=self.guardrail_type,
            )

        if not self.is_available():
            return self._handle_unavailable()

        try:
            # Use OpenAI moderation API
            if self.openai_adapter is None:
                return self._handle_error(Exception("OpenAI adapter not initialized"))

            moderation_result = await self.openai_adapter.moderate_content(content)

            # Determine action based on categories and scores
            blocked_categories = []
            warned_categories = []
            max_score = 0.0

            for category, score in moderation_result.category_scores.items():
                score = score if score is not None else 0.0
                if score > max_score:
                    max_score = score

                if category in self.block_categories and score >= self.confidence_threshold:
                    blocked_categories.append(category)
                elif category in self.warn_categories and score >= self.confidence_threshold:
                    warned_categories.append(category)

            # Determine if content should be blocked
            should_block = len(blocked_categories) > 0
            len(warned_categories) > 0 and not should_block

            # Create result
            reason = self._build_reason(blocked_categories, warned_categories, max_score)

            return GuardrailResult(
                blocked=should_block,
                confidence=max_score,
                reason=reason,
                details={
                    "moderation_result": {
                        "flagged": moderation_result.flagged,
                        "categories": moderation_result.categories,
                        "category_scores": moderation_result.category_scores,
                    },
                    "blocked_categories": blocked_categories,
                    "warned_categories": warned_categories,
                    "confidence_threshold": self.confidence_threshold,
                },
                guardrail_name=self.name,
                guardrail_type=self.guardrail_type,
            )

        except Exception as e:
            logger.error(f"Content moderation analysis failed for {self.name}: {e}")
            return self._handle_error(e)

    def _build_reason(
        self, blocked_categories: list, warned_categories: list, max_score: float
    ) -> str:
        """Build a human-readable reason for the moderation decision."""
        if blocked_categories:
            return f"Content blocked due to {', '.join(blocked_categories)} (confidence: {max_score:.2f})"
        elif warned_categories:
            return (
                f"Content flagged for {', '.join(warned_categories)} (confidence: {max_score:.2f})"
            )
        else:
            return "Content passed moderation checks"

    def _handle_unavailable(self) -> GuardrailResult:
        """Handle case when OpenAI API is unavailable."""
        if self.on_error == "block":
            return GuardrailResult(
                blocked=True,
                confidence=0.0,
                reason="Content moderation unavailable - blocking for safety",
                details={"error": "API unavailable"},
                guardrail_name=self.name,
                guardrail_type=self.guardrail_type,
            )
        elif self.on_error == "warn":
            return GuardrailResult(
                blocked=False,
                confidence=0.0,
                reason="Content moderation unavailable - allowing with warning",
                details={"error": "API unavailable"},
                guardrail_name=self.name,
                guardrail_type=self.guardrail_type,
            )
        else:  # 'allow'
            return GuardrailResult(
                blocked=False,
                confidence=0.0,
                reason="Content moderation unavailable - allowing",
                details={"error": "API unavailable"},
                guardrail_name=self.name,
                guardrail_type=self.guardrail_type,
            )

    def _handle_error(self, error: Exception) -> GuardrailResult:
        """Handle errors during analysis."""
        if self.on_error == "block":
            return GuardrailResult(
                blocked=True,
                confidence=0.0,
                reason=f"Content moderation error - blocking for safety: {str(error)}",
                details={"error": str(error)},
                guardrail_name=self.name,
                guardrail_type=self.guardrail_type,
            )
        elif self.on_error == "warn":
            return GuardrailResult(
                blocked=False,
                confidence=0.0,
                reason=f"Content moderation error - allowing with warning: {str(error)}",
                details={"error": str(error)},
                guardrail_name=self.name,
                guardrail_type=self.guardrail_type,
            )
        else:  # 'allow'
            return GuardrailResult(
                blocked=False,
                confidence=0.0,
                reason=f"Content moderation error - allowing: {str(error)}",
                details={"error": str(error)},
                guardrail_name=self.name,
                guardrail_type=self.guardrail_type,
            )

    def is_available(self) -> bool:
        """Check if the content moderation filter is available."""
        return self.openai_adapter is not None and self.api_key_manager.get_openai_key() is not None

    def get_config(self) -> Dict[str, Any]:
        """Get current configuration of this filter."""
        return {
            "name": self.name,
            "type": self.guardrail_type.value,
            "enabled": self.is_enabled(),
            "confidence_threshold": self.confidence_threshold,
            "block_categories": self.block_categories,
            "warn_categories": self.warn_categories,
            "on_error": self.on_error,
            "available": self.is_available(),
        }

    def update_config(self, config: Dict[str, Any]) -> bool:
        """Update configuration of this filter."""
        try:
            if "confidence_threshold" in config:
                self.confidence_threshold = config["confidence_threshold"]

            if "block_categories" in config:
                self.block_categories = config["block_categories"]

            if "warn_categories" in config:
                self.warn_categories = config["warn_categories"]

            if "on_error" in config:
                self.on_error = config["on_error"]

            if "enabled" in config:
                if config["enabled"]:
                    self.enable()
                else:
                    self.disable()

            logger.info(f"Updated configuration for {self.name}")
            return True

        except Exception as e:
            logger.error(f"Failed to update configuration for {self.name}: {e}")
            return False
