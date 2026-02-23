# Skill: vault-audit

## Objective
Create a skill that allows me to quickly see the status of my Digital FTE's workload. The skill should scan the `AI_Employee_Vault` and its subdirectories: `/Needs_Action`, `/Pending_Approval`, `/In_Progress`, and `/Approved`.

## Functionality
1. **File Scanning**: For each folder, count the files and identify their type (GMAIL, WHATSAPP, or LINKEDIN) based on the filename prefix.
2. **Metadata Extraction**: For files in `/Pending_Approval` and `/Needs_Action`, read the markdown frontmatter to extract the 'from/to' info and the 'received' timestamp.
3. **Visual Report**: Present the findings in a clean Markdown table with columns: [Folder, Type, Subject/Contact, Status, Age].
4. **Summary**: At the end, provide a total count of pending actions versus completed tasks in `/Done`.

## Context
The vault is located at the project root. This skill will act as my CLI Dashboard to manage my AI Employee.

## Usage
```bash
# Run the vault audit skill
python .claude/skills/vault-audit/vault_audit.py

# Or with a specific vault path
python .claude/skills/vault-audit/vault_audit.py --vault-path "D:\Personal AI Employee Hackathon 0\personal-ai-employee-hackathon-0\AI_Employee_Vault"
```

## Output
The skill generates a Markdown-formatted report with:
- Summary statistics
- Detailed tables per folder
- Age analysis of pending items
- Action recommendations

## Files
- `vault_audit.py` - Main script for vault auditing
- `SKILL.md` - This documentation file
