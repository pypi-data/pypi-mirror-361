"""
Simple PII Detection Filter

This module provides a regex-based PII detection filter that can identify
various types of personally identifiable information without requiring AI.
"""

import logging
import re
from typing import Any, Dict, List, Optional

from ..core.config_validator import COMMON_GUARDRAIL_RULES, ValidationRule
from ..core.conversation import Conversation
from ..core.guardrail_interface import GuardrailInterface, GuardrailResult, GuardrailType

logger = logging.getLogger(__name__)


class SimplePIIDetectionGuardrail(GuardrailInterface):
    """Regex-based PII detection filter."""

    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, GuardrailType.PII_DETECTION, config)

        self.pii_patterns = {
            "ssn": r"\b\d{3}-?\d{2}-?\d{4}\b",
            "credit_card": r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b",
            "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "phone": r"\b(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b",
            "ip_address": r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
            "driver_license": r"\b[A-Z]{1,2}\d{6,8}\b",
            "passport": r"\b[A-Z]{1,2}\d{6,9}\b",
            "bank_account": r"\b\d{8,17}\b",
        }

        # Handle nested config structure from pipeline configuration
        nested_config = config.get("config", {})

        self.enabled_patterns = nested_config.get(
            "patterns", config.get("patterns", list(self.pii_patterns.keys()))
        )
        self.confidence_threshold = nested_config.get(
            "confidence_threshold", config.get("confidence_threshold", 0.8)
        )
        self.on_error = config.get("on_error", "block")

        # Validate enabled patterns - filter out unknown patterns
        valid_patterns = []
        for pattern in self.enabled_patterns:
            if pattern in self.pii_patterns:
                valid_patterns.append(pattern)
            else:
                logger.warning(f"Unknown PII pattern '{pattern}' in filter '{name}'")

        self.enabled_patterns = valid_patterns

    def get_validation_rules(self) -> List[ValidationRule]:
        """Get validation rules for simple PII detection guardrail."""
        return COMMON_GUARDRAIL_RULES

    async def analyze(
        self, content: str, conversation: Optional["Conversation"] = None
    ) -> GuardrailResult:
        """Analyze content for PII patterns using regex."""
        if not self.enabled:
            return GuardrailResult(
                blocked=False,
                confidence=0.0,
                reason="PII detection filter disabled",
                details={"method": "regex", "enabled": False},
                guardrail_name=self.name,
                guardrail_type=self.guardrail_type,
            )

        try:
            detected_pii = []
            confidence_scores = {}

            for pii_type, pattern in self.pii_patterns.items():
                if pii_type in self.enabled_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        detected_pii.append(pii_type)
                        # Calculate confidence based on PII type and number of matches
                        # High confidence for unambiguous patterns like SSN, credit cards, and emails
                        if pii_type in ["ssn", "credit_card", "email", "phone"]:
                            confidence_scores[pii_type] = min(0.95, 0.8 + len(matches) * 0.05)
                        else:
                            confidence_scores[pii_type] = min(0.9, 0.5 + len(matches) * 0.1)

            if detected_pii:
                max_confidence = max(confidence_scores.values())
                blocked = max_confidence >= self.confidence_threshold

                return GuardrailResult(
                    blocked=blocked,
                    confidence=max_confidence,
                    reason=f"PII detected (regex): {', '.join(detected_pii)}",
                    details={
                        "detected_pii": detected_pii,
                        "confidence_scores": confidence_scores,
                        "method": "regex",
                    },
                    guardrail_name=self.name,
                    guardrail_type=self.guardrail_type,
                )
            else:
                return GuardrailResult(
                    blocked=False,
                    confidence=0.0,
                    reason="No PII detected (regex)",
                    details={"detected_pii": [], "confidence_scores": {}, "method": "regex"},
                    guardrail_name=self.name,
                    guardrail_type=self.guardrail_type,
                )

        except Exception as e:
            logger.error(f"Error in PII detection filter '{self.name}': {e}")
            blocked = self.on_error == "block"
            return GuardrailResult(
                blocked=blocked,
                confidence=0.0,
                reason=f"PII detection error: {str(e)}",
                details={"error": str(e), "method": "regex"},
                guardrail_name=self.name,
                guardrail_type=self.guardrail_type,
            )

    def is_available(self) -> bool:
        """Check if this guardrail is available."""
        return self.enabled

    def get_config(self) -> Dict[str, Any]:
        """Get current configuration of this guardrail."""
        return {
            "enabled": self.enabled,
            "patterns": self.enabled_patterns,
            "confidence_threshold": self.confidence_threshold,
            "on_error": self.on_error,
        }

    def update_config(self, config: Dict[str, Any]) -> bool:
        """Update configuration of this guardrail."""
        try:
            if "enabled" in config:
                self.enabled = config["enabled"]
            if "patterns" in config:
                self.enabled_patterns = config["patterns"]
            if "confidence_threshold" in config:
                self.confidence_threshold = config["confidence_threshold"]
            if "on_error" in config:
                self.on_error = config["on_error"]
            return True
        except Exception as e:
            logger.error(f"Failed to update PII detection filter config: {e}")
            return False
