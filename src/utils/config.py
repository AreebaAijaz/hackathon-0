"""Environment configuration loader for the AI Employee system.

Loads settings from .env file with sensible defaults matching .env.template.
"""

import os
from pathlib import Path

from dotenv import load_dotenv


def load_config(env_path: str | None = None) -> dict:
    """Load configuration from .env file with defaults.

    Args:
        env_path: Optional path to .env file. If None, searches
                  current directory and parent directories.

    Returns:
        Configuration dict with keys: vault_path, credentials_path,
        token_path, check_interval, dev_mode, dry_run.
    """
    if env_path:
        load_dotenv(env_path)
    else:
        load_dotenv()

    return {
        "vault_path": os.path.abspath(
            os.environ.get("VAULT_PATH", "./AI_Employee_Vault")
        ),
        "credentials_path": os.path.abspath(
            os.environ.get("GMAIL_CREDENTIALS_PATH", "./credentials.json")
        ),
        "token_path": os.path.abspath(
            os.environ.get("GMAIL_TOKEN_PATH", "./token.json")
        ),
        "check_interval": int(os.environ.get("CHECK_INTERVAL", "120")),
        "dev_mode": os.environ.get("DEV_MODE", "false").lower() == "true",
        "dry_run": os.environ.get("DRY_RUN", "false").lower() == "true",
    }
