import os
from pathlib import Path
from dotenv import load_dotenv

# Find the project root (where .env is located)
PROJECT_ROOT = Path(__file__).parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")

def get_gmail_credentials():
    """Returns Gmail client ID and secret from environment."""
    return {
        "client_id": os.getenv("GMAIL_CLIENT_ID"),
        "client_secret": os.getenv("GMAIL_CLIENT_SECRET")
    }

def get_whatsapp_session_path():
    """Returns the path where Playwright should store the WhatsApp session."""
    return os.getenv("WHATSAPP_SESSION_PATH", ".playwright_context/whatsapp")

def is_dry_run():
    """Checks if the system is in DRY_RUN mode."""
    return os.getenv("DRY_RUN", "true").lower() == "true"

def is_dev_mode():
    """Checks if the system is in DEV_MODE."""
    return os.getenv("DEV_MODE", "true").lower() == "true"

if __name__ == "__main__":
    print(f"Project Root: {PROJECT_ROOT}")
    print(f"Gmail Config: {get_gmail_credentials()}")
    print(f"WhatsApp Path: {get_whatsapp_session_path()}")
    print(f"Dry Run: {is_dry_run()}")
