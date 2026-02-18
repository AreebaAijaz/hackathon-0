<!--
  Sync Impact Report
  ===================
  Version change: N/A → 1.0.0
  Bump rationale: MAJOR - Initial constitution creation

  Added principles:
    - I. Local-First Privacy
    - II. Human-in-the-Loop Safety
    - III. Audit Everything
    - IV. Graceful Failure Recovery
    - V. Skills-First Reusability
    - VI. Progressive Enhancement
    - VII. Security Non-Negotiable

  Added sections:
    - Core Principles (7 principles)
    - Technology Stack & Architecture Constraints
    - Development Workflow & Quality Gates
    - Governance

  Removed sections: None (initial creation)

  Templates requiring updates:
    - .specify/templates/plan-template.md ✅ No changes needed
      (Constitution Check section references this file dynamically)
    - .specify/templates/spec-template.md ✅ No changes needed
      (Spec template is principle-agnostic)
    - .specify/templates/tasks-template.md ✅ No changes needed
      (Task phases align with progressive enhancement principle)

  Follow-up TODOs: None
-->

# Personal AI Employee (Digital FTE) Constitution

## Core Principles

### I. Local-First Privacy

All sensitive data MUST remain on the local machine by default.
Credentials, personal information, and vault contents MUST NOT
be transmitted to external services without explicit user consent.

- The Obsidian vault is the canonical local data store.
- `.env` files MUST be gitignored; secrets MUST use environment
  variables.
- Cloud sync (Platinum tier) MUST exclude secrets and credentials.
- Data at rest: consider vault encryption for sensitive content.

**Rationale**: The AI Employee handles personal and business
affairs containing private information. Local-first ensures the
user retains full control over their data.

### II. Human-in-the-Loop Safety

Every sensitive action MUST require explicit human approval before
execution. No autonomous action may modify external state (send
emails, make payments, post publicly) without passing through the
approval workflow.

- Sensitive actions create approval files in `/Pending_Approval/`.
- Human reviews and moves to `/Approved/` or `/Rejected/`.
- Auto-approve thresholds are narrowly scoped:
  - Email replies: known contacts only.
  - Payments: < $50 recurring only.
  - Social media: scheduled posts only.
  - File operations: create/read only (never delete without
    approval).
- The orchestrator MUST watch `/Approved/` before triggering MCP
  execution.

**Rationale**: Autonomous AI acting on behalf of a person carries
real-world consequences. HITL prevents irreversible mistakes.

### III. Audit Everything

Every action taken by the AI Employee MUST be logged with a
structured audit record. Logs MUST capture timestamp, action type,
actor, target, parameters, approval status, and result.

- Logs written to `/Logs/` in JSON format (ISO 8601 timestamps).
- Log schema:
  ```json
  {
    "timestamp": "ISO8601",
    "action_type": "email_send|payment|post|...",
    "actor": "claude_code",
    "target": "recipient/endpoint",
    "parameters": {},
    "approval_status": "approved|auto",
    "approved_by": "human|auto",
    "result": "success|failure"
  }
  ```
- Logs MUST NOT be deleted or modified after creation.
- Weekly Business Audit (Gold tier) consumes logs for CEO Briefing
  generation.

**Rationale**: Accountability requires a complete, immutable trail
of all AI actions for review, debugging, and trust-building.

### IV. Graceful Failure Recovery

The system MUST handle errors without data loss or silent failure.
Every error category MUST have a defined recovery strategy.

- **Transient** (network timeout): Exponential backoff retry.
- **Authentication** (expired token): Alert human, pause
  operations.
- **Logic** (misinterpretation): Route to human review queue.
- **Data** (corrupted file): Quarantine file + alert.
- **System** (orchestrator crash): Watchdog auto-restart via PM2.
- Watchers MUST survive TTY/SSH session closes, unhandled
  exceptions, and system reboots.
- The Ralph Wiggum loop MUST enforce a max iteration cap
  (default: 10) to prevent infinite retries.

**Rationale**: A 24/7 autonomous employee cannot afford to crash
silently. Graceful degradation preserves system trust and uptime.

### V. Skills-First Reusability

ALL AI functionality MUST be implemented as Agent Skills. Skills
are the atomic unit of capability in the system.

- Each skill lives in the `/skills/` directory.
- Each skill MUST have clear inputs, outputs, and usage examples.
- Skills MUST be independently testable and documented.
- Claude Code references skills for consistent, repeatable
  behavior.
- Skills are version-controlled and shareable across projects.

**Rationale**: Skills-first architecture ensures capabilities are
composable, auditable, and reusable rather than buried in ad-hoc
prompts or scripts.

### VI. Progressive Enhancement

Development MUST follow a tiered approach: Bronze, Silver, Gold,
Platinum. Each tier builds on the previous one without breaking
existing functionality.

- **Bronze** (Foundation): Vault structure, one watcher, Claude
  Code integration, basic folder workflow, all skills.
- **Silver** (Functional Assistant): Multiple watchers, one MCP
  server, HITL approval workflow, scheduled automation.
- **Gold** (Autonomous Employee): Cross-domain integration, Odoo,
  social media, weekly audit, Ralph Wiggum loop, error recovery.
- **Platinum** (Cloud + Local): 24/7 cloud VM, vault sync,
  work-zone specialization, agent-to-agent communication.
- Each tier MUST be fully tested before advancing to the next.
- Features from higher tiers MUST NOT be prerequisites for lower
  tiers to function.

**Rationale**: Progressive enhancement reduces risk, enables early
demos, and ensures each increment delivers standalone value.

### VII. Security Non-Negotiable

Security requirements are hard constraints that MUST NOT be
deferred or relaxed regardless of development velocity pressure.

- Credentials MUST use `.env` + environment variables (never
  plaintext in code).
- `DEV_MODE` flag + `--dry-run` MUST be available for all action
  scripts.
- Development MUST use separate test/sandbox accounts.
- Rate limiting MUST be enforced: max 10 emails/hour, 3
  payments/hour (configurable).
- All MCP server communications MUST validate inputs and outputs.
- OWASP top 10 vulnerabilities MUST be avoided in all code.

**Rationale**: The system handles email, payments, and social
media on behalf of a real person. A security breach has direct
personal and financial consequences.

## Technology Stack & Architecture Constraints

The Personal AI Employee follows the architecture pattern:
**PERCEPTION (Watchers) -> MEMORY (Obsidian Vault) -> REASONING
(Claude Code) -> ACTION (MCP Servers) -> HUMAN-IN-THE-LOOP
(Approval) -> COMPLETION (Ralph Wiggum Loop)**

### Stack

| Layer         | Technology                                |
|---------------|-------------------------------------------|
| Brain         | Claude Code CLI (Pro)                     |
| Memory/GUI    | Obsidian (local Markdown vault)           |
| Senses        | Python Watcher scripts                    |
| Hands         | MCP servers (email, browser, calendar)    |
| Orchestration | Python `orchestrator.py` + Ralph Wiggum   |
| Process Mgmt  | PM2 or custom watchdog                    |
| Skills        | Agent Skills in `/skills/`                |

### Vault Structure

All vault paths are relative to the vault root
(`/AI_Employee_Vault/`):

- `Dashboard.md` - Real-time summary
- `Company_Handbook.md` - Rules of engagement
- `Business_Goals.md` - Objectives, metrics, targets
- `Inbox/` - Raw incoming items
- `Needs_Action/` - Tasks awaiting processing
- `Plans/` - Claude-generated action plans
- `Pending_Approval/` - Actions requiring human approval
- `Approved/` - Human-approved actions ready to execute
- `Rejected/` - Human-rejected actions
- `In_Progress/` - Currently being worked on
- `Done/` - Completed tasks (archive)
- `Logs/` - Audit trail (JSON)
- `Briefings/` - Weekly CEO briefings
- `Accounting/` - Financial tracking

### Watcher Pattern

All watchers MUST extend the BaseWatcher pattern:

- `__init__(vault_path, check_interval)`
- `check_for_updates()` returns list of new items
- `create_action_file(item)` writes to `/Needs_Action/`
- `run()` infinite loop with error handling

### MCP Server Requirements

- Email MCP: Send, draft, search emails
- Browser MCP: Navigate, click, fill forms
- Calendar MCP: Create, update events
- Additional MCPs added per tier requirements

## Development Workflow & Quality Gates

### Workflow Sequence

1. Create Obsidian vault structure first.
2. Build ONE watcher + test with Claude Code.
3. Implement HITL approval workflow early.
4. Add MCP servers incrementally.
5. Test each tier thoroughly before advancing.
6. Document architecture and lessons learned.
7. Create demo video showing key features.

### Quality Gates

Before advancing to the next tier, the following MUST be verified:

- [ ] All existing functionality works without regression.
- [ ] Audit logs capture every action taken.
- [ ] HITL workflow correctly blocks sensitive actions.
- [ ] Error recovery handles all defined error categories.
- [ ] Skills are documented with inputs, outputs, examples.
- [ ] Credentials are stored securely (`.env`, not in code).
- [ ] `--dry-run` mode works for all action scripts.

### Code Standards

- Smallest viable diff; no unrelated refactoring.
- All code changes MUST reference specific file paths.
- Python code MUST follow PEP 8 conventions.
- Markdown files MUST use consistent heading hierarchy.
- JSON logs MUST validate against the defined schema.

## Governance

This constitution is the authoritative source of project
principles and constraints. All implementation decisions, specs,
plans, and tasks MUST comply with these principles.

### Amendment Procedure

1. Propose amendment with rationale and impact analysis.
2. Document which principles are affected.
3. Update constitution with new version number.
4. Propagate changes to dependent templates and artifacts.
5. Record amendment in Sync Impact Report (HTML comment).

### Versioning Policy

- **MAJOR**: Principle removal, redefinition, or backward-
  incompatible governance change.
- **MINOR**: New principle added, existing principle materially
  expanded.
- **PATCH**: Clarifications, wording fixes, non-semantic
  refinements.

### Compliance Review

- Every spec MUST reference applicable principles.
- Every plan MUST include a Constitution Check gate.
- Code reviews MUST verify adherence to security and HITL
  principles.
- Weekly audit (Gold tier) MUST include compliance summary.

**Version**: 1.0.0 | **Ratified**: 2026-02-16 | **Last Amended**: 2026-02-16
