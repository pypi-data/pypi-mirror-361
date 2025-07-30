"""
High-Level Guardrail Pipeline API

This module provides a simple, developer-friendly API for using guardrails
without dealing with async complexity or low-level configuration.
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, TypedDict, Union

# Exceptions imported but kept for potential future use
from . import audit
from .config import ConfigLoader
from .conversation import Conversation, Turn
from .guardrail_interface import (
    GuardrailFactory,
    GuardrailInterface,
    GuardrailRegistry,
)
from .input_validation import (
    ResourceExhaustionError,
    ValidationError,
    validate_input_content,
    validate_system_resources,
)
from .preset_configs import PresetConfigs
from .rate_limiter import get_global_rate_limiter

logger = logging.getLogger(__name__)


class PipelineResult(TypedDict):
    """Type definition for guardrail check results."""

    blocked: bool
    warnings: List[str]
    reasons: List[str]
    details: Dict[str, Any]
    pipeline_type: str
    conversation_id: Optional[str]


class PipelineStatus(TypedDict):
    """Type definition for pipeline status information."""

    input_guardrails: List[Dict[str, Any]]
    output_guardrails: List[Dict[str, Any]]
    total_enabled: int
    total_disabled: int


class GuardrailPipeline:
    """
    High-level API for using guardrails with a simple, synchronous interface.

    This class provides a developer-friendly way to:
    - Load configurations from YAML files or use preset configurations
    - Run content through input and output guardrails
    - Get clear, actionable results
    - Handle errors gracefully
    - Support optional conversation context for multi-turn scenarios

    Example:
        ```python
        from stinger import GuardrailPipeline, Conversation

        # Create pipeline from preset
        pipeline = GuardrailPipeline.from_preset("customer_service")

        # Or create from config file
        pipeline = GuardrailPipeline("config.yaml")

        # Check input content (single-turn)
        result = pipeline.check_input("Hello, world!")
        if result['blocked']:
            print(f"Input blocked: {result['reasons']}")

        # Check input content with conversation context
        conversation = Conversation("user_123")
        result = pipeline.check_input("Hello, world!", conversation=conversation)
        if result['blocked']:
            print(f"Input blocked: {result['reasons']}")

        # Check output content
        result = pipeline.check_output("Here's your response...")
        if result['blocked']:
            print(f"Output blocked: {result['reasons']}")
        ```
    """

    def __init__(self, config_path: Optional[Union[str, Path]] = None) -> None:
        """
        Initialize the guardrail pipeline.

        Args:
            config_path: Path to YAML configuration file. If None, uses default config.

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config file is invalid
            RuntimeError: If pipeline initialization fails
        """
        try:
            self.config_loader = ConfigLoader()
            self.registry = GuardrailRegistry()
            self.factory = GuardrailFactory(self.registry)

            # Register all available guardrail factories
            from .guardrail_factory import register_all_factories

            register_all_factories(self.registry)

            # Load configuration
            if config_path:
                config_path = Path(config_path)
                if not config_path.exists():
                    raise FileNotFoundError(f"Configuration file not found: {config_path}")
                self.config = self.config_loader.load(str(config_path))
            else:
                # Use default config
                default_config_path = Path(__file__).parent / "configs" / "models.yaml"
                if not default_config_path.exists():
                    raise FileNotFoundError(
                        f"Default configuration file not found: {default_config_path}"
                    )
                self.config = self.config_loader.load(str(default_config_path))

            # Build pipelines
            self.input_pipeline = self._build_pipeline("input")
            self.output_pipeline = self._build_pipeline("output")

            self.global_rate_limiter = get_global_rate_limiter()

            logger.info(
                f"GuardrailPipeline initialized with {len(self.input_pipeline)} input and {len(self.output_pipeline)} output guardrails"
            )

        except Exception as e:
            logger.error(f"Failed to initialize GuardrailPipeline: {e}")
            raise RuntimeError(f"Pipeline initialization failed: {e}") from e

    @classmethod
    def from_preset(cls, preset_name: str) -> "GuardrailPipeline":
        """
        Create a pipeline from a preset configuration.

        Args:
            preset_name: Name of the preset configuration

        Returns:
            Configured GuardrailPipeline instance

        Raises:
            ValueError: If preset name is invalid
            RuntimeError: If pipeline initialization fails
        """
        try:
            # Get preset configuration
            preset_config = PresetConfigs.get_preset(preset_name)

            # Create temporary config file
            import tempfile

            import yaml

            with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
                yaml.dump(preset_config, f)
                temp_config_path = f.name

            # Create pipeline from temp config
            pipeline = cls(temp_config_path)

            # Clean up temp file
            Path(temp_config_path).unlink()

            logger.info(f"Created pipeline from preset: {preset_name}")
            return pipeline

        except Exception as e:
            logger.error(f"Failed to create pipeline from preset '{preset_name}': {e}")
            raise RuntimeError(f"Preset pipeline creation failed: {e}") from e

    @classmethod
    def get_available_presets(cls) -> Dict[str, str]:
        """
        Get available preset configurations.

        Returns:
            Dictionary mapping preset names to descriptions
        """
        return PresetConfigs.get_available_presets()

    @classmethod
    def save_preset_config(cls, preset_name: str, filename: str) -> None:
        """
        Save a preset configuration to a file.

        Args:
            preset_name: Name of the preset to save
            filename: Output filename

        Raises:
            ValueError: If preset name is invalid
        """
        try:
            preset_config = PresetConfigs.get_preset(preset_name)
            PresetConfigs.save_preset(preset_config, filename)
            logger.info(f"Saved preset '{preset_name}' to {filename}")
        except Exception as e:
            logger.error(f"Failed to save preset '{preset_name}': {e}")
            raise

    def _build_pipeline(self, pipeline_type: str) -> List[GuardrailInterface]:
        """
        Build a pipeline from configuration.

        Args:
            pipeline_type: Type of pipeline ('input' or 'output')

        Returns:
            List of configured guardrail instances

        Raises:
            ValueError: If pipeline_type is invalid
        """
        if pipeline_type not in ["input", "output"]:
            raise ValueError(f"Invalid pipeline type: {pipeline_type}. Must be 'input' or 'output'")

        pipeline_configs = self.config.get("pipeline", {}).get(pipeline_type, [])
        pipeline = []

        for config in pipeline_configs:
            try:
                guardrail = self.factory.create_from_config(config)
                if guardrail:
                    pipeline.append(guardrail)
                    logger.debug(f"Added {pipeline_type} guardrail: {guardrail.name}")
                else:
                    logger.warning(
                        f"Failed to create {pipeline_type} guardrail from config: {config}"
                    )
            except Exception as e:
                # Log the error with full context but continue building pipeline
                guardrail_name = config.get("name", "unknown")
                guardrail_type = config.get("type", "unknown")
                logger.error(
                    f"Failed to create {pipeline_type} guardrail '{guardrail_name}' of type '{guardrail_type}': {e}"
                )
                logger.debug(f"Full config: {config}")
                # Continue processing other guardrails instead of failing completely

        return pipeline

    def check_input(
        self,
        content: str,
        conversation: Optional[Conversation] = None,
        api_key: Optional[str] = None,
        role: Optional[str] = None,
    ) -> PipelineResult:
        """
        Check input content through all input guardrails.

        Args:
            content: The input content to check
            conversation: Optional conversation context for multi-turn scenarios
            api_key: Optional API key for global rate limiting
            role: Optional user role for role-based overrides

        Returns:
            Dict with 'blocked', 'warnings', 'reasons', 'details', and 'conversation_id' keys

        Raises:
            ValueError: If content is None or empty
            RuntimeError: If pipeline execution fails
        """
        if content is None:
            raise ValueError("Content cannot be None")

        # Check global rate limits if API key provided
        if api_key:
            global_rate_result = self.global_rate_limiter.check_rate_limit(api_key, role=role)
            if global_rate_result["exceeded"]:
                return {
                    "blocked": True,
                    "warnings": [],
                    "reasons": [f"Global rate limit exceeded for API key {api_key}"],
                    "details": {"global_rate_limit": global_rate_result},
                    "pipeline_type": "input",
                    "conversation_id": conversation.conversation_id if conversation else None,
                }

            # Record the request
            self.global_rate_limiter.record_request(api_key)

        # Check conversation rate limits if provided
        if conversation and conversation.check_rate_limit():
            return {
                "blocked": True,
                "warnings": [],
                "reasons": [f"Rate limit exceeded for conversation {conversation.conversation_id}"],
                "details": {"rate_limit": "exceeded"},
                "pipeline_type": "input",
                "conversation_id": conversation.conversation_id,
            }

        # Add prompt to conversation if provided
        if conversation:
            conversation.add_prompt(content)

        # Log user prompt to audit trail
        request_id = getattr(conversation, "current_request_id", None) if conversation else None
        user_id = getattr(conversation, "initiator", None) if conversation else None
        conversation_id = conversation.conversation_id if conversation else None

        audit.log_prompt(
            prompt=content,
            user_id=user_id or "",
            conversation_id=conversation_id or "",
            request_id=request_id or "",
        )

        # Run pipeline and get results
        result = self._run_pipeline(self.input_pipeline, content, "input", conversation)

        # Annotate guardrail results into conversation if provided
        if conversation and conversation.turns:
            self._annotate_guardrail_results(conversation.turns[-1], result)

        return result

    def check_output(
        self,
        content: str,
        conversation: Optional[Conversation] = None,
        api_key: Optional[str] = None,
        role: Optional[str] = None,
    ) -> PipelineResult:
        """
        Check output content through all output guardrails.

        Args:
            content: The output content to check
            conversation: Optional conversation context for multi-turn scenarios
            api_key: Optional API key for global rate limiting
            role: Optional user role for role-based overrides

        Returns:
            Dict with 'blocked', 'warnings', 'reasons', 'details', and 'conversation_id' keys

        Raises:
            ValueError: If content is None or empty
            RuntimeError: If pipeline execution fails
        """
        if content is None:
            raise ValueError("Content cannot be None")

        # Check global rate limits if API key provided
        if api_key:
            global_rate_result = self.global_rate_limiter.check_rate_limit(api_key, role=role)
            if global_rate_result["exceeded"]:
                return {
                    "blocked": True,
                    "warnings": [],
                    "reasons": [f"Global rate limit exceeded for API key {api_key}"],
                    "details": {"global_rate_limit": global_rate_result},
                    "pipeline_type": "output",
                    "conversation_id": conversation.conversation_id if conversation else None,
                }

            # Record the request
            self.global_rate_limiter.record_request(api_key)

        # Check conversation rate limits if provided
        if conversation and conversation.check_rate_limit():
            return {
                "blocked": True,
                "warnings": [],
                "reasons": [f"Rate limit exceeded for conversation {conversation.conversation_id}"],
                "details": {"rate_limit": "exceeded"},
                "pipeline_type": "output",
                "conversation_id": conversation.conversation_id,
            }

        # Add response to conversation if provided
        if conversation:
            try:
                # Try to add response to the most recent incomplete turn
                conversation.add_response(content)
            except ValueError as e:
                # If no prompt-only turn exists, this is an error in the conversation flow
                # Log the error and create a new turn with empty prompt and the response
                logger.warning(
                    f"No prompt found for response in conversation {conversation.conversation_id}: {e}"
                )
                conversation.add_turn("", content)

        # Log LLM response to audit trail
        request_id = getattr(conversation, "current_request_id", None) if conversation else None
        user_id = getattr(conversation, "initiator", None) if conversation else None
        conversation_id = conversation.conversation_id if conversation else None

        audit.log_response(
            response=content,
            user_id=user_id or "",
            conversation_id=conversation_id or "",
            request_id=request_id or "",
        )

        # Run pipeline and get results
        result = self._run_pipeline(self.output_pipeline, content, "output", conversation)

        # Annotate guardrail results into conversation if provided
        if conversation and conversation.turns:
            self._annotate_guardrail_results(conversation.turns[-1], result)

        return result

    async def check_input_async(
        self,
        content: str,
        conversation: Optional[Conversation] = None,
        api_key: Optional[str] = None,
        role: Optional[str] = None,
    ) -> PipelineResult:
        """
        Async version of check_input - Check input content through all input guardrails.

        Args:
            content: The input content to check
            conversation: Optional conversation context for multi-turn scenarios
            api_key: Optional API key for global rate limiting
            role: Optional user role for role-based overrides

        Returns:
            Dict with 'blocked', 'warnings', 'reasons', 'details', and 'conversation_id' keys

        Raises:
            ValueError: If content is None or empty
            RuntimeError: If pipeline execution fails
        """
        if content is None:
            raise ValueError("Content cannot be None")

        # Validate input content and system resources
        try:
            validate_input_content(content, "input")
            validate_system_resources()
        except (ValidationError, ResourceExhaustionError) as e:
            from .error_handling import safe_error_message

            safe_msg = safe_error_message(e, "input validation")
            return PipelineResult(
                blocked=True,
                warnings=[safe_msg],
                reasons=[safe_msg],
                details={"validation_error": safe_msg},
                pipeline_type="input",
                conversation_id=conversation.id if conversation else None,
            )

        # Check global rate limits if API key provided
        if api_key:
            global_rate_result = self.global_rate_limiter.check_rate_limit(api_key, role=role)
            if global_rate_result["exceeded"]:
                return {
                    "blocked": True,
                    "warnings": [],
                    "reasons": [f"Global rate limit exceeded for API key {api_key}"],
                    "details": {"global_rate_limit": global_rate_result},
                    "pipeline_type": "input",
                    "conversation_id": conversation.conversation_id if conversation else None,
                }

            # Record the request
            self.global_rate_limiter.record_request(api_key)

        # Check conversation rate limits if provided
        if conversation and conversation.check_rate_limit():
            return {
                "blocked": True,
                "warnings": [],
                "reasons": [f"Rate limit exceeded for conversation {conversation.conversation_id}"],
                "details": {"rate_limit": "exceeded"},
                "pipeline_type": "input",
                "conversation_id": conversation.conversation_id,
            }

        # Add prompt to conversation if provided
        if conversation:
            conversation.add_prompt(content)

        # Log user prompt to audit trail
        request_id = getattr(conversation, "current_request_id", None) if conversation else None
        user_id = getattr(conversation, "initiator", None) if conversation else None
        conversation_id = conversation.conversation_id if conversation else None

        audit.log_prompt(
            prompt=content,
            user_id=user_id or "",
            conversation_id=conversation_id or "",
            request_id=request_id or "",
        )

        # Run pipeline and get results
        result = await self._run_pipeline_async(self.input_pipeline, content, "input", conversation)

        # Annotate guardrail results into conversation if provided
        if conversation and conversation.turns:
            self._annotate_guardrail_results(conversation.turns[-1], result)

        return result

    async def check_output_async(
        self,
        content: str,
        conversation: Optional[Conversation] = None,
        api_key: Optional[str] = None,
        role: Optional[str] = None,
    ) -> PipelineResult:
        """
        Async version of check_output - Check output content through all output guardrails.

        Args:
            content: The output content to check
            conversation: Optional conversation context for multi-turn scenarios
            api_key: Optional API key for global rate limiting
            role: Optional user role for role-based overrides

        Returns:
            Dict with 'blocked', 'warnings', 'reasons', 'details', and 'conversation_id' keys

        Raises:
            ValueError: If content is None or empty
            RuntimeError: If pipeline execution fails
        """
        if content is None:
            raise ValueError("Content cannot be None")

        # Validate output content and system resources
        try:
            validate_input_content(content, "output")
            validate_system_resources()
        except (ValidationError, ResourceExhaustionError) as e:
            from .error_handling import safe_error_message

            safe_msg = safe_error_message(e, "output validation")
            return PipelineResult(
                blocked=True,
                warnings=[safe_msg],
                reasons=[safe_msg],
                details={"validation_error": safe_msg},
                pipeline_type="output",
                conversation_id=conversation.id if conversation else None,
            )

        # Check global rate limits if API key provided
        if api_key:
            global_rate_result = self.global_rate_limiter.check_rate_limit(api_key, role=role)
            if global_rate_result["exceeded"]:
                return {
                    "blocked": True,
                    "warnings": [],
                    "reasons": [f"Global rate limit exceeded for API key {api_key}"],
                    "details": {"global_rate_limit": global_rate_result},
                    "pipeline_type": "output",
                    "conversation_id": conversation.conversation_id if conversation else None,
                }

            # Record the request
            self.global_rate_limiter.record_request(api_key)

        # Check conversation rate limits if provided
        if conversation and conversation.check_rate_limit():
            return {
                "blocked": True,
                "warnings": [],
                "reasons": [f"Rate limit exceeded for conversation {conversation.conversation_id}"],
                "details": {"rate_limit": "exceeded"},
                "pipeline_type": "output",
                "conversation_id": conversation.conversation_id,
            }

        # Add response to conversation if provided
        if conversation:
            try:
                # Try to add response to the most recent incomplete turn
                conversation.add_response(content)
            except ValueError as e:
                # If no prompt-only turn exists, this is an error in the conversation flow
                # Log the error and create a new turn with empty prompt and the response
                logger.warning(
                    f"No prompt found for response in conversation {conversation.conversation_id}: {e}"
                )
                conversation.add_turn("", content)

        # Log LLM response to audit trail
        request_id = getattr(conversation, "current_request_id", None) if conversation else None
        user_id = getattr(conversation, "initiator", None) if conversation else None
        conversation_id = conversation.conversation_id if conversation else None

        audit.log_response(
            response=content,
            user_id=user_id or "",
            conversation_id=conversation_id or "",
            request_id=request_id or "",
        )

        # Run pipeline and get results
        result = await self._run_pipeline_async(
            self.output_pipeline, content, "output", conversation
        )

        # Annotate guardrail results into conversation if provided
        if conversation and conversation.turns:
            self._annotate_guardrail_results(conversation.turns[-1], result)

        return result

    def _annotate_guardrail_results(self, turn: Turn, result: PipelineResult) -> None:
        """
        Annotate guardrail results into turn metadata.

        Args:
            turn: The turn to annotate
            result: The pipeline result to annotate
        """
        # Store guardrail results in turn metadata
        turn.metadata.update(
            {
                "guardrail_results": {
                    "blocked": result["blocked"],
                    "warnings": result["warnings"],
                    "reasons": result["reasons"],
                    "details": result["details"],
                    "pipeline_type": result["pipeline_type"],
                    "timestamp": datetime.now().isoformat(),
                }
            }
        )

        # Log annotation
        logger.debug(
            f"Annotated guardrail results to turn in conversation {result['conversation_id']}: blocked={result['blocked']}"
        )

    def _run_pipeline(
        self,
        pipeline: List[GuardrailInterface],
        content: str,
        pipeline_type: str,
        conversation: Optional[Conversation] = None,
    ) -> PipelineResult:
        """
        Sync wrapper for pipeline execution.

        This method provides a synchronous interface to the async pipeline execution.
        It handles the async/sync boundary safely without creating thread safety issues.
        """
        try:
            # Check if we're already in an async context
            asyncio.get_running_loop()
        except RuntimeError:
            # No running loop, safe to create a new event loop
            # This is the normal case for sync calls
            return asyncio.run(
                self._run_pipeline_async(pipeline, content, pipeline_type, conversation)
            )
        else:
            # We're in an async context, but this is a sync method
            # This indicates incorrect usage - the caller should use the async version
            raise RuntimeError(
                f"Cannot call {pipeline_type} pipeline sync method from async context. "
                f"Use check_{pipeline_type}_async() instead."
            )

    async def _run_pipeline_async(
        self,
        pipeline: List[GuardrailInterface],
        content: str,
        pipeline_type: str,
        conversation: Optional[Conversation] = None,
    ) -> PipelineResult:
        """
        Run content through a pipeline of guardrails.

        Args:
            pipeline: List of guardrail instances
            content: Content to check
            pipeline_type: Type of pipeline for logging
            conversation: Optional conversation context

        Returns:
            Standardized result dictionary

        Raises:
            RuntimeError: If pipeline execution fails catastrophically
        """
        blocked = False
        warnings: List[str] = []
        reasons: List[str] = []
        details: Dict[str, Any] = {}
        conversation_id = conversation.conversation_id if conversation else None

        # Log conversation context if available
        if conversation:
            logger.info(
                f"Processing {pipeline_type} for conversation {conversation_id} (turn {conversation.get_turn_count()})"
            )

        for guardrail in pipeline:
            try:
                # Run the async analyze method properly
                result = await guardrail.analyze(content)

                if result.blocked:
                    blocked = True
                    reasons.append(f"{guardrail.name}: {result.reason}")

                # Check if this should be a warning - only if the original action was 'warn'
                original_action = result.details.get("action", "")
                if original_action == "warn":
                    warnings.append(f"{guardrail.name}: {result.reason}")

                # Store detailed results
                details[guardrail.name] = {
                    "blocked": result.blocked,
                    "confidence": result.confidence,
                    "reason": result.reason,
                    "details": result.details,
                }

                # Log guardrail decision to audit trail
                request_id = (
                    getattr(conversation, "current_request_id", None) if conversation else None
                )
                user_id = getattr(conversation, "initiator", None) if conversation else None

                # Determine decision type for audit based on original action
                original_action = result.details.get("action", "")
                if result.blocked:
                    decision = "block"
                elif original_action == "warn":
                    decision = "warn"
                else:
                    decision = "allow"

                audit.log_guardrail_decision(
                    guardrail_name=guardrail.name,
                    decision=decision,
                    reason=result.reason,
                    user_id=user_id or "",
                    conversation_id=conversation_id or "",
                    request_id=request_id or "",
                    confidence=result.confidence,
                    rule_triggered=getattr(result, "rule_triggered", None) or "",
                )

                # Log with conversation context if available
                if conversation:
                    logger.debug(
                        f"Guardrail {guardrail.name} result for conversation {conversation_id}: blocked={result.blocked}, confidence={result.confidence}"
                    )
                else:
                    logger.debug(
                        f"Guardrail {guardrail.name} result: blocked={result.blocked}, confidence={result.confidence}"
                    )

            except Exception as e:
                error_msg = f"Error running {guardrail.name} guardrail: {e}"
                if conversation:
                    error_msg += f" (conversation {conversation_id})"
                logger.error(error_msg)

                reasons.append(f"{guardrail.name}: Error - {str(e)}")
                details[guardrail.name] = {"error": str(e), "blocked": False, "confidence": 0.0}

                # Log error decision to audit trail
                request_id = (
                    getattr(conversation, "current_request_id", None) if conversation else None
                )
                user_id = getattr(conversation, "initiator", None) if conversation else None

                audit.log_guardrail_decision(
                    guardrail_name=guardrail.name,
                    decision="error",
                    reason=f"Error: {str(e)}",
                    user_id=user_id or "",
                    conversation_id=conversation_id or "",
                    request_id=request_id or "",
                    confidence=0.0,
                )

        return {
            "blocked": blocked,
            "warnings": warnings,
            "reasons": reasons,
            "details": details,
            "pipeline_type": pipeline_type,
            "conversation_id": conversation_id,
        }

    def get_guardrail_status(self) -> PipelineStatus:
        """
        Get status of all guardrails in the pipeline.

        Returns:
            Dictionary with guardrail status information
        """
        status: PipelineStatus = {
            "input_guardrails": [],
            "output_guardrails": [],
            "total_enabled": 0,
            "total_disabled": 0,
        }

        for guardrail in self.input_pipeline:
            status["input_guardrails"].append(
                {
                    "name": guardrail.name,
                    "type": guardrail.guardrail_type.value,
                    "enabled": guardrail.enabled,
                    "available": guardrail.is_available(),
                }
            )
            if guardrail.enabled:
                status["total_enabled"] += 1
            else:
                status["total_disabled"] += 1

        for guardrail in self.output_pipeline:
            status["output_guardrails"].append(
                {
                    "name": guardrail.name,
                    "type": guardrail.guardrail_type.value,
                    "enabled": guardrail.enabled,
                    "available": guardrail.is_available(),
                }
            )
            if guardrail.enabled:
                status["total_enabled"] += 1
            else:
                status["total_disabled"] += 1

        return status

    def enable_guardrail(self, name: str, pipeline_type: Optional[str] = None) -> bool:
        """
        Enable a specific guardrail by name.

        Args:
            name: Name of the guardrail to enable
            pipeline_type: Optional pipeline type ('input', 'output'). If None, enables all matching names.

        Returns:
            True if guardrail was found and enabled, False otherwise
        """
        found = False

        if pipeline_type is None or pipeline_type == "input":
            for guardrail in self.input_pipeline:
                if guardrail.name == name:
                    guardrail.enable()
                    logger.info(f"Enabled input guardrail: {name}")
                    found = True
                    if pipeline_type == "input":
                        break

        if pipeline_type is None or pipeline_type == "output":
            for guardrail in self.output_pipeline:
                if guardrail.name == name:
                    guardrail.enable()
                    logger.info(f"Enabled output guardrail: {name}")
                    found = True
                    if pipeline_type == "output":
                        break

        if not found:
            logger.warning(
                f"Guardrail not found: {name}"
                + (f" in {pipeline_type} pipeline" if pipeline_type else "")
            )
        return found

    def disable_guardrail(self, name: str, pipeline_type: Optional[str] = None) -> bool:
        """
        Disable a specific guardrail by name.

        Args:
            name: Name of the guardrail to disable
            pipeline_type: Optional pipeline type ('input', 'output'). If None, disables all matching names.

        Returns:
            True if guardrail was found and disabled, False otherwise
        """
        found = False

        if pipeline_type is None or pipeline_type == "input":
            for guardrail in self.input_pipeline:
                if guardrail.name == name:
                    guardrail.disable()
                    logger.info(f"Disabled input guardrail: {name}")
                    found = True
                    if pipeline_type == "input":
                        break

        if pipeline_type is None or pipeline_type == "output":
            for guardrail in self.output_pipeline:
                if guardrail.name == name:
                    guardrail.disable()
                    logger.info(f"Disabled output guardrail: {name}")
                    found = True
                    if pipeline_type == "output":
                        break

        if not found:
            logger.warning(
                f"Guardrail not found: {name}"
                + (f" in {pipeline_type} pipeline" if pipeline_type else "")
            )
        return found

    def get_guardrail_config(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get configuration of a specific guardrail.

        Args:
            name: Name of the guardrail

        Returns:
            Guardrail configuration or None if not found
        """
        for guardrail in self.input_pipeline + self.output_pipeline:
            if guardrail.name == name:
                return guardrail.get_config()
        return None

    def update_guardrail_config(self, name: str, config: Dict[str, Any]) -> bool:
        """
        Update configuration of a specific guardrail.

        Args:
            name: Name of the guardrail
            config: New configuration dictionary

        Returns:
            True if guardrail was found and updated, False otherwise
        """
        for guardrail in self.input_pipeline + self.output_pipeline:
            if guardrail.name == name:
                success = guardrail.update_config(config)
                if success:
                    logger.info(f"Updated guardrail config: {name}")
                else:
                    logger.error(f"Failed to update guardrail config: {name}")
                return success
        logger.warning(f"Guardrail not found: {name}")
        return False


# Convenience function for quick usage
def create_pipeline(config_path: Optional[Union[str, Path]] = None) -> GuardrailPipeline:
    """
    Create a guardrail pipeline with the given configuration.

    This is a convenience function for quick pipeline creation.

    Args:
        config_path: Path to YAML configuration file

    Returns:
        Configured GuardrailPipeline instance

    Example:
        ```python
        from stinger import create_pipeline

        pipeline = create_pipeline("my_config.yaml")
        result = pipeline.check_input("Hello, world!")
        ```
    """
    return GuardrailPipeline(config_path)
