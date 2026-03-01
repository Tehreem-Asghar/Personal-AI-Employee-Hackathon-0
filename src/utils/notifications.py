import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.mcp.email_server import send_email
from src.utils.whatsapp_send import send_whatsapp_message
from src.utils.credentials import get_gmail_credentials

logger = logging.getLogger("Notifications")

def send_alert(subject: str, message: str, channel: str = "email"):
    """
    Sends a system alert to the human supervisor.
    :param channel: 'email' or 'whatsapp'
    """
    try:
        # Determine recipient (self)
        creds = get_gmail_credentials()
        # Assuming the authenticated user is the admin for now
        # Ideally, this should be configurable in .env (ADMIN_EMAIL, ADMIN_PHONE)
        
        if channel == "email":
            # For hackathon, we send to 'me' (the authenticated user)
            # In production, use os.getenv("ADMIN_EMAIL")
            send_email(to="me", subject=f"[AI ALERT] {subject}", body=message)
            logger.info(f"Sent email alert: {subject}")
            
        elif channel == "whatsapp":
            # Requires a configured contact name in WhatsApp
            # send_whatsapp_message("Admin", f"🚨 {subject}\n{message}")
            pass

    except Exception as e:
        logger.error(f"Failed to send alert: {e}")

if __name__ == "__main__":
    send_alert("Test Alert", "This is a test notification from the Guardian Watchdog.")
