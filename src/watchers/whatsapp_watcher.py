import os
import sys
import time
import logging
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright
import re

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.watchers.base_watcher import BaseWatcher
from src.utils.paths import find_vault_root
from src.utils.logger import log_event
from src.utils.credentials import get_whatsapp_session_path

class WhatsAppWatcher(BaseWatcher):
    def __init__(self, vault_path: Path, check_interval: int = 60, headed: bool = False):
        super().__init__(vault_path, check_interval)
        self.session_path = Path(get_whatsapp_session_path())
        self.session_path.parent.mkdir(parents=True, exist_ok=True)
        self.headed = headed
        self.keywords = [
            'invoice', 'payment', 'pricing', 'quote', 'budget', 'bill',
            'meeting', 'schedule', 'call', 'appointment', 'zoom',
            'project', 'task', 'update', 'milestone', 'deadline',
            'urgent', 'asap', 'important', 'critical',
            'help', 'question', 'query', 'issue'
        ]
        # Start browser at initialization
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch_persistent_context(
            str(self.session_path),
            headless=not self.headed,
            slow_mo=500,
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
        )
        self.page = self.browser.pages[0] if self.browser.pages else self.browser.new_page()
        self.page.goto("https://web.whatsapp.com")

    def __del__(self):
        # Ensure browser is closed when object is destroyed
        if hasattr(self, 'browser') and self.browser:
            self.browser.close()
        if hasattr(self, 'playwright') and self.playwright:
            self.playwright.stop()

    def check_for_updates(self) -> list:
        """Navigates to WhatsApp Web and identifies chats with unread messages matching keywords."""
        updates = []
        try:
            # Check if we need to re-authenticate (QR code visible)
            self.page.reload(wait_until="domcontentloaded")
            # Wait for the chat list container
            self.page.wait_for_selector('[aria-label="Chat list"]', timeout=60000)

            updates = []
            # WhatsApp now uses role="row" for chat items instead of listitem
            chat_list_items = self.page.locator('div[role="row"]')

            if chat_list_items.count() == 0:
                self.logger.info("WhatsAppWatcher: No chat rows found.")
                return []

            for i in range(chat_list_items.count()):
                chat_item = chat_list_items.nth(i)
                
                # unread messages have a span with aria-label containing "unread message"
                unread_indicator = chat_item.locator('span[aria-label*="unread"]')
                
                if unread_indicator.count() > 0:
                    # Get ALL text in the row for keyword scanning - very robust
                    all_row_text = chat_item.inner_text()
                    
                    # Extract the chat title specifically for the filename
                    title_element = chat_item.locator('span[title]').first
                    chat_title = title_element.get_attribute("title") if title_element.count() > 0 else "Unknown Chat"
                    
                    self.logger.info(f"Checking unread chat: '{chat_title}'")

                    if any(kw in all_row_text.lower() for kw in self.keywords):
                        self.logger.info(f"✅ Found matching keywords in: {chat_title}")
                        
                        # --- NEW: Click and Read Message Content ---
                        actual_message = ""
                        try:
                            chat_item.click()
                            time.sleep(2) # Wait for messages to load
                            
                            # Find the last message in the conversation
                            message_elements = self.page.locator('div.message-in span.selectable-text')
                            if message_elements.count() > 0:
                                actual_message = message_elements.last.inner_text()
                                self.logger.info(f"Extracted message: {actual_message[:30]}...")
                            
                            self.logger.info(f"✔ Marked '{chat_title}' as read.")
                        except Exception as read_error:
                            self.logger.warning(f"Could not read message from '{chat_title}': {read_error}")
                        # -------------------------------------------

                        updates.append({
                            "chat": chat_title,
                            "snippet": actual_message if actual_message else all_row_text.replace('\n', ' ')[:100],
                            "type": "whatsapp",
                            "timestamp": datetime.now().isoformat()
                        })
                    else:
                        self.logger.info(f"ℹ️ Skipping '{chat_title}': No keywords found in preview.")
            
        except Exception as e:
            self.logger.error(f"Error checking WhatsApp updates: {e}")
        
        return updates

    def create_action_file(self, update) -> Path:
        """Creates a .md file for a detected WhatsApp update."""
        chat_name = update['chat']
        timestamp = update['timestamp']
        message_content = update.get('snippet', 'No content extracted.')
        
        content = f"""---
type: whatsapp
from: {chat_name}
received: {timestamp}
status: pending_action
---
# WhatsApp Message from {chat_name}

A potential business request was detected in this chat.

### Details:
- **Chat Name**: {chat_name}
- **Detected at**: {timestamp}

### Message Content:
{message_content}

### Suggested Actions:
- [ ] Open WhatsApp and reply
- [ ] Create a task in Obsidian
"""
        # Create a safe filename
        safe_name = chat_name.replace(' ', '_').replace('+', 'plus')
        file_name = f"WHATSAPP_{safe_name}_{int(time.time())}.md"
        file_path = self.needs_action_path / file_name
        
        file_path.write_text(content, encoding='utf-8')
        
        log_event(
            action_type="whatsapp_perception",
            actor="whatsapp_watcher",
            target=str(file_path),
            result="success",
            details={"chat": chat_name}
        )
        return file_path

    def run(self, once=False):
        print(f"\n--- 📱 WHATSAPP PERCEPTION LAYER ---")
        self.logger.info(f'Starting {self.__class__.__name__} watcher...')
        while True:
            try:
                items = self.check_for_updates()
                if not items:
                    print("   ℹ️  No new unread messages matching keywords.")
                else:
                    print(f"   🎯 Found {len(items)} unread business chats.")
                
                for item in items:
                    action_file_path = self.create_action_file(item)
                    print(f"   ✅ Created Action File: {action_file_path.name}")
            except Exception as e:
                self.logger.error(f'Error in {self.__class__.__name__}: {e}')
            
            if once:
                print("--- WHATSAPP CHECK COMPLETE ---\n")
                break
            time.sleep(self.check_interval)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--headed", action="store_true", help="Run browser in headed mode")
    parser.add_argument("--once", action="store_true", help="Run the watcher only once and exit")
    args = parser.parse_args()

    try:
        vault_root = find_vault_root()
        watcher = WhatsAppWatcher(vault_root, headed=args.headed)
        watcher.run(once=args.once)
    except Exception as e:
        print(f"Failed to start WhatsApp Watcher: {e}")
