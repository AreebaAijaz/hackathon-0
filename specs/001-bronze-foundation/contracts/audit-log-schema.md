# Contract: Audit Log Schema

**Version**: 1.0.0
**Date**: 2026-02-16

## Overview

Defines the structured JSON format for all audit log entries.
Logs are append-only, date-partitioned files in
`AI_Employee_Vault/Logs/`.

## File Format

**Location**: `AI_Employee_Vault/Logs/YYYY-MM-DD.json`
**Format**: Newline-delimited JSON (NDJSON) - one JSON object
per line, no wrapping array.

## Schema

```json
{
  "timestamp": "2026-02-16T14:30:00.000Z",
  "action_type": "email_detected",
  "actor": "gmail_watcher",
  "target": "AI_Employee_Vault/Needs_Action/EMAIL_abc123.md",
  "parameters": {
    "sender": "user@example.com",
    "subject": "Important meeting tomorrow"
  },
  "result": "success",
  "error_message": null
}
```

## Field Definitions

| Field         | Type    | Required | Constraints                      |
|---------------|---------|----------|----------------------------------|
| timestamp     | string  | yes      | ISO 8601 with timezone           |
| action_type   | string  | yes      | One of defined enum values       |
| actor         | string  | yes      | Component name                   |
| target        | string  | yes      | File path or endpoint            |
| parameters    | object  | no       | Additional context, free-form    |
| result        | string  | yes      | "success" or "failure"           |
| error_message | string  | no       | Required when result = "failure" |

## Action Type Enum

| Value              | Actor           | Description                 |
|--------------------|-----------------|-----------------------------|
| email_detected     | gmail_watcher   | New important email found   |
| task_created       | gmail_watcher   | Task file written           |
| task_processed     | orchestrator    | Task read and analyzed      |
| plan_created       | orchestrator    | Plan file written           |
| dashboard_updated  | orchestrator    | Dashboard.md refreshed      |
| task_archived      | orchestrator    | Task moved to Done/         |
| watcher_started    | gmail_watcher   | Watcher process began       |
| watcher_stopped    | gmail_watcher   | Watcher process ended       |
| watcher_error      | gmail_watcher   | Error during check cycle    |
| auth_error         | gmail_watcher   | Authentication failure      |

## Invariants

1. Files MUST NOT be modified after creation (append-only)
2. Every system action MUST produce at least one log entry
3. Failed actions MUST include `error_message`
4. `timestamp` MUST use UTC timezone
5. New entries MUST be appended to the current day's file
