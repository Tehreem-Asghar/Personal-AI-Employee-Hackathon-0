import os.path
import sys
import json
from pathlib import Path
from datetime import datetime
import base64

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.watchers.base_watcher import BaseWatcher
from src.utils.paths import find_vault_root
from src.utils.logger import log_event

# If modifying these scopes, delete the file token.json.
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send'
]

class GmailWatcher(BaseWatcher):
    def __init__(self, vault_path: Path, check_interval: int = 300): # 5 minutes default
        super().__init__(vault_path, check_interval)
        self.creds = self._authenticate()
        self.processed_ids_file = vault_root / ".processed_gmail_ids.json"
        self.processed_ids = self._load_processed_ids()
        self.service = build('gmail', 'v1', credentials=self.creds)
        # Categorized keywords for filtering
        self.keywords = [
            'invoice', 'payment', 'pricing', 'quote', 'budget', 'bill', # Financial
            'meeting', 'schedule', 'call', 'appointment', 'zoom',       # Scheduling
            'project', 'task', 'update', 'milestone', 'deadline',       # Operational
            'urgent', 'asap', 'important', 'critical',                  # Urgency
            'help', 'question', 'query', 'issue'                        # Support
        ]

    def _load_processed_ids(self):
        """Loads processed email IDs from a file."""
        if self.processed_ids_file.exists():
            with open(self.processed_ids_file, 'r') as f:
                return set(json.load(f))
        return set()
    
    def _save_processed_ids(self):
        """Saves processed email IDs to a file."""
        with open(self.processed_ids_file, 'w') as f:
            json.dump(list(self.processed_ids), f)

    def _authenticate(self):
        """Handles Gmail API authentication flow."""
        creds = None
        # The file token.json stores the user's access and refresh tokens.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists('credentials.json'):
                    self.logger.error("credentials.json not found! Please download it from Google Cloud Console.")
                    raise FileNotFoundError("credentials.json missing.")
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        return creds

    def check_for_updates(self) -> list:
        """Fetches unread messages matching keywords."""
        try:
            # Rebuild service to prevent stale connections
            self.service = build('gmail', 'v1', credentials=self.creds, cache_discovery=False)
            
            # Construct query: is:unread {keyword1 keyword2 ...}
            query = f"is:unread {{{' '.join(self.keywords)}}}"
            # Limit results to 20 per poll to avoid overwhelming the system
            results = self.service.users().messages().list(userId='me', q=query, maxResults=20).execute()
            messages = results.get('messages', [])
            
            # Filter out already processed messages
            if not messages:
                self.logger.info("GmailWatcher: No new messages matching keywords.")
                return []
            
            unprocessed_messages = [m for m in messages if m['id'] not in self.processed_ids]
            return unprocessed_messages
        except (HttpError, ConnectionError, BrokenPipeError) as error:
            self.logger.error(f'Connection error occurred: {error}. Will retry next cycle.')
            return []
        except Exception as e:
            self.logger.error(f'Unexpected error in check_for_updates: {e}')
            return []

    def create_action_file(self, message_stub) -> Path:
        """Processes a single message and creates a .md file."""
        msg_id = message_stub['id']
        try:
            message = self.service.users().messages().get(userId='me', id=msg_id).execute()
            payload = message['payload']
            headers = payload.get('headers', [])
            
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), "No Subject")
            sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), "Unknown Sender")
            snippet = message.get('snippet', '')

            content = f"""---
type: email
id: {msg_id}
from: {sender}
subject: {subject}
received: {datetime.now().isoformat()}
status: pending_action
---
# Email from {sender}
## Subject: {subject}

### Content Snippet:
{snippet}

### Suggested Actions:
- [ ] Draft Reply
- [ ] Schedule Meeting
- [ ] Create Task
"""
            # Create a safe filename from the subject
            import re
            safe_subject = re.sub(r'[^\w\s-]', '', subject).strip().replace(' ', '_')
            if not safe_subject:
                safe_subject = "No_Subject"
            # Truncate subject if it's too long
            safe_subject = safe_subject[:50]
            
            file_name = f"GMAIL_{safe_subject}_{msg_id[:8]}.md"
            file_path = self.needs_action_path / file_name
            file_path.write_text(content, encoding='utf-8')
            self.processed_ids.add(msg_id)
            self._save_processed_ids()
            
            # Mark as read (optional - or move to a specific label)
            # self.service.users().messages().batchModify(
            #     userId='me',
            #     body={'ids': [msg_id], 'removeLabelIds': ['UNREAD']}
            # ).execute()

            log_event(
                action_type="gmail_perception",
                actor="gmail_watcher",
                target=str(file_path),
                result="success",
                details={"subject": subject, "from": sender}
            )
            return file_path

        except HttpError as error:
            self.logger.error(f'An error occurred fetching message {msg_id}: {error}')
            return None

    def run(self, once=False):
        print(f"\n--- 📩 GMAIL PERCEPTION LAYER ---")
        self.logger.info(f'Starting {self.__class__.__name__} watcher...')
        while True:
            try:
                items = self.check_for_updates()
                if not items:
                    print("   ℹ️  No new unread/important emails found.")
                else:
                    print(f"   🎯 Found {len(items)} new messages matching keywords.")
                
                for item in items:
                    action_file_path = self.create_action_file(item)
                    if action_file_path:
                        print(f"   ✅ Created Action File: {action_file_path.name}")
            except Exception as e:
                self.logger.error(f'Error in {self.__class__.__name__}: {e}')
            
            if once:
                print("--- GMAIL CHECK COMPLETE ---\n")
                break
            time.sleep(self.check_interval)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true", help="Run the watcher only once and exit")
    args = parser.parse_args()

    try:
        vault_root = find_vault_root()
        watcher = GmailWatcher(vault_root)
        watcher.run(once=args.once)
    except Exception as e:
        print(f"Failed to start Gmail Watcher: {e}")
