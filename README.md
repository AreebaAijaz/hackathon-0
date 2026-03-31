# Personal AI Employee - Bronze Tier

An autonomous AI Employee that monitors your Gmail for important emails, creates structured task files, and generates action plans — all managed through an Obsidian vault.

## Architecture

```
PERCEPTION          MEMORY              REASONING           ACTION
(Gmail Watcher) --> (Obsidian Vault) --> (Claude Code) --> (File Operations)
     |                   |                    |                  |
  Detects           Stores tasks         Analyzes &          Creates plans,
  important         in Needs_Action/     generates plans     updates dashboard,
  emails                                                     archives to Done/
```

## Prerequisites

- **Python 3.13+**
- **UV** package manager — [install guide](https://docs.astral.sh/uv/)
- **Obsidian** v1.10.6+ — [obsidian.md](https://obsidian.md)
- **Claude Code CLI** (Pro version)
- **Google account** with Gmail API access

## Quick Start

1. **Clone and install**:
   ```bash
   git clone <repository-url> hackathon-0
   cd hackathon-0
   uv sync
   ```

2. **Set up Gmail API credentials** (see [Credential Setup](#credential-setup) below)

3. **Configure environment**:
   ```bash
   cp .env.template .env
   # Edit .env with your paths
   ```

4. **First-time Gmail authentication**:
   ```bash
   uv run python -m src.watchers --auth-only
   ```

5. **Start the Gmail Watcher**:
   ```bash
   uv run python -m src.watchers
   ```

6. **Process tasks with Claude Code**:
   ```bash
   uv run python -m src --once
   ```

## Vault Structure

```
AI_Employee_Vault/
├── Dashboard.md          # Real-time system status
├── Company_Handbook.md   # AI behavioral rules
├── Inbox/                # Raw incoming items (future use)
├── Needs_Action/         # Pending task files from watchers
├── Plans/                # Claude-generated action plans
├── Done/                 # Archived processed tasks
├── Logs/                 # Audit trail (NDJSON, date-partitioned)
└── skills/               # Agent skill documentation
    ├── email_processor/
    ├── task_creator/
    ├── dashboard_updater/
    └── plan_generator/
```

Open `AI_Employee_Vault/` as a vault in Obsidian to view the dashboard and all files.

## Credential Setup

### Google Cloud Console

1. Go to [console.cloud.google.com](https://console.cloud.google.com/)
2. Create a new project (e.g., "AI-Employee")
3. Navigate to **APIs & Services > Library** and enable the **Gmail API**
4. Go to **APIs & Services > OAuth consent screen**:
   - Select **External** user type
   - Fill in app name and email
   - Add scope: `https://www.googleapis.com/auth/gmail.readonly`
   - Add your email as a test user
5. Go to **APIs & Services > Credentials**:
   - Click **Create Credentials > OAuth 2.0 Client ID**
   - Select **Desktop application**
   - Download the JSON file and save as `credentials.json` in the project root

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GMAIL_CREDENTIALS_PATH` | `./credentials.json` | Path to OAuth2 credentials |
| `GMAIL_TOKEN_PATH` | `./token.json` | Path to stored auth token |
| `VAULT_PATH` | `./AI_Employee_Vault` | Path to Obsidian vault |
| `CHECK_INTERVAL` | `120` | Seconds between Gmail checks |
| `DEV_MODE` | `false` | Enable development mode |
| `DRY_RUN` | `false` | Simulate without live API calls |

## Usage

### Gmail Watcher

```bash
# Normal mode — checks every 2 minutes
uv run python -m src.watchers

# Dry-run mode — creates sample tasks without Gmail
uv run python -m src.watchers --dry-run

# Auth-only — just authenticate and exit
uv run python -m src.watchers --auth-only

# Custom interval (seconds)
uv run python -m src.watchers --interval 60
```

### Orchestrator

```bash
# Process all pending tasks once and exit
uv run python -m src --once

# Watch mode — continuously poll for new tasks
uv run python -m src

# Dry-run — simulate processing without Claude Code
uv run python -m src --dry-run
```

### Log Viewer

```bash
# View today's logs
uv run python -m src.utils.view_logs

# View logs for a specific date
uv run python -m src.utils.view_logs --date 2026-02-17

# Filter by action type
uv run python -m src.utils.view_logs --type email_detected
```

## Troubleshooting

**"credentials.json not found"**
- Ensure the file is in the project root (or the path in `.env`)
- Download it again from Google Cloud Console

**"Token has been expired or revoked"**
- Delete `token.json` and re-run with `--auth-only`

**"ModuleNotFoundError"**
- Run `uv sync` to install all dependencies

**Watcher crashes on startup**
- Verify `VAULT_PATH` in `.env` points to a valid directory
- Run `uv run python -c "from src.utils.vault import ensure_vault_structure; ensure_vault_structure('./AI_Employee_Vault')"`

**No emails detected**
- Verify you have unread emails marked as important in Gmail
- Check the watcher logs in `AI_Employee_Vault/Logs/`
- Try `--dry-run` mode to verify the watcher runs correctly

## Security

- **Credentials**: Stored in `.env` and `credentials.json`, both gitignored
- **Token**: OAuth2 token stored in `token.json`, gitignored
- **Gmail scope**: Read-only (`gmail.readonly`) — cannot send or modify emails
- **Local-first**: All data stays on your local machine
- **Audit trail**: Every action logged to `Logs/` in structured JSON

## Tier Declaration

**Bronze Tier** — Foundation implementation including:
- Obsidian vault with Dashboard and Company Handbook
- Gmail Watcher (email monitoring)
- Claude Code processing pipeline
- 4 Agent Skills
- Structured audit logging
