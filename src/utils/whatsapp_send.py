import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright
import logging

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.utils.credentials import get_whatsapp_session_path

def send_whatsapp_message(contact_name: str, message_body: str):
    """
    Sends a WhatsApp message using an existing Playwright session.
    """
    session_path = get_whatsapp_session_path()
    
    with sync_playwright() as p:
        try:
            # Launch browser with the SAME session path as the watcher
            browser = p.chromium.launch_persistent_context(
                str(session_path),
                headless=False, # Run in headed mode for debugging
                slow_mo=1000
            )
            page = browser.pages[0]
            page.goto("https://web.whatsapp.com")
            
            # Wait for main chat list to be available
            page.wait_for_selector('[aria-label="Chat list"]', timeout=90000) # Increased timeout to 90s

            # --- FINAL DEBUGGING ---
            screenshot_path = Path("whatsapp_send_debug.png")
            page.screenshot(path=str(screenshot_path))
            logging.info(f"DEBUG: Screenshot taken. See {screenshot_path}")
            # --- END DEBUGGING ---

            # 1. First try to find contact directly in chat list (faster for recent chats)
            chat_found = False
            
            # Try clicking directly on the contact in chat list
            chat_element = page.locator(f'span[title="{contact_name}"]').first
            if chat_element.count() > 0:
                chat_element.click()
                chat_found = True
                print(f"Found '{contact_name}' directly in chat list")
            else:
                # Contact not in recent chats, need to search
                print(f"'{contact_name}' not in recent chats, searching...")
                
                # Wait for page to stabilize
                page.wait_for_timeout(2000)
                
                # Find search box - WhatsApp Web uses an input element with placeholder
                search_box = page.locator('input[type="text"][placeholder*="Search"], input[placeholder*="Search"]').first
                
                if search_box.count() == 0:
                    # Fallback: try aria-label
                    search_box = page.locator('[aria-label="Search or start new chat"]').first
                
                if search_box.count() == 0:
                    # Last fallback: find any input in the search area
                    search_box = page.locator('div[role="search"] input').first
                
                if search_box.count() == 0:
                    raise Exception("Search box not found")
                
                # Clear any existing text first
                search_box.click()
                page.wait_for_timeout(500)
                search_box.fill("")
                page.wait_for_timeout(500)
                
                # Fill the contact name
                search_box.fill(contact_name)
                page.wait_for_timeout(3000)

                # 2. Click the chat from search results - be very specific
                chat_element = page.locator(f'span[title="{contact_name}"]').first
                if chat_element.count() > 0:
                    chat_element.click()
                    chat_found = True
                    print(f"Clicked on contact: {contact_name}")
                else:
                    # Try finding by text content in chat list
                    chat_element = page.locator(f'//div[@aria-label="Chat list"]//span[contains(text(), "{contact_name}")]').first
                    if chat_element.count() > 0:
                        chat_element.click()
                        chat_found = True
                        print(f"Clicked on contact (text match): {contact_name}")
                
                if not chat_found:
                    raise Exception(f"Contact '{contact_name}' not found in search results")
                
                page.wait_for_timeout(2000)
                
                # Verify we're in the correct chat by checking the chat header
                try:
                    chat_header = page.locator(f'span[title="{contact_name}"]').first
                    if chat_header.count() > 0:
                        print(f"Verified: Chat header shows '{contact_name}'")
                except:
                    print("Warning: Could not verify chat header")
            
            if not chat_found:
                raise Exception(f"Contact '{contact_name}' not found")
            
            page.wait_for_timeout(2000)

            # 3. Find message input box - try multiple selectors
            message_box = page.locator('[data-testid="conversation-compose-box-input"], div[contenteditable="true"][data-tab="10"], div[contenteditable="true"][role="textbox"]').first
            message_box.click()
            page.wait_for_timeout(500)
            message_box.fill(message_body)
            page.wait_for_timeout(1000)
            
            # Press Enter to send
            send_button = page.locator('[data-testid="compose-btn-send"]').first
            if send_button.count() > 0:
                send_button.click()
            else:
                message_box.press("Enter")
            
            print(f"Successfully sent WhatsApp message to {contact_name}")
            browser.close()
            return "successfully_sent"

        except Exception as e:
            print(f"Error sending WhatsApp message: {e}")
            return f"failed: {str(e)}"

if __name__ == "__main__":
    # Test send
    if len(sys.argv) > 2:
        send_whatsapp_message(sys.argv[1], sys.argv[2])
    else:
        print("Usage: python send_whatsapp.py 'Contact Name' 'Message'")
