# Feature Specification: Bronze Tier Foundation

**Feature Branch**: `001-bronze-foundation`
**Created**: 2026-02-16
**Status**: Draft
**Input**: User description: "Personal AI Employee Bronze Tier - vault structure, Gmail watcher, Claude Code processing pipeline, agent skills"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Knowledge Vault Setup (Priority: P1)

As a user, I want a structured knowledge vault with a real-time dashboard and a company handbook so that I have a centralized workspace for my AI Employee to operate within, and I can see system status at a glance.

**Why this priority**: The vault is the foundational data layer. Every other component (watchers, processing, skills) depends on this structure existing. Without it, nothing else can function.

**Independent Test**: Create the vault with all folders, populate Dashboard.md with initial status, and populate Company_Handbook.md with operating rules. Verify by opening in Obsidian and confirming all folders and files render correctly.

**Acceptance Scenarios**:

1. **Given** a fresh project directory, **When** the vault is initialized, **Then** the following folders exist: Inbox/, Needs_Action/, Plans/, Done/, Logs/, and skills/.
2. **Given** the vault is initialized, **When** the user opens Dashboard.md, **Then** it displays: system status section (last updated, active watchers), pending tasks count, recent activity list (last 5 items), and quick stats (emails processed today, tasks completed).
3. **Given** the vault is initialized, **When** the user opens Company_Handbook.md, **Then** it contains at least 6 clear, actionable rules governing AI behavior including: professionalism, financial flagging, prioritization, logging, data preservation, and planning.
4. **Given** the vault exists, **When** a file is manually placed in Needs_Action/, **Then** the Dashboard.md pending tasks count reflects the new item after the next update cycle.

---

### User Story 2 - Email Monitoring (Priority: P2)

As a user, I want important unread emails to be automatically detected and converted into structured task files in my vault so that I never miss a critical email and each one becomes a trackable, actionable item.

**Why this priority**: Email monitoring is the primary "sense" for the Bronze tier. It demonstrates the PERCEPTION layer of the architecture and feeds the processing pipeline with real data.

**Independent Test**: Run the email watcher against a live inbox. Send a test email marked as important. Verify within one check cycle that a corresponding task file appears in Needs_Action/ with correct metadata.

**Acceptance Scenarios**:

1. **Given** the watcher is running and the inbox has an unread important email, **When** the next check cycle completes, **Then** a new task file named `EMAIL_{message_id}.md` appears in Needs_Action/ containing: sender, subject, received time, priority level, email snippet, and suggested actions.
2. **Given** the watcher has already processed an email, **When** the same email is still present in the inbox on the next cycle, **Then** no duplicate task file is created (message ID tracking prevents duplicates).
3. **Given** the watcher encounters a network failure, **When** connectivity is restored, **Then** the watcher resumes checking without data loss or crash, and logs the error event.
4. **Given** the watcher is running, **When** no new important emails exist, **Then** no task files are created and the watcher continues checking at the configured interval (default: every 2 minutes).
5. **Given** the watcher is running, **When** API rate limits are approached, **Then** the watcher backs off gracefully and logs a warning.

---

### User Story 3 - Automated Task Processing (Priority: P3)

As a user, I want the AI to automatically read incoming task files, generate action plans, update the dashboard, and archive completed items so that emails are processed end-to-end without manual intervention.

**Why this priority**: This story completes the Bronze tier's core loop (detect → process → plan → update → archive). It demonstrates the REASONING layer and proves the system can operate autonomously for read-only operations.

**Independent Test**: Place a sample task file in Needs_Action/. Trigger the processing pipeline. Verify that: a plan file appears in Plans/, Dashboard.md is updated, and the original task file moves to Done/.

**Acceptance Scenarios**:

1. **Given** a task file exists in Needs_Action/, **When** the processing pipeline runs, **Then** the AI reads the file content and checks Company_Handbook.md rules before taking action.
2. **Given** the AI has read a task file, **When** it generates a plan, **Then** a new Plan.md file appears in Plans/ containing: the original task reference, analysis, recommended actions, and priority assessment.
3. **Given** processing is complete for a task, **When** the pipeline finishes, **Then** Dashboard.md is updated with: the task in recent activity, incremented completion count, and current timestamp.
4. **Given** a task has been fully processed, **When** the plan is written and dashboard updated, **Then** the original task file moves from Needs_Action/ to Done/.
5. **Given** a task file contains a financial matter, **When** the AI processes it, **Then** it flags it for human review per Company_Handbook.md rules and does not auto-resolve.

---

### User Story 4 - Agent Skills Framework (Priority: P4)

As a user, I want all AI capabilities packaged as documented, reusable Agent Skills so that the system is maintainable, extensible, and each capability can be tested and improved independently.

**Why this priority**: Skills provide the organizational structure for all AI functionality. While the system can work without formal skills, packaging capabilities as skills ensures consistency and prepares the foundation for Silver/Gold tier extensions.

**Independent Test**: Invoke each skill independently with sample input. Verify it produces expected output and its documentation accurately describes inputs, outputs, and usage.

**Acceptance Scenarios**:

1. **Given** the skills directory exists, **When** the user lists available skills, **Then** at least 4 skills are present: email processor, task creator, dashboard updater, and plan generator.
2. **Given** an email processor skill, **When** invoked with raw email data, **Then** it returns a categorized, structured representation with priority and suggested actions.
3. **Given** a dashboard updater skill, **When** invoked after a task completes, **Then** Dashboard.md is updated with accurate counts and recent activity without corrupting existing content.
4. **Given** any skill, **When** its documentation is read, **Then** it clearly specifies: purpose, inputs, outputs, and at least one usage example.

---

### Edge Cases

- What happens when the vault directory is deleted or moved while watchers are running? The watcher MUST detect the missing path and halt with a clear error, not silently fail.
- What happens when two task files reference the same email (race condition)? The system MUST use message ID deduplication to prevent processing the same email twice.
- What happens when Dashboard.md is being edited by the user while the system attempts an update? The system MUST not corrupt the file; concurrent write handling is required.
- What happens when the Logs/ directory fills up with many entries? Log files MUST be date-partitioned (one file per day) to prevent any single file from growing unbounded.
- What happens when the email watcher's authentication token expires? The watcher MUST pause, log the authentication error, and alert the user.
- What happens when a task file in Needs_Action/ has malformed content? The system MUST log the error and skip the file rather than crash.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST create and maintain an Obsidian-compatible vault with the folder structure: Inbox/, Needs_Action/, Plans/, Done/, Logs/, skills/.
- **FR-002**: System MUST provide a Dashboard.md file that displays: system status (last updated, active watchers), pending task count, last 5 processed items, and daily statistics (emails processed, tasks completed).
- **FR-003**: System MUST provide a Company_Handbook.md file containing at least 6 operational rules that govern AI behavior, including rules for professionalism, financial flagging, prioritization, logging, data preservation, and planning.
- **FR-004**: System MUST monitor the user's email inbox at a configurable interval (default: 2 minutes) and detect unread important messages.
- **FR-005**: System MUST create structured markdown task files in Needs_Action/ for each detected email, including: sender, subject, received timestamp, priority, content snippet, and suggested actions.
- **FR-006**: System MUST track processed message identifiers to prevent duplicate task file creation.
- **FR-007**: System MUST process task files from Needs_Action/ by reading content, consulting Company_Handbook.md rules, generating a plan in Plans/, updating Dashboard.md, and moving the original file to Done/.
- **FR-008**: System MUST log every action to Logs/ in structured format with: timestamp (ISO 8601), action type, actor, target, and result.
- **FR-009**: System MUST store all credentials in environment variables loaded from a .env file that is excluded from version control.
- **FR-010**: System MUST implement all AI capabilities as documented Agent Skills with defined inputs, outputs, and usage examples.
- **FR-011**: System MUST handle network failures, authentication errors, and malformed data without crashing, using the error recovery strategies defined in the constitution.
- **FR-012**: System MUST provide a --dry-run mode for the email watcher that simulates detection and task creation without accessing the live inbox.

### Key Entities

- **Task File**: A markdown document representing an actionable item. Key attributes: source type (email, manual), unique identifier, sender, subject, priority, content, status (pending, processing, done), creation timestamp.
- **Plan**: A markdown document containing the AI's analysis and recommended actions for a task. Key attributes: task reference, analysis summary, recommended actions, priority assessment, creation timestamp.
- **Audit Log Entry**: A structured record of every system action. Key attributes: timestamp, action type, actor, target, parameters, result (success/failure).
- **Agent Skill**: A packaged AI capability. Key attributes: name, purpose, inputs specification, outputs specification, usage examples, version.
- **Dashboard State**: The current system status snapshot. Key attributes: last updated timestamp, active watcher list, pending task count, recent activity list, daily statistics.

## Assumptions

- The user has a Google account with Gmail API access enabled and can complete OAuth2 setup.
- Obsidian v1.10.6+ is installed locally and can open the vault directory.
- Python 3.13+ is available with UV for dependency management.
- The vault directory resides within the project repository at `AI_Employee_Vault/`.
- The email watcher runs as a long-lived process on the user's local machine.
- For Bronze tier, Claude Code processes tasks on-demand or via manual trigger (not as an always-on daemon).
- Date-partitioned log files use the format `YYYY-MM-DD.json`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Vault initialization completes in under 30 seconds and produces all required folders and files without manual intervention.
- **SC-002**: The email watcher detects a new important email and creates a corresponding task file within one check interval (default: 2 minutes) of the email arriving.
- **SC-003**: Zero duplicate task files are created for the same email across 100 consecutive check cycles.
- **SC-004**: The processing pipeline completes end-to-end (read task → create plan → update dashboard → archive to Done) within 60 seconds per task.
- **SC-005**: Dashboard.md accurately reflects the current state of the system after every processing cycle (pending count matches Needs_Action/ contents, recent activity shows last 5 items).
- **SC-006**: The email watcher recovers from a simulated network failure within 3 retry attempts using exponential backoff, without data loss.
- **SC-007**: All 4 agent skills (email processor, task creator, dashboard updater, plan generator) are independently invocable and produce documented output formats.
- **SC-008**: The system operates with credentials exclusively from environment variables; no secrets appear in version-controlled files.
- **SC-009**: Audit logs capture 100% of system actions with valid structured entries.
- **SC-010**: The user can set up the entire Bronze tier system by following the README in under 15 minutes (excluding OAuth2 credential setup).
