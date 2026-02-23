import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.utils.paths import find_vault_root

def draft_linkedin_post(title: str, content: str):
    """
    Creates a draft LinkedIn post in the /Pending_Approval folder.
    """
    try:
        vault_root = find_vault_root()
        pending_path = vault_root / "Pending_Approval"
        pending_path.mkdir(parents=True, exist_ok=True)

        # Create unique filename
        timestamp = int(datetime.now().timestamp())
        safe_title = title.lower().replace(' ', '_')[:20]
        file_name = f"APPROVAL_LINKEDIN_{safe_title}_{timestamp}.md"
        file_path = pending_path / file_name

        md_body = f"""---
type: linkedin_post
title: {title}
created_at: {datetime.now().isoformat()}
status: pending_review
---
# LinkedIn Post Draft: {title}

## Body
{content}

## Instructions
Move this file to /Approved to publish (simulated in Silver Tier).
"""
        file_path.write_text(md_body, encoding='utf-8')
        print(f"Drafted LinkedIn post: {file_path}")
        return file_path

    except Exception as e:
        print(f"Error drafting LinkedIn post: {e}")
        return None

if __name__ == "__main__":
    draft_linkedin_post("Hackathon Milestone", "Just completed the Silver Tier foundation for my Digital FTE project! #AI #Automation #Python")
