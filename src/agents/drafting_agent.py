import os
import sys
import asyncio
import shutil
import logging
import re
import ast
from pathlib import Path
from dotenv import load_dotenv
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel
from agents.run import RunConfig

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.utils.paths import find_vault_root, get_needs_action_path, get_done_path
from src.utils.planner import create_plan
from src.utils.logger import log_event
from src.utils.odoo_client import OdooClient

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("DraftingAgent")

# AI Setup
gemini_api_key = os.getenv("GEMINI_API_KEY")
external_client = AsyncOpenAI(api_key=gemini_api_key, base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
model = OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=external_client)
config = RunConfig(model=model, model_provider=external_client, tracing_disabled=True)

INSTRUCTIONS = """
You are a professional Digital FTE. Your task is to process incoming requests and provide FINAL deliverables.
NEVER ask questions. 

For Gmail/Emails:
- Generate a professional email reply.

For WhatsApp:
- Generate a short, polite chat reply.

For Social Media (LinkedIn, Twitter, FB, IG):
- Generate the EXACT post text including hashtags.

For Odoo Tasks:
- You MUST extract Partner Name, Amount, and Reference.
- You MUST output these tags at the end of your response:
    PARTNER_NAME: (The Name)
    INVOICE_AMOUNT: (The Number)
    INVOICE_REF: (The Reference)
- Provide a summary in DRAFT_BODY.

Format EXACTLY:
PLAN_OBJECTIVE: [Summary]
PLAN_STEPS: ['step 1', 'step 2']
DRAFT_TO: [Recipient/Platform]
DRAFT_SUBJECT: [Subject]
DRAFT_BODY: [The ACTUAL content. NO QUESTIONS.]
"""

agent = Agent(name="DraftingAgent", instructions=INSTRUCTIONS, model=model)
odoo_client = OdooClient()

def parse_ai_output(output):
    lines = output.split('\n')
    data = {}
    for line in lines:
        line = line.strip()
        if line.startswith('PLAN_OBJECTIVE:'): data['objective'] = line.replace('PLAN_OBJECTIVE:', '').strip()
        if line.startswith('PLAN_STEPS:'): 
            try: data['steps'] = ast.literal_eval(line.replace('PLAN_STEPS:', '').strip())
            except: data['steps'] = ["Process task"]
        if line.startswith('DRAFT_TO:'): data['to'] = line.replace('DRAFT_TO:', '').strip()
        if line.startswith('DRAFT_SUBJECT:'): data['subject'] = line.replace('DRAFT_SUBJECT:', '').strip()
        if line.startswith('PARTNER_NAME:'): data['odoo_partner'] = line.replace('PARTNER_NAME:', '').strip()
        if line.startswith('INVOICE_AMOUNT:'): data['odoo_amount'] = line.replace('INVOICE_AMOUNT:', '').strip()
        if line.startswith('INVOICE_REF:'): data['odoo_ref'] = line.replace('INVOICE_REF:', '').strip()
        if 'DRAFT_BODY:' in line: data['body'] = output.split('DRAFT_BODY:')[-1].strip()
    return data

async def process_needs_action():
    try:
        vault_root = find_vault_root()
        needs_action_path = get_needs_action_path(vault_root)
        pending_path = vault_root / "Pending_Approval"
        in_progress_path = vault_root / "In_Progress"
        
        print(f"\n--- 🧠 AI REASONING LAYER (DRAFTING) ---")
        found_tasks = 0

        for file_path in needs_action_path.iterdir():
            if not file_path.is_file() or file_path.name.endswith(".meta.md") or file_path.name.endswith(".json"):
                continue

            found_tasks += 1
            print(f"   ⚙️  Processing Task: {file_path.name}")
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            # Extract 'from' field if it exists in markdown metadata
            sender_name = "Recipient"
            from_match = re.search(r'^from:\s*(.*)$', content, re.M)
            if from_match:
                sender_name = from_match.group(1).strip()

            # STRICT ROUTING BASED ON FILENAME PREFIX
            name_up = file_path.name.upper()
            is_gmail = "GMAIL_" in name_up
            is_whatsapp = "WHATSAPP_" in name_up
            is_odoo = "ODOO_" in name_up
            is_social = "SOCIAL_" in name_up

            # Create Prompt
            prompt = f"Process this task: {content}"
            if is_odoo: prompt = f"Generate Odoo invoice data from: {content}. Use PARTNER_NAME:, INVOICE_AMOUNT:, INVOICE_REF: tags."

            result = await Runner.run(agent, prompt, run_config=config)
            ai_data = parse_ai_output(result.final_output)
            
            # If AI didn't provide a recipient, use the one we extracted
            if not ai_data.get('to') or ai_data.get('to') == 'Recipient' or ai_data.get('to') == 'WhatsApp':
                ai_data['to'] = sender_name
            
            if 'objective' in ai_data:
                create_plan(file_path.stem, ai_data['objective'], ai_data['steps'])
            
            if ai_data.get('body'):
                odoo_id_str = ""
                header = "Task"
                prefix = "APPROVAL_"

                if is_gmail:
                    header = "Email"
                    prefix = "APPROVAL_EMAIL_"
                elif is_whatsapp:
                    header = "WhatsApp"
                    prefix = "APPROVAL_WHATSAPP_"
                elif is_odoo:
                    header = "Odoo"
                    prefix = "APPROVAL_ODOO_"
                    partner = ai_data.get('odoo_partner', 'Unknown Client').strip('() ')
                    try: amount = float(str(ai_data.get('odoo_amount', '0')).strip('() ').replace('$', ''))
                    except: amount = 0.0
                    ref = ai_data.get('odoo_ref', file_path.stem).strip('() ')
                    print(f"   💸 Calling Odoo API for {partner} (${amount})...")
                    o_id = odoo_client.log_transaction(partner, amount, ref)
                    if o_id: odoo_id_str = f"odoo_id: {o_id}\n"
                elif is_social:
                    header = "Social"
                    prefix = "APPROVAL_SOCIAL_"

                draft_name = f"{prefix}{file_path.stem}.md"
                draft_path = pending_path / draft_name
                draft_path.write_text(f"---\ntype: {header.lower()}\nto: {ai_data.get('to', 'Recipient')}\nsubject: {ai_data.get('subject', 'Action Required')}\n{odoo_id_str}status: pending\n---\n# Approval Required: {header}\n\n## Body\n{ai_data['body']}", encoding='utf-8')
                print(f"   ✅ Draft Created: {draft_name}")

            # Move file to In_Progress
            dest_path = in_progress_path / file_path.name
            try: shutil.move(str(file_path), str(dest_path))
            except: pass
        
        print("--- AI DRAFTING COMPLETE ---\n")
    except Exception as e:
        logger.error(f"Error: {e}")

async def main(once=False):
    while True:
        await process_needs_action()
        if once: break
        await asyncio.sleep(20)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    asyncio.run(main(once=args.once))
