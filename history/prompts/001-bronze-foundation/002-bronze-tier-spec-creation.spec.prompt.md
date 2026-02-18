---
id: 002
title: Bronze Tier Spec Creation
stage: spec
date: 2026-02-16
surface: agent
model: claude-opus-4-6
feature: 001-bronze-foundation
branch: 001-bronze-foundation
user: san
command: /sp.specify
labels: ["spec", "bronze-tier", "vault", "gmail-watcher", "agent-skills"]
links:
  spec: specs/001-bronze-foundation/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-bronze-foundation/spec.md
  - specs/001-bronze-foundation/checklists/requirements.md
tests:
  - N/A
---

## Prompt

# Personal AI Employee - Project Specification

## Current Target: Bronze Tier (Foundation)
We are starting with the Bronze tier to establish a solid foundation before progressing to Silver and Gold tiers.

## Bronze Tier Deliverables
1. Obsidian vault with proper folder structure
2. Dashboard.md - Real-time summary of system state
3. Company_Handbook.md - Rules and guidelines for AI behavior
4. ONE working Watcher script (starting with Gmail Watcher)
5. Claude Code successfully reading from and writing to the vault
6. Basic automation: Watcher detects -> Creates task file -> Claude processes -> Updates Dashboard
7. ALL AI functionality implemented as Agent Skills

(Full user input included detailed sections on: technical stack, folder structure, Gmail watcher requirements, Claude Code integration flow, Dashboard.md structure, Company_Handbook.md rules, agent skills to create, success criteria, non-functional requirements, out of scope items, and development environment setup.)

## Response snapshot

Created feature specification for Bronze Tier Foundation:
- Branch: `001-bronze-foundation` (created and checked out)
- Spec: `specs/001-bronze-foundation/spec.md`
- 4 user stories: Vault Setup (P1), Email Monitoring (P2), Task Processing (P3), Agent Skills (P4)
- 12 functional requirements (FR-001 through FR-012)
- 5 key entities: Task File, Plan, Audit Log Entry, Agent Skill, Dashboard State
- 10 measurable success criteria (SC-001 through SC-010)
- 6 edge cases covering failure modes
- 7 documented assumptions
- Quality checklist: all items PASS, no NEEDS CLARIFICATION markers
- Spec ready for `/sp.clarify` or `/sp.plan`

## Outcome

- ✅ Impact: Complete Bronze tier specification established with 4 independently testable user stories
- 🧪 Tests: N/A (specification artifact)
- 📁 Files: specs/001-bronze-foundation/spec.md, specs/001-bronze-foundation/checklists/requirements.md
- 🔁 Next prompts: /sp.clarify to refine spec, or /sp.plan to create implementation plan
- 🧠 Reflection: User provided exceptionally detailed input. No clarification questions needed. Kept spec WHAT-focused while capturing technology assumptions separately.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Quality checklist PASS (all 12 items)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
