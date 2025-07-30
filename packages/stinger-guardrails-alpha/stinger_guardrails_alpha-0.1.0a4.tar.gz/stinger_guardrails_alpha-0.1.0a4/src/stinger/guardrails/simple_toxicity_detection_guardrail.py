"""
Simple Toxicity Detection Filter

This module provides a regex-based toxicity detection filter that can identify
various types of toxic content without requiring AI.
"""

import logging
import re
from typing import Any, Dict, List, Optional

from ..core.config_validator import COMMON_GUARDRAIL_RULES, ValidationRule
from ..core.conversation import Conversation
from ..core.guardrail_interface import GuardrailInterface, GuardrailResult, GuardrailType

logger = logging.getLogger(__name__)


class SimpleToxicityDetectionGuardrail(GuardrailInterface):
    """Regex-based toxicity detection filter."""

    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, GuardrailType.TOXICITY_DETECTION, config)

        self.toxicity_patterns = {
            "hate_speech": [
                r"\b(nazi|fascist|racist|bigot|homophobe|transphobe)\b",
                r"\b(kill\s+all|exterminate|genocide|ethnic\s+cleansing)\b",
                r"\b(white\s+supremacy|aryan|master\s+race)\b",
            ],
            "harassment": [
                r"\b(stalk|harass|bully|intimidate|threaten)\b",
                r"\b(you\s+suck|you'?re?\s+stupid|you'?re?\s+worthless|you'?re?\s+ugly)\b",
                r"\b(go\s+die|kill\s+yourself|commit\s+suicide)\b",
                r"\b(i\s+hate\s+you|hate\s+you)\b",
            ],
            "threats": [
                r"\b(i\s+will\s+kill|i\s+will\s+hurt|i\s+will\s+destroy)\b",
                r"\b(you\s+will\s+die|you\s+will\s+pay|you\s+will\s+regret)\b",
                r"\b(i\s+hope\s+you\s+die|i\s+wish\s+you\s+were\s+dead)\b",
            ],
            "sexual_harassment": [
                r"\b(sexual|nude|porn|explicit)\b.*\b(harass|assault|abuse)\b",
                r"\b(rape|molest|grope|fondle)\b",
                r"\b(sexy|hot|beautiful)\b.*\b(send\s+pics|show\s+me)\b",
                r"\b(porn\s+site|porn\s+video|xxx|adult\s+content)\b",
            ],
            "violence": [
                r"\b(punch|hit|beat|attack|fight|violence)\b",
                r"\b(gun|shoot|bomb|explode|terrorist)\b",
                r"\b(murder|assassinate|execute|lynch)\b",
                r"\b(let's\s+fight|wanna\s+fight|fight\s+me)\b",
            ],
        }

        # Handle nested config structure from pipeline configuration
        nested_config = config.get("config", {})

        self.enabled_categories = nested_config.get(
            "categories", config.get("categories", list(self.toxicity_patterns.keys()))
        )
        self.confidence_threshold = nested_config.get(
            "confidence_threshold", config.get("confidence_threshold", 0.7)
        )
        self.on_error = config.get("on_error", "block")

        # Category name mappings for common variations
        category_mappings = {
            "hate": "hate_speech",
            "sexual": "sexual_harassment",
            "threat": "threats",
        }

        # Validate enabled categories - filter out unknown categories and map common variations
        valid_categories = []
        for category in self.enabled_categories:
            # Check for direct match
            if category in self.toxicity_patterns:
                valid_categories.append(category)
            # Check for mapped variation
            elif (
                category in category_mappings
                and category_mappings[category] in self.toxicity_patterns
            ):
                valid_categories.append(category_mappings[category])
            else:
                logger.warning(f"Unknown toxicity category '{category}' in filter '{name}'")

        self.enabled_categories = valid_categories

    def get_validation_rules(self) -> List[ValidationRule]:
        """Get validation rules for simple toxicity detection guardrail."""
        return COMMON_GUARDRAIL_RULES

    async def analyze(
        self, content: str, conversation: Optional["Conversation"] = None
    ) -> GuardrailResult:
        """Analyze content for toxicity patterns using regex."""
        if not self.enabled:
            return GuardrailResult(
                blocked=False,
                confidence=0.0,
                reason="Toxicity detection filter disabled",
                details={"method": "regex", "enabled": False},
                guardrail_name=self.name,
                guardrail_type=self.guardrail_type,
            )

        try:
            detected_toxicity = []
            confidence_scores = {}

            for category, patterns in self.toxicity_patterns.items():
                if category in self.enabled_categories:
                    category_matches = 0
                    for pattern in patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        category_matches += len(matches)

                    if category_matches > 0:
                        detected_toxicity.append(category)
                        # Calculate confidence based on category and number of matches
                        # Higher base confidence for more serious categories
                        if category in [
                            "hate_speech",
                            "harassment",
                            "threats",
                            "sexual_harassment",
                        ]:
                            base_confidence = 0.6
                        else:
                            base_confidence = 0.3
                        confidence_scores[category] = min(
                            0.95, base_confidence + category_matches * 0.15
                        )

            if detected_toxicity:
                max_confidence = max(confidence_scores.values())
                blocked = max_confidence >= self.confidence_threshold

                return GuardrailResult(
                    blocked=blocked,
                    confidence=max_confidence,
                    reason=f"Toxic content detected (regex): {', '.join(detected_toxicity)}",
                    details={
                        "detected_toxicity": detected_toxicity,
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
                    reason="No toxic content detected (regex)",
                    details={"detected_toxicity": [], "confidence_scores": {}, "method": "regex"},
                    guardrail_name=self.name,
                    guardrail_type=self.guardrail_type,
                )

        except Exception as e:
            logger.error(f"Error in toxicity detection filter '{self.name}': {e}")
            blocked = self.on_error == "block"
            return GuardrailResult(
                blocked=blocked,
                confidence=0.0,
                reason=f"Toxicity detection error: {str(e)}",
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
            "categories": self.enabled_categories,
            "confidence_threshold": self.confidence_threshold,
            "on_error": self.on_error,
        }

    def update_config(self, config: Dict[str, Any]) -> bool:
        """Update configuration of this guardrail."""
        try:
            if "enabled" in config:
                self.enabled = config["enabled"]
            if "categories" in config:
                self.enabled_categories = config["categories"]
            if "confidence_threshold" in config:
                self.confidence_threshold = config["confidence_threshold"]
            if "on_error" in config:
                self.on_error = config["on_error"]
            return True
        except Exception as e:
            logger.error(f"Failed to update toxicity detection filter config: {e}")
            return False
