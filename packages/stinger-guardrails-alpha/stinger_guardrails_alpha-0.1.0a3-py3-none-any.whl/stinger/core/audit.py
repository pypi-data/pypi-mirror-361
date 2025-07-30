"""
Security Audit Trail System

Provides complete security behavior tracking for forensic analysis and compliance.
This is NOT developer debug logging - this tracks security decisions for audit purposes.
"""

import json
import os
import queue
import sys
import threading
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Union


class AuditTrail:
    """Security audit trail system for tracking all security-related behavior."""

    def __init__(self):
        self._enabled = False
        self._destination = None
        self._redact_pii = False
        self._file_handle = None

        # Async buffering configuration
        self._buffer_size = 1000
        self._flush_interval = 5.0  # seconds
        self._max_retries = 3

        # Async buffering state
        self._log_queue = None
        self._writer_thread = None
        self._shutdown_event = None
        self._stats = {"queued": 0, "written": 0, "dropped": 0}

    def enable(
        self,
        destination: Union[str, List[str]] = None,
        redact_pii: bool = None,
        buffer_size: int = None,
        flush_interval: float = None,
        **kwargs,
    ):
        """
        Enable security audit trail with ultra-simple configuration.

        Args:
            destination: Where to write audit logs:
                        - None: Smart default (stdout in dev, ./audit.log in prod)
                        - "stdout": Console output
                        - "./path/to/file.log": File output
                        - ["./file.log", "stdout"]: Multiple destinations
            redact_pii: Whether to redact PII (smart default based on environment)
            buffer_size: Size of async buffer (default: 1000)
            flush_interval: Flush interval in seconds (default: 5.0)
        """
        self._enabled = True

        # Apply configuration
        if buffer_size is not None:
            self._buffer_size = buffer_size
        if flush_interval is not None:
            self._flush_interval = flush_interval

        # Smart defaults based on environment
        if destination is None:
            destination = self._detect_smart_destination()

        if redact_pii is None:
            redact_pii = self._detect_smart_pii_setting()

        self._destination = destination
        self._redact_pii = redact_pii

        # Initialize async buffering
        self._setup_async_buffering()

        # Initialize destination
        self._setup_destination()

        # Log that audit trail is enabled
        self._write_audit_record(
            {
                "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "event_type": "audit_trail_enabled",
                "destination": destination,
                "redact_pii": redact_pii,
                "buffer_size": self._buffer_size,
                "flush_interval": self._flush_interval,
            }
        )

    def disable(self):
        """Disable audit trail (only allowed in development)."""
        if self._is_production():
            raise RuntimeError("Cannot disable audit trail in production environment")

        self._enabled = False

        # Shutdown async buffering
        self._shutdown_async_buffering()

        # Close file handle safely
        if hasattr(self, "_file_handle") and self._file_handle and self._file_handle != sys.stdout:
            try:
                self._file_handle.close()
            except (IOError, OSError):
                pass  # Ignore errors during cleanup
            self._file_handle = None

    def is_enabled(self) -> bool:
        """Check if audit trail is enabled."""
        return self._enabled

    def log_prompt(
        self,
        prompt: str,
        user_id: str = None,
        conversation_id: str = None,
        request_id: str = None,
        user_ip: str = None,
        user_agent: str = None,
        session_id: str = None,
    ):
        """Log user prompt for audit trail."""
        if not self._enabled:
            return

        record = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "event_type": "user_prompt",
            "request_id": request_id,
            "user_id": user_id,
            "session_id": session_id,
            "conversation_id": conversation_id,
            "user_ip": user_ip,
            "user_agent": user_agent,
            "prompt": self._redact_if_needed(prompt),
        }

        self._write_audit_record(record)

    def log_response(
        self,
        response: str,
        user_id: str = None,
        conversation_id: str = None,
        request_id: str = None,
        model_used: str = None,
        processing_time_ms: int = None,
    ):
        """Log LLM response for audit trail."""
        if not self._enabled:
            return

        record = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "event_type": "llm_response",
            "request_id": request_id,
            "user_id": user_id,
            "conversation_id": conversation_id,
            "response": self._redact_if_needed(response),
            "model_used": model_used,
            "processing_time_ms": processing_time_ms,
        }

        self._write_audit_record(record)

    def log_guardrail_decision(
        self,
        guardrail_name: str,
        decision: str,
        reason: str,
        user_id: str = None,
        conversation_id: str = None,
        request_id: str = None,
        confidence: float = None,
        rule_triggered: str = None,
    ):
        """Log guardrail security decision for audit trail."""
        if not self._enabled:
            return

        record = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "event_type": "guardrail_decision",
            "request_id": request_id,
            "user_id": user_id,
            "conversation_id": conversation_id,
            "guardrail_name": guardrail_name,
            "decision": decision,  # block, allow, warn
            "reason": reason,
            "confidence": confidence,
            "rule_triggered": rule_triggered,
        }

        self._write_audit_record(record)

    def _detect_smart_destination(self) -> str:
        """Detect smart default destination based on environment."""
        if self._is_development():
            return "stdout"
        elif self._is_docker():
            return "stdout"
        else:
            return "./audit.log"

    def _detect_smart_pii_setting(self) -> bool:
        """Detect smart default PII redaction based on environment."""
        if self._is_development():
            return False  # No redaction in dev for easier debugging
        else:
            return True  # Redact PII in production

    def _is_development(self) -> bool:
        """Check if running in development environment."""
        return (
            os.getenv("ENVIRONMENT") == "development"
            or os.getenv("DEV") == "true"
            or os.getenv("DEBUG") == "true"
        )

    def _is_production(self) -> bool:
        """Check if running in production environment."""
        return os.getenv("ENVIRONMENT") == "production" or os.getenv("PROD") == "true"

    def _is_docker(self) -> bool:
        """Check if running in Docker container."""
        return os.path.exists("/.dockerenv") or os.getenv("DOCKER") == "true"

    def _setup_destination(self):
        """Setup the audit log destination."""
        # Close any existing file handle first
        if hasattr(self, "_file_handle") and self._file_handle and self._file_handle != sys.stdout:
            try:
                self._file_handle.close()
            except (IOError, OSError):
                pass  # Ignore errors during cleanup
            self._file_handle = None

        if isinstance(self._destination, list):
            # Multiple destinations not implemented yet - use first one
            destination = self._destination[0]
        else:
            destination = self._destination

        if destination == "stdout":
            self._file_handle = sys.stdout
        else:
            # File destination
            path = Path(destination)
            path.parent.mkdir(parents=True, exist_ok=True)
            try:
                self._file_handle = open(path, "a", encoding="utf-8")
            except Exception as e:
                # Fallback to stdout if file can't be opened
                from .error_handling import safe_error_message, sanitize_path

                safe_path = sanitize_path(str(path))
                safe_msg = safe_error_message(e, f"opening audit log file {safe_path}")
                print(f"Warning: {safe_msg}")
                self._file_handle = sys.stdout

    def _redact_if_needed(self, text: str) -> str:
        """Redact PII if redaction is enabled."""
        if not self._redact_pii or not text:
            return text

        # Basic PII redaction patterns
        import re

        # Email redaction
        text = re.sub(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "[EMAIL_REDACTED]", text
        )

        # Phone number redaction (simple patterns)
        text = re.sub(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b", "[PHONE_REDACTED]", text)

        # SSN redaction
        text = re.sub(r"\b\d{3}-\d{2}-\d{4}\b", "[SSN_REDACTED]", text)

        # Credit card redaction
        text = re.sub(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b", "[CARD_REDACTED]", text)

        return text

    def _setup_async_buffering(self):
        """Setup async buffering system."""
        if self._log_queue is not None:
            return  # Already setup

        self._log_queue = queue.Queue(maxsize=self._buffer_size)
        self._shutdown_event = threading.Event()
        self._writer_thread = threading.Thread(
            target=self._background_writer, name="AuditWriter", daemon=True
        )
        self._writer_thread.start()

    def _shutdown_async_buffering(self):
        """Shutdown async buffering system."""
        if self._shutdown_event:
            self._shutdown_event.set()

        if self._writer_thread and self._writer_thread.is_alive():
            self._writer_thread.join(timeout=5.0)  # Give it 5 seconds to finish

        self._log_queue = None
        self._writer_thread = None
        self._shutdown_event = None

    def _background_writer(self):
        """Background thread that batches and writes audit records."""
        batch = []
        last_flush = time.time()

        while not self._shutdown_event.is_set() or not self._log_queue.empty():
            try:
                # Try to get a record with timeout
                try:
                    record = self._log_queue.get(timeout=0.1)
                    batch.append(record)
                    self._log_queue.task_done()
                except queue.Empty:
                    pass

                # Check if we should flush
                current_time = time.time()
                should_flush = (
                    len(batch) >= 50  # Batch size limit
                    or (batch and current_time - last_flush >= self._flush_interval)  # Time limit
                    or self._shutdown_event.is_set()  # Shutting down
                )

                if should_flush and batch:
                    self._flush_batch(batch)
                    batch = []
                    last_flush = current_time

            except Exception:
                # Don't let background thread crash
                self._stats["dropped"] += len(batch)
                batch = []
                time.sleep(0.1)

    def _flush_batch(self, batch: List[Dict[str, Any]]):
        """Flush a batch of records to disk."""
        if not self._file_handle or not batch:
            return

        try:
            for record in batch:
                json_line = json.dumps(record, separators=(",", ":"))
                self._file_handle.write(json_line + "\n")

            self._file_handle.flush()
            self._stats["written"] += len(batch)

        except Exception:
            # Record the failure but don't crash
            self._stats["dropped"] += len(batch)

    def _write_audit_record(self, record: Dict[str, Any]):
        """Write audit record via async buffering."""
        if not self._enabled:
            return

        if self._log_queue is None:
            # Fallback to synchronous write if async not setup
            self._write_sync(record)
            return

        try:
            self._log_queue.put_nowait(record)
            self._stats["queued"] += 1
        except queue.Full:
            # Queue is full - fallback to sync write to not lose data
            self._write_sync(record)
            self._stats["dropped"] += 1

    def _write_sync(self, record: Dict[str, Any]):
        """Synchronous fallback for writing records."""
        if not self._file_handle:
            return

        try:
            json_line = json.dumps(record, separators=(",", ":"))
            self._file_handle.write(json_line + "\n")
            self._file_handle.flush()
        except Exception:
            # Don't break the main pipeline
            pass

    def get_stats(self) -> Dict[str, int]:
        """Get async buffering statistics."""
        stats = self._stats.copy()
        if self._log_queue:
            stats["queue_size"] = self._log_queue.qsize()
        return stats


# Global audit trail instance
_audit_trail = AuditTrail()


def enable(destination: Union[str, List[str]] = None, redact_pii: bool = None, **kwargs):
    """
    Enable security audit trail with zero-config startup.

    Examples:
        audit.enable()                           # Zero config, smart defaults
        audit.enable("./logs/audit.log")        # File logging
        audit.enable("stdout")                  # Console logging
        audit.enable("./audit.log", redact_pii=True)  # With PII redaction
    """
    _audit_trail.enable(destination, redact_pii, **kwargs)


def disable():
    """Disable audit trail (only allowed in development)."""
    _audit_trail.disable()


def is_enabled() -> bool:
    """Check if audit trail is enabled."""
    return _audit_trail.is_enabled()


def log_prompt(
    prompt: str,
    user_id: str = None,
    conversation_id: str = None,
    request_id: str = None,
    user_ip: str = None,
    user_agent: str = None,
    session_id: str = None,
):
    """Log user prompt for audit trail."""
    _audit_trail.log_prompt(
        prompt, user_id, conversation_id, request_id, user_ip, user_agent, session_id
    )


def log_response(
    response: str,
    user_id: str = None,
    conversation_id: str = None,
    request_id: str = None,
    model_used: str = None,
    processing_time_ms: int = None,
):
    """Log LLM response for audit trail."""
    _audit_trail.log_response(
        response, user_id, conversation_id, request_id, model_used, processing_time_ms
    )


def log_guardrail_decision(
    guardrail_name: str,
    decision: str,
    reason: str,
    user_id: str = None,
    conversation_id: str = None,
    request_id: str = None,
    confidence: float = None,
    rule_triggered: str = None,
):
    """Log guardrail security decision for audit trail."""
    _audit_trail.log_guardrail_decision(
        guardrail_name,
        decision,
        reason,
        user_id,
        conversation_id,
        request_id,
        confidence,
        rule_triggered,
    )


def query(
    conversation_id: str = None,
    user_id: str = None,
    start_time: str = None,
    end_time: str = None,
    event_type: str = None,
    last_hour: bool = False,
    destination: str = "./audit.log",
):
    """
    Simple query function for development use.

    Args:
        conversation_id: Filter by conversation ID
        user_id: Filter by user ID
        start_time: Start time in ISO format
        end_time: End time in ISO format
        event_type: Filter by event type (user_prompt, llm_response, guardrail_decision)
        last_hour: Show only events from the last hour
        destination: Path to audit log file (default: ./audit.log)

    Returns:
        List of matching audit records
    """
    import json
    from pathlib import Path

    try:
        log_path = Path(destination)
        if not log_path.exists():
            print(f"Audit log file not found: {destination}")
            return []

        records = []
        current_time = datetime.now(timezone.utc)

        with open(log_path, "r") as f:
            for line in f:
                try:
                    record = json.loads(line.strip())

                    # Apply filters
                    if conversation_id and record.get("conversation_id") != conversation_id:
                        continue
                    if user_id and record.get("user_id") != user_id:
                        continue
                    if event_type and record.get("event_type") != event_type:
                        continue

                    # Time filtering
                    if last_hour:
                        record_time = datetime.fromisoformat(
                            record["timestamp"].replace("Z", "+00:00")
                        )
                        if record_time < current_time - timedelta(hours=1):
                            continue
                    elif start_time:
                        record_time = datetime.fromisoformat(
                            record["timestamp"].replace("Z", "+00:00")
                        )
                        start_dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
                        if record_time < start_dt:
                            continue
                    elif end_time:
                        record_time = datetime.fromisoformat(
                            record["timestamp"].replace("Z", "+00:00")
                        )
                        end_dt = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
                        if record_time > end_dt:
                            continue

                    records.append(record)

                except json.JSONDecodeError:
                    continue  # Skip invalid JSON lines

        return records

    except Exception as e:
        print(f"Error querying audit log: {e}")
        return []


def print_query_results(records: list, limit: int = 10):
    """
    Print query results in a human-readable format.

    Args:
        records: List of audit records from query()
        limit: Maximum number of records to print
    """
    if not records:
        print("No matching audit records found.")
        return

    print(f"Found {len(records)} matching audit records:")
    print("-" * 80)

    for i, record in enumerate(records[:limit]):
        timestamp = record.get("timestamp", "Unknown")
        event_type = record.get("event_type", "Unknown")
        user_id = record.get("user_id", "Unknown")
        conversation_id = record.get("conversation_id", "Unknown")

        print(f"{i+1}. [{timestamp}] {event_type}")
        print(f"   User: {user_id}, Conversation: {conversation_id}")

        if event_type == "user_prompt":
            prompt = record.get("prompt", "")[:100]
            print(f"   Prompt: {prompt}{'...' if len(record.get('prompt', '')) > 100 else ''}")
        elif event_type == "llm_response":
            response = record.get("response", "")[:100]
            print(
                f"   Response: {response}{'...' if len(record.get('response', '')) > 100 else ''}"
            )
        elif event_type == "guardrail_decision":
            guardrail_name = record.get("guardrail_name", "Unknown")
            decision = record.get("decision", "Unknown")
            reason = record.get("reason", "")[:50]
            print(f"   Filter: {guardrail_name}, Decision: {decision}")
            print(f"   Reason: {reason}{'...' if len(record.get('reason', '')) > 50 else ''}")

        print()

    if len(records) > limit:
        print(f"... and {len(records) - limit} more records")
        print(f"Use query() to get all records programmatically.")


def get_stats() -> Dict[str, int]:
    """
    Get async buffering performance statistics.

    Returns:
        Dictionary with statistics about the audit trail performance
    """
    return _audit_trail.get_stats()


def export_csv(
    destination: str = "./audit.log",
    output_file: str = None,
    conversation_id: str = None,
    user_id: str = None,
    start_time: str = None,
    end_time: str = None,
    event_type: str = None,
) -> str:
    """
    Export audit trail to CSV format for compliance reporting.

    Args:
        destination: Path to audit log file (default: ./audit.log)
        output_file: Output CSV file path (default: auto-generated)
        conversation_id: Filter by conversation ID
        user_id: Filter by user ID
        start_time: Start time in ISO format
        end_time: End time in ISO format
        event_type: Filter by event type

    Returns:
        Path to generated CSV file
    """
    import csv
    from datetime import datetime, timezone

    # Query filtered records
    records = query(
        conversation_id, user_id, start_time, end_time, event_type, destination=destination
    )

    if not records:
        if output_file:
            # Create empty CSV with headers
            with open(output_file, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(
                    ["timestamp", "event_type", "user_id", "conversation_id", "summary"]
                )
        return output_file or ""

    # Generate output filename if not provided
    if not output_file:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        output_file = f"audit_export_{timestamp}.csv"

    # Export to CSV
    with open(output_file, "w", newline="") as f:
        writer = csv.writer(f)

        # Write header
        writer.writerow(
            [
                "timestamp",
                "event_type",
                "user_id",
                "conversation_id",
                "request_id",
                "guardrail_name",
                "decision",
                "reason",
                "confidence",
                "summary",
            ]
        )

        # Write records
        for record in records:
            # Create summary based on event type
            summary = ""
            if record.get("event_type") == "user_prompt":
                prompt = record.get("prompt", "")
                summary = prompt[:100] + "..." if len(prompt) > 100 else prompt
            elif record.get("event_type") == "llm_response":
                response = record.get("response", "")
                summary = response[:100] + "..." if len(response) > 100 else response
            elif record.get("event_type") == "guardrail_decision":
                guardrail_name = record.get("guardrail_name", "")
                decision = record.get("decision", "")
                summary = f"{guardrail_name}: {decision}"
            else:
                summary = record.get("event_type", "")

            writer.writerow(
                [
                    record.get("timestamp", ""),
                    record.get("event_type", ""),
                    record.get("user_id", ""),
                    record.get("conversation_id", ""),
                    record.get("request_id", ""),
                    record.get("guardrail_name", ""),
                    record.get("decision", ""),
                    record.get("reason", ""),
                    record.get("confidence", ""),
                    summary,
                ]
            )

    return output_file


def export_json(
    destination: str = "./audit.log",
    output_file: str = None,
    conversation_id: str = None,
    user_id: str = None,
    start_time: str = None,
    end_time: str = None,
    event_type: str = None,
    pretty: bool = True,
) -> str:
    """
    Export audit trail to JSON format for compliance reporting.

    Args:
        destination: Path to audit log file (default: ./audit.log)
        output_file: Output JSON file path (default: auto-generated)
        conversation_id: Filter by conversation ID
        user_id: Filter by user ID
        start_time: Start time in ISO format
        end_time: End time in ISO format
        event_type: Filter by event type
        pretty: Whether to format JSON with indentation

    Returns:
        Path to generated JSON file
    """
    import json
    from datetime import datetime, timezone

    # Query filtered records
    records = query(
        conversation_id, user_id, start_time, end_time, event_type, destination=destination
    )

    # Generate output filename if not provided
    if not output_file:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        output_file = f"audit_export_{timestamp}.json"

    # Create export data structure
    export_data = {
        "export_timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "guardrails": {
            "conversation_id": conversation_id,
            "user_id": user_id,
            "start_time": start_time,
            "end_time": end_time,
            "event_type": event_type,
            "source_file": destination,
        },
        "total_records": len(records),
        "records": records,
    }

    # Export to JSON
    with open(output_file, "w") as f:
        if pretty:
            json.dump(export_data, f, indent=2, separators=(",", ": "))
        else:
            json.dump(export_data, f, separators=(",", ":"))

    return output_file
