"""Orchestrator for the AI Employee task processing pipeline.

Monitors Needs_Action/ for pending tasks, invokes Claude Code to generate
plans, updates the Dashboard, and archives completed tasks to Done/.

Pipeline: read task → build prompt → invoke Claude → write plan → update dashboard → archive
"""

import json
import logging
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path

from src.audit_logger import log_action
from src.prompt_template import build_processing_prompt
from src.utils.claude_runner import invoke_claude, invoke_claude_dry_run
from src.utils.vault import count_files, list_files, move_file

logger = logging.getLogger(__name__)


class Orchestrator:
    """Processes task files from the vault's Needs_Action/ directory.

    Args:
        vault_path: Absolute path to the Obsidian vault root.
        dry_run: If True, simulate processing without invoking Claude Code.
    """

    def __init__(self, vault_path: str, dry_run: bool = False):
        self.vault_path = vault_path
        self.dry_run = dry_run

    def scan_needs_action(self) -> list[str]:
        """List pending task files in Needs_Action/ sorted oldest-first (FIFO).

        Returns:
            List of absolute file paths to .md task files.
        """
        needs_action_dir = os.path.join(self.vault_path, "Needs_Action")
        files = list_files(needs_action_dir, extension=".md")
        if files:
            logger.info("Found %d pending task(s) in Needs_Action/", len(files))
        else:
            logger.debug("No pending tasks in Needs_Action/")
        return files

    def process_task(self, task_path: str) -> dict:
        """Process a single task file through the full pipeline.

        Args:
            task_path: Absolute path to the task file.

        Returns:
            Dict with keys: task_id, plan_path, dashboard_updated,
            archived, flagged_for_human, error.
        """
        task_id = Path(task_path).stem
        result = {
            "task_id": task_id,
            "plan_path": None,
            "dashboard_updated": False,
            "archived": False,
            "flagged_for_human": False,
            "error": None,
        }

        try:
            # Step 1: Read task file
            logger.info("Processing task: %s", task_id)
            with open(task_path, "r", encoding="utf-8") as f:
                task_content = f.read()

            log_action(
                vault_path=self.vault_path,
                action_type="task_processed",
                actor="orchestrator",
                target=task_path,
                result="success",
                parameters={"step": "read_task", "dry_run": self.dry_run},
            )

            # Step 2: Read Company Handbook rules
            handbook_path = os.path.join(self.vault_path, "Company_Handbook.md")
            handbook_rules = ""
            if os.path.isfile(handbook_path):
                with open(handbook_path, "r", encoding="utf-8") as f:
                    handbook_rules = f.read()

            # Step 3: Read skill documentation
            skill_docs = self._load_skill_docs()

            # Step 4: Build prompt and invoke Claude Code
            prompt = build_processing_prompt(task_content, handbook_rules, skill_docs)

            if self.dry_run:
                plan_data = invoke_claude_dry_run(prompt, task_content)
                logger.info("[DRY RUN] Simulated Claude Code response for %s", task_id)
            else:
                plan_data = invoke_claude(prompt, self.vault_path)
                logger.info("Claude Code processed task: %s", task_id)

            # Step 5: Write plan file
            plan_path = self._write_plan(task_id, plan_data)
            result["plan_path"] = plan_path
            result["flagged_for_human"] = plan_data.get("requires_human", False)

            log_action(
                vault_path=self.vault_path,
                action_type="plan_created",
                actor="orchestrator",
                target=plan_path,
                result="success",
                parameters={
                    "task_id": task_id,
                    "requires_human": plan_data.get("requires_human", False),
                    "dry_run": self.dry_run,
                },
            )

            # Step 6: Update dashboard
            self.update_dashboard()
            result["dashboard_updated"] = True

            # Step 7: Archive task to Done/
            done_dir = os.path.join(self.vault_path, "Done")
            os.makedirs(done_dir, exist_ok=True)
            archived_path = move_file(task_path, done_dir)
            result["archived"] = True

            log_action(
                vault_path=self.vault_path,
                action_type="task_archived",
                actor="orchestrator",
                target=archived_path,
                result="success",
                parameters={"task_id": task_id, "dry_run": self.dry_run},
            )

            logger.info("Task %s processed and archived", task_id)

        except Exception as e:
            result["error"] = str(e)
            logger.error("Failed to process task %s: %s", task_id, e)
            log_action(
                vault_path=self.vault_path,
                action_type="watcher_error",
                actor="orchestrator",
                target=task_path,
                result="failure",
                error_message=str(e),
            )

        return result

    def _load_skill_docs(self) -> dict[str, str]:
        """Load all SKILL.md files from the vault's skills/ directory.

        Returns:
            Dict mapping skill name to SKILL.md content.
        """
        skills_dir = Path(self.vault_path) / "skills"
        skill_docs = {}

        if not skills_dir.is_dir():
            logger.warning("Skills directory not found: %s", skills_dir)
            return skill_docs

        for skill_dir in skills_dir.iterdir():
            if not skill_dir.is_dir():
                continue
            skill_md = skill_dir / "SKILL.md"
            if skill_md.is_file():
                with open(skill_md, "r", encoding="utf-8") as f:
                    skill_docs[skill_dir.name] = f.read()

        logger.info("Loaded %d skill doc(s)", len(skill_docs))
        return skill_docs

    def _write_plan(self, task_id: str, plan_data: dict) -> str:
        """Write a plan file to Plans/ directory.

        Args:
            task_id: Source task identifier.
            plan_data: Dict with plan_title, analysis, recommended_actions,
                       priority, requires_human, flagged_items.

        Returns:
            Absolute path to the created plan file.
        """
        now = datetime.now(timezone.utc)
        timestamp = now.strftime("%Y%m%d")
        now_iso = now.isoformat()

        plan_title = plan_data.get("plan_title", f"Plan for {task_id}")
        analysis = plan_data.get("analysis", "No analysis provided.")
        actions = plan_data.get("recommended_actions", [])
        priority = plan_data.get("priority", "normal")
        requires_human = plan_data.get("requires_human", False)
        flagged_items = plan_data.get("flagged_items", [])

        # Build numbered actions list
        actions_md = ""
        for i, action in enumerate(actions, 1):
            actions_md += f"{i}. {action}\n"

        # Build flagged items section
        flagged_md = ""
        if flagged_items:
            flagged_md = "\n## Flagged Items\n\n"
            for item in flagged_items:
                flagged_md += f"- {item}\n"

        content = f"""---
plan_id: PLAN_{task_id}_{timestamp}
task_reference: {task_id}
created_at: {now_iso}
priority: {priority}
requires_human: {str(requires_human).lower()}
---

# {plan_title}

## Analysis

{analysis}

## Recommended Actions

{actions_md}
## Priority Assessment

**Priority**: {priority}
**Requires Human Review**: {"Yes" if requires_human else "No"}
{flagged_md}"""

        plans_dir = Path(self.vault_path) / "Plans"
        plans_dir.mkdir(parents=True, exist_ok=True)

        filename = f"PLAN_{task_id}_{timestamp}.md"
        filepath = plans_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        logger.info("Created plan: %s", filename)
        return str(filepath)

    def update_dashboard(self):
        """Refresh Dashboard.md with current vault state.

        Updates: last_updated timestamp, pending task count,
        recent activity (last 5), and quick stats.
        """
        dashboard_path = os.path.join(self.vault_path, "Dashboard.md")
        needs_action_dir = os.path.join(self.vault_path, "Needs_Action")
        done_dir = os.path.join(self.vault_path, "Done")
        logs_dir = os.path.join(self.vault_path, "Logs")

        now = datetime.now(timezone.utc)
        now_iso = now.isoformat()
        today_str = now.strftime("%Y-%m-%d")

        # Count pending tasks
        pending_count = count_files(needs_action_dir, extension=".md")

        # Count completed tasks today (Done/ files modified today)
        done_today = 0
        done_path = Path(done_dir)
        if done_path.is_dir():
            for f in done_path.iterdir():
                if f.is_file() and f.suffix == ".md":
                    mtime = datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc)
                    if mtime.strftime("%Y-%m-%d") == today_str:
                        done_today += 1

        # Read today's log for recent activity and email count
        emails_today = 0
        recent_activity = []
        log_file = Path(logs_dir) / f"{today_str}.json"
        if log_file.is_file():
            with open(log_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                        if entry.get("action_type") == "email_detected":
                            emails_today += 1
                        recent_activity.append(entry)
                    except json.JSONDecodeError:
                        continue

        # Take last 5 entries, newest first
        recent_activity = recent_activity[-5:][::-1]

        # Build recent activity table rows
        activity_rows = ""
        for entry in recent_activity:
            ts = entry.get("timestamp", "")
            # Truncate timestamp to time only
            if "T" in ts:
                time_part = ts.split("T")[1][:8]
            else:
                time_part = ts[:19]
            action = entry.get("action_type", "unknown")
            target = entry.get("target", "")
            # Shorten target path for display
            if "/" in target or "\\" in target:
                target = Path(target).name
            activity_rows += f"| {time_part} | {action} | {target} |\n"

        if not activity_rows:
            activity_rows = "| - | No activity recorded | - |\n"

        content = f"""---
title: Dashboard
date: {today_str}
tags: [dashboard, status]
---

# Dashboard

## System Status

| Field | Value |
|-------|-------|
| last_updated | {now_iso} |
| active_watchers | gmail_watcher |

## Pending Tasks

**Count**: {pending_count}

> Check `Needs_Action/` for pending items.

## Recent Activity

| Time | Action | Details |
|------|--------|---------|
{activity_rows}
## Quick Stats

| Metric | Value |
|--------|-------|
| emails_processed_today | {emails_today} |
| tasks_completed_today | {done_today} |
"""

        with open(dashboard_path, "w", encoding="utf-8") as f:
            f.write(content)

        log_action(
            vault_path=self.vault_path,
            action_type="dashboard_updated",
            actor="orchestrator",
            target=dashboard_path,
            result="success",
            parameters={
                "pending_tasks": pending_count,
                "emails_today": emails_today,
                "done_today": done_today,
            },
        )

        logger.info(
            "Dashboard updated (pending=%d, emails=%d, done=%d)",
            pending_count,
            emails_today,
            done_today,
        )

    def run_once(self):
        """Process all pending tasks once, then exit.

        Returns:
            List of processing result dicts.
        """
        tasks = self.scan_needs_action()
        results = []
        for task_path in tasks:
            result = self.process_task(task_path)
            results.append(result)
        return results

    def run(self, poll_interval: int = 30):
        """Continuously poll Needs_Action/ and process new tasks.

        Args:
            poll_interval: Seconds between scan cycles (default: 30).
        """
        logger.info(
            "Orchestrator started (poll_interval=%ds, dry_run=%s)",
            poll_interval,
            self.dry_run,
        )

        import signal

        running = True

        def _shutdown(signum, frame):
            nonlocal running
            logger.info("Orchestrator received signal %s, shutting down...", signum)
            running = False

        signal.signal(signal.SIGINT, _shutdown)
        signal.signal(signal.SIGTERM, _shutdown)
        if hasattr(signal, "SIGBREAK"):
            signal.signal(signal.SIGBREAK, _shutdown)

        try:
            while running:
                tasks = self.scan_needs_action()
                for task_path in tasks:
                    if not running:
                        break
                    self.process_task(task_path)

                if running:
                    time.sleep(poll_interval)
        finally:
            logger.info("Orchestrator stopped")
