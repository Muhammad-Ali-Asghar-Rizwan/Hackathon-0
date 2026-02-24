import os
import json
import pickle
from datetime import datetime
from pathlib import Path
from typing import Optional
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64


class GmailSender:
    """
    A class to send emails using Gmail API with OAuth authentication.
    """

    SCOPES = ['https://www.googleapis.com/auth/gmail.send',
              'https://www.googleapis.com/auth/gmail.readonly',
              'https://www.googleapis.com/auth/gmail.modify']  # for consistency with watcher

    def __init__(self, token_path: str = 'token.json', client_secret_path: str = 'client_secret.json'):
        """
        Initialize the GmailSender.

        Args:
            token_path: Path to the token JSON file (default: 'token.json')
            client_secret_path: Path to the client secret JSON file (default: 'client_secret.json')
        """
        self.token_path = token_path
        self.client_secret_path = client_secret_path
        self.creds = self._authenticate()
        self.service = build('gmail', 'v1', credentials=self.creds)
        self.logs_dir = Path('Logs')
        self._ensure_logs_directory()

    def _authenticate(self):
        """
        Authenticate using OAuth2 and return credentials.

        Returns:
            google.oauth2.credentials.Credentials: Authenticated credentials.
        """
        creds = None

        # Load existing token if available
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)

        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"Error refreshing token: {e}")
                    # If refresh fails, delete the token and get new credentials
                    if os.path.exists(self.token_path):
                        os.remove(self.token_path)
                    creds = None
            else:
                creds = None

            if not creds:
                if not os.path.exists(self.client_secret_path):
                    raise FileNotFoundError(
                        f"Client secret file not found: {self.client_secret_path}. "
                        f"Please ensure the file exists and contains valid credentials."
                    )

                flow = InstalledAppFlow.from_client_secrets_file(
                    self.client_secret_path, self.SCOPES
                )
                creds = flow.run_local_server(port=0)

                # Save credentials for next run
                with open(self.token_path, 'wb') as token:
                    pickle.dump(creds, token)

        return creds

    def _ensure_logs_directory(self):
        """
        Ensure the logs directory exists.
        """
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    def _create_message(self, sender: str, to: str, subject: str, body: str, msg_type: str = 'plain') -> dict:
        """
        Create a message for an email.

        Args:
            sender: Email address of the sender.
            to: Email address of the recipient.
            subject: The subject of the email message.
            body: The text of the email message.
            msg_type: Type of message ('plain' or 'html')

        Returns:
            A message object.
        """
        message = MIMEText(body, msg_type)
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        return {'raw': raw_message}

    def _log_sent_email(self, to: str, subject: str, body: str, status: str, error: Optional[str] = None):
        """
        Log sent email information to a JSON file.

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body content
            status: Status of the email send operation
            error: Error message if the send failed
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "to": to,
            "subject": subject,
            "body": body,
            "status": status,
            "error": error
        }

        # Create filename with timestamp to avoid conflicts
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # Include milliseconds for uniqueness
        filename = f"email_log_{timestamp}.json"

        log_path = self.logs_dir / filename
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(log_entry, f, indent=2, ensure_ascii=False)

    def send_email(self, to: str, subject: str, body: str, msg_type: str = 'plain') -> bool:
        """
        Send an email using the Gmail API.

        Args:
            to: Email address of the recipient.
            subject: The subject of the email message.
            body: The text of the email message.
            msg_type: Type of message ('plain' or 'html') - default is 'plain'

        Returns:
            bool: True if email was sent successfully, False otherwise.
        """
        try:
            # Get sender's email address
            sender = self._get_user_email()

            # Create message
            message = self._create_message(sender, to, subject, body, msg_type)

            # Send the message
            sent_message = self.service.users().messages().send(
                userId="me",
                body=message
            ).execute()

            print(f"Email sent successfully to {to}. Message ID: {sent_message['id']}")

            # Log the successful send
            self._log_sent_email(to, subject, body, "success")

            return True

        except HttpError as error:
            error_msg = f"An HTTP error occurred: {error}"
            print(error_msg)

            # Log the failed send
            self._log_sent_email(to, subject, body, "failed", str(error))

            return False
        except Exception as error:
            error_msg = f"An error occurred: {error}"
            print(error_msg)

            # Log the failed send
            self._log_sent_email(to, subject, body, "failed", str(error))

            return False

    def _get_user_email(self) -> str:
        """
        Get the authenticated user's email address.

        Returns:
            str: The user's email address.
        """
        try:
            profile = self.service.users().getProfile(userId='me').execute()
            return profile.get('emailAddress', 'me')
        except Exception as e:
            print(f"Could not retrieve user's email address: {e}")
            return 'me'  # Use 'me' as default


def send_email(to: str, subject: str, body: str) -> bool:
    """
    Convenience function to send an email using Gmail API.

    Args:
        to: Email address of the recipient
        subject: The subject of the email message
        body: The text of the email message

    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        sender = GmailSender()
        return sender.send_email(to, subject, body)
    except Exception as e:
        print(f"Failed to initialize GmailSender: {e}")
        # Log the error as well
        logs_dir = Path('Logs')
        logs_dir.mkdir(parents=True, exist_ok=True)

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "to": to,
            "subject": subject,
            "body": body,
            "status": "failed",
            "error": f"Failed to initialize GmailSender: {str(e)}"
        }

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        filename = f"email_log_{timestamp}.json"
        log_path = logs_dir / filename
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(log_entry, f, indent=2, ensure_ascii=False)

        return False


def main():
    """
    Example usage of the email sender.
    """
    print("Gmail Email Sender Example")
    print("=" * 30)

    # Example usage
    recipient = "example@example.com"
    subject = "Test Email from Gmail API"
    body = "This is a test email sent using the Gmail API."

    print(f"Sending email to: {recipient}")
    print(f"Subject: {subject}")
    print(f"Body: {body}")

    success = send_email(recipient, subject, body)

    if success:
        print("Email sent successfully!")
    else:
        print("Failed to send email.")


if __name__ == "__main__":
    main()