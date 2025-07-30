from typing import List, Optional

from ..core.config_validator import COMMON_GUARDRAIL_RULES, ValidationRule
from ..core.conversation import Conversation
from ..core.guardrail_interface import GuardrailInterface, GuardrailResult, GuardrailType


class PassThroughGuardrail(GuardrailInterface):
    """Pass-through filter that allows all content."""

    def __init__(self, config: dict):
        """Initialize pass-through filter."""
        name = config.get("name", "pass_through")
        super().__init__(name, GuardrailType.PASS_THROUGH, config)

    def get_validation_rules(self) -> List[ValidationRule]:
        """Get validation rules for pass-through guardrail."""
        return COMMON_GUARDRAIL_RULES  # Only needs common rules

    async def analyze(
        self, content: str, conversation: Optional["Conversation"] = None
    ) -> GuardrailResult:
        """Analyze content (pass-through - always allows)."""
        return GuardrailResult(
            blocked=False,
            confidence=0.0,
            reason="pass_through",
            details={},
            guardrail_name=self.name,
            guardrail_type=self.guardrail_type,
            risk_level="low",
        )

    def is_available(self) -> bool:
        """Check if filter is available (always true for pass-through)."""
        return True

    def get_config(self) -> dict:
        """Get current configuration."""
        return {"name": self.name, "type": self.guardrail_type.value, "enabled": self.enabled}

    def update_config(self, config: dict) -> bool:
        """Update configuration (minimal for pass-through)."""
        if "enabled" in config:
            self.enabled = config["enabled"]
        return True
