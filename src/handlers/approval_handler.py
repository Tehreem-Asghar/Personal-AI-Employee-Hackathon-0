import os
import sys
import time
import shutil
import logging
from pathlib import Path

# Add the project root to the sys.path to allow imports from src
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.append(str(ROOT_DIR))

from src.utils.paths import find_vault_root, get_done_path
from src.utils.logger import log_event
from src.mcp.email_server import send_email
from src.utils.whatsapp_send import send_whatsapp_message
from src.utils.linkedin_post import post_to_linkedin
from src.utils.odoo_client import OdooClient
from src.utils.social_client import SocialClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ApprovalHandler")

def parse_approval_file(file_path: Path):
    """Parses a markdown approval file for metadata and content."""
    try:
        content = file_path.read_text(encoding='utf-8')
        data = {}
        lines = content.split('\n')
        for line in lines:
            if line.startswith('to: '): data['to'] = line.replace('to: ', '').strip()
            if line.startswith('subject: '): data['subject'] = line.replace('subject: ', '').strip()
            if line.startswith('odoo_id: '): data['odoo_id'] = line.replace('odoo_id: ', '').strip()
        
        if "## Body" in content:
            data['body'] = content.split("## Body")[-1].strip()
        else:
            data['body'] = "No body found in approval file."
        return data
    except Exception as e:
        logger.error(f"Error parsing {file_path.name}: {e}")
        return {}

def process_approved_files():
    """Monitors the /Approved folder and processes any files found."""
    try:
        vault_root = find_vault_root()
        approved_path = vault_root / "Approved"
        done_path = get_done_path(vault_root)
        
        approved_path.mkdir(parents=True, exist_ok=True)
        done_path.mkdir(parents=True, exist_ok=True)
        
        odoo_client = OdooClient()
        social_client = SocialClient()

        found_approvals = 0
        for file_path in approved_path.iterdir():
            if file_path.is_file() and file_path.suffix == ".md":
                found_approvals += 1
                logger.info(f"Processing: {file_path.name}")
                
                action_result = "unknown"
                
                if file_path.name.startswith("APPROVAL_EMAIL_"):
                    task_data = parse_approval_file(file_path)
                    if 'to' in task_data and 'subject' in task_data:
                        action_result = send_email(to=task_data['to'], subject=task_data['subject'], body=task_data.get('body', ''))
                    else: action_result = "failed_missing_data"

                elif file_path.name.startswith("APPROVAL_SOCIAL_"):
                    logger.info(f"Processing Multi-Channel Social Post: {file_path.name}")
                    task_data = parse_approval_file(file_path)
                    content = task_data.get('body', '')
                    
                    if content and content != "No body found in approval file.":
                        if "TWITTER" in file_path.name.upper():
                            logger.info("Posting to Twitter/X...")
                            social_client.post_to_twitter(content)
                        
                        if "FACEBOOK" in file_path.name.upper():
                            logger.info("Posting to Facebook...")
                            social_client.post_to_facebook(content)
                            
                        if "INSTAGRAM" in file_path.name.upper():
                            logger.info("Posting to Instagram...")
                            social_client.post_to_instagram(content)
                            
                        if "LINKEDIN" in file_path.name.upper():
                            logger.info("Posting to LinkedIn via Playwright...")
                            post_to_linkedin(content)
                            
                        action_result = "Social posts successfully dispatched."
                    else:
                        action_result = "failed_missing_body"

                elif file_path.name.startswith("APPROVAL_WHATSAPP_"):
                    task_data = parse_approval_file(file_path)
                    contact_name = task_data.get('to', 'Unknown').split(' (')[0].split(' via')[0].strip()
                    if contact_name != "Unknown":
                        action_result = send_whatsapp_message(contact_name=contact_name, message_body=task_data.get('body', ''))
                    else: action_result = "failed_missing_contact"

                elif file_path.name.startswith("APPROVAL_LINKEDIN_"):
                    task_data = parse_approval_file(file_path)
                    if 'body' in task_data and task_data['body'] != "No body found in approval file.":
                        action_result = post_to_linkedin(post_content=task_data['body'])
                    else: action_result = "failed_missing_body"

                elif file_path.name.startswith("APPROVAL_ODOO_"):
                    task_data = parse_approval_file(file_path)
                    if 'odoo_id' in task_data:
                        success = odoo_client.post_invoice(int(task_data['odoo_id']))
                        action_result = f"Odoo invoice {task_data['odoo_id']} successfully posted." if success else f"Failed to post Odoo invoice {task_data['odoo_id']}."
                    else: action_result = "failed_missing_odoo_id"
                
                # Cleanup and move to Done (Only if action was attempted)
                is_actually_success = False
                if "successfully" in action_result.lower() or "dispatched" in action_result.lower():
                    is_actually_success = True
                
                if is_actually_success:
                    dest_path = done_path / file_path.name
                    dest_path.write_text(file_path.read_text(encoding='utf-8').replace("status: pending", "status: completed"), encoding='utf-8')
                    file_path.unlink()

                    original_file_stem = file_path.stem.replace("APPROVAL_EMAIL_", "").replace("APPROVAL_WHATSAPP_", "").replace("APPROVAL_LINKEDIN_", "").replace("APPROVAL_ODOO_", "").replace("APPROVAL_SOCIAL_", "")
                    in_progress_path = vault_root / "In_Progress" / f"{original_file_stem}.md"
                    if in_progress_path.exists():
                        (done_path / f"{original_file_stem}.md").write_text(in_progress_path.read_text(encoding='utf-8').replace("status: new", "status: completed"), encoding='utf-8')
                        in_progress_path.unlink()
                    
                    logger.info(f"Task SUCCESS: {file_path.name}")
                else:
                    logger.error(f"Task FAILED: {file_path.name} - Reason: {action_result}")
                    # Move to a failed folder instead of Done
                    failed_path = vault_root / "Failed"
                    failed_path.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(file_path), str(failed_path / file_path.name))

                log_event(action_type="task_approved_execution", actor="approval_handler", target=str(file_path.name), result="success" if is_actually_success else "failure", details={"log": action_result})
        
        if found_approvals > 0:
            logger.info(f"Successfully executed {found_approvals} tasks.")

    except Exception as e:
        logger.error(f"Error: {e}")

def run_handler(once=False):
    logger.info("Starting Approval Handler...")
    while True:
        process_approved_files()
        if once: break
        time.sleep(30) 

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    run_handler(once=args.once)
