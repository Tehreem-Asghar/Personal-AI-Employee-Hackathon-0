import sys
from pathlib import Path
from datetime import datetime
from typing import List, Optional

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.utils.paths import find_vault_root

def draft_social_post(title: str, content: str, channels: List[str]):
    """
    Creates a unified social post draft in /Pending_Approval for multiple channels.
    """
    try:
        vault_root = find_vault_root()
        pending_path = vault_root / "Pending_Approval"
        pending_path.mkdir(parents=True, exist_ok=True)

        timestamp = int(datetime.now().timestamp())
        safe_title = title.lower().replace(' ', '_')[:20]
        
        # Channels string for filename
        channels_slug = "_".join([c.upper() for c in channels])
        file_name = f"APPROVAL_SOCIAL_{channels_slug}_{safe_title}_{timestamp}.md"
        file_path = pending_path / file_name

        channels_md = ", ".join(channels)
        
        md_body = f"""---
type: social_post
channels: [{", ".join(channels)}]
title: {title}
created_at: {datetime.now().isoformat()}
status: pending
---
# Social Post Draft: {title}

**Target Channels:** {channels_md}

## Body
{content}

## Metadata
- **Twitter Character Count:** {len(content)} / 280
- **Hashtags Found:** {content.count('#')}

## Instructions
Review the body above. Once verified, move this file to **/Approved**. 
The AI Employee will then publish it to the specified channels.
"""
        file_path.write_text(md_body, encoding='utf-8')
        print(f"Drafted unified social post: {file_path}")
        return file_path

    except Exception as e:
        print(f"Error drafting social post: {e}")
        return None

if __name__ == "__main__":
    # Test draft
    draft_social_post(
        "Gold Tier Achievement", 
        "My AI Employee just leveled up to Gold Tier! Now managing Odoo and multi-channel social media autonomously. #AI #Automation #Odoo #Python",
        ["linkedin", "twitter", "facebook"]
    )
