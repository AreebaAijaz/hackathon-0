"""Abstract base class for all watchers in the AI Employee system.

Defines the contract that all watchers (Gmail, file system, etc.) must
follow per the watcher-interface contract. Provides the run loop with
graceful shutdown, exponential backoff retry, and audit logging.
"""

import abc
import logging
import signal
import sys
import time

from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from src.audit_logger import log_action

logger = logging.getLogger(__name__)


class BaseWatcher(abc.ABC):
    """Abstract base class for all AI Employee watchers.

    Subclasses must implement check_for_updates() and create_action_file().

    Args:
        vault_path: Absolute path to the Obsidian vault root.
        check_interval: Seconds between check cycles (default: 120).
    """

    def __init__(self, vault_path: str, check_interval: int = 120):
        if check_interval < 30:
            raise ValueError("check_interval must be >= 30 seconds")

        self.vault_path = vault_path
        self.check_interval = check_interval
        self.running = False
        self._setup_signal_handlers()
        self._setup_logging()

    def _setup_logging(self):
        """Configure structured logging to console."""
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
        handler.setFormatter(formatter)

        root_logger = logging.getLogger()
        if not root_logger.handlers:
            root_logger.addHandler(handler)
            root_logger.setLevel(logging.INFO)

    def _setup_signal_handlers(self):
        """Register signal handlers for graceful shutdown (Windows-compatible)."""
        signal.signal(signal.SIGINT, self._shutdown_handler)
        signal.signal(signal.SIGTERM, self._shutdown_handler)
        if hasattr(signal, "SIGBREAK"):
            signal.signal(signal.SIGBREAK, self._shutdown_handler)

    def _shutdown_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info("Received signal %s, shutting down gracefully...", signum)
        self.running = False

    @abc.abstractmethod
    def check_for_updates(self) -> list[dict]:
        """Poll the external source for new items.

        Returns:
            List of dicts, each representing a new item with at minimum:
            {"id": str, "source_type": str, "title": str, "content": str}

        Raises:
            Exception: On transient errors (will be retried by run loop).
        """

    @abc.abstractmethod
    def create_action_file(self, item: dict) -> str:
        """Write a structured markdown task file to Needs_Action/.

        Args:
            item: Dict from check_for_updates() result.

        Returns:
            Absolute path to the created file.
        """

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        retry=retry_if_exception_type(Exception),
        reraise=True,
    )
    def _check_with_retry(self) -> list[dict]:
        """Call check_for_updates with exponential backoff retry."""
        return self.check_for_updates()

    def run(self):
        """Main watcher loop. Polls and processes until shutdown signal."""
        watcher_name = self.__class__.__name__
        self.running = True
        logger.info("%s started (interval=%ds)", watcher_name, self.check_interval)

        log_action(
            vault_path=self.vault_path,
            action_type="watcher_started",
            actor=watcher_name.lower(),
            target=self.vault_path,
            result="success",
            parameters={"check_interval": self.check_interval},
        )

        try:
            while self.running:
                try:
                    updates = self._check_with_retry()
                    for item in updates:
                        try:
                            path = self.create_action_file(item)
                            logger.info("Created action file: %s", path)
                        except Exception as e:
                            logger.error(
                                "Failed to create action file for %s: %s",
                                item.get("id", "unknown"),
                                e,
                            )
                            log_action(
                                vault_path=self.vault_path,
                                action_type="watcher_error",
                                actor=watcher_name.lower(),
                                target=str(item.get("id", "unknown")),
                                result="failure",
                                error_message=str(e),
                            )
                except Exception as e:
                    logger.error("Check cycle failed after retries: %s", e)
                    log_action(
                        vault_path=self.vault_path,
                        action_type="watcher_error",
                        actor=watcher_name.lower(),
                        target=self.vault_path,
                        result="failure",
                        error_message=str(e),
                    )

                if self.running:
                    time.sleep(self.check_interval)
        finally:
            logger.info("%s stopped", watcher_name)
            log_action(
                vault_path=self.vault_path,
                action_type="watcher_stopped",
                actor=watcher_name.lower(),
                target=self.vault_path,
                result="success",
            )
