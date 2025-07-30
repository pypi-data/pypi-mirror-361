"""
Topic Filter

This filter provides content-based filtering using allow/deny lists for topics or categories.
It can be used to restrict or allow content based on predefined topic lists.
"""

import logging
import re
from typing import Any, Dict, List, Optional

from ..core.config_validator import TOPIC_GUARDRAIL_RULES, ValidationRule
from ..core.conversation import Conversation

# FilterResult removed - now using GuardrailResult only
from ..core.guardrail_interface import GuardrailInterface, GuardrailResult, GuardrailType

logger = logging.getLogger(__name__)


class TopicGuardrail(GuardrailInterface):
    """
    Filter content based on topic allow/deny lists.

    This filter can:
    - Allow only specific topics (whitelist mode)
    - Deny specific topics (blacklist mode)
    - Use both allow and deny lists with priority rules
    - Support regex patterns for topic matching
    - Provide confidence scoring based on match strength
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the topic filter.

        Args:
            config: Configuration dictionary containing:
                - allow_topics: List of allowed topics (whitelist)
                - deny_topics: List of denied topics (blacklist)
                - mode: Filter mode ("allow", "deny", "both")
                - case_sensitive: Whether topic matching is case sensitive
                - use_regex: Whether to treat topics as regex patterns
                - confidence_threshold: Minimum confidence for blocking
        """
        # Initialize GuardrailInterface with required parameters
        name = config.get("name", "topic_filter")
        super().__init__(name, GuardrailType.TOPIC_FILTER, config)

        # Handle nested config structure from pipeline configuration
        nested_config = config.get("config", {})

        self.allow_topics = nested_config.get("allow_topics", config.get("allow_topics", []))
        self.deny_topics = nested_config.get("deny_topics", config.get("deny_topics", []))
        self.mode = nested_config.get("mode", config.get("mode", "deny"))
        self.case_sensitive = nested_config.get(
            "case_sensitive", config.get("case_sensitive", False)
        )
        self.use_regex = nested_config.get("use_regex", config.get("use_regex", False))
        self.confidence_threshold = nested_config.get(
            "confidence_threshold", config.get("confidence_threshold", 0.5)
        )

        # Compile regex patterns if needed
        self._compiled_allow_patterns: List[re.Pattern] = []
        self._compiled_deny_patterns: List[re.Pattern] = []
        self._compile_patterns()

        logger.info(f"Initialized TopicGuardrail '{self.name}' with mode '{self.mode}'")

    def get_validation_rules(self) -> List[ValidationRule]:
        """Get validation rules for topic guardrail."""
        return TOPIC_GUARDRAIL_RULES

    def _compile_patterns(self) -> None:
        """Compile regex patterns for topic matching."""
        self._compiled_allow_patterns = []
        self._compiled_deny_patterns = []

        flags = 0 if self.case_sensitive else re.IGNORECASE

        if self.use_regex:
            # Compile regex patterns
            for topic in self.allow_topics:
                try:
                    pattern = re.compile(topic, flags)
                    self._compiled_allow_patterns.append(pattern)
                except re.error as e:
                    logger.warning(f"Invalid regex pattern in allow_topics: {topic} - {e}")

            for topic in self.deny_topics:
                try:
                    pattern = re.compile(topic, flags)
                    self._compiled_deny_patterns.append(pattern)
                except re.error as e:
                    logger.warning(f"Invalid regex pattern in deny_topics: {topic} - {e}")
        else:
            # Create simple string patterns
            for topic in self.allow_topics:
                pattern = re.compile(re.escape(topic), flags)
                self._compiled_allow_patterns.append(pattern)

            for topic in self.deny_topics:
                pattern = re.compile(re.escape(topic), flags)
                self._compiled_deny_patterns.append(pattern)

    # Legacy run() method removed - now using analyze() method only

    def check(self, content: str) -> GuardrailResult:
        """
        Check content against topic allow/deny lists (GuardrailInterface compatibility).

        Args:
            content: Content to check

        Returns:
            GuardrailResult with blocking decision and details
        """
        if not self.enabled:
            return {
                "blocked": False,
                "warnings": [],
                "reasons": [],
                "details": {"filter": self.name, "enabled": False},
            }

        if not content:
            return {
                "blocked": False,
                "warnings": [],
                "reasons": [],
                "details": {"filter": self.name, "empty_content": True},
            }

        # Find matches
        allow_matches = self._find_matches(
            content, self._compiled_allow_patterns, self.allow_topics
        )
        deny_matches = self._find_matches(content, self._compiled_deny_patterns, self.deny_topics)

        # Determine blocking decision based on mode
        blocked = False
        reasons: List[str] = []
        confidence = 0.0

        if self.mode == "allow":
            # Only allow content if it matches allow_topics
            if not allow_matches:
                blocked = True
                reasons.append("Content does not match any allowed topics")
                confidence = 1.0
            else:
                confidence = min(1.0, len(allow_matches) / max(len(self.allow_topics), 1))

        elif self.mode == "deny":
            # Block content if it matches deny_topics
            if deny_matches:
                confidence = min(1.0, len(deny_matches) / max(len(self.deny_topics), 1))
                if confidence >= self.confidence_threshold:
                    blocked = True
                    reasons.append(f"Content matches denied topics: {', '.join(deny_matches)}")
                else:
                    blocked = False
                    reasons.append(
                        f"Confidence {confidence:.2f} below threshold {self.confidence_threshold}"
                    )

        elif self.mode == "both":
            # Use both lists with deny taking priority
            if deny_matches:
                blocked = True
                reasons.append(f"Content matches denied topics: {', '.join(deny_matches)}")
                confidence = min(1.0, len(deny_matches) / max(len(self.deny_topics), 1))
            elif self.allow_topics and not allow_matches:
                blocked = True
                reasons.append("Content does not match any allowed topics")
                confidence = 1.0

        # Check confidence threshold
        if self.mode == "both" and self.allow_topics and not allow_matches and not deny_matches:
            blocked = False
            reasons = []
        elif confidence < self.confidence_threshold:
            blocked = False
            reasons = []

        return {
            "blocked": blocked,
            "warnings": [],
            "reasons": reasons,
            "details": {
                "filter": self.name,
                "mode": self.mode,
                "allow_matches": allow_matches,
                "deny_matches": deny_matches,
                "confidence": confidence,
                "allow_topics_count": len(self.allow_topics),
                "deny_topics_count": len(self.deny_topics),
            },
        }

    def _find_matches(
        self, content: str, patterns: List[re.Pattern], topics: List[str]
    ) -> List[str]:
        """
        Find topic matches in content.

        Args:
            content: Content to search
            patterns: Compiled regex patterns
            topics: Original topic strings

        Returns:
            List of matched topics
        """
        matches = []

        for i, pattern in enumerate(patterns):
            if pattern.search(content):
                matches.append(topics[i])

        return matches

    def get_config(self) -> Dict[str, Any]:
        """Get filter configuration."""
        return {
            "type": "topic_filter",
            "name": self.name,
            "enabled": self.enabled,
            "allow_topics": self.allow_topics,
            "deny_topics": self.deny_topics,
            "mode": self.mode,
            "case_sensitive": self.case_sensitive,
            "use_regex": self.use_regex,
            "confidence_threshold": self.confidence_threshold,
        }

    def update_config(self, config: Dict[str, Any]) -> bool:
        """
        Update filter configuration.

        Args:
            config: New configuration

        Returns:
            True if update successful, False otherwise
        """
        try:
            if "allow_topics" in config:
                self.allow_topics = config["allow_topics"]
            if "deny_topics" in config:
                self.deny_topics = config["deny_topics"]
            if "mode" in config:
                self.mode = config["mode"]
            if "case_sensitive" in config:
                self.case_sensitive = config["case_sensitive"]
            if "use_regex" in config:
                self.use_regex = config["use_regex"]
            if "confidence_threshold" in config:
                self.confidence_threshold = config["confidence_threshold"]
            if "enabled" in config:
                self.enabled = config["enabled"]

            # Recompile patterns
            self._compile_patterns()

            logger.info(f"Updated TopicGuardrail '{self.name}' configuration")
            return True

        except Exception as e:
            logger.error(f"Failed to update TopicGuardrail '{self.name}' configuration: {e}")
            return False

    def get_guardrail_type(self) -> GuardrailType:
        """Get the guardrail type."""
        return GuardrailType.CONTENT_MODERATION

    def is_available(self) -> bool:
        """Check if the filter is available."""
        return True

    def get_health_status(self) -> Dict[str, Any]:
        """Get filter health status."""
        return {
            "name": self.name,
            "type": "topic_filter",
            "enabled": self.enabled,
            "available": True,
            "allow_topics_count": len(self.allow_topics),
            "deny_topics_count": len(self.deny_topics),
            "compiled_patterns": len(self._compiled_allow_patterns)
            + len(self._compiled_deny_patterns),
        }

    async def analyze(
        self, content: str, conversation: Optional["Conversation"] = None
    ) -> GuardrailResult:
        """
        Analyze content for topic matches (GuardrailInterface async method).

        Args:
            content: Content to analyze
            conversation: Optional conversation context (not used in this filter)

        Returns:
            GuardrailResult with blocking decision and details
        """
        if not self.enabled:
            return GuardrailResult(
                blocked=False,
                confidence=0.0,
                reason="Topic filter disabled",
                details={"enabled": False},
                guardrail_name=self.name,
                guardrail_type=self.guardrail_type,
            )

        if not content:
            return GuardrailResult(
                blocked=False,
                confidence=0.0,
                reason="Empty content",
                details={"empty_content": True},
                guardrail_name=self.name,
                guardrail_type=self.guardrail_type,
            )

        # Find matches
        allow_matches = self._find_matches(
            content, self._compiled_allow_patterns, self.allow_topics
        )
        deny_matches = self._find_matches(content, self._compiled_deny_patterns, self.deny_topics)

        # Determine blocking decision based on mode
        blocked = False
        reason = "Content allowed"
        confidence = 0.0

        if self.mode == "allow":
            # Only allow content if it matches allow_topics
            if not allow_matches:
                blocked = True
                reason = "Content does not match any allowed topics"
                confidence = 1.0
            else:
                confidence = min(1.0, len(allow_matches) / max(len(self.allow_topics), 1))
                reason = f"Content matches allowed topics: {', '.join(allow_matches)}"

        elif self.mode == "deny":
            # Block content if it matches deny_topics
            if deny_matches:
                confidence = min(1.0, len(deny_matches) / max(len(self.deny_topics), 1))
                if confidence >= self.confidence_threshold:
                    blocked = True
                    reason = f"Content matches denied topics: {', '.join(deny_matches)}"
                else:
                    reason = (
                        f"Confidence {confidence:.2f} below threshold {self.confidence_threshold}"
                    )

        elif self.mode == "both":
            # Use both lists with deny taking priority
            if deny_matches:
                blocked = True
                reason = f"Content matches denied topics: {', '.join(deny_matches)}"
                confidence = min(1.0, len(deny_matches) / max(len(self.deny_topics), 1))
            elif self.allow_topics and not allow_matches:
                blocked = True
                reason = "Content does not match any allowed topics"
                confidence = 1.0
            else:
                confidence = (
                    min(1.0, len(allow_matches) / max(len(self.allow_topics), 1))
                    if allow_matches
                    else 0.0
                )
                reason = (
                    f"Content matches allowed topics: {', '.join(allow_matches)}"
                    if allow_matches
                    else "No topic restrictions"
                )

        return GuardrailResult(
            blocked=blocked,
            confidence=confidence,
            reason=reason,
            details={
                "mode": self.mode,
                "allow_matches": allow_matches,
                "deny_matches": deny_matches,
                "allow_topics_count": len(self.allow_topics),
                "deny_topics_count": len(self.deny_topics),
            },
            guardrail_name=self.name,
            guardrail_type=self.guardrail_type,
        )
