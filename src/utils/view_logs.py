"""Log viewer utility for the AI Employee audit logs.

Reads NDJSON log files from the vault's Logs/ directory and displays
them in a human-readable format with filtering and summary stats.

Usage:
    uv run python -m src.utils.view_logs                  # Today's logs
    uv run python -m src.utils.view_logs --date 2026-02-18
    uv run python -m src.utils.view_logs --type email_detected
"""

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

from src.utils.config import load_config


def read_log_entries(log_file: Path) -> list[dict]:
    """Read all NDJSON entries from a log file.

    Args:
        log_file: Path to the NDJSON log file.

    Returns:
        List of parsed log entry dicts.
    """
    entries = []
    if not log_file.is_file():
        return entries

    with open(log_file, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                logging.warning("Skipping malformed JSON at line %d", line_num)

    return entries


def format_table(entries: list[dict], action_filter: str | None = None) -> str:
    """Format log entries as an aligned text table.

    Args:
        entries: List of log entry dicts.
        action_filter: Optional action_type filter.

    Returns:
        Formatted table string.
    """
    if action_filter:
        entries = [e for e in entries if e.get("action_type") == action_filter]

    if not entries:
        return "No matching log entries found."

    # Header
    header = f"{'Time':<22} {'Action':<20} {'Actor':<18} {'Result':<10} {'Target'}"
    separator = "-" * max(len(header), 90)
    lines = [separator, header, separator]

    for entry in entries:
        ts = entry.get("timestamp", "")
        if "T" in ts:
            time_display = ts[:19].replace("T", " ")
        else:
            time_display = ts[:22]

        action = entry.get("action_type", "unknown")
        actor = entry.get("actor", "unknown")
        result = entry.get("result", "?")
        target = entry.get("target", "")

        # Shorten target path
        if len(target) > 35:
            target = "..." + target[-32:]

        line = f"{time_display:<22} {action:<20} {actor:<18} {result:<10} {target}"
        lines.append(line)

        # Show error message if present
        if entry.get("error_message"):
            lines.append(f"  ERROR: {entry['error_message']}")

    lines.append(separator)
    return "\n".join(lines)


def compute_stats(entries: list[dict]) -> str:
    """Compute summary statistics from log entries.

    Args:
        entries: List of log entry dicts.

    Returns:
        Formatted stats string.
    """
    total = len(entries)
    if total == 0:
        return "No entries to analyze."

    success = sum(1 for e in entries if e.get("result") == "success")
    failure = sum(1 for e in entries if e.get("result") == "failure")
    success_rate = (success / total * 100) if total > 0 else 0

    # Count by action type
    action_counts: dict[str, int] = {}
    for entry in entries:
        action = entry.get("action_type", "unknown")
        action_counts[action] = action_counts.get(action, 0) + 1

    lines = [
        "\n--- Summary ---",
        f"Total actions:  {total}",
        f"Success:        {success} ({success_rate:.1f}%)",
        f"Failures:       {failure}",
        "",
        "By action type:",
    ]

    for action, count in sorted(action_counts.items()):
        lines.append(f"  {action:<25} {count}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Personal AI Employee - Audit Log Viewer",
        prog="python -m src.utils.view_logs",
    )
    parser.add_argument(
        "--date",
        type=str,
        default=None,
        help="Date to view logs for (YYYY-MM-DD, default: today)",
    )
    parser.add_argument(
        "--type",
        type=str,
        default=None,
        dest="action_type",
        help="Filter by action_type (e.g., email_detected, task_created)",
    )
    parser.add_argument(
        "--stats-only",
        action="store_true",
        help="Show only summary statistics",
    )
    args = parser.parse_args()

    config = load_config()
    vault_path = config["vault_path"]

    # Determine date
    if args.date:
        date_str = args.date
    else:
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    log_file = Path(vault_path) / "Logs" / f"{date_str}.json"

    print(f"Log file: {log_file}")
    print(f"Date: {date_str}")
    if args.action_type:
        print(f"Filter: {args.action_type}")
    print()

    entries = read_log_entries(log_file)

    if not entries:
        print(f"No log entries found for {date_str}")
        sys.exit(0)

    if not args.stats_only:
        print(format_table(entries, action_filter=args.action_type))

    print(compute_stats(entries if not args.action_type else [
        e for e in entries if e.get("action_type") == args.action_type
    ]))


if __name__ == "__main__":
    main()
