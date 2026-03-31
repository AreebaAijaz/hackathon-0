# Personal AI Employee - Bronze Tier Research

## 1. Gmail API with Python - OAuth2 Desktop Flow & Long-Running Watcher

### Decision
Use `google-auth` and `google-auth-oauthlib` (not deprecated `oauth2client`) with `InstalledAppFlow.from_client_secrets_file()` for OAuth2. For a 2-minute polling watcher, implement simple polling with exponential backoff rather than Gmail Push Notifications (which require Pub/Sub infrastructure).

### Rationale
- **OAuth2 Flow**: The OAuth2 OOB (Out-of-Band) flow is no longer supported. Modern desktop apps must use `InstalledAppFlow.run_local_server()` which spawns a temporary web server on localhost to receive the OAuth callback.
- **Token Management**: Store credentials in `token.json` for automatic refresh on subsequent runs. The flow is: check if stored credentials exist → refresh if expired → run InstalledAppFlow if no valid credentials.
- **Long-Running Watcher Strategy**: For Bronze tier simplicity, polling every 2 minutes is acceptable (vs. Push Notifications):
  - Gmail Push requires Google Cloud Pub/Sub setup, webhook endpoint, and watch renewal every 7 days
  - Simple polling with `users().messages().list(userId='me', q='is:unread AND is:important', maxResults=10)` is sufficient for low-volume personal use
  - Quota: 250 units/user/second (moving average), so 2-minute polling is well within limits (1 request = ~5 units)
- **Rate Limit Handling**: Implement exponential backoff for `429` errors (`userRateLimitExceeded`). The Gmail API returns HTTP 429 when per-user limits are exceeded.

### Alternatives
- **Push Notifications**: More scalable for high-volume or real-time requirements, but adds Pub/Sub infrastructure complexity. Must call `users().watch()` at least every 7 days (recommended daily) and use `historyId` with `history.list()` for incremental sync.
- **Pub/Sub Pull vs Push**: Pull delivery requires explicit `acknowledge()` calls; Push uses webhooks with HTTP 200 as acknowledgment.

### Key Code Patterns
```python
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)

def list_important_unread():
    service = get_gmail_service()
    results = service.users().messages().list(
        userId='me',
        q='is:unread AND is:important',
        maxResults=10
    ).execute()
    return results.get('messages', [])
```

### Sources
- [Gmail API: Unlock Seamless Automation with Python in 2026](https://www.outrightcrm.com/blog/gmail-api-automation-guide/)
- [Using OAuth 2.0 to Access Google APIs](https://developers.google.com/identity/protocols/oauth2)
- [Python quickstart | Gmail](https://developers.google.com/workspace/gmail/api/quickstart/python)
- [Usage limits | Gmail](https://developers.google.com/workspace/gmail/api/reference/quota)
- [Push Notifications | Gmail](https://developers.google.com/workspace/gmail/api/guides/push)
- [Method: users.watch | Gmail](https://developers.google.com/workspace/gmail/api/reference/rest/v1/users/watch)

---

## 2. Python BaseWatcher Pattern - Abstract Base Class Design

### Decision
Create an abstract `BaseWatcher` class using `abc.ABC` with:
- Abstract `check()` method for subclass implementation
- Concrete `run()` method with infinite loop + exponential backoff
- Cross-platform graceful shutdown using `signal.signal()` for SIGINT/SIGTERM/SIGBREAK
- Structured logging using Python's `logging` module with JSON formatter

### Rationale
- **ABC Pattern**: `abc.ABC` with `@abstractmethod` enforces interface contracts for watcher subclasses
- **Windows Signal Handling**: Windows supports limited signals: SIGABRT, SIGFPE, SIGILL, SIGINT, SIGSEGV, SIGTERM, SIGBREAK. Key difference: SIGBREAK (Ctrl+Break) is more reliable than SIGINT (Ctrl+C) on Windows as it cannot be disabled by applications.
- **Exponential Backoff**: Use `tenacity` library (standard for Python retry logic) or lightweight `backoff` library. Both support decorators with `@retry` and event handlers for logging (`on_backoff`, `on_giveup`).
- **Structured Logging**: Use `logging` with `json` formatter or `python-json-logger` for structured output suitable for log aggregation systems.

### Alternatives
- **asyncio Event Loop**: More complex but better for I/O-bound tasks. Windows uses `ProactorEventLoop` (vs `SelectorEventLoop` on Unix), and `asyncio.add_signal_handler()` only works on Unix.
- **watchdog Library**: Provides file system monitoring with `FileSystemEventHandler` pattern, but overkill for simple polling watchers.
- **graceful-shutdown PyPI**: Cross-platform library handling CTRL_CLOSE_EVENT, CTRL_SHUTDOWN_EVENT, CTRL_LOGOFF_EVENT on Windows automatically.

### Key Code Patterns
```python
import abc
import signal
import time
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

class BaseWatcher(abc.ABC):
    def __init__(self, check_interval_seconds=120):
        self.check_interval = check_interval_seconds
        self.running = False
        self.logger = self._setup_logging()

        # Windows-compatible signal handling
        signal.signal(signal.SIGINT, self._shutdown_handler)
        signal.signal(signal.SIGTERM, self._shutdown_handler)
        if hasattr(signal, 'SIGBREAK'):  # Windows only
            signal.signal(signal.SIGBREAK, self._shutdown_handler)

    def _setup_logging(self):
        logger = logging.getLogger(self.__class__.__name__)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
            '"logger": "%(name)s", "message": "%(message)s"}'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        return logger

    def _shutdown_handler(self, signum, frame):
        self.logger.info(f"Received signal {signum}, shutting down gracefully")
        self.running = False

    @abc.abstractmethod
    def check(self):
        """Implement watcher-specific logic. Raise exceptions for retry."""
        pass

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        retry=retry_if_exception_type(Exception),
        reraise=True
    )
    def _check_with_retry(self):
        return self.check()

    def run(self):
        self.running = True
        self.logger.info("Watcher started")

        while self.running:
            try:
                self._check_with_retry()
            except Exception as e:
                self.logger.error(f"Check failed after retries: {e}")

            if self.running:
                time.sleep(self.check_interval)

        self.logger.info("Watcher stopped")
```

### Sources
- [Abstract Base Class (abc) in Python - GeeksforGeeks](https://www.geeksforgeeks.org/python/abstract-base-class-abc-in-python/)
- [signal — Set handlers for asynchronous events](https://docs.python.org/3/library/signal.html)
- [Handling SIGTERM in python on Windows](https://maruel.ca/post/python_windows_signal/)
- [backoff · PyPI](https://pypi.org/project/backoff/)
- [GitHub - jd/tenacity: Retrying library for Python](https://github.com/jd/tenacity)
- [Building Resilient Python Applications with Tenacity](https://www.amitavroy.com/articles/building-resilient-python-applications-with-tenacity-smart-retries-for-a-fail-proof-architecture)

---

## 3. Obsidian Vault Compatibility - Programmatic Markdown Creation

### Decision
Use standard markdown file creation with YAML frontmatter. Prefer **wikilinks** `[[Note Name]]` for internal links if staying within Obsidian ecosystem, or standard markdown `[text](file.md)` for cross-editor compatibility.

### Rationale
- **Frontmatter Requirements**:
  - Must be the **first thing** in file (no blank lines above)
  - Use YAML format: triple-dash delimiters `---`
  - Common fields: `title`, `date`, `tags`, `status`
  - Obsidian auto-detects frontmatter as properties panel
- **File Naming**: No special restrictions. Spaces are allowed (e.g., `My Note.md`). Obsidian handles special characters gracefully.
- **Link Syntax Tradeoffs**:
  - **Wikilinks** `[[Note Name]]` or `[[Note Name|Display Text]]`: Native Obsidian syntax, supports backlinks, but appears as plain text in other editors
  - **Markdown** `[Display Text](Note Name.md)`: Cross-editor compatible, but backlinks don't work in Obsidian
  - Setting: Obsidian → Settings → Files & Links → "Use [[Wikilinks]]"
- **Programmatic Creation**: No special API needed. Standard file I/O works. Obsidian watches the vault directory and auto-reloads changes.

### Alternatives
- **Obsidian MCP Plugin**: Embeds MCP server in Obsidian for structured note creation with custom schemas and validation via Model Context Protocol.
- **Frontmatter Generator Plugin**: Automates frontmatter on save using JSON/JS expressions and Dataview queries.
- **Metatemplates Plugin**: Uses `type`, `nameFormat`, `destFolder` properties in frontmatter for template-based file generation.

### Key Code Patterns
```python
from datetime import datetime
import os

def create_obsidian_note(vault_path, filename, title, content, tags=None):
    """Create a markdown note in Obsidian vault with frontmatter."""
    tags = tags or []

    frontmatter = f"""---
title: {title}
date: {datetime.now().strftime('%Y-%m-%d')}
tags: {tags}
---

"""

    full_content = frontmatter + content

    filepath = os.path.join(vault_path, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(full_content)

    return filepath

# Example usage
create_obsidian_note(
    vault_path="D:/MyVault",
    filename="Daily Note 2026-02-16.md",
    title="Daily Note",
    content="## Morning\n\nImportant email: [[Email Subject]]\n\n## Tasks\n- [ ] Review email",
    tags=["daily", "email"]
)
```

### Gotchas
- **No blank lines before frontmatter**: File must start with `---`
- **Wikilink limitations**: Other markdown editors won't render `[[links]]` as clickable
- **Case sensitivity**: Wikilinks are case-insensitive in Obsidian, but filesystem may be case-sensitive (Linux)
- **Nested folders**: Use forward slashes in wikilinks: `[[folder/note]]`

### Sources
- [Obsidian Markdown Cheatsheet: Every Syntax You Actually Need](https://desktopcommander.app/blog/2026/02/03/obsidian-markdown-cheatsheet-every-syntax-you-actually-need/)
- [Internal links - Obsidian Help](https://help.obsidian.md/links)
- [Wikilink vs Markdown - Obsidian Forum](https://forum.obsidian.md/t/wikilink-vs-markdown-the-latter-suffers-from-lack-of-support/86920)
- [Vault MCP | Awesome MCP Servers](https://mcpservers.org/servers/jlevere/obsidian-mcp-plugin)
- [Frontmatter generator - Obsidian Plugin](https://www.obsidianstats.com/plugins/frontmatter-generator)

---

## 4. Claude Code CLI Integration - Subprocess Invocation from Python

### Decision
Invoke Claude Code CLI as subprocess using `subprocess.Popen()` with piped stdin/stdout for JSON communication. Use minimal `--system-prompt` (or omit) and pass detailed instructions in user prompt to avoid Windows tool permission bugs.

### Rationale
- **Subprocess Pattern**: Claude Code CLI can be invoked programmatically via subprocess. The SDK pattern: spawn CLI as subprocess, communicate via JSON messages on stdin/stdout.
- **Windows-Specific Issue**: Long/complex `--system-prompt` can cause tool permissions to silently fail on Windows, even with `--allowedTools` set correctly. **Workaround**: Keep system prompt minimal, put detailed instructions in user prompt instead.
- **Command-Line Arguments**:
  - Non-interactive: `claude -p "your prompt here"`
  - Key flags: `--output-format json`, `--model sonnet`, `--system-prompt "..."`, `--allowedTools`
  - stdin piping: Bypasses command-line length limits on Windows
- **Process Management**: Use `CREATE_NEW_PROCESS_GROUP` on Windows for better process tree management.

### Alternatives
- **Claude Agent SDK**: Official Python SDK (`claude-agent-sdk`) for spawning Claude Code CLI as subprocess with built-in JSON message handling.
- **Claude MPM**: Multi-agent orchestration framework requiring Claude Code CLI v2.1.3+. Provides workflow management, skills system, MCP integration.
- **Claude Orchestrator**: CLI tool for parallel Claude Code instances using git worktrees (divide-and-conquer strategy).
- **Agent Skill**: `using-claude-code-cli-agent-skill` on GitHub provides standardized invocation pattern for automation pipelines.

### Key Code Patterns
```python
import subprocess
import json

def invoke_claude_code(prompt, system_prompt=None, allowed_tools=None):
    """Invoke Claude Code CLI as subprocess."""
    cmd = ['claude', '-p', prompt]

    if system_prompt:
        # WARNING: Keep system prompt minimal on Windows to avoid tool permission bugs
        cmd.extend(['--system-prompt', system_prompt])

    if allowed_tools:
        cmd.extend(['--allowedTools', ','.join(allowed_tools)])

    # Add JSON output format
    cmd.extend(['--output-format', 'json'])

    # For Windows: CREATE_NEW_PROCESS_GROUP helps with process management
    creationflags = subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0

    process = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=creationflags,
        text=True
    )

    stdout, stderr = process.communicate()

    if process.returncode != 0:
        raise RuntimeError(f"Claude Code failed: {stderr}")

    return json.loads(stdout) if stdout else None

# Example usage
result = invoke_claude_code(
    prompt="Read D:/hackathon-0/README.md and summarize it",
    allowed_tools=['Read', 'Glob']
)
```

### Sources
- [CLI reference - Claude Code Docs](https://code.claude.com/docs/en/cli-reference)
- [Running Claude Code from Windows CLI: A Practical Guide](https://dstreefkerk.github.io/2026-01-running-claude-code-from-windows-cli/)
- [GitHub - bobmatnyc/claude-mpm: Claude Multi-Agent Project Manager](https://github.com/bobmatnyc/claude-mpm)
- [Inside the Claude Agent SDK: stdin/stdout Communication](https://buildwithaws.substack.com/p/inside-the-claude-agent-sdk-from)
- [GitHub - SpillwaveSolutions/using-claude-code-cli-agent-skill](https://github.com/SpillwaveSolutions/using-claude-code-cli-agent-skill)
- [[BUG]: CLI error with system prompt - Issue #4930](https://github.com/anthropics/claude-code/issues/4930)

---

## 5. UV Python Project Setup - Windows Dependency Management

### Decision
Use `uv init` for project creation, `uv add` for dependencies (auto-creates `.venv` and updates `pyproject.toml` + `uv.lock`), and commit `uv.lock` for reproducible builds. Use environment markers for Windows-specific dependencies.

### Rationale
- **UV Overview**: Fast Rust-based package manager and project manager. Combines functionality of pip, venv, poetry, pipenv into single tool.
- **Project Structure Best Practices**:
  - Virtual environment: `.venv` (auto-created by UV, local to project)
  - Source organization: Use `src/` directory for non-trivial projects (not root)
  - Lock file: `uv.lock` is cross-platform, contains exact resolved versions, should be checked into version control
  - Config: `pyproject.toml` specifies broad requirements, `uv.lock` specifies exact versions
- **Dependency Management**:
  - Single command: `uv add <package>` handles environment creation, installation, and config updates
  - Windows-specific deps: Use environment markers: `colorama>=0.4.6; platform_system == "Windows"`
- **Reproducibility**: `uv.lock` ensures consistent installs across machines/platforms. UV resolves dependencies once, locks them, then installs exact versions.

### Alternatives
- **Poetry**: Similar lock file approach (`poetry.lock`), but slower than UV and more opinionated project structure.
- **pip + venv**: Manual environment management, no lock file by default (requires `pip freeze > requirements.txt`).
- **Pipenv**: Has `Pipfile.lock` but slower and less actively maintained than UV.

### Key Commands
```bash
# Initialize new project
uv init my-project
cd my-project

# Add dependencies (auto-creates .venv if needed)
uv add google-auth google-auth-oauthlib google-api-python-client
uv add python-dotenv watchdog tenacity

# Add Windows-specific dependency
uv add "colorama>=0.4.6; platform_system == 'Windows'"

# Install all dependencies from lock file (on another machine)
uv sync

# Run script with project environment
uv run python src/main.py

# Update dependencies
uv lock --upgrade
```

### Project Structure Example
```
my-project/
├── .venv/              # Virtual environment (auto-created, gitignored)
├── src/
│   └── my_project/
│       ├── __init__.py
│       └── main.py
├── tests/
├── pyproject.toml      # Broad requirements
├── uv.lock             # Exact versions (commit this!)
└── README.md
```

### pyproject.toml Example
```toml
[project]
name = "personal-ai-employee"
version = "0.1.0"
description = "Bronze tier AI email assistant"
requires-python = ">=3.10"
dependencies = [
    "google-auth>=2.0.0",
    "google-auth-oauthlib>=1.0.0",
    "google-api-python-client>=2.0.0",
    "python-dotenv>=1.0.0",
    "watchdog>=3.0.0",
    "tenacity>=8.0.0",
    "colorama>=0.4.6; platform_system == 'Windows'",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

### Sources
- [Managing dependencies | uv](https://docs.astral.sh/uv/concepts/projects/dependencies/)
- [Managing Python Projects With uv: An All-in-One Solution – Real Python](https://realpython.com/python-uv/)
- [Python UV: The Ultimate Guide to the Fastest Python Package Manager | DataCamp](https://www.datacamp.com/tutorial/python-uv)
- [Getting Started with uv: Setting Up Your Python Project in 2026](https://www.bitdoze.com/uv-get-start/)
- [uv: An In-Depth Guide to Python's Fast Package Manager](https://www.saaspegasus.com/guides/uv-deep-dive/)
- [Working on projects | uv](https://docs.astral.sh/uv/guides/projects/)

---

## Summary Recommendations for Bronze Tier

1. **Gmail Watcher**: Simple 2-minute polling (not Push) with exponential backoff via `tenacity`
2. **Watcher Pattern**: ABC with Windows signal handling (SIGINT/SIGTERM/SIGBREAK) and structured logging
3. **Obsidian**: Standard markdown + YAML frontmatter, wikilinks for internal references
4. **Claude Code**: Subprocess invocation with minimal `--system-prompt` (avoid Windows bug), JSON output format
5. **UV Setup**: `uv init` + `uv add` workflow, commit `uv.lock`, use `src/` structure

All components are Windows-compatible, suitable for personal use (low volume), and minimize infrastructure complexity while maintaining good software practices.
