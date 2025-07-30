"""
Centralized Model Configuration System

This module provides a unified abstraction for AI models across all guardrails,
ensuring consistent model usage and configuration management.
"""

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


class ModelError(Exception):
    """Exception raised for model-related errors."""


class ModelProvider(ABC):
    """Abstract interface for model providers."""

    @abstractmethod
    async def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate a response from the model."""

    @abstractmethod
    def get_model_name(self) -> str:
        """Get the name of the model being used."""

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the model is available."""


class OpenAIModelProvider(ModelProvider):
    """OpenAI model provider implementation."""

    def __init__(self, model_name: str, api_key: str, **kwargs):
        self.model_name = model_name
        self.client = AsyncOpenAI(api_key=api_key)
        self.temperature = kwargs.get("temperature", 0.1)
        self.max_tokens = kwargs.get("max_tokens", 500)
        self.timeout = kwargs.get("timeout", 30)

    async def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate a response using OpenAI API."""
        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant. Respond only with valid JSON.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=kwargs.get("temperature", self.temperature),
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            raise ModelError(f"OpenAI API error: {e}")

    def get_model_name(self) -> str:
        return self.model_name

    def is_available(self) -> bool:
        return self.client is not None


class ModelFactory:
    """Factory for creating model providers."""

    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            # Use path relative to this file
            config_path = Path(__file__).parent / "configs" / "models.yaml"
        self.config = self._load_config(config_path)

    def _load_config(self, config_path: Any) -> Dict[str, Any]:
        """Load model configuration from YAML file."""
        try:
            with open(str(config_path), "r") as f:
                config = yaml.safe_load(f)
                if isinstance(config, dict) and "models" in config:
                    return config["models"]
                return config
        except Exception as e:
            logger.warning(f"Failed to load model config from {config_path}: {e}")
            # Fallback to default configuration
            return {
                "default": "gpt-4.1-nano",
                "guardrails": {
                    "content_moderation": "gpt-4.1-nano",
                    "prompt_injection": "gpt-4.1-nano",
                    "pii_detection": "gpt-4.1-nano",
                    "toxicity_detection": "gpt-4.1-nano",
                    "code_generation": "gpt-4.1-nano",
                },
                "settings": {"temperature": 0.1, "max_tokens": 500, "timeout": 30},
            }

    def create_model_provider(self, guardrail_type: str, api_key: str) -> ModelProvider:
        """Create a model provider for a specific guardrail type."""
        # Check both 'guardrails' and 'filters' for backward compatibility
        guardrails_config = self.config.get("guardrails", self.config.get("filters", {}))
        model_name = guardrails_config.get(guardrail_type, self.config["default"])
        settings = self.config.get("settings", {})

        return OpenAIModelProvider(model_name=model_name, api_key=api_key, **settings)

    def get_model_name(self, guardrail_type: str) -> str:
        """Get the model name for a specific guardrail type."""
        # Check both 'guardrails' and 'filters' for backward compatibility
        guardrails_config = self.config.get("guardrails", self.config.get("filters", {}))
        return guardrails_config.get(guardrail_type, self.config["default"])

    def get_settings(self) -> Dict[str, Any]:
        """Get the global model settings."""
        return self.config["settings"].copy()
