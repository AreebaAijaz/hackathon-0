# Skill: Task Creator

**Version**: 1.0.0
**Purpose**: Generate structured task files from processed items

## Inputs

- **id**: Unique identifier for the source item (e.g., Gmail message ID)
- **source_type**: Origin type — "email", "manual", or other watcher type
- **sender**: Who sent the item (email address or name)
- **subject**: Title or subject of the item
- **received_at**: ISO 8601 timestamp of when the item was received
- **content**: Body text or snippet of the item
- **priority**: Assessed priority level from email_processor skill

## Outputs

- A markdown file written to `Needs_Action/` with:
  - YAML frontmatter containing all metadata fields
  - Body section with content
  - Suggested actions checklist

## Rules

1. **Filename Pattern**: `{SOURCE_TYPE}_{id}.md`
   - Example: `EMAIL_18d4f2a3b5c.md`
2. **Required Frontmatter Fields**: id, source_type, sender, subject,
   received_at, priority, status, created_at
3. **Status**: MUST be "pending" on creation
4. **created_at**: MUST be set to current ISO 8601 UTC timestamp
5. **Content Preservation**: Include the full content/snippet — never
   truncate or modify the original text
6. **Suggested Actions**: Include at least 3 actionable checklist items

## Examples

### Example 1: Email Task File

**Input**:
```
id: 18d4f2a3b5c
source_type: email
sender: accounting@acmecorp.com
subject: Invoice #1234 - Payment Due Feb 20
received_at: 2026-02-17T10:30:00Z
content: Please find attached invoice #1234 for $2,500.00 due by Feb 20th.
priority: urgent
```

**Output** (`Needs_Action/EMAIL_18d4f2a3b5c.md`):
```markdown
---
id: 18d4f2a3b5c
source_type: email
sender: accounting@acmecorp.com
subject: "Invoice #1234 - Payment Due Feb 20"
received_at: 2026-02-17T10:30:00Z
priority: urgent
status: pending
created_at: 2026-02-17T10:32:00Z
---

## Content

Please find attached invoice #1234 for $2,500.00 due by Feb 20th.

## Suggested Actions

- [ ] Review invoice amount and due date
- [ ] Determine if payment is approved
- [ ] Create action plan for processing
```
