"""
Simple Code Generation Filter

This module provides a regex-based code generation detection filter that can identify
various types of code and programming content without requiring AI.
"""

import logging
import re
from typing import Any, Dict, List, Optional

from ..core.config_validator import COMMON_GUARDRAIL_RULES, ValidationRule
from ..core.conversation import Conversation
from ..core.guardrail_interface import GuardrailInterface, GuardrailResult, GuardrailType

logger = logging.getLogger(__name__)


class SimpleCodeGenerationGuardrail(GuardrailInterface):
    """Regex-based code generation detection filter."""

    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, GuardrailType.CODE_GENERATION, config)

        self.code_patterns = {
            "code_requests": [
                r"\b(write|create|generate|code|implement|build)\s+.*?(function|script|program|query|class|api|endpoint)\b",
                r"\b(write|create|generate|code|implement|build)\s+a\s+\w+\s+(function|script|program|query|class|api|endpoint)\b",
                r"\b(generate|create|write)\s+(sql|javascript|python|java|code|script)\b",
                r"\bcode\s+a\s+solution\b",
                r"\bimplement\s+a\s+\w+\b",
            ],
            "code_blocks": [
                r"```[\w]*\n.*?\n```",  # Markdown code blocks
                r"`.*?`",  # Inline code
                r"<code>.*?</code>",  # HTML code tags
                r"<pre>.*?</pre>",  # HTML pre tags
            ],
            "programming_keywords": [
                r"\b(function|def|class|import|export|require|var|let|const)\b",
                r"\b(if|else|for|while|switch|case|break|continue|return)\b",
                r"\b(public|private|protected|static|final|abstract|interface)\b",
                r"\b(try|catch|finally|throw|throws)\b",
                r"\b(new|delete|typeof|instanceof|void)\b",
            ],
            "code_injection": [
                r"\b(eval|exec|system|shell|bash|python|javascript|php)\b",
                r"\b(script|alert|console\.log|document\.write)\b",
                r"\b(sql|query|database|table|select|insert|update|delete)\b",
                r"\b(execute|run|compile|interpret)\b",
            ],
            "file_operations": [
                r"\b(file|read|write|open|close|delete|remove|create)\b",
                r"\b(path|directory|folder|mkdir|rmdir|chmod|chown)\b",
                r"\b(copy|move|rename|download|upload)\b",
            ],
            "system_commands": [
                r"\b(cmd|command|terminal|bash|shell|powershell)\b",
                r"\b(ls|dir|cd|pwd|mkdir|rmdir|cp|mv|rm)\b",
                r"\b(git|svn|npm|pip|apt|yum|brew)\b",
            ],
        }

        # Handle nested config structure from pipeline configuration
        nested_config = config.get("config", {})

        self.enabled_categories = nested_config.get(
            "categories", config.get("categories", list(self.code_patterns.keys()))
        )
        self.confidence_threshold = nested_config.get(
            "confidence_threshold", config.get("confidence_threshold", 0.6)
        )
        self.min_keywords = nested_config.get("min_keywords", config.get("min_keywords", 3))
        self.on_error = config.get("on_error", "warn")

        # Validate enabled categories - filter out unknown categories
        valid_categories = []
        for category in self.enabled_categories:
            if category in self.code_patterns:
                valid_categories.append(category)
            else:
                logger.warning(f"Unknown code generation category '{category}' in filter '{name}'")

        self.enabled_categories = valid_categories

    def get_validation_rules(self) -> List[ValidationRule]:
        """Get validation rules for simple code generation guardrail."""
        return COMMON_GUARDRAIL_RULES

    async def analyze(
        self, content: str, conversation: Optional["Conversation"] = None
    ) -> GuardrailResult:
        """Analyze content for code generation patterns using regex."""
        if not self.enabled:
            return GuardrailResult(
                blocked=False,
                confidence=0.0,
                reason="Code generation filter disabled",
                details={"method": "regex", "enabled": False},
                guardrail_name=self.name,
                guardrail_type=self.guardrail_type,
            )

        try:
            detected_code = []
            confidence_scores = {}
            total_keywords = 0

            for category, patterns in self.code_patterns.items():
                if category in self.enabled_categories:
                    category_matches = 0
                    for pattern in patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
                        category_matches += len(matches)

                    if category_matches > 0:
                        detected_code.append(category)
                        total_keywords += category_matches
                        # Calculate confidence based on category and number of matches
                        if category == "code_requests":
                            base_confidence = 0.6  # High confidence for explicit code requests
                        elif category == "code_blocks":
                            base_confidence = 0.4
                        else:
                            base_confidence = 0.2
                        confidence_scores[category] = min(
                            0.9, base_confidence + category_matches * 0.15
                        )

            # Code requests are explicit, so require fewer matches
            min_required = 1 if "code_requests" in detected_code else self.min_keywords
            if detected_code and total_keywords >= min_required:
                max_confidence = max(confidence_scores.values())
                blocked = max_confidence >= self.confidence_threshold

                return GuardrailResult(
                    blocked=blocked,
                    confidence=max_confidence,
                    reason=f"Code generation detected (regex): {', '.join(detected_code)}",
                    details={
                        "detected_code": detected_code,
                        "confidence_scores": confidence_scores,
                        "total_keywords": total_keywords,
                        "method": "regex",
                    },
                    guardrail_name=self.name,
                    guardrail_type=self.guardrail_type,
                )
            else:
                return GuardrailResult(
                    blocked=False,
                    confidence=0.0,
                    reason="No code generation detected (regex)",
                    details={
                        "detected_code": [],
                        "confidence_scores": {},
                        "total_keywords": 0,
                        "method": "regex",
                    },
                    guardrail_name=self.name,
                    guardrail_type=self.guardrail_type,
                )

        except Exception as e:
            logger.error(f"Error in code generation filter '{self.name}': {e}")
            blocked = self.on_error == "block"
            return GuardrailResult(
                blocked=blocked,
                confidence=0.0,
                reason=f"Code generation detection error: {str(e)}",
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
            "min_keywords": self.min_keywords,
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
            if "min_keywords" in config:
                self.min_keywords = config["min_keywords"]
            if "on_error" in config:
                self.on_error = config["on_error"]
            return True
        except Exception as e:
            logger.error(f"Failed to update code generation filter config: {e}")
            return False
