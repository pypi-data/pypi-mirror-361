"""
Stinger - AI Guardrails Framework

A powerful, easy-to-use framework for safeguarding LLM applications with
comprehensive content filtering and moderation capabilities.
"""

__version__ = "0.1.0a5"
__author__ = "Stinger Team"

# Security audit trail
from .core import audit

# Configuration utilities
from .core.config import ConfigLoader

# Conversation abstraction
from .core.conversation import Conversation, Turn

# Core components for advanced usage
from .core.guardrail_interface import (
    GuardrailFactory,
    GuardrailInterface,
    GuardrailRegistry,
    GuardrailResult,
    GuardrailType,
)

# High-level API - the main way developers should use Stinger
from .core.pipeline import GuardrailPipeline, create_pipeline

# Common guardrail types for easy access
__all__ = [
    # High-level API
    "GuardrailPipeline",
    "create_pipeline",
    # Core components
    "GuardrailInterface",
    "GuardrailResult",
    "GuardrailType",
    "GuardrailRegistry",
    "GuardrailFactory",
    # Configuration
    "ConfigLoader",
    # Conversation abstraction
    "Conversation",
    "Turn",
    # Security audit trail
    "audit",
]
