"""Prompt template builder for Claude Code task processing.

Constructs structured prompts that include task content, Company Handbook
rules, and skill documentation for Claude Code to analyze and generate
action plans.
"""


def build_processing_prompt(
    task_content: str,
    handbook_rules: str,
    skill_docs: dict[str, str],
) -> str:
    """Build a Claude Code processing prompt from task data and context.

    Args:
        task_content: Full content of the task file (markdown with YAML frontmatter).
        handbook_rules: Full content of Company_Handbook.md.
        skill_docs: Dict mapping skill name to SKILL.md content.
            Expected keys: email_processor, task_creator, plan_generator,
            dashboard_updater.

    Returns:
        Formatted prompt string for Claude Code invocation.
    """
    skill_section = ""
    for name, doc in skill_docs.items():
        skill_section += f"\n### Skill: {name}\n\n{doc}\n"

    prompt = f"""You are a Personal AI Employee processing a task from the inbox.
Analyze the task below and produce a structured action plan.

## Company Handbook (MUST follow these rules)

{handbook_rules}

## Available Skills Reference
{skill_section}
## Task to Process

{task_content}

## Instructions

1. Analyze the task content and determine its nature (email, request, notification, etc.)
2. Assess priority using the email_processor skill rules
3. Check if this involves financial matters - if so, set requires_human to true
4. Generate a clear action plan following the plan_generator skill format
5. Be specific and actionable in your recommended actions

## Required Output Format

Respond with ONLY valid JSON matching this schema:

```json
{{
  "plan_title": "Brief descriptive title for the plan",
  "analysis": "1-3 sentence analysis of what was received and its significance",
  "recommended_actions": [
    "Specific action step 1",
    "Specific action step 2",
    "Specific action step 3"
  ],
  "priority": "urgent|important|normal",
  "requires_human": true|false,
  "flagged_items": ["List of items needing human attention, or empty array"]
}}
```

IMPORTANT: Output ONLY the JSON object, no markdown fences, no extra text."""

    return prompt
