from typing import List, Optional

from ..core.config_validator import COMMON_GUARDRAIL_RULES, ValidationRule
from ..core.conversation import Conversation
from ..core.guardrail_interface import GuardrailInterface, GuardrailResult, GuardrailType


class KeywordBlockGuardrail(GuardrailInterface):
    def __init__(self, config: dict):
        """Initialize keyword block filter."""
        name = config.get("name", "keyword_block")

        # Prepare config for validation - if nested config exists, merge it up for validation
        validation_config = config.copy()
        if "config" in config:
            nested = config["config"]
            for key, value in nested.items():
                if key not in validation_config:
                    validation_config[key] = value

        super().__init__(name, GuardrailType.KEYWORD_BLOCK, validation_config)

        # Handle nested config structure from pipeline configuration
        nested_config = config.get("config", {})

        keyword = nested_config.get("keyword", config.get("keyword", ""))
        self.keyword = keyword.lower() if keyword else ""
        self.case_sensitive = nested_config.get(
            "case_sensitive", config.get("case_sensitive", False)
        )

    def get_validation_rules(self) -> List[ValidationRule]:
        """Get validation rules for keyword block guardrail."""
        return COMMON_GUARDRAIL_RULES + [
            ValidationRule(
                field="keyword",
                required=True,
                field_type=str,
                min_length=1,
                error_message="keyword must be a non-empty string",
            )
        ]

    async def analyze(
        self, content: str, conversation: Optional["Conversation"] = None
    ) -> GuardrailResult:
        """Analyze content for blocked keywords."""
        if not self.keyword:
            return GuardrailResult(
                blocked=False,
                confidence=0.0,
                reason="No keyword configured",
                details={},
                guardrail_name=self.name,
                guardrail_type=self.guardrail_type,
                risk_level="low",
            )

        if not content:
            return GuardrailResult(
                blocked=False,
                confidence=0.0,
                reason="No content to analyze",
                details={},
                guardrail_name=self.name,
                guardrail_type=self.guardrail_type,
                risk_level="low",
            )

        if self.keyword in content.lower():
            return GuardrailResult(
                blocked=True,
                confidence=1.0,
                reason=f"Blocked keyword found: {self.keyword}",
                details={"keyword": self.keyword},
                guardrail_name=self.name,
                guardrail_type=self.guardrail_type,
                risk_level="high",
            )

        return GuardrailResult(
            blocked=False,
            confidence=0.0,
            reason="No keyword match found",
            details={"keyword": self.keyword},
            guardrail_name=self.name,
            guardrail_type=self.guardrail_type,
            risk_level="low",
        )

    def is_available(self) -> bool:
        """Check if filter is available."""
        return True

    def get_config(self) -> dict:
        """Get current configuration."""
        return {
            "name": self.name,
            "type": self.guardrail_type.value,
            "enabled": self.enabled,
            "keyword": self.keyword,
        }

    def update_config(self, config: dict) -> bool:
        """Update configuration."""
        try:
            if "keyword" in config:
                self.keyword = config["keyword"].lower()
            if "enabled" in config:
                self.enabled = config["enabled"]
            return True
        except Exception:
            return False
