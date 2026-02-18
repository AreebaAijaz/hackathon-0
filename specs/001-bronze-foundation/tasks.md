# Tasks: Bronze Tier Foundation

**Input**: Design documents from `/specs/001-bronze-foundation/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are OPTIONAL - not explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Vault content: `AI_Employee_Vault/` at repository root
- Skills: `AI_Employee_Vault/skills/` inside the vault

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Initialize UV project, Git configuration, and vault directory structure

- [x] T001 Initialize UV Python project with `uv init` and configure `pyproject.toml` for `personal-ai-employee` (name, version 0.1.0, requires-python >=3.13) at repository root
- [x] T002 Add Python dependencies: `uv add google-auth google-auth-oauthlib google-api-python-client python-dotenv tenacity` at repository root
- [x] T003 [P] Create `.gitignore` with entries: `.env`, `__pycache__/`, `*.pyc`, `.venv/`, `credentials.json`, `token.json`, `AI_Employee_Vault/Logs/`, `AI_Employee_Vault/Needs_Action/`, `AI_Employee_Vault/Done/`, `AI_Employee_Vault/Inbox/`
- [x] T004 [P] Create `.env.template` with placeholder variables: `GMAIL_CREDENTIALS_PATH=./credentials.json`, `GMAIL_TOKEN_PATH=./token.json`, `VAULT_PATH=./AI_Employee_Vault`, `CHECK_INTERVAL=120`, `DEV_MODE=false`, `DRY_RUN=false`
- [x] T005 Create vault directory structure: `AI_Employee_Vault/` with subdirectories `Inbox/`, `Needs_Action/`, `Plans/`, `Done/`, `Logs/`, `skills/` (add `.gitkeep` in each empty directory)
- [x] T006 [P] Create `src/__init__.py`, `src/watchers/__init__.py`, `src/utils/__init__.py` package files

**Checkpoint**: UV project created, dependencies installed, vault directories exist, Git-ready

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T007 Create audit logger utility in `src/audit_logger.py` implementing: `log_action(vault_path, action_type, actor, target, result, parameters=None, error_message=None)` function that appends NDJSON to `AI_Employee_Vault/Logs/YYYY-MM-DD.json` per audit-log-schema contract (ISO 8601 UTC timestamps, action_type enum validation)
- [x] T008 [P] Create vault utility helpers in `src/utils/vault.py` implementing: `get_vault_path()` (reads from .env), `ensure_vault_structure(vault_path)` (creates missing directories), `count_files(directory)` (counts .md files), `list_files(directory)` (returns sorted .md file paths), `move_file(src, dst)` (moves file between vault directories)
- [x] T009 [P] Create environment configuration loader in `src/utils/config.py` implementing: `load_config()` function using python-dotenv to load `.env` and return a config dict with keys: `vault_path`, `credentials_path`, `token_path`, `check_interval`, `dev_mode`, `dry_run` (with defaults matching `.env.template`)
- [x] T010 Create abstract BaseWatcher class in `src/watchers/base_watcher.py` per watcher-interface contract: constructor accepts `vault_path` and `check_interval` (default 120), abstract methods `check_for_updates() -> list[dict]` and `create_action_file(item) -> str`, concrete `run()` method with infinite loop, Windows-compatible signal handling (SIGINT/SIGTERM/SIGBREAK), exponential backoff retry via tenacity (3 attempts), structured logging to console, and audit log integration via `src/audit_logger.py`

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Knowledge Vault Setup (Priority: P1) MVP

**Goal**: Create the Obsidian vault with Dashboard.md, Company_Handbook.md, and README.md so the user has a centralized workspace visible in Obsidian

**Independent Test**: Open `AI_Employee_Vault/` in Obsidian. Verify Dashboard.md shows system status sections, Company_Handbook.md contains 6+ rules, and all folders are visible in the sidebar.

### Implementation for User Story 1

- [x] T011 [P] [US1] Create `AI_Employee_Vault/Dashboard.md` with sections: System Status (last_updated timestamp, active_watchers list showing "None"), Pending Tasks (count: 0, note to check Needs_Action/), Recent Activity (table with columns: Time, Action, Details - empty initially), Quick Stats (emails_processed_today: 0, tasks_completed_today: 0). Use Obsidian-compatible markdown with YAML frontmatter (title, date, tags: [dashboard, status])
- [x] T012 [P] [US1] Create `AI_Employee_Vault/Company_Handbook.md` with YAML frontmatter (title, version: 1.0) and 6 numbered rules: 1) Communication: Always be professional and polite, 2) Financial Flagging: Flag ALL financial matters (invoices, payments, expenses) for human review - never auto-resolve, 3) Prioritization: Process urgent items first then important then normal, 4) Action Logging: Log every action taken to Logs/ directory, 5) Data Preservation: Never delete original emails or source documents - archive to Done/ only, 6) Planning: Create clear actionable plans with specific next steps for every task
- [x] T013 [P] [US1] Create `README.md` at repository root with sections: Project Overview (Personal AI Employee - Bronze Tier), Architecture Diagram (PERCEPTION->MEMORY->REASONING->ACTION flow in text), Prerequisites (Python 3.13+, UV, Obsidian, Claude Code CLI, Google account), Quick Start (6 steps: clone, uv sync, Gmail setup, .env config, start watcher, run orchestrator), Vault Structure (folder listing), Credential Setup (Google Cloud Console steps), Usage (watcher and orchestrator commands), Troubleshooting (common errors and solutions), Security (how credentials are handled, what's gitignored)

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently. Open Obsidian and verify.

---

## Phase 4: User Story 2 - Email Monitoring (Priority: P2)

**Goal**: Gmail watcher continuously monitors inbox for important unread emails and creates structured task files in Needs_Action/

**Independent Test**: Start the Gmail watcher. Send a test email marked as important. Within 2 minutes, verify `EMAIL_{id}.md` appears in `AI_Employee_Vault/Needs_Action/` with correct frontmatter (sender, subject, priority, status: pending).

### Implementation for User Story 2

- [x] T014 [US2] Create Gmail authentication helper in `src/watchers/gmail_auth.py` implementing: `get_gmail_service(credentials_path, token_path)` function using `InstalledAppFlow.from_client_secrets_file()` with scope `gmail.readonly`, automatic token refresh via `Credentials.from_authorized_user_file()`, token persistence to `token.json`, and `run_local_server(port=0)` for first-time OAuth2 consent. Include `--auth-only` CLI mode that just authenticates and exits.
- [x] T015 [US2] Create GmailWatcher class in `src/watchers/gmail_watcher.py` extending BaseWatcher: constructor accepts `credentials_path`, `token_path`, `vault_path`, `check_interval`; initializes Gmail service via `gmail_auth.get_gmail_service()`; maintains `processed_ids: set` for deduplication. Implement `check_for_updates()` to query `users().messages().list(userId='me', q='is:unread AND is:important', maxResults=10)` and return list of new message dicts (filtering out processed_ids). Handle `HttpError` 429 (rate limit) by raising for tenacity retry.
- [x] T016 [US2] Implement `create_action_file(item)` method in `src/watchers/gmail_watcher.py`: call `users().messages().get(userId='me', id=item['id'], format='metadata', metadataHeaders=['From','Subject','Date'])` to fetch details; extract sender, subject, date from headers; determine priority ("important" for all since query filters important); write YAML frontmatter + body to `AI_Employee_Vault/Needs_Action/EMAIL_{message_id}.md` per data-model Task File schema; add suggested actions checklist (Review email, Determine response needed, Create action plan); add message_id to `processed_ids`; call `audit_logger.log_action()` for both `email_detected` and `task_created` events.
- [x] T017 [US2] Add `--dry-run` mode to GmailWatcher: when enabled, generate 3 sample task files with fake email data (test sender, subject, snippet) in Needs_Action/ without connecting to Gmail API. Load `DRY_RUN` from config. Log dry-run actions to audit log with `parameters: {"dry_run": true}`.
- [x] T018 [US2] Create `__main__.py` entry point in `src/watchers/gmail_watcher.py` (or `src/watchers/__main__.py`): parse CLI args (`--auth-only`, `--dry-run`, `--interval`), load config from `.env`, instantiate GmailWatcher, call `watcher.run()`. Runnable via `uv run python -m src.watchers.gmail_watcher`.

**Checkpoint**: At this point, User Story 2 should be fully functional. Send an important email and verify detection within 2 minutes.

---

## Phase 5: User Story 3 - Automated Task Processing (Priority: P3)

**Goal**: Orchestrator reads task files from Needs_Action/, invokes Claude Code to generate plans, updates Dashboard.md, and archives tasks to Done/

**Independent Test**: Manually place a sample `EMAIL_test123.md` in `Needs_Action/`. Run the orchestrator. Verify: plan appears in `Plans/`, Dashboard.md updates, task file moves to `Done/`.

### Implementation for User Story 3

- [x] T019 [US3] Create prompt template in `src/prompt_template.py` implementing: `build_processing_prompt(task_content, handbook_rules, skill_docs)` function that constructs a Claude Code prompt containing: the task file content, Company_Handbook.md rules, skill documentation references, and instructions to output a JSON response with fields: `plan_title`, `analysis`, `recommended_actions` (list), `priority`, `requires_human` (boolean), `flagged_items` (list). Include clear output format specification.
- [x] T020 [US3] Create Claude Code invocation utility in `src/utils/claude_runner.py` implementing: `invoke_claude(prompt, vault_path, allowed_tools=None)` function that runs `claude -p "<prompt>" --output-format json` as subprocess via `subprocess.Popen()`, handles Windows `CREATE_NEW_PROCESS_GROUP`, parses JSON stdout response, raises `RuntimeError` on non-zero exit or timeout (120s default). Include error logging.
- [x] T021 [US3] Create Orchestrator class in `src/orchestrator.py` per orchestrator-interface contract: constructor accepts `vault_path` and `dry_run` flag; implement `scan_needs_action()` to list `.md` files in Needs_Action/ sorted by creation time (FIFO); implement `process_task(task_path)` pipeline: read task file, read Company_Handbook.md, read skill docs from skills/, build prompt via `prompt_template.build_processing_prompt()`, invoke Claude via `claude_runner.invoke_claude()`, write plan to `Plans/PLAN_{task_id}_{timestamp}.md` with YAML frontmatter per data-model Plan schema, call `update_dashboard()`, move task to `Done/`, log all actions via audit_logger.
- [x] T022 [US3] Implement `update_dashboard()` method in `src/orchestrator.py`: read current Dashboard.md, update `last_updated` timestamp, recalculate `pending_tasks` count from Needs_Action/ via `vault.count_files()`, prepend latest action to Recent Activity table (keep last 5), increment Quick Stats counters, write updated Dashboard.md preserving section structure.
- [x] T023 [US3] Create `__main__.py` entry point for orchestrator: parse CLI args (`--dry-run`, `--once` for single run vs watch mode), load config from `.env`, instantiate Orchestrator. In `--once` mode: scan and process all pending tasks then exit. In watch mode: poll Needs_Action/ every 30 seconds for new files. Runnable via `uv run python -m src.orchestrator`.

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should work end-to-end. Place a task file, run orchestrator, verify full pipeline.

---

## Phase 6: User Story 4 - Agent Skills Framework (Priority: P4)

**Goal**: Create 4 documented Agent Skills that Claude Code references during task processing

**Independent Test**: Read each SKILL.md file. Verify it contains: Name, Version, Purpose, Inputs, Outputs, Rules, and at least one Example. Invoke Claude Code with a skill reference and sample input; verify it follows the skill's documented behavior.

### Implementation for User Story 4

- [x] T024 [P] [US4] Create `AI_Employee_Vault/skills/email_processor/SKILL.md` per skill-interface contract: Name: email_processor, Version: 1.0.0, Purpose: Categorize and assess priority of incoming emails, Inputs: raw email metadata (sender, subject, snippet, headers), Outputs: priority level (urgent/important/normal), category (financial/request/notification/personal), suggested actions list. Rules: flag financial emails for human review, prioritize by sender domain and subject keywords. Example: given email from "accounting@company.com" with subject "Invoice #1234", output priority: urgent, category: financial, requires_human: true.
- [x] T025 [P] [US4] Create `AI_Employee_Vault/skills/task_creator/SKILL.md` per skill-interface contract: Name: task_creator, Version: 1.0.0, Purpose: Generate structured task files from processed items, Inputs: processed item data (id, source_type, metadata), Outputs: markdown file with YAML frontmatter per data-model Task File schema in Needs_Action/. Rules: MUST include all required frontmatter fields, filename MUST follow pattern `{SOURCE_TYPE}_{id}.md`, status MUST be "pending" on creation. Example: given email data, output complete EMAIL_abc123.md with frontmatter and body.
- [x] T026 [P] [US4] Create `AI_Employee_Vault/skills/dashboard_updater/SKILL.md` per skill-interface contract: Name: dashboard_updater, Version: 1.0.0, Purpose: Refresh Dashboard.md with current system state, Inputs: vault state (file counts, recent log entries, daily stats), Outputs: updated Dashboard.md. Rules: MUST update last_updated to current ISO 8601, pending_tasks MUST match actual Needs_Action/ count, recent_activity shows last 5 items newest-first, MUST NOT delete existing sections. Example: given 2 pending tasks and 3 completed today, output updated Dashboard.md with correct counts.
- [x] T027 [P] [US4] Create `AI_Employee_Vault/skills/plan_generator/SKILL.md` per skill-interface contract: Name: plan_generator, Version: 1.0.0, Purpose: Create action plans for processed tasks, Inputs: task file content + Company_Handbook.md rules, Outputs: Plan markdown file in Plans/ with YAML frontmatter per data-model Plan schema. Rules: MUST reference source task_id, MUST flag financial matters with requires_human: true, recommended_actions MUST be numbered and specific. Example: given email about meeting request, output PLAN_abc123_20260216.md with analysis and 3 recommended actions.

**Checkpoint**: All user stories should now be independently functional. Skills are documented and referenced by orchestrator.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: End-to-end validation, documentation updates, and submission preparation

- [x] T028 Create sample test data: 3 sample EMAIL task files in `tests/fixtures/` directory: `sample_email_urgent.md` (financial invoice), `sample_email_important.md` (meeting request), `sample_email_normal.md` (newsletter). Use realistic frontmatter per data-model Task File schema.
- [x] T029 [P] Create log viewer utility in `src/utils/view_logs.py` implementing: CLI script that reads `AI_Employee_Vault/Logs/YYYY-MM-DD.json`, supports `--date` filter (default: today) and `--type` filter (action_type), pretty-prints entries as table, shows summary stats (total actions, success rate). Runnable via `uv run python -m src.utils.view_logs`.
- [x] T030 [P] Add `--dry-run` mode to orchestrator in `src/orchestrator.py`: when enabled, read task files and log what would happen without invoking Claude Code or moving files. Write simulated plan content. Log dry-run actions to audit log with `parameters: {"dry_run": true}`.
- [x] T031 Validate end-to-end flow: place `tests/fixtures/sample_email_important.md` into `AI_Employee_Vault/Needs_Action/`, run orchestrator in `--once` mode, verify: plan created in `Plans/`, Dashboard.md updated, task moved to `Done/`, audit log entries written to `Logs/`. Document any issues found.
- [x] T032 [P] Update `README.md` with final tested content: actual working commands, verified setup steps, example output screenshots placeholder descriptions, architecture explanation, security disclosure (credentials handling), tier declaration (Bronze), and link to demo video placeholder.
- [x] T033 Run `uv run python -m py_compile src/watchers/base_watcher.py src/watchers/gmail_watcher.py src/orchestrator.py src/audit_logger.py` to verify all Python files compile without syntax errors. Fix any issues found.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Phase 1 (vault dirs exist)
- **User Story 2 (Phase 4)**: Depends on Phase 2 (BaseWatcher, audit_logger, config)
- **User Story 3 (Phase 5)**: Depends on Phase 2 (audit_logger, vault utils, config) + Phase 3 (Dashboard.md, Company_Handbook.md exist)
- **User Story 4 (Phase 6)**: Depends on Phase 1 (skills/ directory exists)
- **Polish (Phase 7)**: Depends on Phases 3-6 being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Phase 1 - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Phase 2 - No dependencies on other stories
- **User Story 3 (P3)**: Depends on US1 (needs Dashboard.md and Company_Handbook.md to exist) and Phase 2
- **User Story 4 (P4)**: Can start after Phase 1 - No dependencies on other stories. Skills are referenced by US3 orchestrator but can be created in parallel.

### Within Each User Story

- Models/schemas before services
- Services before endpoints/runners
- Core implementation before CLI entry points
- Story complete before moving to next priority

### Parallel Opportunities

- T003 and T004 can run in parallel (different files)
- T007, T008, T009 can run in parallel (different files, different concerns)
- T011, T012, T013 can run in parallel (different files in US1)
- T024, T025, T026, T027 can run in parallel (4 independent skill docs in US4)
- T028, T029, T030, T032 can run in parallel (different files in Polish)
- US1 and US4 can start in parallel after Phase 1 (no cross-dependencies)

---

## Parallel Example: User Story 1

```bash
# Launch all US1 tasks together (all different files):
Task: "Create Dashboard.md in AI_Employee_Vault/Dashboard.md"
Task: "Create Company_Handbook.md in AI_Employee_Vault/Company_Handbook.md"
Task: "Create README.md at repository root"
```

## Parallel Example: User Story 4

```bash
# Launch all US4 skill docs together (all independent files):
Task: "Create email_processor SKILL.md in AI_Employee_Vault/skills/email_processor/"
Task: "Create task_creator SKILL.md in AI_Employee_Vault/skills/task_creator/"
Task: "Create dashboard_updater SKILL.md in AI_Employee_Vault/skills/dashboard_updater/"
Task: "Create plan_generator SKILL.md in AI_Employee_Vault/skills/plan_generator/"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks US2, US3)
3. Complete Phase 3: User Story 1 (Vault + Dashboard + Handbook)
4. **STOP and VALIDATE**: Open Obsidian, verify vault renders correctly
5. Can demo vault structure at this point

### Incremental Delivery

1. Complete Setup + Foundational -> Foundation ready
2. Add User Story 1 -> Test independently -> Vault visible in Obsidian (MVP!)
3. Add User Story 4 -> Skills docs ready (can start in parallel with US2)
4. Add User Story 2 -> Test independently -> Gmail watcher detects emails
5. Add User Story 3 -> Test independently -> Full end-to-end pipeline works
6. Polish phase -> Final validation, docs, demo prep
7. Each story adds value without breaking previous stories

### Suggested Execution Order (Solo Developer)

Phase 1 (Setup) -> Phase 2 (Foundational) -> Phase 3 (US1) + Phase 6 (US4) in parallel -> Phase 4 (US2) -> Phase 5 (US3) -> Phase 7 (Polish)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each phase or logical group
- Stop at any checkpoint to validate story independently
- Gmail API Phase 3 from user's input (Google Cloud Console setup) is a MANUAL prerequisite - not a code task. User must complete OAuth2 setup before US2 can run.
- All paths are relative to repository root unless otherwise noted
