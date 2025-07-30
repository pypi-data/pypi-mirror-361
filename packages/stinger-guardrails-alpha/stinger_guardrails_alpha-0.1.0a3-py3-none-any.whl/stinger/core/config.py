import os
import re
from typing import Any, Dict, Optional

import jsonschema
import yaml

from ..utils.exceptions import ConfigurationError

CONFIG_SCHEMA = {
    "type": "object",
    "properties": {
        "version": {"type": "string"},
        "pipeline": {
            "type": "object",
            "properties": {
                "input": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "type": {
                                "type": "string",
                                "enum": [
                                    "keyword_block",
                                    "keyword_list",
                                    "regex_filter",
                                    "length_filter",
                                    "url_filter",
                                    "pass_through",
                                    "content_moderation",
                                    "prompt_injection",
                                    "simple_pii_detection",
                                    "ai_pii_detection",
                                    "simple_toxicity_detection",
                                    "ai_toxicity_detection",
                                    "simple_code_generation",
                                    "ai_code_generation",
                                ],
                            },
                            "enabled": {"type": "boolean"},
                            "on_error": {
                                "type": "string",
                                "enum": ["block", "allow", "skip", "warn"],
                            },
                            "min_length": {"type": "integer"},
                            "max_length": {"type": "integer"},
                            "keyword": {"type": "string"},
                            "keywords": {
                                "oneOf": [
                                    {"type": "array", "items": {"type": "string"}},
                                    {"type": "string"},
                                ]
                            },
                            "keywords_file": {"type": "string"},
                            "keyword_files": {"type": "array", "items": {"type": "string"}},
                            "case_sensitive": {"type": "boolean"},
                            "patterns": {"type": "array", "items": {"type": "string"}},
                            "action": {"type": "string"},
                            "thresholds": {
                                "type": "object",
                                "properties": {
                                    "allow": {
                                        "type": "array",
                                        "items": {"type": "integer"},
                                        "minItems": 2,
                                        "maxItems": 2,
                                    },
                                    "warn": {
                                        "type": "array",
                                        "items": {"type": "integer"},
                                        "minItems": 2,
                                        "maxItems": 2,
                                    },
                                    "block": {
                                        "type": "array",
                                        "items": {"type": "integer"},
                                        "minItems": 2,
                                        "maxItems": 2,
                                    },
                                },
                            },
                            "rules": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "type": {
                                            "type": "string",
                                            "enum": [
                                                "regex",
                                                "keyword",
                                                "combination",
                                                "ai_scorer",
                                            ],
                                        },
                                        "certainty": {
                                            "type": "integer",
                                            "minimum": 1,
                                            "maximum": 100,
                                        },
                                        "description": {"type": "string"},
                                        "pattern": {"type": "string"},
                                        "keywords": {"type": "array", "items": {"type": "string"}},
                                        "logic": {"type": "string"},
                                        "case_sensitive": {"type": "boolean"},
                                    },
                                    "required": ["name", "type", "certainty", "description"],
                                },
                            },
                        },
                        "required": ["name", "type", "enabled", "on_error"],
                    },
                },
                "output": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "type": {
                                "type": "string",
                                "enum": [
                                    "keyword_block",
                                    "keyword_list",
                                    "regex_filter",
                                    "length_filter",
                                    "url_filter",
                                    "pass_through",
                                    "content_moderation",
                                    "prompt_injection",
                                    "simple_pii_detection",
                                    "ai_pii_detection",
                                    "simple_toxicity_detection",
                                    "ai_toxicity_detection",
                                    "simple_code_generation",
                                    "ai_code_generation",
                                ],
                            },
                            "enabled": {"type": "boolean"},
                            "on_error": {
                                "type": "string",
                                "enum": ["block", "allow", "skip", "warn"],
                            },
                            "min_length": {"type": "integer"},
                            "max_length": {"type": "integer"},
                            "keyword": {"type": "string"},
                            "keywords": {
                                "oneOf": [
                                    {"type": "array", "items": {"type": "string"}},
                                    {"type": "string"},
                                ]
                            },
                            "keywords_file": {"type": "string"},
                            "keyword_files": {"type": "array", "items": {"type": "string"}},
                            "case_sensitive": {"type": "boolean"},
                            "patterns": {"type": "array", "items": {"type": "string"}},
                            "action": {"type": "string"},
                            "thresholds": {
                                "type": "object",
                                "properties": {
                                    "allow": {
                                        "type": "array",
                                        "items": {"type": "integer"},
                                        "minItems": 2,
                                        "maxItems": 2,
                                    },
                                    "warn": {
                                        "type": "array",
                                        "items": {"type": "integer"},
                                        "minItems": 2,
                                        "maxItems": 2,
                                    },
                                    "block": {
                                        "type": "array",
                                        "items": {"type": "integer"},
                                        "minItems": 2,
                                        "maxItems": 2,
                                    },
                                },
                            },
                            "rules": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "type": {
                                            "type": "string",
                                            "enum": [
                                                "regex",
                                                "keyword",
                                                "combination",
                                                "ai_scorer",
                                            ],
                                        },
                                        "certainty": {
                                            "type": "integer",
                                            "minimum": 1,
                                            "maximum": 100,
                                        },
                                        "description": {"type": "string"},
                                        "pattern": {"type": "string"},
                                        "keywords": {"type": "array", "items": {"type": "string"}},
                                        "logic": {"type": "string"},
                                        "case_sensitive": {"type": "boolean"},
                                    },
                                    "required": ["name", "type", "certainty", "description"],
                                },
                            },
                        },
                        "required": ["name", "type", "enabled", "on_error"],
                    },
                },
            },
            "required": ["input"],
        },
    },
    "required": ["version", "pipeline"],
}


class ConfigLoader:
    def __init__(self):
        self.config = None

    def _substitute_env_vars(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively substitute environment variables in config."""
        if isinstance(config, dict):
            return {k: self._substitute_env_vars(v) for k, v in config.items()}
        elif isinstance(config, list):
            return [self._substitute_env_vars(item) for item in config]
        elif isinstance(config, str):
            # Replace ${VAR} with environment variable values
            def replace_var(match):
                var_name = match.group(1)
                value = os.getenv(var_name)
                if value is None:
                    raise ConfigurationError(f"Environment variable {var_name} not set")
                return value

            return re.sub(r"\$\{([^}]+)\}", replace_var, config)
        return config

    def load(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file and validate against schema."""
        try:
            with open(config_path, "r") as f:
                self.config = yaml.safe_load(f)

            if not self.config:
                raise ConfigurationError("Empty configuration file")

            # Substitute environment variables
            self.config = self._substitute_env_vars(self.config)

            # Schema validation
            try:
                jsonschema.validate(instance=self.config, schema=CONFIG_SCHEMA)
            except jsonschema.ValidationError as e:
                # Try to provide line number if possible
                msg = f"Config schema validation error: {e.message}"
                if e.path:
                    msg += f" at {list(e.path)}"
                raise ConfigurationError(msg)

            return self.config

        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML: {str(e)}")
        except FileNotFoundError:
            raise ConfigurationError(f"Configuration file not found: {config_path}")

    def get_pipeline_config(self, pipeline_type: str = "input") -> list:
        """Get pipeline configuration for specified type."""
        if not self.config:
            raise ConfigurationError("No configuration loaded")

        pipeline = self.config.get("pipeline", {})
        return pipeline.get(pipeline_type, [])

    def build_filters(self, config: Optional[Dict[str, Any]] = None) -> list:
        """Build filter instances from configuration."""
        if config is None:
            if self.config is None:
                raise ConfigurationError("No configuration provided")
            config = self.config
        else:
            self.config = config  # Ensure get_pipeline_config works

        from ..guardrails import GUARDRAIL_REGISTRY

        guardrails = []
        pipeline_config = self.get_pipeline_config("input")

        for guardrail_config in pipeline_config:
            guardrail_type = guardrail_config.get("type")
            if guardrail_type not in GUARDRAIL_REGISTRY:
                raise ConfigurationError(f"Unknown filter type: {guardrail_type}")

            filter_class = GUARDRAIL_REGISTRY[guardrail_type]
            guardrail_instance = filter_class(config=guardrail_config)
            guardrails.append(guardrail_instance)

        return guardrails
