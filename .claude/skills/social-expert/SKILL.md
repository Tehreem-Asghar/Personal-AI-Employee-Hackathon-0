# Skill: social-expert

## Objective
Create a skill that takes a raw project idea or update from me, and drafts 3 different versions of a LinkedIn post:
- **Professional** - Formal, business-oriented tone
- **Story-telling** - Narrative, personal journey style
- **Short/Punchy** - Concise, impactful, viral-style

The drafts are saved as `.md` files in `AI_Employee_Vault/Pending_Approval` with the prefix `APPROVAL_LINKEDIN_`.

## Usage
```bash
# Basic usage with quoted input
python .claude/skills/social-expert/social_expert.py "Just launched my new AI project!"

# With custom author name
python .claude/skills/social-expert/social_expert.py "Completed my AI certification" --author "John Doe"

# Save to specific vault path
python .claude/skills/social-expert/social_expert.py "New milestone achieved" --vault-path "D:\path\to\AI_Employee_Vault"
```

## Output
Creates 3 markdown files in `AI_Employee_Vault/Pending_Approval/`:
- `APPROVAL_LINKEDIN_Professional_YYYYMMDD_HHMMSS.md`
- `APPROVAL_LINKEDIN_Storytelling_YYYYMMDD_HHMMSS.md`
- `APPROVAL_LINKEDIN_Punchy_YYYYMMDD_HHMMSS.md`

Each file contains:
- YAML frontmatter with metadata (type, style, status, created timestamp)
- The drafted LinkedIn post content
- Suggested hashtags

## Files
- `social_expert.py` - Main script for LinkedIn post generation
- `SKILL.md` - This documentation file
