"""
Configuration Validator for Stinger Guardrails

This module provides a centralized, rule-based configuration validation system
for all guardrails, eliminating duplicate validation logic and ensuring consistency.
"""

import re
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple, Union


@dataclass
class ValidationRule:
    """Defines a single validation rule for a configuration field."""

    field: str  # The configuration field name to validate
    required: bool = False  # Whether this field is required
    field_type: Optional[type] = None  # Expected type (e.g., str, int, list)
    min_value: Optional[Union[int, float]] = None  # Minimum numeric value
    max_value: Optional[Union[int, float]] = None  # Maximum numeric value
    min_length: Optional[int] = None  # Minimum length for strings/lists
    max_length: Optional[int] = None  # Maximum length for strings/lists
    regex: Optional[str] = None  # Regex pattern the value must match
    choices: Optional[List[Any]] = None  # Allowed values
    custom_validator: Optional[Callable[[Any], bool]] = None  # Custom validation function
    error_message: Optional[str] = None  # Custom error message

    def validate(self, value: Any) -> Tuple[bool, Optional[str]]:
        """
        Validate a value against this rule.

        Returns:
            Tuple of (is_valid, error_message)
        """
        # None is always valid unless field is required
        if value is None:
            return True, None

        # Check type
        if self.field_type is not None and not isinstance(value, self.field_type):
            # Handle tuple of types
            if isinstance(self.field_type, tuple):
                type_names = " or ".join(t.__name__ for t in self.field_type)
                return False, f"{self.field} must be of type {type_names}"
            return False, f"{self.field} must be of type {self.field_type.__name__}"

        # Numeric range validation
        if isinstance(value, (int, float)):
            if self.min_value is not None and value < self.min_value:
                # Use "non-negative" for min_value = 0 for backward compatibility
                if self.field in ["min_length", "max_length"] and self.min_value == 0:
                    return False, f"{self.field} must be non-negative"
                return False, f"{self.field} must be >= {self.min_value}"
            if self.max_value is not None and value > self.max_value:
                return False, f"{self.field} must be <= {self.max_value}"

        # Length validation
        if hasattr(value, "__len__"):
            length = len(value)
            if self.min_length is not None and length < self.min_length:
                return False, f"{self.field} must have length >= {self.min_length}"
            if self.max_length is not None and length > self.max_length:
                return False, f"{self.field} must have length <= {self.max_length}"

        # Regex validation
        if self.regex and isinstance(value, str):
            if not re.match(self.regex, value):
                return False, f"{self.field} does not match required pattern"

        # Choices validation
        if self.choices is not None and value not in self.choices:
            return False, f"{self.field} must be one of {self.choices}"

        # Custom validation
        if self.custom_validator:
            if not self.custom_validator(value):
                return False, self.error_message or f"{self.field} failed custom validation"

        return True, None


class ConfigValidator:
    """Centralized configuration validator for all guardrails."""

    def __init__(self, rules: List[ValidationRule]):
        """
        Initialize validator with a list of rules.

        Args:
            rules: List of ValidationRule objects defining the validation schema
        """
        self.rules = {rule.field: rule for rule in rules}

    def validate(self, config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate a configuration dictionary against all rules.

        Args:
            config: Configuration dictionary to validate

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Check required fields
        for field_name, rule in self.rules.items():
            if rule.required and field_name not in config:
                errors.append(f"Required field '{field_name}' is missing")

        # Validate present fields
        for field_name, value in config.items():
            if field_name in self.rules:
                rule = self.rules[field_name]
                is_valid, error_msg = rule.validate(value)
                if not is_valid:
                    errors.append(error_msg)

        return len(errors) == 0, errors

    def validate_with_exception(self, config: Dict[str, Any]):
        """
        Validate configuration and raise ValueError if invalid.

        Args:
            config: Configuration dictionary to validate

        Raises:
            ValueError: If configuration is invalid
        """
        is_valid, errors = self.validate(config)
        if not is_valid:
            raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")


# Standard validation rule sets for common guardrail patterns

# Common rules for all guardrails
COMMON_GUARDRAIL_RULES = [
    ValidationRule(field="name", required=False, field_type=str),
    ValidationRule(field="enabled", required=False, field_type=bool),
]

# Rules for AI-based guardrails
AI_GUARDRAIL_RULES = COMMON_GUARDRAIL_RULES + [
    ValidationRule(
        field="confidence_threshold",
        required=False,
        field_type=(int, float),
        min_value=0.0,
        max_value=1.0,
    ),
    ValidationRule(
        field="on_error", required=False, field_type=str, choices=["allow", "block", "warn"]
    ),
]

# Rules for regex-based guardrails
REGEX_GUARDRAIL_RULES = COMMON_GUARDRAIL_RULES + [
    ValidationRule(field="patterns", required=True, field_type=list),
    ValidationRule(
        field="action", required=False, field_type=str, choices=["block", "allow", "warn"]
    ),
    ValidationRule(field="case_sensitive", required=False, field_type=bool),
    ValidationRule(field="flags", required=False, field_type=int),
]

# Rules for keyword list guardrails
KEYWORD_GUARDRAIL_RULES = COMMON_GUARDRAIL_RULES + [
    ValidationRule(
        field="keywords",
        required=False,
        field_type=(list, str),
        custom_validator=lambda v: v != [] if isinstance(v, list) else True,
        error_message="Keywords list cannot be empty if provided",
    ),
    ValidationRule(field="keywords_file", required=False, field_type=str),
    ValidationRule(field="case_sensitive", required=False, field_type=bool),
]

# Rules for length guardrails
LENGTH_GUARDRAIL_RULES = COMMON_GUARDRAIL_RULES + [
    ValidationRule(field="min_length", required=False, field_type=(int, float), min_value=0),
    ValidationRule(field="max_length", required=False, field_type=(int, float), min_value=0),
    ValidationRule(
        field="action", required=False, field_type=str, choices=["block", "allow", "warn"]
    ),
]

# Rules for URL guardrails
URL_GUARDRAIL_RULES = COMMON_GUARDRAIL_RULES + [
    ValidationRule(field="blocked_domains", required=False, field_type=list),
    ValidationRule(field="allowed_domains", required=False, field_type=list),
    ValidationRule(
        field="action", required=False, field_type=str, choices=["block", "allow", "warn"]
    ),
]

# Rules for topic guardrails
TOPIC_GUARDRAIL_RULES = COMMON_GUARDRAIL_RULES + [
    ValidationRule(field="allowed_topics", required=False, field_type=list),
    ValidationRule(field="denied_topics", required=False, field_type=list),
    ValidationRule(
        field="detection_method",
        required=False,
        field_type=str,
        choices=["ai", "regex", "compound"],
    ),
]


def create_length_validator() -> ConfigValidator:
    """Create a validator for length guardrail."""

    class LengthConfigValidator(ConfigValidator):
        """Custom validator for length guardrail with cross-field validation."""

        def validate(self, config: Dict[str, Any]) -> Tuple[bool, List[str]]:
            """Validate with additional cross-field checks."""
            # Run standard validation first
            is_valid, errors = super().validate(config)

            # Add cross-field validation only if basic validation passed
            if is_valid:
                min_len = config.get("min_length", 0)
                max_len = config.get("max_length")

                if max_len is not None and min_len > max_len:
                    errors.append("min_length cannot be greater than max_length")
                    is_valid = False

            return is_valid, errors

    return LengthConfigValidator(LENGTH_GUARDRAIL_RULES)
