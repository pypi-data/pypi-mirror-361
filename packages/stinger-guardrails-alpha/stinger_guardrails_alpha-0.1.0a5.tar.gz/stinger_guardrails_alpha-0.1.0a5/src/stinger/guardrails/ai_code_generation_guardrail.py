"""
AI-Based Code Generation Filter

This module provides an AI-based code generation detection filter using the BaseAIGuardrail
with centralized model configuration.
"""

import logging
from typing import Any, Dict, Tuple

from ..core.guardrail_interface import GuardrailType
from .base_ai_guardrail import BaseAIGuardrail

logger = logging.getLogger(__name__)


class AICodeGenerationGuardrail(BaseAIGuardrail):
    """AI-based code generation detection filter using centralized model configuration."""

    # Code generation detection prompt template
    CODE_PROMPT = """
You are a security analyst specializing in code injection detection. Analyze the following text and determine if it contains code generation or injection attempts.

Code generation/injection includes:
- Programming code blocks
- Code snippets and functions
- System commands and scripts
- Database queries
- File operations
- Code execution attempts

Respond with a JSON object containing:
- "detected": boolean (true if code generation detected)
- "code_types": array of strings (types of code found)
- "confidence": float (0.0 to 1.0)
- "details": string (brief explanation)

Text to analyze: {content}
"""

    def __init__(self, name: str, config: Dict[str, Any]):
        """Initialize the AI code generation filter."""
        super().__init__(
            name=name,
            guardrail_type=GuardrailType.CODE_GENERATION,
            config=config,
            default_confidence_threshold=0.6,
            default_on_error="warn",
        )

    def get_analysis_prompt(self) -> str:
        """Get the code generation detection prompt template."""
        return self.CODE_PROMPT

    def parse_ai_response(self, data: Dict[str, Any]) -> Tuple[bool, list, float]:
        """Parse the AI response for code generation detection."""
        detected = data.get("detected", False)
        code_types = data.get("code_types", [])
        confidence = data.get("confidence", 0.0)
        return detected, code_types, confidence

    def get_categories_field_name(self) -> str:
        """Get the field name for code categories."""
        return "code"
