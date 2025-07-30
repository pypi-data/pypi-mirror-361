"""
Simplified OpenAI Adapter

This module provides a clean adapter for OpenAI API services focused purely on
model communication without any guardrail-specific logic.
"""

import asyncio
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional

# Optional OpenAI import
try:
    from openai import AsyncOpenAI

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    AsyncOpenAI = None

logger = logging.getLogger(__name__)


@dataclass
class ModerationResult:
    """Result from OpenAI content moderation."""

    flagged: bool
    categories: Dict[str, bool]  # hate, harassment, self_harm, sexual, violence, etc.
    category_scores: Dict[str, float]
    confidence: float


@dataclass
class CompletionResult:
    """Result from OpenAI chat completion."""

    content: str
    model: str
    usage: Dict[str, int]
    finish_reason: str


@dataclass
class HealthStatus:
    """Health status of OpenAI services."""

    available: bool
    error_message: Optional[str] = None
    response_time_ms: Optional[float] = None


class OpenAIAdapter:
    """Simplified adapter for OpenAI API services - pure model communication only."""

    def __init__(self, api_key: str, base_url: Optional[str] = None):
        """Initialize the OpenAI adapter."""
        if not OPENAI_AVAILABLE or AsyncOpenAI is None:
            raise ImportError("OpenAI library not available. Install with: pip install openai")

        self.api_key = api_key
        self.base_url = base_url
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    async def moderate_content(self, content: str) -> ModerationResult:
        """Moderate content using OpenAI Moderation API."""
        try:
            response = await self.client.moderations.create(input=content)
            result = response.results[0]

            # Convert category scores to floats, replacing None with 0.0
            raw_scores = result.category_scores.model_dump()
            category_scores = {
                k: (float(v) if v is not None else 0.0) for k, v in raw_scores.items()
            }

            return ModerationResult(
                flagged=result.flagged,
                categories=result.categories.model_dump(),
                category_scores=category_scores,
                confidence=max(category_scores.values()) if category_scores else 0.0,
            )
        except Exception as e:
            logger.error(f"OpenAI moderation failed: {e}")
            raise

    async def complete(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4o-mini",
        temperature: float = 0.1,
        max_tokens: int = 500,
        **kwargs,
    ) -> CompletionResult:
        """Generate a chat completion using OpenAI API."""
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )

            choice = response.choices[0]
            return CompletionResult(
                content=choice.message.content or "",
                model=response.model,
                usage=response.usage.model_dump() if response.usage else {},
                finish_reason=choice.finish_reason or "unknown",
            )
        except Exception as e:
            logger.error(f"OpenAI completion failed: {e}")
            raise

    async def health_check(self) -> HealthStatus:
        """Check OpenAI API health and availability."""
        try:
            start_time = asyncio.get_event_loop().time()

            # Simple test call to check API connectivity
            await self.complete(messages=[{"role": "user", "content": "test"}], max_tokens=5)

            end_time = asyncio.get_event_loop().time()
            response_time_ms = (end_time - start_time) * 1000

            return HealthStatus(available=True, response_time_ms=response_time_ms)
        except Exception as e:
            return HealthStatus(available=False, error_message=str(e))

    def get_models(self) -> List[str]:
        """Get list of available models."""
        return ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"]
