import re
from typing import List, Optional

from ..core.config_validator import REGEX_GUARDRAIL_RULES, ValidationRule
from ..core.conversation import Conversation
from ..core.guardrail_interface import GuardrailInterface, GuardrailResult, GuardrailType
from ..core.regex_security import RegexSecurityValidator, SecurityError


class RegexGuardrail(GuardrailInterface):
    def __init__(self, config: dict):
        """Initialize regex filter."""
        name = config.get("name", "regex_filter")

        # Prepare config for validation - if nested config exists, merge it up for validation
        validation_config = config.copy()
        if "config" in config:
            nested = config["config"]
            for key, value in nested.items():
                if key not in validation_config:
                    validation_config[key] = value

        # Initialize with validation
        super().__init__(name, GuardrailType.REGEX_FILTER, validation_config)

        # Handle nested config structure from pipeline configuration
        nested_config = config.get("config", {})

        self.patterns = nested_config.get("patterns", config.get("patterns", []))
        self.action = nested_config.get(
            "action", config.get("action", "block")
        )  # 'block', 'allow', 'warn'
        self.flags = nested_config.get("flags", config.get("flags", 0))
        self.case_sensitive = nested_config.get(
            "case_sensitive", config.get("case_sensitive", True)
        )

        # Initialize security validator
        self.security_validator = RegexSecurityValidator()

        # Compile patterns with security validation
        self.compiled_patterns = []
        for pattern in self.patterns:
            try:
                # Validate pattern for security before compiling
                is_safe, reason = self.security_validator.validate_pattern(pattern)
                if not is_safe:
                    raise SecurityError(f"Unsafe regex pattern '{pattern}': {reason}")

                flags = 0 if self.case_sensitive else re.IGNORECASE
                flags |= self.flags

                # Use safe compilation
                compiled = self.security_validator.safe_compile(pattern, flags)
                self.compiled_patterns.append(compiled)

            except (re.error, SecurityError) as e:
                raise ValueError(f"Invalid or unsafe regex pattern '{pattern}': {str(e)}")

    def get_validation_rules(self) -> List[ValidationRule]:
        """Get validation rules for regex guardrail."""
        return REGEX_GUARDRAIL_RULES

    async def analyze(
        self, content: str, conversation: Optional["Conversation"] = None
    ) -> GuardrailResult:
        """Analyze content for regex pattern matches."""
        if not content or not self.compiled_patterns:
            return GuardrailResult(
                blocked=False,
                confidence=0.0,
                reason="No content or patterns to match",
                details={"patterns_count": len(self.patterns)},
                guardrail_name=self.name,
                guardrail_type=self.guardrail_type,
                risk_level="low",
            )

        matches = []
        for i, pattern in enumerate(self.compiled_patterns):
            try:
                # Use safe search with timeout protection
                match = self.security_validator.safe_search(pattern, content)
                if match:
                    matches.append(self.patterns[i])
            except SecurityError as e:
                # Log security error but continue processing other patterns
                import logging

                logging.warning(f"Regex security error for pattern '{self.patterns[i]}': {e}")
                continue

        if matches:
            return GuardrailResult(
                blocked=True,
                confidence=1.0,
                reason=f"Matched patterns: {', '.join(matches)}",
                details={
                    "matched_patterns": matches,
                    "total_patterns": len(self.patterns),
                    "action": self.action,
                },
                guardrail_name=self.name,
                guardrail_type=self.guardrail_type,
                risk_level="high",
            )

        return GuardrailResult(
            blocked=False,
            confidence=0.0,
            reason="No pattern matches found",
            details={"matched_patterns": [], "total_patterns": len(self.patterns)},
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
            "patterns": self.patterns,
            "action": self.action,
            "flags": self.flags,
            "case_sensitive": self.case_sensitive,
        }

    def update_config(self, config: dict) -> bool:
        """Update configuration."""
        try:
            if "patterns" in config:
                self.patterns = config["patterns"]
                # Recompile patterns
                self._compile_patterns()
            if "action" in config:
                self.action = config["action"]
            if "flags" in config:
                self.flags = config["flags"]
            if "case_sensitive" in config:
                self.case_sensitive = config["case_sensitive"]
            if "enabled" in config:
                self.enabled = config["enabled"]
            return True
        except Exception:
            return False

    def _compile_patterns(self):
        """Recompile patterns after configuration update."""
        self.compiled_patterns = []
        for pattern in self.patterns:
            try:
                # Validate pattern for security before compiling
                is_safe, reason = self.security_validator.validate_pattern(pattern)
                if not is_safe:
                    raise SecurityError(f"Unsafe regex pattern '{pattern}': {reason}")

                flags = 0 if self.case_sensitive else re.IGNORECASE
                flags |= self.flags

                # Use safe compilation
                compiled = self.security_validator.safe_compile(pattern, flags)
                self.compiled_patterns.append(compiled)

            except (re.error, SecurityError) as e:
                raise ValueError(f"Invalid or unsafe regex pattern '{pattern}': {str(e)}")
