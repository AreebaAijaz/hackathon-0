"""Gmail watcher that monitors inbox for important unread emails.

Extends BaseWatcher to poll Gmail API every check_interval seconds,
detect new important unread messages, and create structured task files
in the vault's Needs_Action/ directory.
"""

import logging
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

from src.audit_logger import log_action
from src.watchers.base_watcher import BaseWatcher

logger = logging.getLogger(__name__)

# Gmail query: important unread messages only
GMAIL_QUERY = "is:unread AND is:important"
MAX_RESULTS = 10

# Sample data for dry-run mode
DRY_RUN_SAMPLES = [
    {
        "id": "dry_run_001",
        "sender": "accounting@acmecorp.com",
        "subject": "Invoice #1234 - Payment Due Feb 20",
        "snippet": "Please find attached invoice #1234 for $2,500.00 due by February 20th.",
        "date": "Mon, 17 Feb 2026 10:30:00 +0000",
    },
    {
        "id": "dry_run_002",
        "sender": "sarah@team.com",
        "subject": "Team standup moved to 3pm Thursday",
        "snippet": "Hi, just a heads up that our weekly standup has been rescheduled to 3pm Thursday.",
        "date": "Mon, 17 Feb 2026 11:00:00 +0000",
    },
    {
        "id": "dry_run_003",
        "sender": "newsletter@techdigest.com",
        "subject": "Weekly Tech Digest - AI Updates",
        "snippet": "This week in AI: new language model benchmarks, robotics breakthroughs, and more.",
        "date": "Mon, 17 Feb 2026 09:00:00 +0000",
    },
]


class GmailWatcher(BaseWatcher):
    """Watches Gmail inbox for important unread emails.

    Args:
        credentials_path: Path to OAuth2 client secrets JSON file.
        token_path: Path to stored/cached user token.
        vault_path: Path to the Obsidian vault root directory.
        check_interval: Seconds between polling cycles (default: 120).
        dry_run: If True, generate sample task files without connecting to Gmail.
    """

    def __init__(
        self,
        credentials_path: str,
        token_path: str,
        vault_path: str,
        check_interval: int = 120,
        dry_run: bool = False,
    ):
        super().__init__(vault_path=vault_path, check_interval=check_interval)
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.dry_run = dry_run
        self.processed_ids: set[str] = set()
        self._service = None

    def _get_service(self):
        """Lazy-initialize the Gmail API service."""
        if self._service is None and not self.dry_run:
            from src.watchers.gmail_auth import get_gmail_service

            self._service = get_gmail_service(
                self.credentials_path, self.token_path
            )
        return self._service

    def check_for_updates(self) -> list[dict]:
        """Poll Gmail for new important unread messages.

        Returns:
            List of message dicts with keys: id, sender, subject, snippet, date.
        """
        if self.dry_run:
            return self._check_dry_run()

        service = self._get_service()
        try:
            results = (
                service.users()
                .messages()
                .list(userId="me", q=GMAIL_QUERY, maxResults=MAX_RESULTS)
                .execute()
            )
        except Exception as e:
            logger.error("Gmail API list error: %s", e)
            raise

        messages = results.get("messages", [])
        if not messages:
            logger.debug("No new important unread messages")
            return []

        new_items = []
        for msg in messages:
            msg_id = msg["id"]
            if msg_id in self.processed_ids:
                continue

            try:
                detail = (
                    service.users()
                    .messages()
                    .get(
                        userId="me",
                        id=msg_id,
                        format="metadata",
                        metadataHeaders=["From", "Subject", "Date"],
                    )
                    .execute()
                )
            except Exception as e:
                logger.error("Gmail API get error for %s: %s", msg_id, e)
                raise

            headers = {
                h["name"]: h["value"] for h in detail.get("payload", {}).get("headers", [])
            }

            new_items.append(
                {
                    "id": msg_id,
                    "sender": headers.get("From", "unknown"),
                    "subject": headers.get("Subject", "(no subject)"),
                    "snippet": detail.get("snippet", ""),
                    "date": headers.get("Date", ""),
                }
            )

            log_action(
                vault_path=self.vault_path,
                action_type="email_detected",
                actor="gmail_watcher",
                target=msg_id,
                result="success",
                parameters={"sender": headers.get("From", "unknown")},
            )

        if new_items:
            logger.info("Found %d new important email(s)", len(new_items))
        return new_items

    def _check_dry_run(self) -> list[dict]:
        """Generate sample email data for dry-run testing."""
        new_items = []
        for sample in DRY_RUN_SAMPLES:
            if sample["id"] in self.processed_ids:
                continue
            new_items.append(sample)

            log_action(
                vault_path=self.vault_path,
                action_type="email_detected",
                actor="gmail_watcher",
                target=sample["id"],
                result="success",
                parameters={"sender": sample["sender"], "dry_run": True},
            )

        if new_items:
            logger.info("[DRY RUN] Generated %d sample email(s)", len(new_items))
        return new_items

    def create_action_file(self, item: dict) -> str:
        """Write a structured task file to Needs_Action/.

        Args:
            item: Dict with keys: id, sender, subject, snippet, date.

        Returns:
            Absolute path to the created task file.
        """
        msg_id = item["id"]
        sender = item.get("sender", "unknown")
        subject = item.get("subject", "(no subject)")
        snippet = item.get("snippet", "")
        date_str = item.get("date", "")

        now = datetime.now(timezone.utc)
        now_iso = now.isoformat()

        # Determine priority based on email_processor skill rules
        priority = self._assess_priority(sender, subject, snippet)

        # Build the task file content
        content = f"""---
id: {msg_id}
source_type: email
sender: "{sender}"
subject: "{subject}"
received_at: "{date_str}"
priority: {priority}
status: pending
created_at: {now_iso}
---

## Content

{snippet}

## Suggested Actions

- [ ] Review email content and assess urgency
- [ ] Determine if response is needed
- [ ] Create action plan for processing
"""

        # Write to Needs_Action/
        needs_action_dir = Path(self.vault_path) / "Needs_Action"
        needs_action_dir.mkdir(parents=True, exist_ok=True)

        filename = f"EMAIL_{msg_id}.md"
        filepath = needs_action_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        # Track as processed
        self.processed_ids.add(msg_id)

        # Audit log
        log_action(
            vault_path=self.vault_path,
            action_type="task_created",
            actor="gmail_watcher",
            target=str(filepath),
            result="success",
            parameters={
                "message_id": msg_id,
                "priority": priority,
                "dry_run": self.dry_run,
            },
        )

        logger.info("Created task file: %s (priority: %s)", filename, priority)
        return str(filepath)

    def _assess_priority(self, sender: str, subject: str, snippet: str) -> str:
        """Assess email priority per email_processor skill rules.

        Args:
            sender: Email sender address.
            subject: Email subject line.
            snippet: Email body snippet.

        Returns:
            Priority level: "urgent", "important", or "normal".
        """
        text = f"{subject} {snippet}".lower()

        # Financial detection → urgent
        financial_keywords = [
            "invoice", "payment", "expense", "subscription",
            "refund", "$", "amount due", "overdue",
        ]
        if any(kw in text for kw in financial_keywords):
            return "urgent"

        # Urgency keywords → urgent
        urgency_keywords = ["urgent", "asap", "deadline", "escalation"]
        if any(kw in text for kw in urgency_keywords):
            return "urgent"

        # Meeting/request keywords → important
        request_keywords = ["meeting", "schedule", "calendar", "request", "standup"]
        if any(kw in text for kw in request_keywords):
            return "important"

        # Newsletter/notification → normal
        notification_keywords = ["newsletter", "digest", "update", "unsubscribe"]
        if any(kw in text for kw in notification_keywords):
            return "normal"

        # Automated/noreply → normal
        sender_lower = sender.lower()
        if "noreply" in sender_lower or "no-reply" in sender_lower:
            return "normal"

        # Default for important-flagged Gmail messages
        return "important"
