# Quickstart: Bronze Tier Foundation

**Feature**: `001-bronze-foundation`
**Date**: 2026-02-16
**Estimated Setup Time**: ~15 minutes (excluding Gmail OAuth2)

## Prerequisites

- Python 3.13+
- UV package manager (`pip install uv` or see https://docs.astral.sh/uv/)
- Obsidian v1.10.6+ (https://obsidian.md)
- Claude Code CLI (Pro version)
- Google account with Gmail API access
- Git

## Step 1: Clone and Initialize

```bash
git clone <repository-url> hackathon-0
cd hackathon-0
git checkout 001-bronze-foundation
```

## Step 2: Install Python Dependencies

```bash
uv sync
```

This reads `pyproject.toml` and `uv.lock` to install exact
dependency versions into `.venv/`.

## Step 3: Gmail API Credentials

1. Go to https://console.cloud.google.com/
2. Create a new project (or select existing)
3. Enable the Gmail API
4. Configure OAuth consent screen (External, test mode)
5. Create OAuth 2.0 credentials (Desktop application)
6. Download `credentials.json`

## Step 4: Configure Environment

```bash
cp .env.template .env
```

Edit `.env` and set:
```
GMAIL_CREDENTIALS_PATH=./credentials.json
GMAIL_TOKEN_PATH=./token.json
VAULT_PATH=./AI_Employee_Vault
CHECK_INTERVAL=120
DEV_MODE=false
DRY_RUN=false
```

Place `credentials.json` in the project root.

## Step 5: First-Time Gmail Authentication

```bash
uv run python -m src.watchers.gmail_watcher --auth-only
```

This opens a browser for Google OAuth2 consent. After approval,
`token.json` is created locally. This only needs to happen once.

## Step 6: Open Obsidian Vault

1. Open Obsidian
2. Select "Open folder as vault"
3. Navigate to `hackathon-0/AI_Employee_Vault/`
4. Verify Dashboard.md and folder structure are visible

## Step 7: Start the Gmail Watcher

```bash
uv run python -m src.watchers.gmail_watcher
```

The watcher will:
- Check Gmail every 2 minutes for important unread emails
- Create task files in `AI_Employee_Vault/Needs_Action/`
- Log all activity to `AI_Employee_Vault/Logs/`

## Step 8: Process Tasks with Claude Code

```bash
uv run python -m src.orchestrator
```

The orchestrator will:
- Scan `Needs_Action/` for pending task files
- Invoke Claude Code to analyze each task
- Create plans in `Plans/`
- Update `Dashboard.md`
- Archive processed tasks to `Done/`

## Verification Checklist

- [ ] Obsidian vault opens with all folders visible
- [ ] Dashboard.md shows system status
- [ ] Company_Handbook.md contains operational rules
- [ ] Gmail watcher detects a test email (mark one as important)
- [ ] Task file appears in Needs_Action/
- [ ] Orchestrator processes the task
- [ ] Plan appears in Plans/
- [ ] Dashboard.md updates with recent activity
- [ ] Task file moves to Done/
- [ ] Log entries appear in Logs/

## Dry-Run Mode

To test without live Gmail access:

```bash
# Set in .env
DRY_RUN=true

# Or pass as flag
uv run python -m src.watchers.gmail_watcher --dry-run
```

This creates sample task files without connecting to Gmail.

## Troubleshooting

**"credentials.json not found"**
- Ensure the file is in the project root
- Check `GMAIL_CREDENTIALS_PATH` in `.env`

**"Token has been expired or revoked"**
- Delete `token.json` and re-run Step 5

**"ModuleNotFoundError"**
- Run `uv sync` to install dependencies

**Watcher crashes on startup**
- Verify `VAULT_PATH` points to a valid directory
- Check that all vault folders exist

**No emails detected**
- Verify you have unread emails marked as important
- Check the Gmail query: `is:unread AND is:important`
- Review watcher logs in `AI_Employee_Vault/Logs/`
