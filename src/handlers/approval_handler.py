import os
import sys
import time
import shutil
import logging
from pathlib import Path

# Add the project root to the sys.path to allow imports from src
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.utils.paths import find_vault_root, get_done_path
from src.utils.logger import log_event
from src.mcp.email_server import send_email
from src.utils.whatsapp_send import send_whatsapp_message
from src.utils.linkedin_post import post_to_linkedin

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ApprovalHandler")

def parse_approval_file(file_path: Path):
    """Parses a markdown approval file for metadata and content."""
    content = file_path.read_text(encoding='utf-8')
    # Simple extraction for Silver Tier (assuming consistent format from Claude)
    data = {}
    lines = content.split('\n')
    for line in lines:
        if line.startswith('to: '): data['to'] = line.replace('to: ', '').strip()
        if line.startswith('subject: '): data['subject'] = line.replace('subject: ', '').strip()
    
    # Body usually starts after the second --- or specific header
    if "## Body" in content:
        data['body'] = content.split("## Body")[-1].strip()
    else:
        data['body'] = "No body found in approval file."
    
    return data

def process_approved_files():
    """
    Monitors the /Approved folder and processes any files found.
    """
    try:
        vault_root = find_vault_root()
        approved_path = vault_root / "Approved"
        done_path = get_done_path(vault_root)
        
        approved_path.mkdir(parents=True, exist_ok=True)
        done_path.mkdir(parents=True, exist_ok=True)

        print(f"\n--- 🚀 ACTION LAYER (EXECUTION) ---")
        found_approvals = 0

        # Check for files in /Approved
        for file_path in approved_path.iterdir():
            if file_path.is_file():
                found_approvals += 1
                logger.info(f"Detected approved task: {file_path.name}")
                print(f"   🚀 Executing Approved Task: {file_path.name}")
                
                action_result = "unknown"
                task_data = {} # General variable to hold data for enrichment
                
                if file_path.name.startswith("APPROVAL_EMAIL_"):
                    logger.info(f"Processing Email Send for: {file_path.name}")
                    task_data = parse_approval_file(file_path)
                    
                    if 'to' in task_data and 'subject' in task_data:
                        result_msg = send_email(
                            to=task_data['to'], 
                            subject=task_data['subject'], 
                            body=task_data.get('body', '')
                        )
                        logger.info(result_msg)
                        action_result = result_msg
                    else:
                        logger.error(f"Missing required email data in {file_path.name}")
                        action_result = "failed_missing_data"

                elif file_path.name.startswith("APPROVAL_WHATSAPP_"):
                    logger.info(f"Processing WhatsApp Send for: {file_path.name}")
                    task_data = parse_approval_file(file_path)
                    
                    # Clean up contact name (remove suffixes like '(via WhatsApp)')
                    contact_name = task_data.get('to', 'Unknown')
                    contact_name = contact_name.split(' (')[0].split(' via')[0].strip()
                    
                    if contact_name != "Unknown":
                        result_msg = send_whatsapp_message(
                            contact_name=contact_name, 
                            message_body=task_data.get('body', '')
                        )
                        logger.info(result_msg)
                        action_result = result_msg
                    else:
                        logger.error(f"Missing required WhatsApp contact name in {file_path.name}")
                        action_result = "failed_missing_contact"

                elif file_path.name.startswith("APPROVAL_LINKEDIN_"):
                    logger.info(f"Processing LinkedIn Post for: {file_path.name}")
                    task_data = parse_approval_file(file_path)
                    
                    if 'body' in task_data and task_data['body'] != "No body found in approval file.":
                        logger.info("Executing actual LinkedIn post...")
                        result_msg = post_to_linkedin(post_content=task_data['body'])
                        logger.info(result_msg)
                        action_result = result_msg
                    else:
                        logger.error(f"Missing required LinkedIn post body in {file_path.name}")
                        action_result = "failed_missing_body"
                
                # Update status and move approved file to /Done
                content = file_path.read_text(encoding='utf-8')
                updated_content = content.replace("status: pending", "status: completed")
                
                dest_path = done_path / file_path.name
                dest_path.write_text(updated_content, encoding='utf-8')
                
                # Delete the original file from Approved
                file_path.unlink()
                logger.info(f"Processed and moved {file_path.name} to /Done")

                # ALSO find and move the original file from /In_Progress to /Done
                original_file_stem = file_path.stem.replace("APPROVAL_EMAIL_", "").replace("APPROVAL_WHATSAPP_", "").replace("APPROVAL_LINKEDIN_", "")
                original_file_name = f"{original_file_stem}.md"
                
                in_progress_path = vault_root / "In_Progress" / original_file_name
                if in_progress_path.exists():
                    # Read original content and update it with the published body
                    orig_content = in_progress_path.read_text(encoding='utf-8')
                    
                    # Update metadata and add the actual published content
                    updated_orig = orig_content.replace("status: new", "status: completed").replace("status: pending_action", "status: completed")
                    
                    if "### Published Content" not in updated_orig:
                        updated_orig += f"\n\n### Published Content\n{task_data.get('body', 'N/A')}\n"
                    
                    # Save the enriched file to /Done
                    done_file_path = done_path / original_file_name
                    done_file_path.write_text(updated_orig, encoding='utf-8')
                    
                    # Remove from In_Progress
                    in_progress_path.unlink()
                    logger.info(f"Enriched and moved original task {original_file_name} to /Done")
                
                # Log the action
                log_event(
                    action_type="task_approved_execution",
                    actor="approval_handler",
                    target=str(dest_path),
                    result="success" if "successfully" in action_result.lower() or "simulated" in action_result else "failure",
                    details={"original_name": file_path.name, "execution_log": action_result}
                )
        
        if found_approvals == 0:
            print("   ℹ️  No new files in Approved folder.")
        else:
            print(f"   🎯 Successfully executed {found_approvals} approved tasks.")
        
        print("--- ACTION LAYER COMPLETE ---\n")

    except FileNotFoundError as e:
        logger.error(f"Vault root not found: {e}")
    except Exception as e:
        logger.error(f"Error processing approved files: {e}")

def run_handler(once=False):
    logger.info("Starting Approval Handler...")
    while True:
        process_approved_files()
        if once:
            logger.info("Approval Handler completed single run.")
            break
        # In a real heartbeat, this might run once and exit (called by Task Scheduler)
        # But for testing in terminal, we use a loop.
        time.sleep(30) 

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true", help="Run only once and exit")
    args = parser.parse_args()
    
    run_handler(once=args.once)




















# import os
# import sys
# import time
# import shutil
# import logging
# from pathlib import Path

# # Add the project root to the sys.path to allow imports from src
# sys.path.append(str(Path(__file__).parent.parent.parent))

# from src.utils.paths import find_vault_root, get_done_path
# from src.utils.logger import log_event
# from src.mcp.email_server import send_email
# from src.utils.whatsapp_send import send_whatsapp_message
# from src.utils.linkedin_post import post_to_linkedin

# # Configure logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# logger = logging.getLogger("ApprovalHandler")

# def parse_approval_file(file_path: Path):
#     """Parses a markdown approval file for metadata and content."""
#     content = file_path.read_text(encoding='utf-8')
#     # Simple extraction for Silver Tier (assuming consistent format from Claude)
#     data = {}
#     lines = content.split('\n')
#     for line in lines:
#         if line.startswith('to: '): data['to'] = line.replace('to: ', '').strip()
#         if line.startswith('subject: '): data['subject'] = line.replace('subject: ', '').strip()
    
#     # Body usually starts after the second --- or specific header
#     if "## Body" in content:
#         data['body'] = content.split("## Body")[-1].strip()
#     else:
#         data['body'] = "No body found in approval file."
    
#     return data

# def process_approved_files():
#     """
#     Monitors the /Approved folder and processes any files found.
#     """
#     try:
#         vault_root = find_vault_root()
#         approved_path = vault_root / "Approved"
#         done_path = get_done_path(vault_root)
        
#         approved_path.mkdir(parents=True, exist_ok=True)
#         done_path.mkdir(parents=True, exist_ok=True)

#         print(f"\n--- 🚀 ACTION LAYER (EXECUTION) ---")
#         found_approvals = 0

#         # Check for files in /Approved
#         for file_path in approved_path.iterdir():
#             if file_path.is_file():
#                 found_approvals += 1
#                 logger.info(f"Detected approved task: {file_path.name}")
#                 print(f"   🚀 Executing Approved Task: {file_path.name}")
                
#                 action_result = "unknown"
#                 task_data = {} # General variable to hold data for enrichment
                
#                 if file_path.name.startswith("APPROVAL_EMAIL_"):
#                     logger.info(f"Processing Email Send for: {file_path.name}")
#                     task_data = parse_approval_file(file_path)
                    
#                     if 'to' in task_data and 'subject' in task_data:
#                         result_msg = send_email(
#                             to=task_data['to'], 
#                             subject=task_data['subject'], 
#                             body=task_data.get('body', '')
#                         )
#                         logger.info(result_msg)
#                         action_result = result_msg
#                     else:
#                         logger.error(f"Missing required email data in {file_path.name}")
#                         action_result = "failed_missing_data"

#                 elif file_path.name.startswith("APPROVAL_WHATSAPP_"):
#                     logger.info(f"Processing WhatsApp Send for: {file_path.name}")
#                     task_data = parse_approval_file(file_path)
                    
#                     # Clean up contact name (remove suffixes like '(via WhatsApp)')
#                     contact_name = task_data.get('to', 'Unknown')
#                     contact_name = contact_name.split(' (')[0].split(' via')[0].strip()
                    
#                     if contact_name != "Unknown":
#                         result_msg = send_whatsapp_message(
#                             contact_name=contact_name, 
#                             message_body=task_data.get('body', '')
#                         )
#                         logger.info(result_msg)
#                         action_result = result_msg
#                     else:
#                         logger.error(f"Missing required WhatsApp contact name in {file_path.name}")
#                         action_result = "failed_missing_contact"

#                 elif file_path.name.startswith("APPROVAL_LINKEDIN_"):
#                     logger.info(f"Processing LinkedIn Post for: {file_path.name}")
#                     task_data = parse_approval_file(file_path)
                    
#                     if 'body' in task_data and task_data['body'] != "No body found in approval file.":
#                         logger.info("Executing actual LinkedIn post...")
#                         result_msg = post_to_linkedin(post_content=task_data['body'])
#                         logger.info(result_msg)
#                         action_result = result_msg
#                     else:
#                         logger.error(f"Missing required LinkedIn post body in {file_path.name}")
#                         action_result = "failed_missing_body"
                
#                 # Update status and move approved file to /Done
#                 content = file_path.read_text(encoding='utf-8')
#                 updated_content = content.replace("status: pending", "status: completed")
                
#                 dest_path = done_path / file_path.name
#                 dest_path.write_text(updated_content, encoding='utf-8')
                
#                 # Delete the original file from Approved
#                 file_path.unlink()
#                 logger.info(f"Processed and moved {file_path.name} to /Done")

#                 # ALSO find and move the original file from /In_Progress to /Done
#                 original_file_stem = file_path.stem.replace("APPROVAL_EMAIL_", "").replace("APPROVAL_WHATSAPP_", "").replace("APPROVAL_LINKEDIN_", "")
#                 original_file_name = f"{original_file_stem}.md"
                
#                 in_progress_path = vault_root / "In_Progress" / original_file_name
#                 if in_progress_path.exists():
#                     # Read original content and update it with the published body
#                     orig_content = in_progress_path.read_text(encoding='utf-8')
                    
#                     # Update metadata and add the actual published content
#                     updated_orig = orig_content.replace("status: new", "status: completed").replace("status: pending_action", "status: completed")
                    
#                     if "### Published Content" not in updated_orig and 'body' in task_data:
#                         updated_orig += f"\n\n### Published Content\n{task_data['body']}\n"
                    
#                     # Save the enriched file to /Done
#                     done_file_path = done_path / original_file_name
#                     done_file_path.write_text(updated_orig, encoding='utf-8')
                    
#                     # Remove from In_Progress
#                     in_progress_path.unlink()
#                     logger.info(f"Enriched and moved original task {original_file_name} to /Done")
                
#                 # Log the action
#                                     log_event(
#                                         action_type="task_approved_execution",
#                                         actor="approval_handler",
#                                         target=str(dest_path),
#                                         result="success" if "successfully" in action_result.lower() or "simulated" in action_result else "failure",
#                                         details={"original_name": file_path.name, "execution_log": action_result}
#                                     )
                        
#                         if found_approvals == 0:
#                             print("   ℹ️  No new files in Approved folder.")
#                         else:
#                             print(f"   🎯 Successfully executed {found_approvals} approved tasks.")
                        
#                         print("--- ACTION LAYER COMPLETE ---\n")
#                     except FileNotFoundError as e:
#         logger.error(f"Vault root not found: {e}")
#     except Exception as e:
#         logger.error(f"Error processing approved files: {e}")

# def run_handler(once=False):
#     logger.info("Starting Approval Handler...")
#     while True:
#         process_approved_files()
#         if once:
#             logger.info("Approval Handler completed single run.")
#             break
#         # In a real heartbeat, this might run once and exit (called by Task Scheduler)
#         # But for testing in terminal, we use a loop.
#         time.sleep(30) 

# if __name__ == "__main__":
#     import argparse
#     parser = argparse.ArgumentParser()
#     parser.add_argument("--once", action="store_true", help="Run only once and exit")
#     args = parser.parse_args()
    
#     run_handler(once=args.once)
