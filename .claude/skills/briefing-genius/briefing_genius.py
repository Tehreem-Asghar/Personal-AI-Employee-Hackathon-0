#!/usr/bin/env python3
"""
Briefing Genius Skill - Daily CEO Briefing Generator

Analyzes all files in AI_Employee_Vault/Done folder and generates
a 'Daily CEO Briefing' markdown file summarizing activities.
"""

import argparse
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict


def extract_frontmatter(content: str) -> Dict[str, str]:
    """Extract YAML frontmatter from markdown content."""
    frontmatter = {}
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if match:
        fm_text = match.group(1)
        for line in fm_text.strip().split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                frontmatter[key.strip()] = value.strip().strip('"\'')
    return frontmatter


def detect_file_type(filename: str, frontmatter: Dict) -> str:
    """Detect the type of file (email, whatsapp, linkedin, task)."""
    filename_upper = filename.upper()
    
    # Check frontmatter first
    file_type = frontmatter.get("type", "").lower()
    if "email" in file_type:
        return "email"
    if "whatsapp" in file_type:
        return "whatsapp"
    if "linkedin" in file_type:
        return "linkedin"
    
    # Check filename prefixes
    if "GMAIL" in filename_upper or "EMAIL" in filename_upper:
        return "email"
    if "WHATSAPP" in filename_upper:
        return "whatsapp"
    if "LINKEDIN" in filename_upper:
        return "linkedin"
    
    return "other"


def scan_done_folder(done_path: Path, target_date: Optional[datetime] = None) -> Dict:
    """Scan the Done folder and categorize files."""
    stats = {
        "email": [],
        "whatsapp": [],
        "linkedin": [],
        "other": [],
        "total": 0,
    }
    
    if not done_path.exists():
        return stats
    
    for item in done_path.iterdir():
        if item.is_file() and item.suffix.lower() in [".md"]:
            try:
                content = item.read_text(encoding="utf-8")
                frontmatter = extract_frontmatter(content)
                
                # Check if file matches target date
                file_date = None
                if "created" in frontmatter:
                    try:
                        file_date = datetime.fromisoformat(
                            frontmatter["created"].replace("Z", "+00:00")
                        )
                    except Exception:
                        pass
                
                # Filter by date if specified
                if target_date and file_date:
                    if file_date.date() != target_date.date():
                        continue
                
                # Categorize file
                file_type = detect_file_type(item.name, frontmatter)
                stats[file_type].append({
                    "filename": item.name,
                    "frontmatter": frontmatter,
                    "path": str(item),
                    "date": file_date,
                })
                stats["total"] += 1
                
            except Exception as e:
                print(f"[WARN] Could not process {item.name}: {e}")
    
    return stats


def extract_subject_or_contact(frontmatter: Dict, filename: str) -> str:
    """Extract subject or contact from file."""
    # Try common fields
    for field in ["subject", "to", "from", "contact"]:
        if field in frontmatter:
            value = frontmatter[field]
            # Clean up email addresses
            if "<" in value:
                value = value.split("<")[0].strip()
            return value[:50]
    
    # Extract from filename
    name = Path(filename).stem
    # Remove prefixes
    name = re.sub(r"^(APPROVAL_)?(EMAIL_)?(GMAIL_)?(WHATSAPP_)?(LINKEDIN_)?", "", name, flags=re.IGNORECASE)
    name = name.replace("_", " ")
    return name[:50]


def generate_briefing(stats: Dict, date: datetime, author: str = "AI Employee") -> str:
    """Generate the CEO Briefing markdown content."""
    
    lines = []
    
    # Header
    lines.append(f"# Daily CEO Briefing")
    lines.append(f"\n**Date:** {date.strftime('%Y-%m-%d')}")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"**Prepared by:** {author}")
    lines.append("")
    
    # Executive Summary
    lines.append("## Executive Summary")
    lines.append("")
    
    total_emails = len(stats["email"])
    total_whatsapp = len(stats["whatsapp"])
    total_linkedin = len(stats["linkedin"])
    total_tasks = stats["total"]
    
    if total_tasks == 0:
        lines.append("*No completed activities recorded for this period.*")
    else:
        lines.append(f"Today, the AI Employee completed **{total_tasks} tasks** across all channels.")
        lines.append("")
        
        # Activity breakdown
        if total_emails > 0:
            lines.append(f"- **Emails sent:** {total_emails}")
        if total_whatsapp > 0:
            lines.append(f"- **WhatsApp messages processed:** {total_whatsapp}")
        if total_linkedin > 0:
            lines.append(f"- **LinkedIn posts published:** {total_linkedin}")
    
    lines.append("")
    
    # Summary Table
    lines.append("## Activity Breakdown")
    lines.append("")
    lines.append("| Channel | Count | Status |")
    lines.append("|---------|-------|--------|")
    lines.append(f"| Emails | {total_emails} | {'Active' if total_emails > 0 else 'No activity'} |")
    lines.append(f"| WhatsApp | {total_whatsapp} | {'Active' if total_whatsapp > 0 else 'No activity'} |")
    lines.append(f"| LinkedIn | {total_linkedin} | {'Active' if total_linkedin > 0 else 'No activity'} |")
    lines.append(f"| **TOTAL** | **{total_tasks}** | {'Productive' if total_tasks > 0 else 'Idle'} |")
    lines.append("")
    
    # Detailed sections per category
    if stats["email"]:
        lines.append("## Emails Sent")
        lines.append("")
        lines.append("| Subject/Recipient | Status |")
        lines.append("|-------------------|--------|")
        for item in stats["email"][:10]:  # Limit to 10
            subject = extract_subject_or_contact(item["frontmatter"], item["filename"])
            status = item["frontmatter"].get("status", "completed")
            lines.append(f"| {subject} | {status} |")
        if len(stats["email"]) > 10:
            lines.append(f"| ... and {len(stats['email']) - 10} more | |")
        lines.append("")
    
    if stats["whatsapp"]:
        lines.append("## WhatsApp Messages Processed")
        lines.append("")
        lines.append("| Contact/Subject | Status |")
        lines.append("|-----------------|--------|")
        for item in stats["whatsapp"][:10]:
            subject = extract_subject_or_contact(item["frontmatter"], item["filename"])
            status = item["frontmatter"].get("status", "completed")
            lines.append(f"| {subject} | {status} |")
        if len(stats["whatsapp"]) > 10:
            lines.append(f"| ... and {len(stats['whatsapp']) - 10} more | |")
        lines.append("")
    
    if stats["linkedin"]:
        lines.append("## LinkedIn Posts Published")
        lines.append("")
        lines.append("| Style/Topic | Status |")
        lines.append("|-------------|--------|")
        for item in stats["linkedin"][:10]:
            style = item["frontmatter"].get("style", "post")
            subject = extract_subject_or_contact(item["frontmatter"], item["filename"])
            lines.append(f"| {style.title()} - {subject} | published |")
        if len(stats["linkedin"]) > 10:
            lines.append(f"| ... and {len(stats['linkedin']) - 10} more | |")
        lines.append("")
    
    # Recommendations
    lines.append("## Recommendations for Tomorrow")
    lines.append("")
    
    if total_tasks == 0:
        lines.append("1. Review Pending_Approval folder for items awaiting action")
        lines.append("2. Check Needs_Action for new incoming items")
        lines.append("3. Consider scheduling regular briefing reviews")
    else:
        lines.append("1. Continue current productivity momentum")
        if total_emails > 5:
            lines.append("2. Consider batching email responses for efficiency")
        if total_linkedin > 0:
            lines.append("3. Monitor engagement on published LinkedIn posts")
        if total_whatsapp > 5:
            lines.append("4. Review WhatsApp automation rules for optimization")
    
    lines.append("")
    lines.append("---")
    lines.append("*Generated by Briefing Genius Skill - AI Employee Dashboard*")
    
    return "\n".join(lines)


def detect_project_root() -> Path:
    """Detect the project root directory."""
    script_dir = Path(__file__).parent
    return script_dir.parent.parent.parent


def main():
    parser = argparse.ArgumentParser(
        description="Briefing Genius - Daily CEO Briefing Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python briefing_genius.py
  python briefing_genius.py --date 2026-02-22
  python briefing_genius.py --vault-path "D:\\path\\to\\vault"
  python briefing_genius.py --output "D:\\briefings\\ceo_briefing.md"
        """
    )
    
    parser.add_argument(
        "--date",
        type=str,
        default=None,
        help="Target date for briefing (YYYY-MM-DD format, default: today)"
    )
    
    parser.add_argument(
        "--vault-path",
        type=str,
        default=None,
        help="Path to AI_Employee_Vault (default: auto-detect)"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output file path (default: vault root)"
    )
    
    parser.add_argument(
        "--author",
        type=str,
        default="AI Employee",
        help="Author name for the briefing"
    )
    
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Preview briefing in console without saving"
    )
    
    args = parser.parse_args()
    
    # Determine vault path
    if args.vault_path:
        vault_path = Path(args.vault_path)
    else:
        vault_path = detect_project_root() / "AI_Employee_Vault"
    
    if not vault_path.exists():
        print(f"[ERROR] Vault not found at {vault_path}")
        return 1
    
    # Determine target date
    if args.date:
        try:
            target_date = datetime.strptime(args.date, "%Y-%m-%d")
        except ValueError:
            print(f"[ERROR] Invalid date format. Use YYYY-MM-DD")
            return 1
    else:
        target_date = datetime.now()
    
    # Scan Done folder
    done_path = vault_path / "Done"
    stats = scan_done_folder(done_path, target_date)
    
    # Generate briefing
    briefing = generate_briefing(stats, target_date, args.author)
    
    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        # Save into a dedicated subfolder
        briefings_dir = vault_path / "Briefings" / "Daily"
        briefings_dir.mkdir(parents=True, exist_ok=True)
        output_path = briefings_dir / f"Daily_CEO_Briefing_{target_date.strftime('%Y-%m-%d')}.md"
    
    if args.preview:
        # Handle Windows console encoding
        try:
            print(briefing)
        except UnicodeEncodeError:
            print(briefing.encode('utf-8', errors='replace').decode('utf-8'))
        print(f"\n[INFO] Briefing would be saved to: {output_path}")
    else:
        output_path.write_text(briefing, encoding="utf-8")
        print(f"\n[OK] Daily CEO Briefing generated!")
        print(f"Location: {output_path}")
        print(f"\nSummary:")
        print(f"  - Emails: {len(stats['email'])}")
        print(f"  - WhatsApp: {len(stats['whatsapp'])}")
        print(f"  - LinkedIn: {len(stats['linkedin'])}")
        print(f"  - Total: {stats['total']}")
    
    return 0


if __name__ == "__main__":
    exit(main())
