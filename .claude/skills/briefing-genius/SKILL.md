# Skill: briefing-genius

## Objective
Create a skill that analyzes all files in the `AI_Employee_Vault/Done` folder and generates a 'Daily CEO Briefing' markdown file in the vault root.

The briefing summarizes:
1. Total emails sent
2. WhatsApp messages processed
3. LinkedIn posts published

## Usage
```bash
# Basic usage
python .claude/skills/briefing-genius/briefing_genius.py

# With custom vault path
python .claude/skills/briefing-genius/briefing_genius.py --vault-path "D:\path\to\AI_Employee_Vault"

# For a specific date
python .claude/skills/briefing-genius/briefing_genius.py --date 2026-02-22

# Save to custom output location
python .claude/skills/briefing-genius/briefing_genius.py --output "D:\briefings\ceo_briefing.md"
```

## Output
Creates a markdown file named `Daily_CEO_Briefing_YYYY-MM-DD.md` in the vault root with:
- Executive summary
- Activity breakdown table
- Top accomplishments
- Recommendations for tomorrow

## Files
- `briefing_genius.py` - Main script for briefing generation
- `SKILL.md` - This documentation file
