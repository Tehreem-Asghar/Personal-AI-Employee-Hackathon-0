import sys
from pathlib import Path
from datetime import datetime
from typing import List

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.utils.paths import find_vault_root

def create_plan(source_task_name: str, objective: str, steps: List[str]):
    """
    Creates a structured Plan.md file in the /Plans folder.
    """
    try:
        vault_root = find_vault_root()
        plans_path = vault_root / "Plans"
        plans_path.mkdir(parents=True, exist_ok=True)

        # Create unique filename
        timestamp = int(datetime.now().timestamp())
        plan_file_name = f"PLAN_{source_task_name}_{timestamp}.md"
        plan_file_path = plans_path / plan_file_name

        # Construct markdown content
        steps_md = "\n".join([f"- [ ] {step}" for step in steps])
        
        content = f"""---
created_at: {datetime.now().isoformat()}
source_task: {source_task_name}
status: pending
---
# Plan: {objective}

## Objective
{objective}

## Execution Steps
{steps_md}

## Approval Status
- [ ] Logic Verified by Human
"""
        plan_file_path.write_text(content, encoding='utf-8')
        print(f"Created plan: {plan_file_path}")
        return plan_file_path

    except Exception as e:
        print(f"Error creating plan: {e}")
        return None

if __name__ == "__main__":
    import argparse
    import ast
    
    parser = argparse.ArgumentParser(description="Create a task plan in Obsidian.")
    parser.add_argument("name", help="Source task name")
    parser.add_argument("objective", help="Main objective")
    parser.add_argument("steps", help="List of steps as a string (e.g. \"['step1', 'step2']\")")
    
    args = parser.parse_args()
    
    try:
        # Convert string representation of list to actual list
        steps_list = ast.literal_eval(args.steps)
        create_plan(args.name, args.objective, steps_list)
    except Exception as e:
        print(f"Failed to parse arguments or create plan: {e}")
