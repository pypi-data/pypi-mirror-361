import logging
from pathlib import Path
from typing import List, Optional, Tuple

from ..core.config_validator import KEYWORD_GUARDRAIL_RULES, ConfigValidator, ValidationRule
from ..core.conversation import Conversation
from ..core.guardrail_interface import GuardrailInterface, GuardrailResult, GuardrailType
from ..utils.exceptions import GuardrailError

logger = logging.getLogger(__name__)


class KeywordListGuardrail(GuardrailInterface):
    """
    Filter that blocks content containing any of a list of keywords.
    Supports both inline keywords and loading from external files.
    """

    def __init__(self, config: dict):
        """Initialize keyword list filter."""
        name = config.get("name", "keyword_list")

        # Prepare config for validation - if nested config exists, merge it up for validation
        validation_config = config.copy()
        if "config" in config:
            nested = config["config"]
            for key, value in nested.items():
                if key not in validation_config:
                    validation_config[key] = value

        # Initialize with validation
        super().__init__(name, GuardrailType.KEYWORD_LIST, validation_config)

        self.config = config  # Keep for compatibility with _load_keywords
        self.keywords = []

        # Handle nested config structure
        nested_config = config.get("config", {})
        self.case_sensitive = nested_config.get(
            "case_sensitive", config.get("case_sensitive", False)
        )

        self._load_keywords()

    def get_validation_rules(self) -> List[ValidationRule]:
        """Get validation rules for keyword list guardrail."""
        return KEYWORD_GUARDRAIL_RULES

    def get_config_validator(self) -> ConfigValidator:
        """Get custom validator with keyword validation logic."""

        class KeywordListValidator(ConfigValidator):
            def validate(self, config: dict) -> Tuple[bool, List[str]]:
                is_valid, errors = super().validate(config)

                # Additional validation: must have either keywords or keywords_file
                if not config.get("keywords") and not config.get("keywords_file"):
                    errors.append("Either 'keywords' or 'keywords_file' must be provided")
                    is_valid = False

                return is_valid, errors

        return KeywordListValidator(KEYWORD_GUARDRAIL_RULES)

    def _load_keywords(self):
        """Load keywords from config or file."""
        # Handle nested config structure
        nested_config = self.config.get("config", {})

        # Get inline keywords from nested or flat config
        inline_keywords = nested_config.get("keywords", self.config.get("keywords", []))
        if isinstance(inline_keywords, str):
            inline_keywords = [inline_keywords]

        # Get file path for keywords from nested or flat config
        keywords_file = nested_config.get("keywords_file", self.config.get("keywords_file"))

        if keywords_file:
            try:
                file_keywords = self._load_keywords_from_file(keywords_file)
                # Combine file keywords with inline keywords (file takes precedence)
                self.keywords = file_keywords + [
                    kw for kw in inline_keywords if kw not in file_keywords
                ]
            except Exception as e:
                # If file loading fails, use only inline keywords
                from ..core.error_handling import safe_error_message, sanitize_path

                safe_path = sanitize_path(keywords_file)
                safe_msg = safe_error_message(e, f"loading keywords from file {safe_path}")
                self.keywords = inline_keywords
                logger.warning(f"{safe_msg}")
                logger.warning(f"Using fallback keywords: {inline_keywords}")
        else:
            self.keywords = inline_keywords

        # Validate keywords
        if not self.keywords:
            raise GuardrailError("No keywords provided for KeywordListGuardrail")

        # Convert to lowercase for case-insensitive matching
        if not self.case_sensitive:
            self.keywords = [kw.lower() for kw in self.keywords]

    def _load_keywords_from_file(self, file_path: str) -> List[str]:
        """Load keywords from a text file."""
        # Resolve relative path from config file location
        config_dir = self.config.get("_config_dir", ".")
        resolved_path = Path(config_dir) / file_path

        if not resolved_path.exists():
            raise FileNotFoundError(f"Keywords file not found: {resolved_path}")

        keywords = []
        try:
            with open(resolved_path, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    # Skip empty lines and comments
                    if line and not line.startswith("#"):
                        keywords.append(line)
        except Exception as e:
            from ..core.error_handling import safe_error_message, sanitize_path

            safe_path = sanitize_path(str(resolved_path))
            # Check if this is a file access error (before any lines processed)
            if "line_num" not in locals():
                safe_msg = safe_error_message(e, f"opening keywords file {safe_path}")
            else:
                safe_msg = safe_error_message(
                    e, f"reading keywords file {safe_path} at line {line_num}"
                )
            raise GuardrailError(f"Failed to read keywords file: {safe_msg}")

        return keywords

    async def analyze(
        self, content: str, conversation: Optional["Conversation"] = None
    ) -> GuardrailResult:
        """Analyze content for blocked keywords."""
        if not content:
            return GuardrailResult(
                blocked=False,
                confidence=0.0,
                reason="No content to analyze",
                details={"keywords_count": len(self.keywords)},
                guardrail_name=self.name,
                guardrail_type=self.guardrail_type,
                risk_level="low",
            )

        if not self.keywords:
            return GuardrailResult(
                blocked=False,
                confidence=0.0,
                reason="No keywords configured",
                details={"keywords_count": 0},
                guardrail_name=self.name,
                guardrail_type=self.guardrail_type,
                risk_level="low",
            )

        # Prepare content for matching
        content_to_check = content if self.case_sensitive else content.lower()

        # Check for matches
        matched_keywords = []
        for keyword in self.keywords:
            if keyword in content_to_check:
                matched_keywords.append(keyword)

        if matched_keywords:
            return GuardrailResult(
                blocked=True,
                confidence=1.0,
                reason=f'Blocked keywords found: {", ".join(matched_keywords)}',
                details={
                    "matched_keywords": matched_keywords,
                    "total_keywords": len(self.keywords),
                    "case_sensitive": self.case_sensitive,
                },
                guardrail_name=self.name,
                guardrail_type=self.guardrail_type,
                risk_level="high",
            )

        return GuardrailResult(
            blocked=False,
            confidence=0.0,
            reason="No keyword matches found",
            details={
                "matched_keywords": [],
                "total_keywords": len(self.keywords),
                "case_sensitive": self.case_sensitive,
            },
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
            "keywords": self.keywords,
            "case_sensitive": self.case_sensitive,
            "keywords_file": self.config.get("keywords_file"),
        }

    def update_config(self, config: dict) -> bool:
        """Update configuration."""
        try:
            # Update config dict for _load_keywords compatibility
            if "keywords" in config:
                self.config["keywords"] = config["keywords"]
            if "keywords_file" in config:
                self.config["keywords_file"] = config["keywords_file"]
            if "case_sensitive" in config:
                self.case_sensitive = config["case_sensitive"]
                self.config["case_sensitive"] = config["case_sensitive"]
            if "enabled" in config:
                self.enabled = config["enabled"]

            # Reload keywords if keywords or file changed
            if "keywords" in config or "keywords_file" in config or "case_sensitive" in config:
                self._load_keywords()

            return True
        except Exception:
            return False

    def validate_config(self) -> bool:
        """Validate filter configuration."""
        # Check that we have either keywords or keywords_file
        has_inline = bool(self.config.get("keywords"))
        has_file = bool(self.config.get("keywords_file"))

        if not has_inline and not has_file:
            raise GuardrailError(
                "KeywordListGuardrail requires either 'keywords' or 'keywords_file' configuration"
            )

        return True
