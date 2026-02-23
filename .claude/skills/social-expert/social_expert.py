#!/usr/bin/env python3
"""
Social Expert Skill - LinkedIn Post Generator

Takes a raw project idea or update and drafts 3 different versions
of a LinkedIn post: Professional, Story-telling, and Short/Punchy.
"""

import argparse
import re
from datetime import datetime
from pathlib import Path
from typing import List, Tuple


def extract_hashtags(text: str) -> List[str]:
    """Extract potential hashtags from text."""
    # Common tech/AI hashtags based on keywords
    hashtag_map = {
        'ai': '#AI',
        'artificial intelligence': '#ArtificialIntelligence',
        'machine learning': '#MachineLearning',
        'ml': '#ML',
        'project': '#Project',
        'launch': '#Launch',
        'startup': '#Startup',
        'tech': '#Tech',
        'technology': '#Technology',
        'innovation': '#Innovation',
        'developer': '#Developer',
        'coding': '#Coding',
        'programming': '#Programming',
        'python': '#Python',
        'software': '#Software',
        'engineer': '#Engineering',
        'career': '#Career',
        'learning': '#Learning',
        'growth': '#Growth',
        'milestone': '#Milestone',
        'achievement': '#Achievement',
        'hackathon': '#Hackathon',
        'automation': '#Automation',
        'agent': '#AIAgent',
        'employee': '#DigitalEmployee',
        'fte': '#FutureOfWork',
    }
    
    hashtags = []
    text_lower = text.lower()
    
    for keyword, tag in hashtag_map.items():
        if keyword in text_lower and tag not in hashtags:
            hashtags.append(tag)
    
    # Limit to 5 hashtags
    return hashtags[:5] if hashtags else ['#AI', '#Technology', '#Innovation']


def generate_professional_version(input_text: str, author: str) -> str:
    """Generate a professional, business-oriented LinkedIn post."""

    hashtags = extract_hashtags(input_text)

    content = f"""I'm excited to share an update on my latest work.

{input_text}

This represents a significant step forward in leveraging technology to solve real-world challenges. I'm grateful for the opportunity to work on meaningful projects that push boundaries and create value.

Looking forward to connecting with others who are passionate about innovation and the future of technology.

#Professional #Career { ' '.join(hashtags)}

- {author if author else 'Author'}"""

    return content.strip()


def generate_storytelling_version(input_text: str, author: str) -> str:
    """Generate a narrative, personal journey style LinkedIn post."""

    hashtags = extract_hashtags(input_text)

    content = f"""Let me take you back to where this all started...

{input_text}

It hasn't been an easy journey. There were moments of doubt, late nights, and countless iterations. But here's what I learned along the way:

- Every challenge is an opportunity in disguise
- The best solutions come from understanding real problems
- Persistence beats perfection every time

To anyone working on their own project right now: keep going. The breakthrough you're waiting for is closer than you think.

What's a recent win you're celebrating? Drop it in the comments - I'd love to hear your story.

#Journey #Storytelling #GrowthMindset {' '.join(hashtags)}

- {author if author else 'Author'}"""

    return content.strip()


def generate_punchy_version(input_text: str, author: str) -> str:
    """Generate a short, impactful, viral-style LinkedIn post."""

    hashtags = extract_hashtags(input_text)

    # Make it punchy with line breaks
    content = f"""{input_text}

That's it. That's the post.

Big things coming soon.

{' '.join(hashtags)}

- {author if author else 'Author'}"""

    # Keep it under 280 characters for maximum impact if possible
    return content.strip()


def create_linkedin_file(
    vault_path: Path,
    style: str,
    content: str,
    input_text: str,
    timestamp: datetime
) -> Path:
    """Create a markdown file with frontmatter in the Pending_Approval folder."""
    
    pending_path = vault_path / "Pending_Approval"
    pending_path.mkdir(parents=True, exist_ok=True)
    
    # Generate filename with timestamp
    filename = f"APPROVAL_LINKEDIN_{style}_{timestamp.strftime('%Y%m%d_%H%M%S')}.md"
    file_path = pending_path / filename
    
    # Create frontmatter
    frontmatter = f"""---
type: linkedin_post
style: {style.lower()}
status: pending_approval
created: {timestamp.isoformat()}
input_hash: {hash(input_text) & 0xFFFFFFFF:08x}
---
"""
    
    # Write file with ## Body header
    full_content = frontmatter + "\n## Body\n" + content
    file_path.write_text(full_content, encoding='utf-8')
    
    return file_path


def generate_posts(input_text: str, author: str, vault_path: Path) -> List[Tuple[str, Path]]:
    """Generate all 3 post versions and save them."""
    
    timestamp = datetime.now()
    results = []
    
    # Generate each style
    styles = [
        ("Professional", generate_professional_version),
        ("Storytelling", generate_storytelling_version),
        ("Punchy", generate_punchy_version),
    ]
    
    for style_name, generator in styles:
        content = generator(input_text, author)
        file_path = create_linkedin_file(
            vault_path, style_name, content, input_text, timestamp
        )
        results.append((style_name, file_path))
    
    return results


def detect_project_root() -> Path:
    """Detect the project root directory."""
    # Start from the skill's location
    script_dir = Path(__file__).parent
    # Go up: .qwen/skills/social-expert -> .qwen/skills -> .qwen -> project_root
    return script_dir.parent.parent.parent


def main():
    parser = argparse.ArgumentParser(
        description="Social Expert - LinkedIn Post Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python social_expert.py "Just launched my AI project!"
  python social_expert.py "New certification achieved" --author "Jane Doe"
  python social_expert.py "Milestone reached" --vault-path "D:\\path\\to\\vault"
        """
    )
    
    parser.add_argument(
        "input",
        type=str,
        help="Your raw project idea or update text"
    )
    
    parser.add_argument(
        "--author",
        type=str,
        default="",
        help="Author name to sign the posts (optional)"
    )
    
    parser.add_argument(
        "--vault-path",
        type=str,
        default=None,
        help="Path to AI_Employee_Vault (default: auto-detect)"
    )
    
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Preview posts in console without saving"
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
    
    # Generate posts
    results = generate_posts(args.input, args.author, vault_path)
    
    if args.preview:
        # Show preview in console
        print("\n" + "=" * 60)
        print("LINKEDIN POST PREVIEWS")
        print("=" * 60 + "\n")

        for style_name, file_path in results:
            content = file_path.read_text(encoding='utf-8')
            print(f"\n--- {style_name.upper()} ---\n")
            # Remove frontmatter for preview
            post_content = re.sub(r'^---\n.*?\n---\n', '', content, flags=re.DOTALL)
            # Handle Windows console encoding
            try:
                print(post_content)
            except UnicodeEncodeError:
                print(post_content.encode('utf-8', errors='replace').decode('utf-8'))
            print("\n" + "-" * 60)

        print(f"\n[OK] Posts saved to: {vault_path / 'Pending_Approval'}")
    else:
        print("\n[OK] LinkedIn posts generated successfully!\n")
        print("Files created:")
        for style_name, file_path in results:
            print(f"  - {style_name}: {file_path.name}")
        print(f"\nLocation: {vault_path / 'Pending_Approval'}")
        print("\n[INFO] Review and move to /Approved when ready to post.")
    
    return 0


if __name__ == "__main__":
    exit(main())
