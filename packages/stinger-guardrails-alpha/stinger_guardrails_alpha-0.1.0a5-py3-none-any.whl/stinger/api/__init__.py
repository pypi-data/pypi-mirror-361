"""
Stinger API Service

REST API for Stinger Guardrails Framework, enabling remote clients
like browser extensions to use guardrail functionality.
"""

from stinger.api.app import app

__all__ = ["app"]
