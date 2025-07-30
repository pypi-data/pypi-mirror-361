"""
Pydantic models for API request/response validation.
"""

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class CheckRequest(BaseModel):
    """Request model for content checking."""

    text: str = Field(..., description="Text content to check")
    kind: Literal["prompt", "response"] = Field(
        "prompt", description="Type of content - user prompt or LLM response"
    )
    context: Optional[Dict[str, Any]] = Field(
        None, description="Optional context (userId, sessionId, etc.)"
    )
    preset: Optional[str] = Field("customer_service", description="Guardrail preset to use")


class CheckResponse(BaseModel):
    """Response model for content checking."""

    action: Literal["allow", "warn", "block"] = Field(..., description="Action to take")
    reasons: List[str] = Field(default_factory=list, description="Reasons for the action")
    warnings: List[str] = Field(default_factory=list, description="Non-blocking warnings")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class RulesResponse(BaseModel):
    """Response model for rules configuration."""

    preset: str = Field(..., description="Active preset name")
    guardrails: Dict[str, Any] = Field(..., description="Active guardrail configurations")
    version: str = Field(..., description="Configuration version")
