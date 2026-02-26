import os
import requests
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv


class LinkedInPoster:
    """
    LinkedIn poster class to post content to LinkedIn profile using LinkedIn API
    """

    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()

        # Get LinkedIn access token from environment
        self.access_token = os.getenv('LINKEDIN_ACCESS_TOKEN')

        if not self.access_token:
            raise ValueError("LINKEDIN_ACCESS_TOKEN not found in environment variables")

        # LinkedIn API endpoints
        self.api_url = "https://api.linkedin.com/v2"
        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'
        }

        # Set up logging
        self.logs_dir = Path('Logs')
        self.logs_dir.mkdir(exist_ok=True)

        log_file = self.logs_dir / 'linkedin_log.txt'

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def get_user_profile(self):
        """
        Get the authenticated user's LinkedIn profile information
        """
        try:
            # Get the user's profile to verify access token and get profile ID
            profile_url = f"{self.api_url}/me"
            response = requests.get(profile_url, headers=self.headers)

            if response.status_code == 200:
                profile_data = response.json()
                return profile_data
            else:
                self.logger.error(f"Failed to get user profile: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            self.logger.error(f"Error getting user profile: {str(e)}")
            return None

    def post_to_linkedin(self, content):
        """
        Post content to LinkedIn profile

        Args:
            content (str): The text content to post

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get user profile to get the URN
            profile_data = self.get_user_profile()
            if not profile_data or 'id' not in profile_data:
                self.logger.error("Could not retrieve user profile information")
                return False

            author_urn = f"urn:li:person:{profile_data['id']}"

            # Prepare the post payload according to LinkedIn API specification
            post_payload = {
                "author": author_urn,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": content
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }

            # Make the API request to create the post
            post_url = f"{self.api_url}/ugcPosts"
            response = requests.post(post_url, headers=self.headers, json=post_payload)

            if response.status_code in [200, 201]:
                post_response = response.json()
                post_id = post_response.get('id', 'Unknown')

                log_entry = (
                    f"LinkedIn post created successfully at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}:\n"
                    f"  Content: {content[:100]}{'...' if len(content) > 100 else ''}\n"
                    f"  Post ID: {post_id}\n"
                    f"  Status: SUCCESS\n\n"
                )

                self.logger.info(log_entry)
                print(f"Successfully posted to LinkedIn: {content[:50]}{'...' if len(content) > 50 else ''}")
                return True
            else:
                error_msg = f"Failed to post to LinkedIn: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                print(f"Error posting to LinkedIn: {response.status_code} - {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            error_msg = f"Request error while posting to LinkedIn: {str(e)}"
            self.logger.error(error_msg)
            print(f"Request error: {str(e)}")
            return False
        except Exception as e:
            error_msg = f"Unexpected error while posting to LinkedIn: {str(e)}"
            self.logger.error(error_msg)
            print(f"Error: {str(e)}")
            return False


def post_to_linkedin(content):
    """
    Convenience function to post content to LinkedIn

    Args:
        content (str): The text content to post

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        poster = LinkedInPoster()
        return poster.post_to_linkedin(content)
    except Exception as e:
        print(f"Error initializing LinkedInPoster: {str(e)}")
        return False


def main():
    """
    Main function for testing the LinkedInPoster
    """
    try:
        # Initialize the LinkedIn poster
        poster = LinkedInPoster()

        # Test connection by trying to get user profile
        profile = poster.get_user_profile()
        if profile:
            print(f"Successfully authenticated with LinkedIn as {profile.get('localizedFirstName', 'User')}")

            # Example usage (commented out to prevent accidental posting):
            # result = poster.post_to_linkedin("This is a test post from my Python app!")
            # print(f"Post result: {result}")
        else:
            print("Failed to authenticate with LinkedIn API")

    except ValueError as e:
        print(f"Configuration error: {e}")
        print("Please make sure you have set the LINKEDIN_ACCESS_TOKEN in your environment variables")
    except Exception as e:
        print(f"Error initializing LinkedIn poster: {e}")


if __name__ == "__main__":
    main()