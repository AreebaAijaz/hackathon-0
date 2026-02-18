# Contract: BaseWatcher Interface

**Version**: 1.0.0
**Date**: 2026-02-16

## Overview

All watchers MUST implement this interface. The BaseWatcher
abstract class defines the contract that Gmail Watcher (and
future watchers) must follow.

## Interface Definition

### Constructor

```
BaseWatcher(vault_path: str, check_interval: int = 120)
```

**Parameters**:
- `vault_path`: Absolute path to the Obsidian vault root
- `check_interval`: Seconds between check cycles (default: 120)

**Preconditions**:
- `vault_path` MUST exist and contain the required folder structure
- `check_interval` MUST be >= 30 (minimum 30 seconds)

**Postconditions**:
- Signal handlers registered for graceful shutdown
- Logger initialized with structured JSON format

---

### check_for_updates() -> list[dict]

**Description**: Poll the external source for new items.

**Returns**: List of dicts, each representing a new item:
```json
{
  "id": "string (unique identifier)",
  "source_type": "string (email|file|manual)",
  "title": "string",
  "content": "string",
  "metadata": {}
}
```

**Error Handling**:
- Network errors: Raise exception (BaseWatcher retries with backoff)
- Auth errors: Raise `AuthenticationError` (halts watcher)
- Empty result: Return empty list `[]`

---

### create_action_file(item: dict) -> str

**Description**: Write a structured markdown file to Needs_Action/.

**Parameters**:
- `item`: Dict from `check_for_updates()` result

**Returns**: Absolute path to the created file.

**File Format**:
```markdown
---
id: {item.id}
source_type: {item.source_type}
sender: {from metadata}
subject: {item.title}
received_at: {ISO 8601}
priority: {assessed priority}
status: pending
created_at: {ISO 8601 now}
---

## Content

{item.content}

## Suggested Actions

- [ ] {action 1}
- [ ] {action 2}
```

**Postconditions**:
- File exists at `{vault_path}/Needs_Action/{filename}.md`
- Item ID recorded in processed set (deduplication)
- Audit log entry written

---

### run() -> None

**Description**: Main loop. Calls check_for_updates() and
create_action_file() on each cycle.

**Behavior**:
1. Set `running = True`
2. While `running`:
   a. Call `check_for_updates()` with retry (3 attempts, exponential backoff)
   b. For each new item, call `create_action_file(item)`
   c. Log results
   d. Sleep for `check_interval` seconds
3. On signal (SIGINT/SIGTERM/SIGBREAK): set `running = False`
4. Log shutdown and exit cleanly

**Guarantees**:
- Never crashes on transient errors (retries up to 3 times)
- Halts on authentication errors (requires human intervention)
- Logs every action and error
- No duplicate files for the same item ID
