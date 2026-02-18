# Implementation Plan: Bronze Tier Foundation

**Branch**: `001-bronze-foundation` | **Date**: 2026-02-16 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-bronze-foundation/spec.md`

## Summary

Build the foundational Bronze tier of the Personal AI Employee: an Obsidian vault with dashboard and handbook, a Gmail watcher that detects important emails and creates task files, a Claude Code orchestrator that processes tasks into plans, and four Agent Skills that package all AI capabilities as reusable units. The system follows PERCEPTION (Gmail Watcher) -> MEMORY (Obsidian Vault) -> REASONING (Claude Code) -> ACTION (file operations) architecture.

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: google-auth, google-auth-oauthlib, google-api-python-client, python-dotenv, tenacity
**Storage**: Obsidian-compatible Markdown vault (file system)
**Testing**: pytest + manual integration testing
**Target Platform**: Windows 10 (local machine)
**Project Type**: Single project with src/ layout
**Performance Goals**: Process one task within 60 seconds; watcher check cycle every 2 minutes
**Constraints**: Gmail API rate limit (250 quota units/second/user); credentials in .env only; local-first data
**Scale/Scope**: Single user, ~10-50 emails/day, 4 agent skills

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| # | Principle | Status | Evidence |
|---|-----------|--------|----------|
| I | Local-First Privacy | PASS | Vault is local filesystem; credentials in .env (gitignored); no cloud sync in Bronze |
| II | Human-in-the-Loop Safety | PASS | Bronze tier is read-only (no email sending, no payments); financial matters flagged in Company_Handbook.md |
| III | Audit Everything | PASS | Structured JSON logging to Logs/YYYY-MM-DD.json; every action logged per audit-log-schema contract |
| IV | Graceful Failure Recovery | PASS | BaseWatcher with exponential backoff (tenacity); error categories handled per watcher-interface contract |
| V | Skills-First Reusability | PASS | 4 Agent Skills defined (email_processor, task_creator, dashboard_updater, plan_generator) |
| VI | Progressive Enhancement | PASS | Bronze-only scope; no Silver/Gold dependencies; vault structure supports future tiers |
| VII | Security Non-Negotiable | PASS | .env for credentials; --dry-run mode; gmail.readonly scope only; .gitignore excludes secrets |

**Result**: All 7 gates PASS. No violations requiring justification.

**Post-Phase 1 Re-check**: All gates still PASS. Data model and contracts align with constitution principles.

## Project Structure

### Documentation (this feature)

```text
specs/001-bronze-foundation/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0 research findings
├── data-model.md        # Entity definitions and relationships
├── quickstart.md        # Setup and verification guide
├── contracts/
│   ├── watcher-interface.md     # BaseWatcher contract
│   ├── orchestrator-interface.md # Orchestrator contract
│   ├── audit-log-schema.md      # Log entry schema
│   └── skill-interface.md       # Agent Skill template
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
src/
├── __init__.py
├── watchers/
│   ├── __init__.py
│   ├── base_watcher.py       # Abstract BaseWatcher class
│   └── gmail_watcher.py      # Gmail inbox monitor
├── orchestrator.py            # Task processing pipeline
├── audit_logger.py            # Structured JSON logging utility
└── utils/
    ├── __init__.py
    └── vault.py               # Vault path helpers and file ops

AI_Employee_Vault/
├── Dashboard.md               # Live system status
├── Company_Handbook.md        # AI behavioral rules
├── Inbox/                     # Raw incoming (future use)
├── Needs_Action/              # Pending task files
├── Plans/                     # Claude-generated action plans
├── Done/                      # Archived processed tasks
├── Logs/                      # Audit trail (NDJSON)
└── skills/
    ├── email_processor/
    │   └── SKILL.md
    ├── task_creator/
    │   └── SKILL.md
    ├── dashboard_updater/
    │   └── SKILL.md
    └── plan_generator/
        └── SKILL.md

tests/
├── __init__.py
├── unit/
│   ├── test_base_watcher.py
│   ├── test_audit_logger.py
│   └── test_vault_utils.py
└── integration/
    ├── test_gmail_watcher.py
    └── test_orchestrator.py
```

**Structure Decision**: Single project layout with `src/` directory. The vault (`AI_Employee_Vault/`) sits at the repository root as a peer to `src/` since it is both runtime data and user-facing content (Obsidian). Skills live inside the vault per the constitution's skills-first principle.

## Key Design Decisions

### 1. Gmail Polling vs Push Notifications

**Decision**: Simple 2-minute polling with `users().messages().list()`.

**Rationale**: Push notifications require Google Cloud Pub/Sub infrastructure, webhook endpoints, and watch renewal every 7 days. For a personal use case (~10-50 emails/day), polling every 2 minutes is well within Gmail API quota limits (~5 quota units per request vs 250 units/second/user). Polling is simpler, more reliable, and sufficient for Bronze tier.

**Alternative rejected**: Push via Pub/Sub - adds infrastructure complexity inappropriate for Bronze tier.

### 2. Claude Code Invocation via Subprocess

**Decision**: Invoke `claude -p "prompt" --output-format json` as subprocess from Python orchestrator.

**Rationale**: Direct subprocess invocation is the simplest integration pattern. The orchestrator constructs a prompt with task content + Company_Handbook.md rules, then parses Claude's JSON response. This avoids SDK complexity and works reliably on Windows with `subprocess.Popen()`.

**Alternative rejected**: Claude Agent SDK - more complex, not needed for Bronze tier's simple prompt-response pattern.

### 3. Audit Logs as NDJSON

**Decision**: Newline-delimited JSON (one JSON object per line) in date-partitioned files.

**Rationale**: NDJSON is append-only friendly (no array wrapper to manage), easy to parse line-by-line, and each file stays reasonably sized (one per day). Standard JSON arrays require reading the entire file to append, which risks corruption on concurrent writes.

**Alternative rejected**: SQLite database - adds dependency, harder to inspect manually, not Obsidian-viewable.

### 4. Skills as Markdown Documentation

**Decision**: Agent Skills are SKILL.md documentation files, not executable code.

**Rationale**: In Bronze tier, Claude Code reads skill documentation to understand how to perform tasks. This is simpler than building a plugin system and aligns with the skills-first principle. Skills define inputs, outputs, rules, and examples that Claude follows during processing.

**Alternative rejected**: Python skill modules with execute() methods - over-engineering for Bronze tier where Claude Code is the execution engine.

### 5. UV for Dependency Management

**Decision**: Use UV with `pyproject.toml` and `uv.lock` for reproducible builds.

**Rationale**: UV is fast (Rust-based), handles virtual environment creation automatically, and `uv.lock` ensures exact version reproducibility across machines. Single command (`uv sync`) sets up the entire environment.

**Alternative rejected**: pip + requirements.txt - no lock file, manual venv management.

## Complexity Tracking

> No Constitution Check violations. No complexity justifications needed.
