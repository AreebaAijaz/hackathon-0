# Data Model: Bronze Tier Foundation

**Feature**: `001-bronze-foundation`
**Date**: 2026-02-16
**Source**: spec.md Key Entities + research.md findings

## Entities

### 1. Task File

A markdown document in the vault representing an actionable item
detected by a watcher.

**Location**: `AI_Employee_Vault/Needs_Action/` (pending),
`AI_Employee_Vault/Done/` (archived)

**Filename Pattern**: `EMAIL_{message_id}.md`

**Fields** (YAML frontmatter):

| Field        | Type     | Required | Description                         |
|--------------|----------|----------|-------------------------------------|
| id           | string   | yes      | Unique message identifier           |
| source_type  | string   | yes      | Origin: "email", "manual"           |
| sender       | string   | yes      | Email sender address                |
| subject      | string   | yes      | Email subject line                  |
| received_at  | datetime | yes      | ISO 8601 timestamp of receipt       |
| priority     | string   | yes      | "urgent", "important", "normal"     |
| status       | string   | yes      | "pending", "processing", "done"     |
| created_at   | datetime | yes      | ISO 8601 timestamp of file creation |

**Body Content**:
- Email snippet (first ~200 characters)
- Full email body (if available)
- Suggested actions checklist

**State Transitions**:
```
[created] → pending (in Needs_Action/)
pending → processing (being read by pipeline)
processing → done (moved to Done/)
```

**Validation Rules**:
- `id` MUST be unique across all task files
- `source_type` MUST be one of: "email", "manual"
- `priority` MUST be one of: "urgent", "important", "normal"
- `status` MUST be one of: "pending", "processing", "done"
- `received_at` and `created_at` MUST be valid ISO 8601

---

### 2. Plan

A markdown document containing the AI's analysis and recommended
actions for a processed task.

**Location**: `AI_Employee_Vault/Plans/`

**Filename Pattern**: `PLAN_{task_id}_{timestamp}.md`

**Fields** (YAML frontmatter):

| Field            | Type     | Required | Description                        |
|------------------|----------|----------|------------------------------------|
| plan_id          | string   | yes      | Unique plan identifier             |
| task_reference   | string   | yes      | ID of the source task file         |
| created_at       | datetime | yes      | ISO 8601 timestamp                 |
| priority         | string   | yes      | Assessed priority level            |
| requires_human   | boolean  | yes      | Whether human review is needed     |

**Body Content**:
- Task summary (what was received)
- Analysis (what the AI determined)
- Recommended actions (numbered list)
- Priority assessment with rationale
- Flagged items (financial, sensitive)

**Validation Rules**:
- `task_reference` MUST match an existing or archived task file ID
- `requires_human` MUST be true for financial matters

---

### 3. Audit Log Entry

A structured JSON record of every system action. Entries are
append-only within date-partitioned files.

**Location**: `AI_Employee_Vault/Logs/`

**Filename Pattern**: `YYYY-MM-DD.json` (one file per day,
newline-delimited JSON)

**Fields**:

| Field            | Type   | Required | Description                          |
|------------------|--------|----------|--------------------------------------|
| timestamp        | string | yes      | ISO 8601 datetime                    |
| action_type      | string | yes      | Action category (see enum below)     |
| actor            | string | yes      | "gmail_watcher", "orchestrator", etc |
| target           | string | yes      | File path or endpoint acted upon     |
| parameters       | object | no       | Additional context (key-value)       |
| result           | string | yes      | "success" or "failure"               |
| error_message    | string | no       | Error details if result is failure   |

**Action Types (enum)**:
- `email_detected` - Watcher found new email
- `task_created` - Task file written to Needs_Action/
- `task_processed` - Pipeline read and analyzed a task
- `plan_created` - Plan.md written to Plans/
- `dashboard_updated` - Dashboard.md refreshed
- `task_archived` - Task file moved to Done/
- `watcher_started` - Watcher process began
- `watcher_stopped` - Watcher process ended
- `watcher_error` - Watcher encountered an error
- `auth_error` - Authentication failure

**Validation Rules**:
- `timestamp` MUST be valid ISO 8601
- `action_type` MUST be from the defined enum
- `result` MUST be "success" or "failure"
- Entries MUST NOT be modified after creation (append-only)

---

### 4. Agent Skill

A documented AI capability package. Skills are markdown-based
documentation files that define how Claude Code should perform
specific tasks.

**Location**: `AI_Employee_Vault/skills/{skill_name}/`

**Structure**:
```
skills/{skill_name}/
└── SKILL.md
```

**SKILL.md Fields**:

| Section       | Required | Description                          |
|---------------|----------|--------------------------------------|
| Name          | yes      | Skill identifier                     |
| Purpose       | yes      | What this skill does                 |
| Inputs        | yes      | Expected input format/data           |
| Outputs       | yes      | What the skill produces              |
| Rules         | yes      | Constraints and guidelines           |
| Examples      | yes      | At least one usage example           |
| Version       | yes      | Semantic version                     |

**Required Skills (Bronze)**:
1. `email_processor` - Categorize and prioritize email data
2. `task_creator` - Generate structured task files
3. `dashboard_updater` - Refresh Dashboard.md
4. `plan_generator` - Create action plans from tasks

---

### 5. Dashboard State

The Dashboard.md file serves as a live status display. Its
content is regenerated on each update cycle.

**Location**: `AI_Employee_Vault/Dashboard.md`

**Sections**:

| Section          | Description                              |
|------------------|------------------------------------------|
| System Status    | Last updated, list of active watchers    |
| Pending Tasks    | Count of files in Needs_Action/          |
| Recent Activity  | Last 5 processed items (newest first)    |
| Quick Stats      | Emails processed today, tasks completed  |

**Update Rules**:
- `last_updated` MUST be set to current ISO 8601 on every write
- `pending_tasks` MUST match actual file count in Needs_Action/
- `recent_activity` MUST show last 5 items, sorted newest-first
- Updates MUST NOT corrupt existing content

---

## Entity Relationships

```
Gmail Inbox
    │
    ▼ (watcher detects)
Task File [Needs_Action/]
    │
    ├──▶ Audit Log Entry (email_detected, task_created)
    │
    ▼ (pipeline processes)
Plan [Plans/]
    │
    ├──▶ Audit Log Entry (task_processed, plan_created)
    │
    ▼ (dashboard refresh)
Dashboard State
    │
    ├──▶ Audit Log Entry (dashboard_updated)
    │
    ▼ (archive)
Task File [Done/]
    │
    └──▶ Audit Log Entry (task_archived)
```

- One Task File produces exactly one Plan
- One Task File generates multiple Audit Log Entries (lifecycle)
- Dashboard State aggregates data from all Task Files
- Agent Skills are referenced during processing (not stored as data)
