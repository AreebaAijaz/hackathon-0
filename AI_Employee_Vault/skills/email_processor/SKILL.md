# Skill: Email Processor

**Version**: 1.0.0
**Purpose**: Categorize and assess priority of incoming emails

## Inputs

- **sender**: Email address of the sender (e.g., "accounting@company.com")
- **subject**: Email subject line
- **snippet**: First ~200 characters of email body
- **headers**: Raw email headers (optional, for additional context)

## Outputs

- **priority**: One of "urgent", "important", "normal"
- **category**: One of "financial", "request", "notification", "personal"
- **suggested_actions**: List of recommended next steps
- **requires_human**: Boolean — true if human review is needed

## Rules

1. **Financial Detection**: If the email mentions invoices, payments,
   expenses, subscriptions, refunds, or monetary amounts, set
   `category: financial` and `requires_human: true`.
2. **Priority Assessment**:
   - `urgent`: Time-sensitive items (deadlines within 24h, escalations,
     financial matters)
   - `important`: Items requiring action but not immediately
     (meeting requests, project updates)
   - `normal`: Informational items (newsletters, notifications,
     automated reports)
3. **Sender Domain Signals**:
   - Known business domains → higher priority
   - Automated/noreply addresses → lower priority
   - Unknown senders → flag for review
4. **Subject Keyword Signals**:
   - "urgent", "asap", "deadline", "overdue" → priority: urgent
   - "invoice", "payment", "expense" → category: financial
   - "meeting", "schedule", "calendar" → category: request
   - "newsletter", "update", "digest" → category: notification

## Examples

### Example 1: Financial Email

**Input**:
```
sender: accounting@acmecorp.com
subject: Invoice #1234 - Payment Due Feb 20
snippet: Please find attached invoice #1234 for $2,500.00 due by February 20th...
```

**Output**:
```
priority: urgent
category: financial
requires_human: true
suggested_actions:
  - Review invoice amount and due date
  - Verify vendor relationship
  - Flag for human approval before any payment action
```

### Example 2: Meeting Request

**Input**:
```
sender: sarah@team.com
subject: Team standup moved to 3pm Thursday
snippet: Hi, just a heads up that our weekly standup has been rescheduled...
```

**Output**:
```
priority: important
category: request
requires_human: false
suggested_actions:
  - Update calendar entry for weekly standup
  - Acknowledge the schedule change
  - No immediate action required
```
