"""CLI entry point for the Orchestrator.

Usage:
    uv run python -m src --once              # Process all pending tasks and exit
    uv run python -m src                     # Watch mode (poll every 30s)
    uv run python -m src --dry-run           # Simulate without calling Claude
    uv run python -m src --dry-run --once    # Simulate once and exit
"""

import argparse
import logging
import sys

from src.orchestrator import Orchestrator
from src.utils.config import load_config


def main():
    parser = argparse.ArgumentParser(
        description="Personal AI Employee - Orchestrator",
        prog="python -m src",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Process all pending tasks once and exit (no polling)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate processing without invoking Claude Code",
    )
    parser.add_argument(
        "--poll-interval",
        type=int,
        default=30,
        help="Seconds between scan cycles in watch mode (default: 30)",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

    config = load_config()
    dry_run = args.dry_run or config["dry_run"]

    orchestrator = Orchestrator(
        vault_path=config["vault_path"],
        dry_run=dry_run,
    )

    if dry_run:
        logging.getLogger(__name__).info("Starting in DRY RUN mode")

    if args.once:
        results = orchestrator.run_once()
        processed = sum(1 for r in results if r["error"] is None)
        failed = sum(1 for r in results if r["error"] is not None)
        flagged = sum(1 for r in results if r["flagged_for_human"])
        logging.getLogger(__name__).info(
            "Completed: %d processed, %d failed, %d flagged for human review",
            processed,
            failed,
            flagged,
        )
        sys.exit(1 if failed > 0 else 0)
    else:
        orchestrator.run(poll_interval=args.poll_interval)


if __name__ == "__main__":
    main()
