"""Claude Code CLI invocation utility for the AI Employee system.

Runs Claude Code as a subprocess and parses its JSON output.
"""

import json
import logging
import subprocess
import sys

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 120  # seconds


def invoke_claude(
    prompt: str,
    vault_path: str,
    allowed_tools: list[str] | None = None,
    timeout: int = DEFAULT_TIMEOUT,
) -> dict:
    """Invoke Claude Code CLI with a prompt and return parsed JSON response.

    Args:
        prompt: The prompt text to send to Claude Code.
        vault_path: Path to the vault (used as working context).
        allowed_tools: Optional list of allowed tool names for Claude.
        timeout: Maximum seconds to wait for response (default: 120).

    Returns:
        Parsed JSON dict from Claude Code's response.

    Raises:
        RuntimeError: If Claude Code exits with non-zero status,
                      times out, or returns invalid JSON.
        FileNotFoundError: If the claude CLI is not found on PATH.
    """
    cmd = [
        "claude",
        "-p",
        prompt,
        "--output-format",
        "json",
    ]

    if allowed_tools:
        for tool in allowed_tools:
            cmd.extend(["--allowedTools", tool])

    logger.info("Invoking Claude Code (timeout=%ds)...", timeout)

    try:
        # Use CREATE_NEW_PROCESS_GROUP on Windows for clean process management
        creation_flags = 0
        if sys.platform == "win32":
            creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            creationflags=creation_flags,
        )
    except FileNotFoundError:
        raise FileNotFoundError(
            "Claude Code CLI not found. Ensure 'claude' is installed and on PATH. "
            "Install with: npm install -g @anthropic-ai/claude-code"
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError(
            f"Claude Code timed out after {timeout}s. "
            "Consider increasing timeout or simplifying the prompt."
        )

    if result.returncode != 0:
        error_msg = result.stderr.strip() if result.stderr else "Unknown error"
        raise RuntimeError(
            f"Claude Code exited with code {result.returncode}: {error_msg}"
        )

    stdout = result.stdout.strip()
    if not stdout:
        raise RuntimeError("Claude Code returned empty output")

    # Parse the JSON response - Claude --output-format json wraps in a result object
    try:
        response = json.loads(stdout)
    except json.JSONDecodeError as e:
        logger.error("Failed to parse Claude output as JSON: %s", stdout[:500])
        raise RuntimeError(f"Claude Code returned invalid JSON: {e}")

    # Extract the actual result text if wrapped in Claude's output format
    if isinstance(response, dict) and "result" in response:
        result_text = response["result"]
        # The result text itself might be JSON
        try:
            return json.loads(result_text)
        except (json.JSONDecodeError, TypeError):
            return response
    elif isinstance(response, list):
        # Claude output-format json returns a list of content blocks
        # Find the text block and parse its content
        for block in response:
            if isinstance(block, dict) and block.get("type") == "text":
                text = block.get("text", "")
                try:
                    return json.loads(text)
                except json.JSONDecodeError:
                    continue
        # If no parseable JSON in blocks, return the raw response
        return {"raw_response": response}

    return response


def invoke_claude_dry_run(prompt: str, task_content: str) -> dict:
    """Simulate Claude Code invocation for dry-run mode.

    Generates a plausible plan response without calling Claude.

    Args:
        prompt: The prompt that would have been sent.
        task_content: The task file content for context.

    Returns:
        Simulated plan response dict.
    """
    # Check for financial keywords to set requires_human
    text_lower = task_content.lower()
    financial_keywords = ["invoice", "payment", "expense", "$", "amount due"]
    is_financial = any(kw in text_lower for kw in financial_keywords)

    return {
        "plan_title": "[DRY RUN] Simulated Plan",
        "analysis": "This is a simulated analysis generated in dry-run mode. "
        "No Claude Code invocation was made.",
        "recommended_actions": [
            "Review the original task content",
            "Determine appropriate follow-up actions",
            "Update task status after review",
        ],
        "priority": "important",
        "requires_human": is_financial,
        "flagged_items": ["Financial matter detected - requires human review"]
        if is_financial
        else [],
    }
