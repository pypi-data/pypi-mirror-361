"""
Conversation Abstraction

This module provides a Conversation class for managing multi-turn conversations,
including rate limiting, logging context, and conversation history.
"""

import logging
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from .input_validation import ValidationError, validate_conversation_limits, validate_input_content

logger = logging.getLogger(__name__)


@dataclass
class Turn:
    """Represents a complete prompt-response exchange in a conversation."""

    timestamp: datetime
    prompt: str
    speaker: str  # Who said the prompt
    listener: str  # Who received the prompt
    response: Optional[str] = None  # None if response hasn't been generated yet
    speaker_type: str = "human"  # human, bot, agent, ai_model
    listener_type: str = "ai_model"  # human, bot, agent, ai_model
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if isinstance(self.timestamp, (int, float)):
            self.timestamp = datetime.fromtimestamp(self.timestamp)


class Conversation:
    """
    Manages a multi-turn conversation with rate limiting and logging context.

    This class provides:
    - Unique conversation ID for tracking
    - Participant tracking (initiator/responder with types)
    - Model information for AI conversations
    - Ordered conversation history (complete exchanges)
    - Per-conversation rate limiting
    - Metadata storage
    - Logging context for traceability

    Example:
        ```python
        # Simple human-AI conversation
        conv = Conversation.human_ai("user_123", "gpt-4")

        # Bot-to-bot conversation
        conv = Conversation.bot_to_bot("service_bot", "billing_bot")

        # Agent-to-agent conversation
        conv = Conversation.agent_to_agent("orchestrator", "specialist")

        # Custom conversation with simplified constructor
        conv = Conversation(
            initiator="user_123",
            responder="gpt-4",
            initiator_type="human",
            responder_type="ai_model"
        )

        # Add complete exchanges (turns)
        conv.add_exchange("Hello, how can I help?", "I'm here to assist you!")
        conv.add_exchange("I need help with my account", "What specific issue?")

        # Or add just a prompt (response will be added later)
        conv.add_prompt("What's your account number?")
        # Later...
        conv.add_response("My account is 123-45-6789")

        # Check rate limits
        if conv.check_rate_limit():
            print("Rate limit exceeded")

        # Get conversation history
        history = conv.get_history()
        ```
    """

    def __init__(
        self,
        initiator: Optional[str] = None,
        responder: Optional[str] = None,
        initiator_type: str = "human",
        responder_type: str = "ai_model",
        conversation_id: Optional[str] = None,
        model_info: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        rate_limit: Optional[Dict[str, int]] = None,
        # Legacy support
        participants: Optional[Dict[str, str]] = None,
    ):
        """
        Initialize a conversation with simplified parameters.

        Args:
            initiator: The initiator's identifier (required unless participants provided)
            responder: The responder's identifier (required unless participants provided)
            initiator_type: Type of initiator ('human', 'bot', 'agent', 'ai_model')
            responder_type: Type of responder ('human', 'bot', 'agent', 'ai_model')
            conversation_id: Unique conversation identifier. If None, generates UUID.
            model_info: Optional model information for AI conversations.
            metadata: Optional metadata dictionary.
            rate_limit: Optional rate limit configuration.
            participants: Legacy parameter for backward compatibility.
        """
        self.conversation_id = conversation_id or str(uuid.uuid4())
        self.metadata = metadata or {}
        self.turns: List[Turn] = []
        self.created_at = datetime.now()
        self.last_activity = self.created_at

        # Thread safety lock for state mutations
        self._lock = threading.Lock()

        # Rate limiting configuration
        self.rate_limit = rate_limit or {}
        self.rate_limit_turns: List[datetime] = []

        # Handle legacy participants parameter for backward compatibility
        if participants:
            self.participants = participants
            self.model_info = model_info or {}
            self.initiator = participants.get("initiator", "unknown")
            self.responder = participants.get("responder", "unknown")
            self.initiator_type = participants.get("initiator_type", "unknown")
            self.responder_type = participants.get("responder_type", "unknown")
        else:
            # New simplified approach - require initiator and responder
            if initiator is None or responder is None:
                raise ValueError(
                    "initiator and responder are required unless participants is provided"
                )

            self.participants = {
                "initiator": initiator,
                "responder": responder,
                "initiator_type": initiator_type,
                "responder_type": responder_type,
            }
            self.model_info = model_info or {}
            self.initiator = initiator
            self.responder = responder
            self.initiator_type = initiator_type
            self.responder_type = responder_type

        logger.info(
            f"Created conversation {self.conversation_id} between {self.initiator} ({self.initiator_type}) and {self.responder} ({self.responder_type})"
        )

    @classmethod
    def human_ai(
        cls, user_id: str, model_id: str, model_info: Optional[Dict[str, str]] = None, **kwargs
    ) -> "Conversation":
        """
        Create a human-to-AI conversation.

        Args:
            user_id: The human user's identifier
            model_id: The AI model's identifier
            model_info: Optional model information
            **kwargs: Additional arguments for Conversation constructor

        Returns:
            Conversation instance
        """
        if model_info is None:
            model_info = {}

        # Ensure model_id is always set
        model_info = model_info.copy()
        model_info["model_id"] = model_id

        # Set default provider if not specified
        if "provider" not in model_info:
            model_info["provider"] = "openai"

        return cls(
            initiator=user_id,
            responder=model_id,
            initiator_type="human",
            responder_type="ai_model",
            model_info=model_info,
            **kwargs,
        )

    @classmethod
    def bot_to_bot(cls, bot1_id: str, bot2_id: str, **kwargs) -> "Conversation":
        """
        Create a bot-to-bot conversation.

        Args:
            bot1_id: First bot's identifier
            bot2_id: Second bot's identifier
            **kwargs: Additional arguments for Conversation constructor

        Returns:
            Conversation instance
        """
        return cls(
            initiator=bot1_id,
            responder=bot2_id,
            initiator_type="bot",
            responder_type="bot",
            **kwargs,
        )

    @classmethod
    def agent_to_agent(cls, agent1_id: str, agent2_id: str, **kwargs) -> "Conversation":
        """
        Create an agent-to-agent conversation.

        Args:
            agent1_id: First agent's identifier
            agent2_id: Second agent's identifier
            **kwargs: Additional arguments for Conversation constructor

        Returns:
            Conversation instance
        """
        return cls(
            initiator=agent1_id,
            responder=agent2_id,
            initiator_type="agent",
            responder_type="agent",
            **kwargs,
        )

    @classmethod
    def human_to_human(cls, user1_id: str, user2_id: str, **kwargs) -> "Conversation":
        """
        Create a human-to-human conversation.

        Args:
            user1_id: First user's identifier
            user2_id: Second user's identifier
            **kwargs: Additional arguments for Conversation constructor

        Returns:
            Conversation instance
        """
        return cls(
            initiator=user1_id,
            responder=user2_id,
            initiator_type="human",
            responder_type="human",
            **kwargs,
        )

    def add_exchange(
        self, prompt: str, response: str, metadata: Optional[Dict[str, Any]] = None
    ) -> Turn:
        """
        Add a complete exchange (prompt-response) to the conversation.
        This is the preferred method for adding complete turns.

        Args:
            prompt: The initiator's prompt/message
            response: The responder's response
            metadata: Optional metadata for this turn

        Returns:
            The created Turn object
        """
        return self.add_turn(prompt, response, metadata)

    def add_turn(
        self, prompt: str, response: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None
    ) -> Turn:
        """
        Add a complete turn (prompt-response exchange) to the conversation.

        Args:
            prompt: The initiator's prompt/message
            response: The responder's response (optional, can be added later)
            metadata: Optional metadata for this turn

        Returns:
            The created Turn object

        Raises:
            ValidationError: If conversation limits or content validation fails
        """
        # Validate prompt content
        try:
            validate_input_content(prompt, "prompt")
            if response:
                validate_input_content(response, "response")
        except ValidationError as e:
            from .error_handling import safe_error_message

            safe_msg = safe_error_message(e, "conversation content validation")
            logger.warning(
                f"Content validation failed for conversation {self.conversation_id}: {safe_msg}"
            )
            raise

        with self._lock:
            # Validate conversation limits before adding turn
            conversation_data = {
                "turn_count": len(self.turns) + 1,  # +1 for the turn we're about to add
                "memory_usage_mb": self._estimate_memory_usage(),
                "created_time": self.created_at.timestamp(),
            }

            try:
                validate_conversation_limits(conversation_data)
            except ValidationError as e:
                from .error_handling import safe_error_message

                safe_msg = safe_error_message(e, "conversation limits validation")
                logger.warning(
                    f"Conversation limits exceeded for {self.conversation_id}: {safe_msg}"
                )
                raise
            turn = Turn(
                timestamp=datetime.now(),
                prompt=prompt,
                response=response,
                speaker=self.initiator,
                listener=self.responder,
                speaker_type=self.initiator_type,
                listener_type=self.responder_type,
                metadata=metadata or {},
            )

            self.turns.append(turn)
            self.last_activity = turn.timestamp
            self.rate_limit_turns.append(turn.timestamp)

            # Clean up old rate limit entries
            self._cleanup_rate_limit_entries()

            logger.debug(
                f"Added turn to conversation {self.conversation_id}: {self.initiator} -> {self.responder}"
            )
            return turn

    def add_prompt(self, prompt: str, metadata: Optional[Dict[str, Any]] = None) -> Turn:
        """
        Add just a prompt (for when response isn't ready yet).

        Args:
            prompt: The initiator's prompt/message
            metadata: Optional metadata for this turn

        Returns:
            The created Turn object
        """
        return self.add_turn(prompt, response=None, metadata=metadata)

    def add_response(self, response: str, metadata: Optional[Dict[str, Any]] = None) -> Turn:
        """
        Add a response to the most recent prompt-only turn.

        Args:
            response: The responder's response
            metadata: Optional metadata to merge with existing turn metadata

        Returns:
            The updated Turn object

        Raises:
            ValueError: If no prompt-only turn exists
        """
        with self._lock:
            if not self.turns or self.turns[-1].response is not None:
                raise ValueError("No prompt-only turn exists to add response to")

            turn = self.turns[-1]
            turn.response = response
            if metadata:
                turn.metadata.update(metadata)

            self.last_activity = datetime.now()

            logger.debug(
                f"Added response to conversation {self.conversation_id}: {self.responder} -> {self.initiator}"
            )
            return turn

    def get_history(self, limit: Optional[int] = None) -> List[Turn]:
        """
        Get conversation history (complete exchanges).

        Args:
            limit: Optional limit on number of turns to return

        Returns:
            List of turns in chronological order
        """
        if limit is None:
            return self.turns.copy()
        return self.turns[-limit:]

    def get_complete_turns(self) -> List[Turn]:
        """Get all complete turns (with both prompt and response)."""
        return [turn for turn in self.turns if turn.response is not None]

    def get_incomplete_turns(self) -> List[Turn]:
        """Get all incomplete turns (prompt only, no response yet)."""
        return [turn for turn in self.turns if turn.response is None]

    def get_turn_count(self) -> int:
        """Get total number of turns."""
        return len(self.turns)

    def get_complete_turn_count(self) -> int:
        """Get number of complete turns."""
        return len(self.get_complete_turns())

    def get_duration(self) -> float:
        """Get conversation duration in seconds."""
        if not self.turns:
            return 0.0
        return (self.last_activity - self.created_at).total_seconds()

    def check_rate_limit(self, action: str = "block") -> bool:
        """
        Check if rate limit is exceeded.

        Args:
            action: Action to take when limit exceeded ('block', 'warn', 'log')

        Returns:
            True if rate limit is exceeded, False otherwise
        """
        if not self.rate_limit:
            return False

        now = datetime.now()
        exceeded = False
        details = []

        # Check per-minute limit using rolling 60-second window
        if "turns_per_minute" in self.rate_limit:
            minute_ago = now.replace(microsecond=0) - timedelta(seconds=60)
            minute_turns = [t for t in self.rate_limit_turns if t >= minute_ago]
            if len(minute_turns) >= self.rate_limit["turns_per_minute"]:
                exceeded = True
                details.append(
                    f"minute limit: {len(minute_turns)}/{self.rate_limit['turns_per_minute']}"
                )

        # Check per-hour limit using rolling 3600-second window
        if "turns_per_hour" in self.rate_limit:
            hour_ago = now.replace(microsecond=0) - timedelta(seconds=3600)
            hour_turns = [t for t in self.rate_limit_turns if t >= hour_ago]
            if len(hour_turns) >= self.rate_limit["turns_per_hour"]:
                exceeded = True
                details.append(f"hour limit: {len(hour_turns)}/{self.rate_limit['turns_per_hour']}")

        if exceeded:
            message = (
                f"Rate limit exceeded for conversation {self.conversation_id}: {', '.join(details)}"
            )

            if action == "block":
                logger.warning(f"{message} - BLOCKING")
            elif action == "warn":
                logger.warning(f"{message} - WARNING")
            else:  # log
                logger.info(message)

        return exceeded

    def _estimate_memory_usage(self) -> float:
        """
        Estimate memory usage of this conversation in MB.

        Returns:
            Estimated memory usage in megabytes
        """
        total_chars = 0

        # Count characters in all turns
        for turn in self.turns:
            total_chars += len(turn.prompt)
            if turn.response:
                total_chars += len(turn.response)
            # Add metadata size (rough estimate)
            total_chars += len(str(turn.metadata))

        # Add metadata and other fields
        total_chars += len(str(self.metadata))
        total_chars += len(self.conversation_id)
        total_chars += len(self.initiator) + len(self.responder)

        # Rough conversion: 1 character ≈ 1 byte, plus object overhead
        # Add 50% overhead for Python objects, Unicode, etc.
        estimated_bytes = total_chars * 1.5

        # Convert to MB
        return estimated_bytes / (1024 * 1024)

    def set_rate_limit(self, rate_limit: Dict[str, int]) -> None:
        """
        Set or update rate limit configuration.

        Args:
            rate_limit: Rate limit configuration
                Format: {"turns_per_minute": 10, "turns_per_hour": 100}
        """
        with self._lock:
            self.rate_limit = rate_limit
            logger.info(f"Updated rate limit for conversation {self.conversation_id}: {rate_limit}")

    def reset_rate_limit(self) -> None:
        """Reset rate limit tracking."""
        with self._lock:
            self.rate_limit_turns.clear()
            logger.info(f"Reset rate limit tracking for conversation {self.conversation_id}")

    def _cleanup_rate_limit_entries(self) -> None:
        """Remove old rate limit entries to prevent memory bloat."""
        if not self.rate_limit:
            return

        now = datetime.now()
        cutoff = now

        # Keep entries from the last hour if we have hourly limits (rolling 3600-second window)
        if "turns_per_hour" in self.rate_limit:
            cutoff = now.replace(microsecond=0) - timedelta(seconds=3600)
        # Keep entries from the last minute if we have minute limits (rolling 60-second window)
        elif "turns_per_minute" in self.rate_limit:
            cutoff = now.replace(microsecond=0) - timedelta(seconds=60)

        self.rate_limit_turns = [t for t in self.rate_limit_turns if t >= cutoff]

    def to_dict(self) -> Dict[str, Any]:
        """Convert conversation to dictionary for serialization."""
        return {
            "conversation_id": self.conversation_id,
            "participants": self.participants,
            "model_info": self.model_info,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "turn_count": len(self.turns),
            "rate_limit": self.rate_limit,
            "turns": [
                {
                    "timestamp": turn.timestamp.isoformat(),
                    "prompt": turn.prompt,
                    "response": turn.response,
                    "speaker": turn.speaker,
                    "listener": turn.listener,
                    "speaker_type": turn.speaker_type,
                    "listener_type": turn.listener_type,
                    "metadata": turn.metadata,
                }
                for turn in self.turns
            ],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Conversation":
        """Create conversation from dictionary."""
        participants = data.get("participants", {})

        # Extract participant info for the new constructor
        initiator = participants.get("initiator", "unknown")
        responder = participants.get("responder", "unknown")
        initiator_type = participants.get("initiator_type", "unknown")
        responder_type = participants.get("responder_type", "unknown")

        # Use new constructor with extracted values
        conv = cls(
            initiator=initiator,
            responder=responder,
            initiator_type=initiator_type,
            responder_type=responder_type,
            conversation_id=data.get("conversation_id"),
            model_info=data.get("model_info", {}),
            metadata=data.get("metadata", {}),
            rate_limit=data.get("rate_limit", {}),
        )

        # Restore turns
        for turn_data in data.get("turns", []):
            turn = Turn(
                timestamp=datetime.fromisoformat(turn_data["timestamp"]),
                prompt=turn_data["prompt"],
                response=turn_data.get("response"),
                speaker=turn_data.get("speaker", "unknown"),
                listener=turn_data.get("listener", "unknown"),
                speaker_type=turn_data.get("speaker_type", "unknown"),
                listener_type=turn_data.get("listener_type", "unknown"),
                metadata=turn_data.get("metadata", {}),
            )
            conv.turns.append(turn)
            conv.rate_limit_turns.append(turn.timestamp)

        # Restore timestamps
        if "created_at" in data:
            conv.created_at = datetime.fromisoformat(data["created_at"])
        if "last_activity" in data:
            conv.last_activity = datetime.fromisoformat(data["last_activity"])

        return conv

    def __str__(self) -> str:
        """String representation of conversation."""
        return f"Conversation({self.conversation_id}, {len(self.turns)} turns, {self.initiator}->{self.responder})"

    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"Conversation(conversation_id='{self.conversation_id}', participants={self.participants}, turns={len(self.turns)})"
