import os
import pickle
import json
import base64
import re
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GmailWatcher:
    """
    A class to watch Gmail inbox and process unread emails using Gmail API.
    """

    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
              'https://www.googleapis.com/auth/gmail.modify']

    def __init__(self, client_secret_path: str = 'client_secret.json'):
        """
        Initialize the GmailWatcher.

        Args:
            client_secret_path: Path to the client secret JSON file.
        """
        load_dotenv()  # Load environment variables
        self.client_secret_path = client_secret_path
        self.creds = self._authenticate()
        self.service = build('gmail', 'v1', credentials=self.creds)
        self.vault_path = os.getenv('VAULT_PATH', 'Needs_Action')
        self._ensure_vault_directory()

    def _authenticate(self):
        """
        Authenticate using OAuth2 and return credentials.

        Returns:
            google.oauth2.credentials.Credentials: Authenticated credentials.
        """
        creds = None

        # Load existing token if available
        if os.path.exists('token.json'):
            with open('token.json', 'rb') as token:
                creds = pickle.load(token)

        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"Error refreshing token: {e}")
                    # If refresh fails, delete the token and get new credentials
                    if os.path.exists('token.json'):
                        os.remove('token.json')
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
                with open('token.json', 'wb') as token:
                    pickle.dump(creds, token)

        return creds

    def _ensure_vault_directory(self):
        """
        Ensure the vault directory exists.
        """
        vault_dir = Path(self.vault_path)
        vault_dir.mkdir(parents=True, exist_ok=True)

    def _decode_base64_text(self, encoded_text: str) -> str:
        """
        Decode base64 encoded text.

        Args:
            encoded_text: Base64 encoded string.

        Returns:
            str: Decoded string.
        """
        if not encoded_text:
            return ""

        # Remove any padding if not present
        missing_padding = len(encoded_text) % 4
        if missing_padding:
            encoded_text += '=' * (4 - missing_padding)

        try:
            decoded_bytes = base64.urlsafe_b64decode(encoded_text)
            return decoded_bytes.decode('utf-8')
        except Exception as e:
            print(f"Error decoding base64 text: {e}")
            return ""

    def _clean_subject(self, subject: str) -> str:
        """
        Clean the email subject to create a valid filename.

        Args:
            subject: Original email subject.

        Returns:
            str: Cleaned subject suitable for filename.
        """
        if not subject:
            return "Untitled_Email"

        # Replace invalid characters for filenames
        cleaned = re.sub(r'[<>:"/\\|?*]', '_', subject)

        # Limit length to avoid filesystem issues
        if len(cleaned) > 150:
            cleaned = cleaned[:150]

        # Remove leading/trailing whitespace
        cleaned = cleaned.strip()

        # Ensure filename is not empty after cleaning
        if not cleaned:
            cleaned = "Untitled_Email"

        return cleaned

    def _extract_plain_text_body(self, message: Dict[str, Any]) -> str:
        """
        Extract plain text body from email message.

        Args:
            message: Gmail API message object.

        Returns:
            str: Plain text body of the email.
        """
        body = ""

        if 'payload' in message and 'parts' in message['payload']:
            # Look for plain text part first
            for part in message['payload']['parts']:
                if part['mimeType'] == 'text/plain':
                    body = self._decode_base64_text(part['body'].get('data', ''))
                    break
            # If no plain text part, try HTML to text conversion
            if not body:
                for part in message['payload']['parts']:
                    if part['mimeType'] == 'text/html':
                        html_body = self._decode_base64_text(part['body'].get('data', ''))
                        body = self._html_to_text(html_body)
        elif 'payload' in message and 'body' in message['payload']:
            # For simple messages without parts
            body = self._decode_base64_text(message['payload']['body'].get('data', ''))

        return body

    def _html_to_text(self, html: str) -> str:
        """
        Convert HTML to plain text.

        Args:
            html: HTML string to convert.

        Returns:
            str: Plain text version of HTML.
        """
        import re
        # Remove HTML tags
        clean_text = re.sub(r'<[^>]+>', '', html)
        # Convert some common HTML entities
        clean_text = clean_text.replace('&nbsp;', ' ')
        clean_text = clean_text.replace('&amp;', '&')
        clean_text = clean_text.replace('&lt;', '<')
        clean_text = clean_text.replace('&gt;', '>')
        clean_text = clean_text.replace('&quot;', '"')
        clean_text = clean_text.replace('&#39;', "'")

        # Normalize whitespace
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()

        return clean_text

    def _get_email_headers(self, message: Dict[str, Any]) -> Dict[str, str]:
        """
        Extract email headers such as subject, from, date.

        Args:
            message: Gmail API message object.

        Returns:
            Dict[str, str]: Dictionary of email headers.
        """
        headers = {}

        if 'payload' in message and 'headers' in message['payload']:
            for header in message['payload']['headers']:
                name = header.get('name', '').lower()
                if name in ['subject', 'from', 'date', 'to']:
                    headers[name] = header.get('value', '')

        return headers

    def _create_email_content(self, headers: Dict[str, str], body: str) -> str:
        """
        Create the content to save in the text file.

        Args:
            headers: Email headers.
            body: Email body.

        Returns:
            str: Formatted email content.
        """
        content = f"From: {headers.get('from', 'Unknown')}\n"
        content += f"To: {headers.get('to', 'Unknown')}\n"
        content += f"Date: {headers.get('date', 'Unknown')}\n"
        content += f"Subject: {headers.get('subject', 'No Subject')}\n"
        content += f"---\n\n"
        content += body if body else "No body content found."
        content += "\n\n---\nEmail processed by GmailWatcher on " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return content

    def _mark_email_as_read(self, message_id: str) -> bool:
        """
        Mark an email as read by removing the UNREAD label.

        Args:
            message_id: ID of the message to mark as read.

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={
                    'removeLabelIds': ['UNREAD']
                }
            ).execute()
            return True
        except HttpError as e:
            print(f"Error marking email {message_id} as read: {e}")
            return False

    def fetch_unread_emails(self) -> List[Dict[str, Any]]:
        """
        Fetch unread emails from Gmail.

        Returns:
            List[Dict]: List of unread email messages.
        """
        try:
            # Get list of unread message IDs
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread'
            ).execute()

            messages = results.get('messages', [])
            unread_emails = []

            for msg in messages:
                try:
                    # Get full message details
                    message = self.service.users().messages().get(
                        userId='me',
                        id=msg['id']
                    ).execute()

                    unread_emails.append(message)
                except HttpError as e:
                    print(f"Error fetching message {msg['id']}: {e}")
                    continue

            return unread_emails
        except HttpError as e:
            print(f"Error fetching unread emails: {e}")
            return []

    def process_email(self, message: Dict[str, Any]) -> bool:
        """
        Process a single email message.

        Args:
            message: Gmail API message object.

        Returns:
            bool: True if processing was successful, False otherwise.
        """
        try:
            # Extract headers and body
            headers = self._get_email_headers(message)
            subject = headers.get('subject', 'No Subject')

            # Extract plain text body
            body = self._extract_plain_text_body(message)

            # Create content to save
            content = self._create_email_content(headers, body)

            # Clean subject for filename
            clean_subject = self._clean_subject(subject)

            # Create filename with timestamp to avoid conflicts
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{clean_subject}_{timestamp}.txt"

            # Ensure unique filename
            counter = 1
            original_filename = filename
            while os.path.exists(os.path.join(self.vault_path, filename)):
                name_part = original_filename.replace('.txt', '')
                filename = f"{name_part}_({counter}).txt"
                counter += 1

            # Write email content to file
            file_path = os.path.join(self.vault_path, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"Saved email '{subject}' to {file_path}")

            # Mark as read
            if self._mark_email_as_read(message['id']):
                print(f"Marked email '{subject}' as read")
                return True
            else:
                print(f"Failed to mark email '{subject}' as read")
                return False

        except Exception as e:
            print(f"Error processing email: {e}")
            return False

    def process_unread_emails(self) -> int:
        """
        Process all unread emails.

        Returns:
            int: Number of emails successfully processed.
        """
        print("Fetching unread emails...")
        unread_emails = self.fetch_unread_emails()

        if not unread_emails:
            print("No unread emails found.")
            return 0

        print(f"Found {len(unread_emails)} unread emails.")
        successful_count = 0

        for i, email in enumerate(unread_emails, 1):
            print(f"Processing email {i}/{len(unread_emails)}...")
            if self.process_email(email):
                successful_count += 1

        print(f"Successfully processed {successful_count}/{len(unread_emails)} emails.")
        return successful_count

    def run(self):
        """
        Run the Gmail watcher to fetch and process unread emails.
        """
        print("Starting Gmail API Watcher...")
        try:
            processed_count = self.process_unread_emails()
            print(f"Gmail API Watcher completed. Processed {processed_count} emails.")
        except Exception as e:
            print(f"Error running Gmail API Watcher: {e}")


def main():
    """
    Main function to run the GmailWatcher.
    """
    try:
        watcher = GmailWatcher()
        watcher.run()
    except KeyboardInterrupt:
        print("\nGmail API Watcher stopped by user.")
    except Exception as e:
        print(f"Error running Gmail API Watcher: {e}")


if __name__ == "__main__":
    main()