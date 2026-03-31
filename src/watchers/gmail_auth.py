"""Gmail API authentication helper for the AI Employee system.

Handles OAuth2 Desktop flow with automatic token refresh and persistence.
Scope: gmail.readonly (read-only access to Gmail).
"""

import logging
import os
import sys

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def get_gmail_service(credentials_path: str, token_path: str):
    """Authenticate and return an authorized Gmail API service client.

    Uses stored token if available and valid; otherwise initiates
    the OAuth2 consent flow via a local server.

    Args:
        credentials_path: Path to the OAuth2 client secrets JSON file
                          (downloaded from Google Cloud Console).
        token_path: Path where the authorized user token is stored/cached.

    Returns:
        googleapiclient.discovery.Resource: Authorized Gmail API service.

    Raises:
        FileNotFoundError: If credentials_path does not exist.
        RuntimeError: If authentication fails.
    """
    if not os.path.isfile(credentials_path):
        raise FileNotFoundError(
            f"OAuth2 credentials file not found: {credentials_path}. "
            "Download it from Google Cloud Console → APIs & Services → Credentials."
        )

    creds = None

    # Try loading existing token
    if os.path.isfile(token_path):
        try:
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
            logger.info("Loaded existing token from %s", token_path)
        except Exception as e:
            logger.warning("Failed to load token file: %s", e)
            creds = None

    # Refresh or initiate new auth flow
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            logger.info("Token refreshed successfully")
        except Exception as e:
            logger.warning("Token refresh failed: %s. Re-authenticating...", e)
            creds = None

    if not creds or not creds.valid:
        logger.info("Starting OAuth2 consent flow...")
        flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
        creds = flow.run_local_server(port=0)
        logger.info("OAuth2 authentication completed")

    # Persist token for next run
    with open(token_path, "w", encoding="utf-8") as f:
        f.write(creds.to_json())
    logger.info("Token saved to %s", token_path)

    # Build and return the service
    from googleapiclient.discovery import build

    service = build("gmail", "v1", credentials=creds)
    return service


def auth_only(credentials_path: str, token_path: str) -> bool:
    """Run authentication flow only, then exit.

    Useful for first-time setup or re-authentication.

    Args:
        credentials_path: Path to OAuth2 client secrets JSON file.
        token_path: Path to store the authorized user token.

    Returns:
        True if authentication succeeded.
    """
    try:
        service = get_gmail_service(credentials_path, token_path)
        # Verify by fetching profile
        profile = service.users().getProfile(userId="me").execute()
        logger.info("Authenticated as: %s", profile.get("emailAddress", "unknown"))
        return True
    except Exception as e:
        logger.error("Authentication failed: %s", e)
        return False


if __name__ == "__main__":
    import argparse

    from src.utils.config import load_config

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

    parser = argparse.ArgumentParser(description="Gmail authentication helper")
    parser.add_argument(
        "--auth-only",
        action="store_true",
        default=True,
        help="Authenticate and verify Gmail access (default behavior)",
    )
    args = parser.parse_args()

    config = load_config()
    success = auth_only(config["credentials_path"], config["token_path"])
    sys.exit(0 if success else 1)
