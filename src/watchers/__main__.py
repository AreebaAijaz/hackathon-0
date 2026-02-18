"""CLI entry point for the Gmail watcher.

Usage:
    uv run python -m src.watchers              # Start watching Gmail
    uv run python -m src.watchers --auth-only  # Authenticate only
    uv run python -m src.watchers --dry-run    # Run with sample data
    uv run python -m src.watchers --interval 60  # Custom interval
"""

import argparse
import logging
import sys

from src.utils.config import load_config
from src.watchers.gmail_auth import auth_only
from src.watchers.gmail_watcher import GmailWatcher


def main():
    parser = argparse.ArgumentParser(
        description="Personal AI Employee - Gmail Watcher",
        prog="python -m src.watchers",
    )
    parser.add_argument(
        "--auth-only",
        action="store_true",
        help="Authenticate with Gmail and exit (first-time setup)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate sample task files without connecting to Gmail",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=None,
        help="Override check interval in seconds (default: from .env or 120)",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

    config = load_config()

    # Auth-only mode
    if args.auth_only:
        success = auth_only(config["credentials_path"], config["token_path"])
        sys.exit(0 if success else 1)

    # Determine dry_run from CLI flag or config
    dry_run = args.dry_run or config["dry_run"]

    # Determine check interval
    interval = args.interval if args.interval is not None else config["check_interval"]

    watcher = GmailWatcher(
        credentials_path=config["credentials_path"],
        token_path=config["token_path"],
        vault_path=config["vault_path"],
        check_interval=interval,
        dry_run=dry_run,
    )

    if dry_run:
        logging.getLogger(__name__).info("Starting in DRY RUN mode")

    watcher.run()


if __name__ == "__main__":
    main()
