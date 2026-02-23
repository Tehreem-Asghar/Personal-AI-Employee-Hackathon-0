import sys
import os
import base64
from pathlib import Path
from email.message import EmailMessage

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from mcp.server.fastmcp import FastMCP

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

# Initialize FastMCP server
mcp = FastMCP("EmailServer")

def get_gmail_service():
    """Builds and returns the Gmail service using existing token.json."""
    if not os.path.exists('token.json'):
        raise FileNotFoundError("token.json not found! Please run src/watchers/gmail_watcher.py once to authenticate.")
    
    # Define scopes (ensure they match gmail_watcher.py)
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.send'
    ]
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    return build('gmail', 'v1', credentials=creds)

@mcp.tool()
def send_email(to: str, subject: str, body: str) -> str:
    """
    Sends an email via the Gmail API.
    :param to: Recipient email address.
    :param subject: Email subject line.
    :param body: Plain text email body.
    """
    try:
        service = get_gmail_service()
        message = EmailMessage()
        message.set_content(body)
        message['To'] = to
        message['From'] = 'me'
        message['Subject'] = subject

        # Encoded message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {'raw': encoded_message}
        
        send_message = (service.users().messages().send(userId="me", body=create_message).execute())
        
        return f"Email successfully sent to {to}. Message ID: {send_message['id']}"

    except HttpError as error:
        return f"An error occurred while sending email: {error}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"

if __name__ == "__main__":
    # Start the MCP server
    mcp.run()
