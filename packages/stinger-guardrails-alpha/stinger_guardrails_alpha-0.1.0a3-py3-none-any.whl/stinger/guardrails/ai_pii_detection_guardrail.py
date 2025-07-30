"""
AI-Based PII Detection Filter

This module provides an AI-based PII detection filter using the BaseAIGuardrail
with centralized model configuration.
"""

import logging
from typing import Any, Dict, Tuple

from ..core.guardrail_interface import GuardrailType
from .base_ai_guardrail import BaseAIGuardrail

logger = logging.getLogger(__name__)


class AIPIIDetectionGuardrail(BaseAIGuardrail):
    """AI-based PII detection filter using centralized model configuration."""

    # PII detection prompt template
    PII_PROMPT = """
You are a data privacy specialist. Analyze the following text and identify any Personally Identifiable Information (PII).

PII includes:
- Social Security Numbers (SSN)
- Credit card numbers
- Email addresses
- Phone numbers
- IP addresses
- Driver's license numbers
- Passport numbers
- Bank account numbers

Respond with a JSON object containing:
- "detected": boolean (true if PII detected)
- "pii_types": array of strings (types of PII found)
- "confidence": float (0.0 to 1.0)
- "details": string (brief explanation)

Text to analyze: {content}
"""

    def __init__(self, name: str, config: Dict[str, Any]):
        """Initialize the AI PII detection filter."""
        super().__init__(
            name=name,
            guardrail_type=GuardrailType.PII_DETECTION,
            config=config,
            default_confidence_threshold=0.8,
            default_on_error="allow",
        )

    def get_analysis_prompt(self) -> str:
        """Get the PII detection prompt template."""
        return self.PII_PROMPT

    def parse_ai_response(self, data: Dict[str, Any]) -> Tuple[bool, list, float]:
        """Parse the AI response for PII detection."""
        detected = data.get("detected", False)
        pii_types = data.get("pii_types", [])
        confidence = data.get("confidence", 0.0)
        return detected, pii_types, confidence

    def get_categories_field_name(self) -> str:
        """Get the field name for PII categories."""
        return "pii"
