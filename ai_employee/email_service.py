import os
import json
import logging
from datetime import datetime
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class EmailService:
    """
    Mini MCP server for sending emails via Gmail API
    """

    def __init__(self, token_file='token.json', credentials_file='credentials.json', scopes=None):
        """
        Initialize EmailService with Gmail API credentials
        """
        if scopes is None:
            scopes = ['https://www.googleapis.com/auth/gmail.send']

        self.token_file = token_file
        self.credentials_file = credentials_file
        self.scopes = scopes
        self.service = None
        self.logs_dir = Path('Logs')

        # Create logs directory if it doesn't exist
        self.logs_dir.mkdir(exist_ok=True)

        # Set up logging
        self._setup_logging()

        # Initialize the Gmail API service
        self._authenticate()

    def _setup_logging(self):
        """
        Set up logging for email service
        """
        log_file = self.logs_dir / 'email_log.txt'

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def _authenticate(self):
        """
        Authenticate with Gmail API using token.json
        """
        try:
            creds = None

            # Check if token file exists
            if os.path.exists(self.token_file):
                creds = Credentials.from_authorized_user_file(self.token_file, self.scopes)

            # If there are no valid credentials, request authorization
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    try:
                        creds.refresh(Request())
                    except Exception as e:
                        self.logger.error(f"Failed to refresh credentials: {e}")
                        # If refresh fails, try to get new credentials
                        if os.path.exists(self.credentials_file):
                            flow = InstalledAppFlow.from_client_secrets_file(
                                self.credentials_file, self.scopes
                            )
                            creds = flow.run_local_server(port=0)
                        else:
                            raise FileNotFoundError(
                                f"Credentials file {self.credentials_file} not found. "
                                f"Please set up OAuth2 credentials for Gmail API."
                            )
                else:
                    if os.path.exists(self.credentials_file):
                        flow = InstalledAppFlow.from_client_secrets_file(
                            self.credentials_file, self.scopes
                        )
                        creds = flow.run_local_server(port=0)
                    else:
                        raise FileNotFoundError(
                            f"Credentials file {self.credentials_file} not found. "
                            f"Please set up OAuth2 credentials for Gmail API."
                        )

                # Save the credentials for the next run
                with open(self.token_file, 'w') as token:
                    token.write(creds.to_json())

            # Build the Gmail API service
            self.service = build('gmail', 'v1', credentials=creds)
            self.logger.info("Successfully authenticated with Gmail API")

        except Exception as e:
            self.logger.error(f"Authentication error: {str(e)}")
            raise

    def _create_message(self, to, subject, body, sender=None):
        """
        Create a message for sending via Gmail API
        """
        try:
            message = MIMEMultipart()
            message['to'] = to
            message['subject'] = subject

            # Use sender if provided, otherwise use the authenticated user
            if sender:
                message['from'] = sender
            else:
                # Get the authenticated user's email
                profile = self.service.users().getProfile(userId='me').execute()
                message['from'] = profile.get('emailAddress', 'me')

            # Add the body to the message
            message.attach(MIMEText(body, 'plain'))

            # Encode the message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            return {'raw': raw_message}

        except Exception as e:
            self.logger.error(f"Error creating message: {str(e)}")
            raise

    def send_email(self, to, subject, body):
        """
        Send an email using Gmail API

        Args:
            to (str): Recipient email address
            subject (str): Email subject
            body (str): Email body content

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create the email message
            message = self._create_message(to, subject, body)

            # Send the email
            result = self.service.users().messages().send(
                userId='me',
                body=message
            ).execute()

            # Log the sent email
            log_entry = (
                f"Email sent successfully at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}:\n"
                f"  To: {to}\n"
                f"  Subject: {subject}\n"
                f"  Message ID: {result['id']}\n"
                f"  Status: SUCCESS\n\n"
            )

            self.logger.info(log_entry)
            print(f"Email sent successfully to {to} with subject: {subject}")
            return True

        except HttpError as error:
            error_msg = f"HTTP error occurred while sending email: {error}"
            self.logger.error(error_msg)
            print(f"Error sending email: {error}")
            return False

        except Exception as e:
            error_msg = f"Error sending email to {to}: {str(e)}"
            self.logger.error(error_msg)
            print(f"Error sending email: {e}")
            return False

    def test_connection(self):
        """
        Test the Gmail API connection by getting user profile
        """
        try:
            profile = self.service.users().getProfile(userId='me').execute()
            email_address = profile.get('emailAddress', 'Unknown')
            self.logger.info(f"Connection test successful. Authenticated user: {email_address}")
            return True
        except Exception as e:
            self.logger.error(f"Connection test failed: {str(e)}")
            return False


def main():
    """
    Main function for testing the EmailService
    """
    try:
        # Initialize the email service
        email_service = EmailService()

        # Test the connection
        if email_service.test_connection():
            print("Email service initialized successfully!")

            # Example usage (commented out to prevent accidental sending):
            # result = email_service.send_email(
            #     to="recipient@example.com",
            #     subject="Test Email",
            #     body="This is a test email sent via Gmail API."
            # )
            # print(f"Email sent: {result}")
        else:
            print("Failed to connect to Gmail API")

    except FileNotFoundError as e:
        print(f"Setup error: {e}")
        print("Please ensure you have set up OAuth2 credentials for Gmail API.")
        print("You need: token.json (user credentials) and credentials.json (app credentials)")
    except Exception as e:
        print(f"Error initializing email service: {e}")


if __name__ == "__main__":
    main()