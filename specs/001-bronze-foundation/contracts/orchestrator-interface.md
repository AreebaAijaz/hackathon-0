# Contract: Orchestrator Interface

**Version**: 1.0.0
**Date**: 2026-02-16

## Overview

The orchestrator monitors Needs_Action/ for new task files and
triggers Claude Code to process them. It manages the end-to-end
pipeline: read → process → plan → update → archive.

## Interface Definition

### Constructor

```
Orchestrator(vault_path: str, dry_run: bool = False)
```

**Parameters**:
- `vault_path`: Absolute path to the Obsidian vault root
- `dry_run`: If true, simulate processing without invoking Claude

**Preconditions**:
- `vault_path` MUST exist with required folder structure
- Claude Code CLI MUST be accessible on system PATH

---

### scan_needs_action() -> list[str]

**Description**: List all pending task files in Needs_Action/.

**Returns**: List of absolute file paths, sorted by creation time
(oldest first for FIFO processing).

**Filter**: Only `.md` files matching known patterns (EMAIL_*.md).

---

### process_task(task_path: str) -> dict

**Description**: Process a single task file through the pipeline.

**Parameters**:
- `task_path`: Absolute path to the task file

**Returns**:
```json
{
  "task_id": "string",
  "plan_path": "string (path to created plan)",
  "dashboard_updated": true,
  "archived": true,
  "flagged_for_human": false,
  "error": null
}
```

**Pipeline Steps**:
1. Read task file content
2. Read Company_Handbook.md rules
3. Invoke Claude Code with task + rules context
4. Write plan to Plans/PLAN_{task_id}_{timestamp}.md
5. Update Dashboard.md via dashboard_updater skill
6. Move task file from Needs_Action/ to Done/
7. Write audit log entries for each step

**Error Handling**:
- Claude Code timeout: Log error, skip task, leave in Needs_Action/
- File write error: Log error, rollback (don't move to Done/)
- Malformed task: Log error, skip (leave in Needs_Action/)

---

### update_dashboard() -> None

**Description**: Refresh Dashboard.md with current system state.

**Behavior**:
1. Count files in Needs_Action/ (pending tasks)
2. Read recent entries from Logs/ (last 5 actions)
3. Calculate daily stats from today's log file
4. Write updated Dashboard.md preserving structure

---

### run() -> None

**Description**: Main processing loop (one-shot or continuous).

**Behavior**:
1. Scan Needs_Action/ for pending tasks
2. Process each task in FIFO order
3. Update dashboard after all tasks processed
4. Log summary of processing cycle

**Guarantees**:
- Tasks processed in order (oldest first)
- Each task processed exactly once per run
- Dashboard always updated after processing
- All actions logged to audit trail
