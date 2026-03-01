import sys
from pathlib import Path
from mcp.server.fastmcp import FastMCP
from typing import List

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.utils.social_draft import draft_social_post
from src.utils.social_client import SocialClient

# Initialize FastMCP server
mcp = FastMCP("SocialServer")
client = SocialClient()

@mcp.tool()
def draft_social_media_post(title: str, content: str, channels: List[str]) -> str:
    """
    Drafts a post for review across multiple social media channels.
    :param title: A brief title for the draft file.
    :param content: The body text of the post.
    :param channels: List of platforms (linkedin, twitter, facebook, instagram).
    """
    if not channels:
        return "Error: At least one channel must be specified."
        
    file_path = draft_social_post(title, content, channels)
    if not file_path:
        return "Error: Failed to create post draft."
        
    return f"Successfully drafted post for {', '.join(channels)}. File: {file_path.name}"

@mcp.tool()
def publish_to_twitter(text: str) -> str:
    """Directly publishes a post to Twitter/X. USE ONLY AFTER HUMAN APPROVAL."""
    success = client.post_to_twitter(text)
    return "Tweet posted successfully." if success else "Failed to post tweet."

@mcp.tool()
def publish_to_facebook(text: str) -> str:
    """Directly publishes a post to Facebook. USE ONLY AFTER HUMAN APPROVAL."""
    success = client.post_to_facebook(text)
    return "Facebook post published successfully." if success else "Failed to publish Facebook post."

if __name__ == "__main__":
    mcp.run()
