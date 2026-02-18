# Skill: Plan Generator

**Version**: 1.0.0
**Purpose**: Create action plans for processed tasks

## Inputs

- **task_content**: Full content of the task file from Needs_Action/
- **task_id**: Unique identifier from the task's frontmatter
- **handbook_rules**: Content of Company_Handbook.md

## Outputs

- A plan markdown file written to `Plans/` with:
  - YAML frontmatter (plan_id, task_reference, created_at, priority,
    requires_human)
  - Task summary section
  - Analysis section
  - Recommended actions (numbered list)
  - Priority assessment with rationale

## Rules

1. **Filename Pattern**: `PLAN_{task_id}_{YYYYMMDD}.md`
   - Example: `PLAN_18d4f2a3b5c_20260217.md`
2. **Task Reference**: MUST include the source task_id in frontmatter
3. **Financial Flagging**: If the task involves financial matters,
   MUST set `requires_human: true` in frontmatter
4. **Recommended Actions**: MUST be numbered, specific, and
   actionable — not vague suggestions
5. **Handbook Compliance**: All recommendations MUST comply with
   Company_Handbook.md rules (especially rules 2 and 5)
6. **Priority Assessment**: MUST include rationale explaining why
   the priority level was assigned

## Examples

### Example 1: Financial Email Plan

**Input**:
```
task_id: 18d4f2a3b5c
task_content: Invoice #1234 from accounting@acmecorp.com for $2,500
handbook_rules: [Company Handbook content]
```

**Output** (`Plans/PLAN_18d4f2a3b5c_20260217.md`):
```markdown
---
plan_id: PLAN_18d4f2a3b5c_20260217
task_reference: 18d4f2a3b5c
created_at: 2026-02-17T10:35:00Z
priority: urgent
requires_human: true
---

## Task Summary

Received invoice #1234 from accounting@acmecorp.com for $2,500.00
with a payment due date of February 20, 2026.

## Analysis

This is a financial matter involving a payment obligation. Per
Company Handbook Rule 2 (Financial Flagging), all financial items
must be flagged for human review. The due date is within 3 days,
making this time-sensitive.

## Recommended Actions

1. Review the invoice amount ($2,500.00) and verify it matches
   any existing purchase orders or agreements
2. Confirm the vendor (acmecorp.com) is a known and approved vendor
3. Flag for human approval — payment cannot be auto-approved
   (per Handbook Rule 2)
4. Once approved, process payment before the Feb 20 deadline
5. Archive the original email task to Done/ after resolution

## Priority Assessment

**Priority**: Urgent

**Rationale**: Financial obligation with a deadline within 3 days.
Per Handbook Rule 3, urgent items with near-term deadlines take
highest priority. Additionally, Handbook Rule 2 requires human
review for all financial matters, so prompt attention ensures
the human reviewer has adequate time to act.
```

### Example 2: Meeting Request Plan

**Input**:
```
task_id: 29e5g3b4c6d
task_content: Team standup moved to 3pm Thursday from sarah@team.com
handbook_rules: [Company Handbook content]
```

**Output** (`Plans/PLAN_29e5g3b4c6d_20260217.md`):
```markdown
---
plan_id: PLAN_29e5g3b4c6d_20260217
task_reference: 29e5g3b4c6d
created_at: 2026-02-17T11:00:00Z
priority: important
requires_human: false
---

## Task Summary

Schedule change notification: weekly team standup moved to 3pm
Thursday, sent by sarah@team.com.

## Analysis

Routine scheduling update from a known team member. No financial
implications. Simple calendar adjustment required.

## Recommended Actions

1. Note the new standup time: Thursday 3pm (changed from previous)
2. Check for calendar conflicts at the new time
3. Acknowledge the schedule change to sarah@team.com

## Priority Assessment

**Priority**: Important

**Rationale**: Schedule changes affect team coordination but are
not time-critical for immediate action. Classified as important
per Handbook Rule 3.
```
