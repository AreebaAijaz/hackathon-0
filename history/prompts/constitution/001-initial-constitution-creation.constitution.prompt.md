---
id: 001
title: Initial Constitution Creation
stage: constitution
date: 2026-02-16
surface: agent
model: claude-opus-4-6
feature: none
branch: master
user: san
command: /sp.constitution
labels: ["constitution", "project-setup", "principles", "governance"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - N/A
---

## Prompt

# Personal AI Employee (Digital FTE) - Project Constitution

## Project Vision
Build an autonomous AI Employee that proactively manages personal and business affairs 24/7 using Claude Code as the reasoning engine, Obsidian as the memory/dashboard, Python Watchers as sensors, and MCP servers as action executors.

## Core Architecture Pattern
PERCEPTION (Watchers) → MEMORY (Obsidian Vault) → REASONING (Claude Code) → ACTION (MCP Servers) → HUMAN-IN-THE-LOOP (Approval) → COMPLETION (Ralph Wiggum Loop)

## Technology Stack
- Brain: Claude Code CLI (Pro version available)
- Memory/GUI: Obsidian (local Markdown vault)
- Senses: Python Watcher scripts (Gmail, WhatsApp, File System)
- Hands: MCP servers (email, browser, calendar, etc.)
- Orchestration: Python orchestrator.py + Ralph Wiggum loop pattern
- Process Management: PM2 or custom watchdog for daemon processes
- Skills: All AI functionality implemented as Agent Skills

## Development Principles
1. Local-first for privacy
2. Human-in-the-loop for safety
3. Audit everything for accountability
4. Fail gracefully with recovery
5. Skills-first for reusability
6. Progressive enhancement (Bronze → Gold)
7. Security is non-negotiable

(Full input included comprehensive details on: Obsidian vault structure, implementation tiers Bronze/Silver/Gold/Platinum, watcher patterns, MCP server requirements, Ralph Wiggum loop, HITL safety workflow, auto-approve thresholds, weekly business audit, security & privacy requirements, log format, error handling categories, agent skills philosophy, process management, development workflow, submission requirements, and key success metrics.)

## Response snapshot

Created the project constitution v1.0.0 at `.specify/memory/constitution.md` with:
- 7 core principles derived from user's development principles (Local-First Privacy, Human-in-the-Loop Safety, Audit Everything, Graceful Failure Recovery, Skills-First Reusability, Progressive Enhancement, Security Non-Negotiable)
- Technology Stack & Architecture Constraints section capturing the full stack and vault structure
- Development Workflow & Quality Gates section with tier advancement gates
- Governance section with amendment procedure, versioning policy, and compliance review
- Sync Impact Report as HTML comment documenting template compatibility
- All templates verified compatible (plan, spec, tasks) - no updates needed

## Outcome

- ✅ Impact: Constitution established as authoritative project governance document
- 🧪 Tests: N/A (documentation artifact)
- 📁 Files: .specify/memory/constitution.md (created)
- 🔁 Next prompts: /sp.specify to create first feature spec, or start Bronze tier implementation
- 🧠 Reflection: User provided exceptionally detailed input covering all aspects of the system. Constitution captures 7 principles (expanded from template's 6 slots) with concrete, testable constraints rather than vague guidelines.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Manual validation PASS - no unresolved placeholders, all principles declarative and testable, dates in ISO format, version line matches report
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
