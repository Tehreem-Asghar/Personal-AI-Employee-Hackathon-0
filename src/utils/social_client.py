import os
import logging
import tweepy
import facebook
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class SocialClient:
    """
    Unified client for posting to multiple social media channels.
    """
    def __init__(self):
        # Twitter/X credentials
        self.x_api_key = os.getenv("X_API_KEY")
        self.x_api_secret = os.getenv("X_API_SECRET")
        self.x_access_token = os.getenv("X_ACCESS_TOKEN")
        self.x_access_secret = os.getenv("X_ACCESS_SECRET")
        
        # Meta (FB/IG) credentials
        self.fb_access_token = os.getenv("FB_ACCESS_TOKEN")
        
        # LinkedIn credentials
        self.li_access_token = os.getenv("LI_ACCESS_TOKEN")

    def post_to_twitter(self, text: str) -> bool:
        """Posts a tweet to Twitter/X."""
        try:
            client = tweepy.Client(
                consumer_key=self.x_api_key,
                consumer_secret=self.x_api_secret,
                access_token=self.x_access_token,
                access_token_secret=self.x_access_secret
            )
            client.create_tweet(text=text)
            logger.info("Successfully posted to Twitter/X")
            return True
        except Exception as e:
            logger.error(f"Failed to post to Twitter: {e}")
            return False

    def post_to_facebook(self, text: str) -> bool:
        # ... (keep existing fb logic) ...
        try:
            page_id = os.getenv("FB_PAGE_ID")
            if not page_id or page_id == "your_page_id_here":
                logger.error("FB_PAGE_ID missing in .env")
                return False
                
            graph = facebook.GraphAPI(access_token=self.fb_access_token)
            graph.put_object(parent_object=page_id, connection_name='feed', message=text)
            logger.info(f"Successfully posted to Facebook Page: {page_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to post to Facebook: {e}")
            return False

    def post_to_instagram(self, text: str, image_url: str = None) -> bool:
        """
        Posts to Instagram Business Account. 
        Note: Instagram REQUIRES an image. If none provided, we use a placeholder.
        """
        try:
            ig_user_id = os.getenv("IG_USER_ID")
            if not ig_user_id:
                logger.error("IG_USER_ID missing in .env")
                return False
            
            # Instagram requires an image URL to post. 
            # For hackathon text-only test, we use a generic placeholder image.
            img = image_url or "https://images.unsplash.com/photo-1611162617474-5b21e879e113?q=80&w=1000&auto=format&fit=crop"
            
            import requests
            # 1. Create Media Container
            post_url = f"https://graph.facebook.com/v19.0/{ig_user_id}/media"
            payload = {
                'image_url': img,
                'caption': text,
                'access_token': self.fb_access_token
            }
            r = requests.post(post_url, data=payload)
            result = r.json()
            
            if 'id' in result:
                creation_id = result['id']
                # 2. Publish Media Container
                publish_url = f"https://graph.facebook.com/v19.0/{ig_user_id}/media_publish"
                publish_payload = {
                    'creation_id': creation_id,
                    'access_token': self.fb_access_token
                }
                r_pub = requests.post(publish_url, data=publish_payload)
                if 'id' in r_pub.json():
                    logger.info(f"Successfully posted to Instagram: {r_pub.json()['id']}")
                    return True
            
            logger.error(f"Instagram Post Failed: {result}")
            return False
        except Exception as e:
            logger.error(f"Failed to post to Instagram: {e}")
            return False

    def post_to_linkedin(self, text: str) -> bool:
        """Posts a share to LinkedIn (Simplified placeholder)."""
        # In a real scenario, this uses the LinkedIn Marketing Developer Platform API
        # Here we simulate the intent.
        logger.info(f"LinkedIn Post Intent: {text[:50]}...")
        return True

    def post_all(self, content: Dict[str, str]) -> Dict[str, bool]:
        """Posts content to all specified channels."""
        results = {}
        if 'twitter' in content:
            results['twitter'] = self.post_to_twitter(content['twitter'])
        if 'facebook' in content:
            results['facebook'] = self.post_to_facebook(content['facebook'])
        if 'linkedin' in content:
            results['linkedin'] = self.post_to_linkedin(content['linkedin'])
        return results
