# Skill: Dashboard Updater

**Version**: 1.0.0
**Purpose**: Refresh Dashboard.md with current system state

## Inputs

- **vault_path**: Path to the vault root directory
- **action_performed**: Description of the latest action (for Recent Activity)
- **action_details**: Additional details about the action

## Outputs

- Updated `Dashboard.md` file with current:
  - Last Updated timestamp
  - Pending Tasks count
  - Recent Activity entries (last 5)
  - Quick Stats counters

## Rules

1. **Last Updated**: MUST be set to current ISO 8601 UTC timestamp
   on every update.
2. **Pending Tasks Count**: MUST match the actual number of `.md`
   files in `Needs_Action/` — count the directory, do not rely on
   a stored counter.
3. **Recent Activity**: Show the last 5 actions, newest first.
   When adding a new entry, prepend it and remove the oldest if
   there are more than 5.
4. **Quick Stats**: Increment the appropriate counter:
   - `Emails Processed` — incremented when a new email task is created
   - `Tasks Completed` — incremented when a task moves to Done/
5. **Section Preservation**: MUST NOT delete or reorder existing
   sections. Only update values within sections.
6. **Active Watchers**: List watchers that are currently running.
   Set to "None" if no watchers are active.

## Examples

### Example 1: After Processing a Task

**Input**:
```
action_performed: Task processed
action_details: EMAIL_18d4f2a3b5c - Invoice from accounting@acmecorp.com
```

**Output** (updated Dashboard.md sections):
```markdown
## System Status

| Field            | Value          |
|------------------|----------------|
| **Last Updated** | 2026-02-17T10:35:00Z |
| **Active Watchers** | gmail_watcher |
| **System State** | Running        |

## Pending Tasks

**Count**: 2

## Recent Activity

| Time                 | Action          | Details                                    |
|----------------------|-----------------|--------------------------------------------|
| 2026-02-17T10:35:00Z | Task processed  | EMAIL_18d4f2a3b5c - Invoice from accounting |
| 2026-02-17T10:32:00Z | Email detected  | New important email from sarah@team.com    |

## Quick Stats

| Metric                    | Today |
|---------------------------|-------|
| **Emails Processed**      | 3     |
| **Tasks Completed**       | 1     |
```
