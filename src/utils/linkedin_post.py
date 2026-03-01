import sys
import time
import logging
from pathlib import Path
from playwright.sync_api import sync_playwright

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("LinkedInPost")

def post_to_linkedin(post_content: str):
    """
    Automates posting to LinkedIn using Playwright.
    """
    session_path = Path(".playwright_context/linkedin")
    session_path.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch_persistent_context(
                str(session_path),
                headless=False,
                slow_mo=1000,
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
            )
            page = browser.pages[0]
            page.goto("https://www.linkedin.com/feed/")

            if "feed" not in page.url:
                logger.warning("Login required for LinkedIn.")
                page.wait_for_url("**/feed/**", timeout=120000)

            # 1. Open Composer
            start_btn = page.locator('button:has-text("Start a post"), .share-box-feed-entry__trigger').first
            start_btn.click()
            page.wait_for_selector('div[role="dialog"]', timeout=10000)

            # 2. Type Content
            # Try multiple selectors for the editor
            editor = page.locator('div.ql-editor, div[contenteditable="true"][role="textbox"]').first
            
            # Clean content from extra quotes
            clean_content = post_content.strip('"\'')
            
            editor.click()
            editor.fill(clean_content)
            page.wait_for_timeout(3000) # Wait for UI to update

            # 3. Click Post
            # Look for specifically the blue primary Post button
            post_btn = page.locator('button.share-actions__primary-action').first
            if post_btn.count() == 0:
                post_btn = page.locator('button:has-text("Post")').last # Usually the last 'Post' is the real one
            
            page.wait_for_timeout(2000)
            if post_btn.is_visible() and not post_btn.is_disabled():
                post_btn.click()
                logger.info("Post button clicked.")
                page.wait_for_timeout(5000) # Crucial wait for post to submit
            else:
                # Last resort if button is disabled/hidden
                page.evaluate("document.querySelector('button.share-actions__primary-action').click()")

            # 4. Verification
            success = False
            for _ in range(10):
                if page.locator('div[role="dialog"]').count() == 0:
                    success = True
                    break
                if page.locator('text="Post successful", text="Posted"').is_visible():
                    success = True
                    break
                time.sleep(2)

            browser.close()
            return "successfully_posted" if success else "failed: confirmation timeout"

        except Exception as e:
            logger.error(f"LinkedIn Error: {e}")
            return f"failed: {str(e)}"
