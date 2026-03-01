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

def get_odoo_credentials():
    """Returns Odoo URL, DB, user and password."""
    return {
        "url": os.getenv("ODOO_URL", "http://localhost:8069"),
        "db": os.getenv("ODOO_DB", "ai_employee"),
        "user": os.getenv("ODOO_USER"),
        "pass": os.getenv("ODOO_PASS")
    }

def get_social_credentials():
    """Returns credentials for Twitter, Facebook, and LinkedIn."""
    return {
        "twitter": {
            "api_key": os.getenv("X_API_KEY"),
            "api_secret": os.getenv("X_API_SECRET"),
            "access_token": os.getenv("X_ACCESS_TOKEN"),
            "access_secret": os.getenv("X_ACCESS_SECRET")
        },
        "facebook": {
            "access_token": os.getenv("FB_ACCESS_TOKEN")
        },
        "linkedin": {
            "access_token": os.getenv("LI_ACCESS_TOKEN")
        }
    }

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
