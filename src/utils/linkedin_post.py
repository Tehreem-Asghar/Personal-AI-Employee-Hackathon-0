import sys
import time
import logging
from pathlib import Path
from playwright.sync_api import sync_playwright

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.utils.credentials import get_whatsapp_session_path # We'll use a similar approach for session storage

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("LinkedInPost")

def post_to_linkedin(post_content: str):
    """
    Automates posting to LinkedIn using Playwright.
    Uses a persistent browser context to maintain the session.
    """
    # Use a dedicated session path for LinkedIn
    session_path = Path(".playwright_context/linkedin")
    session_path.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        try:
            # Launch browser with persistent context
            browser = p.chromium.launch_persistent_context(
                str(session_path),
                headless=False, # Set to False initially for manual login/QR check
                slow_mo=500,
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
            )
            page = browser.pages[0]
            page.goto("https://www.linkedin.com/feed/")

            # Check if we need to log in
            if "feed" not in page.url:
                logger.warning("LinkedIn session not found. Please log in manually in the opened browser.")
                # Wait for user to log in manually - giving 2 minutes
                page.wait_for_url("**/feed/**", timeout=120000)

            logger.info("LinkedIn Feed loaded. Initiating post...")
            
            # Take initial screenshot for debugging
            initial_screenshot = "linkedin_initial_state.png"
            page.screenshot(path=initial_screenshot)
            logger.info(f"Initial screenshot saved: {initial_screenshot}")
            
            # Also save initial HTML for debugging
            initial_html = "linkedin_initial_state.html"
            with open(initial_html, "w", encoding="utf-8") as f:
                f.write(page.content())
            logger.info(f"Initial HTML saved: {initial_html}")

            # 1. Check if composer is already open (inline or modal)
            composer_found = False
            
            # Check for draft text at top of feed (most reliable detection)
            try:
                draft_text = page.locator('text="Draft:"').first
                if draft_text.is_visible(timeout=5000):
                    logger.info("Draft text found - composer is already open!")
                    composer_found = True
            except Exception as e:
                logger.info(f"No draft text found: {e}")
            
            # Check for expanded composer with editable area
            if not composer_found:
                try:
                    # Look for the editable content area (only visible when composer is expanded)
                    editable = page.locator('div[contenteditable="true"]').first
                    if editable.is_visible(timeout=5000):
                        logger.info("Editable composer area found!")
                        composer_found = True
                except Exception as e:
                    logger.info(f"No editable area found: {e}")
            
            # Check for modal composer
            if not composer_found:
                try:
                    modal_composer = page.locator('div[role="dialog"] div.ql-editor, div[role="dialog"] div[contenteditable="true"]').first
                    if modal_composer.is_visible(timeout=5000):
                        logger.info("Modal composer found!")
                        composer_found = True
                except Exception as e:
                    logger.info(f"No modal composer found: {e}")
            
            # If composer found, clear it. Otherwise, try to open one.
            if composer_found:
                logger.info("Expanding and clearing existing composer content...")
                
                # First click on the draft area to expand the composer
                try:
                    draft_area = page.locator('text="Draft:"').first
                    draft_area.click()
                    page.wait_for_timeout(2000)
                except Exception as de:
                    logger.info(f"Draft text not clickable, proceeding: {de}")
                
                # LinkedIn inline composer uses div[contenteditable="true"]
                editor = page.locator('div[contenteditable="true"]').first
                
                # Wait for editor to be visible
                editor.wait_for(state='visible', timeout=10000)
                editor.click()
                page.wait_for_timeout(500)
                
                # Clear content
                page.keyboard.press('Control+A')
                page.keyboard.press('Delete')
                page.wait_for_timeout(500)
                logger.info("Composer cleared and ready")
            else:
                # 2. Click 'Start a post' to open fresh composer
                logger.info("Opening fresh composer...")
                composer_opened = False
                
                try:
                    start_post_button = page.get_by_role("button", name="Start a post")
                    if start_post_button.count() > 1:
                        start_post_button.nth(1).click()
                    else:
                        start_post_button.click()
                    page.wait_for_timeout(3000)
                    composer_opened = True
                    logger.info("Composer opened successfully")
                except Exception as click_err:
                    logger.warning(f"Failed to click via role, trying fallback: {click_err}")
                    # Try alternative selectors for LinkedIn's post button
                    for selector in [
                        'button.share-box-feed-entry__trigger',
                        '.share-box-feed-entry__trigger',
                        'button:has-text("Start a post")',
                        '[data-test-id="share-box-feed-entry"]'
                    ]:
                        try:
                            page.locator(selector).first.click(timeout=5000)
                            logger.info(f"Clicked using fallback selector: {selector}")
                            composer_opened = True
                            page.wait_for_timeout(2000)
                            break
                        except Exception as fallback_err:
                            logger.info(f"Selector {selector} failed: {fallback_err}")
                            continue
                    
                    if not composer_opened:
                        # Take screenshot before failing
                        error_screenshot = "linkedin_start_post_error.png"
                        page.screenshot(path=error_screenshot)
                        logger.error(f"Error screenshot saved: {error_screenshot}")
                        
                        # Save HTML for debugging
                        error_html = "linkedin_start_post_error.html"
                        with open(error_html, "w", encoding="utf-8") as f:
                            f.write(page.content())
                        logger.error(f"Error HTML saved to {error_html}")
                        
                        raise Exception("Could not find Start a post button with any selector")

            # Type content in the editor
            logger.info("Typing post content...")
            
            # Use correct selector for inline composer
            editor = page.locator('div[contenteditable="true"]').first
            editor.wait_for(state='visible', timeout=20000)
            editor.click()
            page.wait_for_timeout(500)
            editor.fill(post_content)
            page.wait_for_timeout(2000)

            # 3. Click the 'Post' button directly
            logger.info("Looking for Post button...")

            # Take screenshot before posting
            debug_screenshot = "linkedin_before_post.png"
            page.screenshot(path=debug_screenshot)
            logger.info(f"Debug screenshot saved: {debug_screenshot}")
            
            # Also save HTML for debugging
            debug_html = "linkedin_before_post.html"
            html_content = page.content()
            with open(debug_html, "w", encoding="utf-8") as f:
                f.write(html_content)
            logger.info(f"Debug HTML saved: {debug_html}")

            final_post_clicked = False

            try:
                # LinkedIn inline composer has Post button in footer
                # Look for the blue Post button (not "Start a post")
                post_button = page.locator('button:has-text("Post"):not(:has-text("Start"))').first
                
                # Wait for it to be enabled
                for i in range(10):
                    if not post_button.is_disabled():
                        logger.info("Post button is enabled!")
                        break
                    logger.info(f"Post button still disabled, waiting... ({i+1}/10)")
                    page.wait_for_timeout(1000)

                # Click using JavaScript for reliability
                logger.info("Clicking Post button with JavaScript...")
                post_button.evaluate("el => el.click()")
                page.wait_for_timeout(2000)

                logger.info("Post button clicked!")
                final_post_clicked = True

            except Exception as e:
                logger.error(f"Failed to click Post button: {e}")
                screenshot_path = "linkedin_post_button_error.png"
                page.screenshot(path=screenshot_path)
                logger.error(f"Screenshot saved to {screenshot_path}")
                
                # Save HTML for debugging
                error_html = "linkedin_post_button_error.html"
                with open(error_html, "w", encoding="utf-8") as f:
                    f.write(page.content())
                logger.error(f"Error HTML saved to {error_html}")

                # Retry with alternative selector
                try:
                    logger.info("Retrying with alternative selector...")
                    alt_post_button = page.locator('div[role="dialog"] footer button:has-text("Post")').first
                    alt_post_button.click(force=True)
                    logger.info("Alternative Post button clicked!")
                    final_post_clicked = True
                except Exception as e2:
                    logger.error(f"Retry also failed: {e2}")

            if not final_post_clicked:
                browser.close()
                return "failed: Could not click Post button"

            # Check for processing state
            try:
                page.wait_for_selector('button:disabled:has-text("Posting")', state="visible", timeout=5000)
                logger.info("Post processing confirmed!")
            except:
                logger.info("Post clicked (processing may be brief)")

            # 4. Handle Post settings modal (appears only ONCE after clicking Post)
            logger.info("Checking for Post settings modal...")
            try:
                page.wait_for_timeout(2000)
                
                # Close "Select a group" modal if it appears (click X button)
                group_modal = page.locator('div[role="dialog"]:has-text("Select a group")').first
                if group_modal.is_visible(timeout=2000):
                    logger.info("Group modal found, closing it...")
                    close_x = group_modal.locator('button.artdeco-modal__dismiss').first
                    if close_x.is_visible(timeout=2000):
                        close_x.click()
                        logger.info("Group modal closed via X button")
                    else:
                        back_btn = group_modal.locator('button:has-text("Back")').first
                        back_btn.click()
                        logger.info("Group modal closed via Back button")
                    page.wait_for_timeout(2000)
                
                # Handle Post settings modal (ONLY ONCE)
                settings_modal = page.locator('div[role="dialog"]:has-text("Post settings")').first
                if settings_modal.is_visible(timeout=3000):
                    logger.info("Settings modal found, handling it...")
                    
                    # Take screenshot for debugging
                    settings_screenshot = "linkedin_settings_modal.png"
                    page.screenshot(path=settings_screenshot)
                    logger.info(f"Settings modal screenshot saved: {settings_screenshot}")
                    
                    # Scroll the modal content to enable Done button
                    logger.info("Scrolling settings modal to enable Done button...")
                    
                    # Find and scroll the actual scrollable container
                    scroll_container = settings_modal.locator('div.share-box-modal-content__container').first
                    
                    # Scroll using JavaScript on the container
                    for i in range(5):
                        scroll_container.evaluate(f"el => el.scrollTop = {i * 150}")
                        page.wait_for_timeout(300)
                    
                    # Scroll to bottom
                    scroll_container.evaluate("el => el.scrollTop = el.scrollHeight")
                    page.wait_for_timeout(1000)
                    
                    # Click Anyone option to ensure selection
                    logger.info("Selecting Anyone option...")
                    anyone_btn = settings_modal.locator('button#ANYONE[role="radio"]').first
                    anyone_btn.click(force=True)
                    page.wait_for_timeout(1000)
                    
                    # Scroll to bottom again
                    scroll_container.evaluate("el => el.scrollTop = el.scrollHeight")
                    page.wait_for_timeout(1000)
                    
                    # Click Done
                    done_btn = settings_modal.locator('button:has-text("Done")').first
                    for i in range(15):
                        if not done_btn.is_disabled():
                            logger.info("Done button is enabled!")
                            break
                        logger.info(f"Waiting for Done button... ({i+1}/15)")
                        page.wait_for_timeout(1000)
                    
                    done_btn.evaluate("el => el.click()")
                    page.wait_for_timeout(3000)
                    
                    # Wait for modal to close
                    for i in range(5):
                        if not settings_modal.is_visible():
                            logger.info("Settings modal closed!")
                            break
                        logger.info(f"Waiting for modal to close... ({i+1}/5)")
                        page.wait_for_timeout(5000)
                    
                    logger.info("Settings modal handling complete")
                    
                    # After clicking Done, the post submits automatically
                    # DO NOT click Post button again - this causes settings to reopen!
                    logger.info("Post should be submitting automatically...")
                    page.wait_for_timeout(3000)
                else:
                    logger.info("No settings modal found - post may have submitted directly")
                    
            except Exception as e:
                logger.info(f"Modal handling: {e}")

            # 5. Wait for modal to close OR success message
            logger.info("Waiting for post to complete (up to 60 seconds)...")
            post_completed = False

            # Wait for all modals to close
            for attempt in range(12):
                try:
                    # Check for success notification first
                    success_toast = page.locator('text="Post successful", text="Posted"').first
                    if success_toast.is_visible(timeout=2000):
                        logger.info("SUCCESS: Post successful notification detected!")
                        post_completed = True
                        break

                    # Check if any dialog is still open
                    composer_modal = page.locator('div[data-test-modal-id="sharebox"]').first
                    settings_modal_check = page.locator('div[role="dialog"]:has-text("Post settings")').first
                    
                    if not composer_modal.is_visible() and not settings_modal_check.is_visible():
                        logger.info(f"All modals closed after {attempt * 5} seconds!")
                        post_completed = True
                        break

                    logger.info(f"Post still processing... (attempt {attempt + 1}/12)")
                except Exception as e:
                    logger.warning(f"Error checking status: {e}")
                    # If we can't find modals, assume they're closed
                    post_completed = True
                    break

                page.wait_for_timeout(5000)

            if not post_completed:
                logger.error("Post did not complete after 60 seconds!")
                screenshot_path = "linkedin_post_error.png"
                page.screenshot(path=screenshot_path)
                logger.error(f"Screenshot saved to {screenshot_path}")
                
                # Save HTML for debugging
                error_html = "linkedin_post_error.html"
                with open(error_html, "w", encoding="utf-8") as f:
                    f.write(page.content())
                logger.error(f"Error HTML saved to {error_html}")
                
                browser.close()
                return "failed: Post did not complete"

            # 5. Wait for success confirmation
            logger.info("Waiting for final success confirmation...")
            try:
                page.wait_for_timeout(3000)
                success_toast = page.locator('text="Post successful", text="Posted", text="Post published"').first
                if success_toast.is_visible(timeout=5000):
                    logger.info("Post success confirmed!")
                else:
                    logger.info("Assuming success (modal closed)")
            except Exception as e:
                logger.info(f"Status check: {e}")

            page.wait_for_timeout(2000)
            browser.close()
            logger.info("LinkedIn post completed successfully!")
            return "successfully_posted"

        except Exception as e:
            logger.error(f"Error during LinkedIn posting: {e}")
            return f"failed: {str(e)}"

if __name__ == "__main__":
    test_content = "Automated post test from my AI Employee project! #AI #Automation #Python"
    print(post_to_linkedin(test_content))
