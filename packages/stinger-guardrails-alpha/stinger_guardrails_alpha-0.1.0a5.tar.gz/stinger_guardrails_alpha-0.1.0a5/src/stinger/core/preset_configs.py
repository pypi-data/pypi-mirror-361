"""
Preset configurations for common guardrail use cases.

This module provides ready-to-use configurations for typical scenarios
like content moderation, customer service, medical applications, etc.
"""

from pathlib import Path
from typing import Any, Dict


class PresetConfigs:
    """Collection of preset configurations for common use cases."""

    @staticmethod
    def basic_pipeline() -> Dict[str, Any]:
        """Create a basic pipeline configuration with common guardrails."""
        return {
            "version": "1.0",
            "pipeline": {
                "input": [
                    {
                        "name": "toxicity_check",
                        "type": "simple_toxicity_detection",
                        "enabled": True,
                        "on_error": "block",
                    },
                    {
                        "name": "pii_check",
                        "type": "simple_pii_detection",
                        "enabled": True,
                        "on_error": "warn",
                    },
                    {
                        "name": "code_generation_check",
                        "type": "simple_code_generation",
                        "enabled": True,
                        "on_error": "block",
                    },
                ],
                "output": [
                    {
                        "name": "toxicity_check",
                        "type": "simple_toxicity_detection",
                        "enabled": True,
                        "on_error": "block",
                    },
                    {
                        "name": "pii_check",
                        "type": "simple_pii_detection",
                        "enabled": True,
                        "on_error": "warn",
                    },
                    {
                        "name": "code_generation_check",
                        "type": "simple_code_generation",
                        "enabled": True,
                        "on_error": "block",
                    },
                ],
            },
        }

    @staticmethod
    def content_moderation_pipeline() -> Dict[str, Any]:
        """Create a content moderation pipeline for social media/content platforms."""
        return {
            "version": "1.0",
            "pipeline": {
                "input": [
                    {
                        "name": "toxicity_check",
                        "type": "simple_toxicity_detection",
                        "enabled": True,
                        "on_error": "block",
                        "config": {
                            "categories": [
                                "hate_speech",
                                "harassment",
                                "threats",
                                "sexual_harassment",
                            ],
                            "confidence_threshold": 0.7,
                        },
                    },
                    {
                        "name": "profanity_filter",
                        "type": "keyword_list",
                        "enabled": True,
                        "on_error": "warn",
                        "config": {"keywords": ["profanity", "slurs"], "case_sensitive": False},
                    },
                    {
                        "name": "length_check",
                        "type": "length_filter",
                        "enabled": True,
                        "on_error": "warn",
                        "config": {"max_length": 1000, "min_length": 1},
                    },
                ],
                "output": [
                    {
                        "name": "toxicity_check",
                        "type": "simple_toxicity_detection",
                        "enabled": True,
                        "on_error": "block",
                    },
                    {
                        "name": "pii_check",
                        "type": "simple_pii_detection",
                        "enabled": True,
                        "on_error": "warn",
                    },
                ],
            },
        }

    @staticmethod
    def customer_service_pipeline() -> Dict[str, Any]:
        """Create a customer service pipeline for support interactions."""
        return {
            "version": "1.0",
            "pipeline": {
                "input": [
                    {
                        "name": "pii_check",
                        "type": "simple_pii_detection",
                        "enabled": True,
                        "on_error": "block",
                        "config": {"confidence_threshold": 0.6},
                    },
                    {
                        "name": "toxicity_check",
                        "type": "simple_toxicity_detection",
                        "enabled": True,
                        "on_error": "warn",
                        "config": {
                            "categories": ["harassment", "threats"],
                            "confidence_threshold": 0.8,
                        },
                    },
                    {
                        "name": "length_check",
                        "type": "length_filter",
                        "enabled": True,
                        "on_error": "warn",
                        "config": {"max_length": 2000, "min_length": 1},
                    },
                ],
                "output": [
                    {
                        "name": "pii_check",
                        "type": "simple_pii_detection",
                        "enabled": True,
                        "on_error": "block",
                    },
                    {
                        "name": "code_generation_check",
                        "type": "simple_code_generation",
                        "enabled": True,
                        "on_error": "block",
                    },
                ],
            },
        }

    @staticmethod
    def medical_pipeline() -> Dict[str, Any]:
        """Create a medical pipeline for healthcare applications."""
        return {
            "version": "1.0",
            "pipeline": {
                "input": [
                    {
                        "name": "pii_check",
                        "type": "simple_pii_detection",
                        "enabled": True,
                        "on_error": "block",
                    },
                    {
                        "name": "medical_identifiers",
                        "type": "regex_filter",
                        "enabled": True,
                        "on_error": "warn",
                        "config": {
                            "patterns": [
                                r"\b\d{9}\b",  # SSN
                                r"\b[A-Z]{2}-\d{6}\b",  # Medical record numbers
                                r"\bRX-\d{6}\b",  # Prescription numbers
                            ]
                        },
                    },
                    {
                        "name": "length_check",
                        "type": "length_filter",
                        "enabled": True,
                        "on_error": "warn",
                        "config": {"max_length": 5000, "min_length": 1},
                    },
                ],
                "output": [
                    {
                        "name": "pii_check",
                        "type": "simple_pii_detection",
                        "enabled": True,
                        "on_error": "block",
                    },
                    {
                        "name": "medical_advice_filter",
                        "type": "keyword_list",
                        "enabled": True,
                        "on_error": "warn",
                        "config": {
                            "keywords": ["diagnose", "prescribe", "treatment", "medical advice"],
                            "case_sensitive": False,
                        },
                    },
                ],
            },
        }

    @staticmethod
    def educational_pipeline() -> Dict[str, Any]:
        """Create an educational pipeline for learning platforms."""
        return {
            "version": "1.0",
            "pipeline": {
                "input": [
                    {
                        "name": "toxicity_check",
                        "type": "simple_toxicity_detection",
                        "enabled": True,
                        "on_error": "block",
                        "config": {
                            "categories": [
                                "hate_speech",
                                "harassment",
                                "violence",
                                "sexual_harassment",
                            ],
                            "confidence_threshold": 0.6,
                        },
                    },
                    {
                        "name": "pii_check",
                        "type": "simple_pii_detection",
                        "enabled": True,
                        "on_error": "warn",
                    },
                    {
                        "name": "length_check",
                        "type": "length_filter",
                        "enabled": True,
                        "on_error": "warn",
                        "config": {"max_length": 3000, "min_length": 1},
                    },
                ],
                "output": [
                    {
                        "name": "toxicity_check",
                        "type": "simple_toxicity_detection",
                        "enabled": True,
                        "on_error": "block",
                    },
                    {
                        "name": "pii_check",
                        "type": "simple_pii_detection",
                        "enabled": True,
                        "on_error": "block",
                    },
                    {
                        "name": "code_generation_check",
                        "type": "simple_code_generation",
                        "enabled": True,
                        "on_error": "warn",
                    },
                ],
            },
        }

    @staticmethod
    def financial_pipeline() -> Dict[str, Any]:
        """Create a financial pipeline for banking/financial applications."""
        return {
            "version": "1.0",
            "pipeline": {
                "input": [
                    {
                        "name": "pii_check",
                        "type": "simple_pii_detection",
                        "enabled": True,
                        "on_error": "block",
                    },
                    {
                        "name": "financial_identifiers",
                        "type": "regex_filter",
                        "enabled": True,
                        "on_error": "warn",
                        "config": {
                            "patterns": [
                                r"\b\d{4}-\d{4}-\d{4}-\d{4}\b",  # Credit card
                                r"\b\d{9}\b",  # SSN
                                r"\b\d{3}-\d{2}-\d{4}\b",  # SSN with dashes
                                r"\b\d{10,11}\b",  # Account numbers
                            ]
                        },
                    },
                    {
                        "name": "length_check",
                        "type": "length_filter",
                        "enabled": True,
                        "on_error": "warn",
                        "config": {"max_length": 2000, "min_length": 1},
                    },
                    {
                        "name": "prompt_injection",
                        "type": "prompt_injection",
                        "enabled": True,
                        "on_error": "block",
                        "config": {
                            "risk_threshold": 60,
                            "block_levels": ["medium", "high", "critical"],
                        },
                    },
                ],
                "output": [
                    {
                        "name": "pii_check",
                        "type": "simple_pii_detection",
                        "enabled": True,
                        "on_error": "block",
                    },
                    {
                        "name": "financial_advice_filter",
                        "type": "keyword_list",
                        "enabled": True,
                        "on_error": "warn",
                        "config": {
                            "keywords": [
                                "invest",
                                "buy",
                                "sell",
                                "financial advice",
                                "investment advice",
                            ],
                            "case_sensitive": False,
                        },
                    },
                ],
            },
        }

    @staticmethod
    def get_available_presets() -> Dict[str, str]:
        """Get available preset configurations with descriptions."""
        return {
            "basic": "Basic pipeline with toxicity, PII, and code generation checks",
            "content_moderation": "Content moderation for social media platforms",
            "customer_service": "Customer service with PII and toxicity checks",
            "medical": "Medical pipeline with strict PII protection",
            "educational": "Educational platform with safety and learning checks",
            "financial": "Financial pipeline with strict PII and financial data protection",
        }

    @staticmethod
    def get_preset(name: str) -> Dict[str, Any]:
        """Get a specific preset configuration by name."""
        presets = {
            "basic": PresetConfigs.basic_pipeline,
            "content_moderation": PresetConfigs.content_moderation_pipeline,
            "customer_service": PresetConfigs.customer_service_pipeline,
            "medical": PresetConfigs.medical_pipeline,
            "educational": PresetConfigs.educational_pipeline,
            "financial": PresetConfigs.financial_pipeline,
        }

        if name not in presets:
            available = list(presets.keys())
            raise ValueError(f"Unknown preset '{name}'. Available presets: {available}")

        return presets[name]()

    @staticmethod
    def save_preset(config: Dict[str, Any], filename: str) -> None:
        """Save a preset configuration to a file."""
        import yaml

        config_dir = Path("configs")
        config_dir.mkdir(exist_ok=True)

        config_path = config_dir / filename
        with open(config_path, "w") as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)
