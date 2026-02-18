# Contract: Agent Skill Interface

**Version**: 1.0.0
**Date**: 2026-02-16

## Overview

Defines the standard structure for Agent Skills. Each skill is a
documented capability that Claude Code references for consistent
behavior.

## Skill Directory Structure

```
AI_Employee_Vault/skills/{skill_name}/
└── SKILL.md
```

## SKILL.md Template

```markdown
# Skill: {Skill Name}

**Version**: {semver}
**Purpose**: {One-line description}

## Inputs

{Description of what this skill expects as input}

- **Required**: {list of required inputs}
- **Optional**: {list of optional inputs}

## Outputs

{Description of what this skill produces}

- **Format**: {output format description}
- **Location**: {where output is written, if applicable}

## Rules

{Constraints and guidelines for this skill}

1. {Rule 1}
2. {Rule 2}

## Examples

### Example 1: {scenario}

**Input**:
{sample input}

**Output**:
{sample output}
```

## Required Skills (Bronze Tier)

### 1. email_processor

- **Purpose**: Categorize and assess priority of email data
- **Input**: Raw email metadata (sender, subject, snippet)
- **Output**: Priority level, category, suggested actions
- **Rules**: Flag financial emails, prioritize by urgency

### 2. task_creator

- **Purpose**: Generate structured task files from raw data
- **Input**: Processed item data (from any watcher)
- **Output**: Markdown file with frontmatter in Needs_Action/
- **Rules**: Follow Task File schema, ensure unique IDs

### 3. dashboard_updater

- **Purpose**: Refresh Dashboard.md with current system state
- **Input**: Current vault state (file counts, recent logs)
- **Output**: Updated Dashboard.md
- **Rules**: Preserve structure, accurate counts, timestamp

### 4. plan_generator

- **Purpose**: Create action plans for processed tasks
- **Input**: Task file content + Company_Handbook.md rules
- **Output**: Plan.md in Plans/ directory
- **Rules**: Reference source task, flag human-review items
