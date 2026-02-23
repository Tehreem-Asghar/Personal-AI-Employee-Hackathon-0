import os
import sys
import asyncio
import shutil
import logging
from pathlib import Path
from dotenv import load_dotenv
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel
from agents.run import RunConfig

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.utils.paths import find_vault_root, get_needs_action_path, get_done_path
from src.utils.planner import create_plan
from src.utils.logger import log_event

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("DraftingAgent")

# AI Setup
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    logger.error("GEMINI_API_KEY not found in .env!")
    sys.exit(1)

external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client
)

config = RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled=True
)

# Agent Instructions
INSTRUCTIONS = """
You are a professional AI Assistant. Your job is to read an incoming task (usually an email or message) 
and generate two things:
1. A structured implementation plan (steps to handle the request).
2. A polite and professional draft reply.

Format your response exactly as follows:
PLAN_OBJECTIVE: [Short summary of what needs to be done]
PLAN_STEPS: ['step 1', 'step 2', 'step 3']
DRAFT_TO: [The email address from the sender]
DRAFT_SUBJECT: [A professional subject line, start with Re: if appropriate]
DRAFT_BODY: [The actual message content]
"""

agent = Agent(name="DraftingAgent", instructions=INSTRUCTIONS, model=model)

def parse_ai_output(output):
    """Parses the formatted output from the agent."""
    lines = output.split('\n')
    data = {}
    for line in lines:
        if line.startswith('PLAN_OBJECTIVE:'): data['objective'] = line.replace('PLAN_OBJECTIVE:', '').strip()
        if line.startswith('PLAN_STEPS:'): 
            try:
                import ast
                data['steps'] = ast.literal_eval(line.replace('PLAN_STEPS:', '').strip())
            except:
                data['steps'] = ["Process the request"]
        if line.startswith('DRAFT_TO:'): data['to'] = line.replace('DRAFT_TO:', '').strip()
        if line.startswith('DRAFT_SUBJECT:'): data['subject'] = line.replace('DRAFT_SUBJECT:', '').strip()
        if 'DRAFT_BODY:' in line: data['body'] = output.split('DRAFT_BODY:')[-1].strip()
    return data

async def process_needs_action():
    """Scans Needs_Action and processes new files."""
    try:
        vault_root = find_vault_root()
        needs_action_path = get_needs_action_path(vault_root)
        pending_path = vault_root / "Pending_Approval"
        in_progress_path = vault_root / "In_Progress"
        
        pending_path.mkdir(parents=True, exist_ok=True)
        in_progress_path.mkdir(parents=True, exist_ok=True)

        print(f"\n--- 🧠 AI REASONING LAYER (DRAFTING) ---")
        found_tasks = 0

        for file_path in needs_action_path.iterdir():
            if not file_path.is_file() or file_path.suffix != ".md":
                continue

            is_gmail = file_path.name.startswith("GMAIL_")
            is_whatsapp = file_path.name.startswith("WHATSAPP_")
            is_linkedin_req = "LINKEDIN" in file_path.name.upper()

            if is_gmail or is_whatsapp or is_linkedin_req:
                found_tasks += 1
                print(f"   ⚙️  Drafting response for: {file_path.name}")
                logger.info(f"Processing new task: {file_path.name}")
                content = file_path.read_text(encoding='utf-8')
                
                # Custom prompt based on type
                if is_linkedin_req:
                    prompt = f"The user wants to create a LinkedIn post. Based on their instructions below, write a professional and engaging LinkedIn post with hashtags:\n\n{content}"
                else:
                    prompt = f"Please process this task from the vault:\n\n{content}"

                result = await Runner.run(agent, prompt, run_config=config)
                ai_data = parse_ai_output(result.final_output)
                
                # 1. Create Plan
                if 'objective' in ai_data and 'steps' in ai_data:
                    create_plan(file_path.stem, ai_data['objective'], ai_data['steps'])
                
                # 2. Create Draft in Pending_Approval
                if ai_data.get('body'):
                    if is_linkedin_req:
                        draft_file_name = f"APPROVAL_LINKEDIN_{file_path.stem}.md"
                        draft_type = "linkedin_approval"
                        header = "LinkedIn Post"
                    else:
                        draft_prefix = "APPROVAL_WHATSAPP_" if is_whatsapp else "APPROVAL_EMAIL_"
                        draft_file_name = f"{draft_prefix}{file_path.stem}.md"
                        draft_type = "whatsapp_approval" if is_whatsapp else "email_approval"
                        header = "WhatsApp" if is_whatsapp else "Email"
                    
                    draft_path = pending_path / draft_file_name
                    draft_content = f"""---
type: {draft_type}
to: {ai_data.get('to', 'LinkedIn Feed')}
subject: {ai_data.get('subject', 'New Post')}
status: pending
---
# Approval Required: {header} Reply

## Context
Auto-drafted response to {file_path.name}

## Body
{ai_data.get('body', 'No body generated.')}
"""
                    draft_path.write_text(draft_content, encoding='utf-8')
                    logger.info(f"Created draft: {draft_path.name}")
                
                # 3. Move original file to In_Progress
                dest_path = in_progress_path / file_path.name
                shutil.move(str(file_path), str(dest_path))
                logger.info(f"Task moved to /In_Progress: {file_path.name}")
                
                log_event(
                    action_type="agent_drafting",
                    actor="drafting_agent",
                    target=str(file_path.name),
                    result="success"
                )
        
        if found_tasks == 0:
            print("   ℹ️  No new tasks in Needs_Action.")
        else:
            print(f"   🎯 Successfully drafted {found_tasks} responses.")
        
        print("--- AI DRAFTING COMPLETE ---\n")

    except Exception as e:
        logger.error(f"Error in process_needs_action: {e}")

async def main(once=False):
    logger.info("Drafting Agent is online and watching /Needs_Action...")
    while True:
        await process_needs_action()
        if once:
            logger.info("Drafting Agent completed single run.")
            break
        await asyncio.sleep(20) # Check every 20 seconds

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true", help="Run only once and exit")
    args = parser.parse_args()

    try:
        asyncio.run(main(once=args.once))
    except KeyboardInterrupt:
        logger.info("Agent stopped by user.")
