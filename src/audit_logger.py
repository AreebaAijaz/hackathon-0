"""Structured audit logging utility for the AI Employee system.

Appends NDJSON log entries to date-partitioned files in the vault's Logs/ directory.
Every system action MUST be logged per Constitution Principle III (Audit Everything).
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

VALID_ACTION_TYPES = {
    "email_detected",
    "task_created",
    "task_processed",
    "plan_created",
    "dashboard_updated",
    "task_archived",
    "watcher_started",
    "watcher_stopped",
    "watcher_error",
    "auth_error",
}


def log_action(
    vault_path: str,
    action_type: str,
    actor: str,
    target: str,
    result: str,
    parameters: dict | None = None,
    error_message: str | None = None,
) -> str:
    """Append a structured audit log entry to today's log file.

    Args:
        vault_path: Absolute or relative path to the Obsidian vault root.
        action_type: One of the defined action type enum values.
        actor: Component name (e.g., "gmail_watcher", "orchestrator").
        target: File path or endpoint acted upon.
        result: "success" or "failure".
        parameters: Optional additional context as key-value pairs.
        error_message: Required when result is "failure".

    Returns:
        Path to the log file that was written to.

    Raises:
        ValueError: If action_type or result is invalid.
    """
    if action_type not in VALID_ACTION_TYPES:
        raise ValueError(
            f"Invalid action_type '{action_type}'. "
            f"Must be one of: {sorted(VALID_ACTION_TYPES)}"
        )

    if result not in ("success", "failure"):
        raise ValueError(f"Invalid result '{result}'. Must be 'success' or 'failure'.")

    if result == "failure" and not error_message:
        raise ValueError("error_message is required when result is 'failure'.")

    now = datetime.now(timezone.utc)
    entry = {
        "timestamp": now.isoformat(),
        "action_type": action_type,
        "actor": actor,
        "target": target,
        "result": result,
    }

    if parameters:
        entry["parameters"] = parameters

    if error_message:
        entry["error_message"] = error_message

    logs_dir = Path(vault_path) / "Logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    log_file = logs_dir / f"{now.strftime('%Y-%m-%d')}.json"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    return str(log_file)
