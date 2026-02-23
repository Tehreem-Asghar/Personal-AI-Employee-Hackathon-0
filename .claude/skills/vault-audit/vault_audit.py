#!/usr/bin/env python3
"""
Vault Audit Skill - CLI Dashboard for AI Employee Workload

This script scans the AI_Employee_Vault and generates a status report
showing the workload across different folders.
"""

import os
import re
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# Folder priorities for scanning
FOLDERS_TO_SCAN = [
    "Needs_Action",
    "Pending_Approval",
    "In_Progress",
    "Approved",
]

# File type prefixes to detect
TYPE_PREFIXES = ["GMAIL", "WHATSAPP", "LINKEDIN", "APPROVAL_EMAIL"]


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


def get_file_type(filename: str) -> str:
    """Determine file type based on filename prefix."""
    filename_upper = filename.upper()
    for prefix in TYPE_PREFIXES:
        if prefix in filename_upper:
            if prefix == "APPROVAL_EMAIL":
                # Extract the actual type from approval emails
                for t in ["GMAIL", "WHATSAPP", "LINKEDIN"]:
                    if t in filename_upper:
                        return t
            return prefix
    return "UNKNOWN"


def extract_subject_from_filename(filename: str) -> str:
    """Extract subject/contact from filename."""
    # Remove extension
    name = Path(filename).stem
    
    # Remove common prefixes
    for prefix in TYPE_PREFIXES:
        name = re.sub(rf"^_?{prefix}_?", "", name, flags=re.IGNORECASE)
    
    # Clean up
    name = name.replace("_", " ")
    
    # Truncate if too long
    if len(name) > 50:
        name = name[:47] + "..."
    
    return name


def calculate_age(received_str: str) -> str:
    """Calculate age from received timestamp."""
    if not received_str:
        return "N/A"
    
    try:
        # Parse ISO format timestamp
        received = datetime.fromisoformat(received_str.replace("Z", "+00:00"))
        now = datetime.now(received.tzinfo) if received.tzinfo else datetime.now()
        
        delta = now - received
        days = delta.days
        hours = delta.seconds // 3600
        
        if days > 0:
            return f"{days}d {hours}h"
        elif hours > 0:
            return f"{hours}h"
        else:
            return f"{delta.seconds // 60}m"
    except Exception:
        return "N/A"


def get_contact_or_subject(frontmatter: Dict, file_type: str, filename: str) -> str:
    """Extract contact or subject from frontmatter or filename."""
    # Try 'from' field first (for emails/messages)
    from_field = frontmatter.get("from", "")
    if from_field:
        # Extract just the name if email is included
        if "<" in from_field:
            name = from_field.split("<")[0].strip()
            if len(name) > 40:
                name = name[:37] + "..."
            return name
        return from_field[:40]
    
    # Try 'to' field (for pending approvals)
    to_field = frontmatter.get("to", "")
    if to_field:
        return f"To: {to_field[:35]}"
    
    # Fall back to subject
    subject = frontmatter.get("subject", "")
    if subject:
        return subject[:40]
    
    # Extract from filename
    return extract_subject_from_filename(filename)


def scan_folder(folder_path: Path) -> List[Dict]:
    """Scan a folder and extract file information."""
    files = []
    
    if not folder_path.exists():
        return files
    
    for item in folder_path.iterdir():
        if item.is_file() and item.suffix.lower() in [".md", ".txt"]:
            file_info = {
                "filename": item.name,
                "type": get_file_type(item.name),
                "folder": folder_path.name,
                "path": str(item),
            }
            
            # Try to read and extract frontmatter
            try:
                content = item.read_text(encoding="utf-8")
                frontmatter = extract_frontmatter(content)
                file_info["frontmatter"] = frontmatter
                file_info["received"] = frontmatter.get("received", "")
                file_info["status"] = frontmatter.get("status", "unknown")
                file_info["subject"] = get_contact_or_subject(
                    frontmatter, file_info["type"], item.name
                )
            except Exception:
                file_info["frontmatter"] = {}
                file_info["received"] = ""
                file_info["status"] = "unknown"
                file_info["subject"] = extract_subject_from_filename(item.name)
            
            # Calculate age
            file_info["age"] = calculate_age(file_info["received"])
            
            files.append(file_info)
    
    return files


def generate_report(vault_path: Path) -> str:
    """Generate the full audit report."""
    report_lines = []
    report_lines.append("# AI Employee Vault Audit Report")
    report_lines.append(f"\n*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
    
    # Summary statistics
    total_files = 0
    folder_counts = {}
    type_counts = {"GMAIL": 0, "WHATSAPP": 0, "LINKEDIN": 0, "OTHER": 0}
    pending_count = 0
    done_count = 0
    
    all_files = {}
    
    # Scan all folders
    for folder_name in FOLDERS_TO_SCAN:
        folder_path = vault_path / folder_name
        files = scan_folder(folder_path)
        all_files[folder_name] = files
        folder_counts[folder_name] = len(files)
        total_files += len(files)
        
        # Count types
        for f in files:
            file_type = f["type"]
            if file_type in type_counts:
                type_counts[file_type] += 1
            else:
                type_counts["OTHER"] += 1
            
            if folder_name in ["Needs_Action", "Pending_Approval"]:
                pending_count += 1
    
    # Count Done folder separately
    done_path = vault_path / "Done"
    done_files = scan_folder(done_path)
    done_count = len(done_files)
    folder_counts["Done"] = done_count
    
    # Summary section
    report_lines.append("## Summary")
    report_lines.append("")
    report_lines.append("| Metric | Count |")
    report_lines.append("|--------|-------|")
    report_lines.append(f"| **Total Files Scanned** | {total_files} |")
    report_lines.append(f"| **Pending Actions** | {pending_count} |")
    report_lines.append(f"| **Completed (Done)** | {done_count} |")
    report_lines.append("")
    
    # Type breakdown
    report_lines.append("### By Type")
    report_lines.append("")
    report_lines.append("| Type | Count |")
    report_lines.append("|------|-------|")
    for type_name, count in type_counts.items():
        if count > 0:
            report_lines.append(f"| {type_name} | {count} |")
    report_lines.append("")
    
    # Detailed tables per folder
    report_lines.append("## Detailed Breakdown")
    report_lines.append("")
    
    for folder_name in FOLDERS_TO_SCAN + ["Done"]:
        files = all_files.get(folder_name, [])
        if folder_name == "Done":
            files = done_files
        
        if not files:
            continue
        
        report_lines.append(f"### {folder_name} ({len(files)} files)")
        report_lines.append("")
        report_lines.append("| Type | Subject/Contact | Status | Age |")
        report_lines.append("|------|-----------------|--------|-----|")
        
        for f in files:
            status = f.get("status", "N/A")
            if len(status) > 15:
                status = status[:12] + "..."
            
            report_lines.append(
                f"| {f['type']} | {f['subject']} | {status} | {f['age']} |"
            )
        
        report_lines.append("")
    
    # Action recommendations
    report_lines.append("## Action Recommendations")
    report_lines.append("")
    
    if pending_count == 0 and done_count > 0:
        report_lines.append("[OK] All caught up! No pending actions. Great job!")
    elif pending_count > 10:
        report_lines.append(f"[WARNING] High workload alert! You have {pending_count} pending items.")
        report_lines.append("- Consider prioritizing by age (oldest first)")
        report_lines.append("- Batch similar tasks together")
    elif pending_count > 0:
        report_lines.append(f"[INFO] You have {pending_count} pending action(s) to review.")
        report_lines.append("- Check `Pending_Approval` for emails awaiting approval")
        report_lines.append("- Check `Needs_Action` for new items requiring attention")
    
    report_lines.append("")
    report_lines.append("---")
    report_lines.append("*Vault Audit Skill - Digital FTE Dashboard*")
    
    return "\n".join(report_lines)


def main():
    parser = argparse.ArgumentParser(
        description="AI Employee Vault Audit - CLI Dashboard"
    )
    parser.add_argument(
        "--vault-path",
        type=str,
        default=None,
        help="Path to AI_Employee_Vault (default: auto-detect from project root)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output file path (default: print to console)",
    )
    
    args = parser.parse_args()
    
    # Determine vault path
    if args.vault_path:
        vault_path = Path(args.vault_path)
    else:
        # Auto-detect from project root (skill is at .qwen/skills/vault-audit/)
        script_dir = Path(__file__).parent
        # Go up: .qwen/skills/vault-audit -> .qwen/skills -> .qwen -> project_root
        project_root = script_dir.parent.parent.parent
        vault_path = project_root / "AI_Employee_Vault"
    
    if not vault_path.exists():
        print(f"[ERROR] Vault not found at {vault_path}")
        return 1
    
    # Generate report
    report = generate_report(vault_path)
    
    # Output
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(report, encoding="utf-8")
        print(f"[OK] Report saved to: {output_path}")
    else:
        # Use UTF-8 encoding for Windows console
        try:
            print(report)
        except UnicodeEncodeError:
            # Fallback for Windows console
            print(report.encode('utf-8', errors='replace').decode('utf-8'))
    
    return 0


if __name__ == "__main__":
    exit(main())
