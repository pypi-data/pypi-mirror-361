"""
AI-Based Toxicity Detection Filter

This module provides an AI-based toxicity detection filter using the BaseAIGuardrail
with centralized model configuration.
"""

import logging
from typing import Any, Dict, Tuple

from ..core.guardrail_interface import GuardrailType
from .base_ai_guardrail import BaseAIGuardrail

logger = logging.getLogger(__name__)


class AIToxicityDetectionGuardrail(BaseAIGuardrail):
    """AI-based toxicity detection filter using centralized model configuration."""

    # Toxicity detection prompt template
    TOXICITY_PROMPT = """
You are a content moderation specialist. Analyze the following text for toxic content.

Toxic content includes:
- Hate speech and discrimination
- Harassment and bullying
- Threats and violence
- Sexual harassment
- Explicit or inappropriate content

Respond with a JSON object containing:
- "detected": boolean (true if toxic content detected)
- "toxicity_types": array of strings (types of toxicity found)
- "confidence": float (0.0 to 1.0)
- "details": string (brief explanation)

Text to analyze: {content}
"""

    def __init__(self, name: str, config: Dict[str, Any]):
        """Initialize the AI toxicity detection filter."""
        super().__init__(
            name=name,
            guardrail_type=GuardrailType.TOXICITY_DETECTION,
            config=config,
            default_confidence_threshold=0.7,
            default_on_error="allow",
        )

    def get_analysis_prompt(self) -> str:
        """Get the toxicity detection prompt template."""
        return self.TOXICITY_PROMPT

    def parse_ai_response(self, data: Dict[str, Any]) -> Tuple[bool, list, float]:
        """Parse the AI response for toxicity detection."""
        detected = data.get("detected", False)
        toxicity_types = data.get("toxicity_types", [])
        confidence = data.get("confidence", 0.0)
        return detected, toxicity_types, confidence

    def get_categories_field_name(self) -> str:
        """Get the field name for toxicity categories."""
        return "toxicity"
