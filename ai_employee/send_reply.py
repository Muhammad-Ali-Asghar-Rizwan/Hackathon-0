import os
import base64
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def _create_message(sender, to, subject, body):
    """
    Create a message for sending via Gmail API
    """
    try:
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        if sender:
            message['from'] = sender

        # Encode the message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        return {'raw': raw_message}

    except Exception as e:
        print(f"Error creating message: {str(e)}")
        raise


def send_email_to_address(to_email, subject, body, token_file='token.json', credentials_file='client_secret.json'):
    """
    Send an email to a specific address using Gmail API
    """
    # Scopes for sending emails - include profile scope for getting user info
    scopes = [
        # 'https://www.googleapis.com/auth/gmail.send',
        # 'https://www.googleapis.com/auth/userinfo.email',
        # 'https://www.googleapis.com/auth/userinfo.profile'
          'https://www.googleapis.com/auth/gmail.readonly',
          'https://www.googleapis.com/auth/gmail.modify',
          'https://www.googleapis.com/auth/gmail.send'
    ]

    creds = None

    # Check if token file exists and is valid
    if os.path.exists(token_file):
        try:
            creds = Credentials.from_authorized_user_file(token_file, scopes)
        except Exception as e:
            print(f"Invalid or corrupted token file: {e}")
            print("Deleting corrupted token file...")
            os.remove(token_file)

    # If there are no valid credentials, request authorization
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Failed to refresh credentials: {e}")
                # If refresh fails, try to get new credentials
                if os.path.exists(credentials_file):
                    flow = InstalledAppFlow.from_client_secrets_file(
                        credentials_file, scopes
                    )
                    creds = flow.run_local_server(port=0)
                else:
                    raise FileNotFoundError(
                        f"Credentials file {credentials_file} not found. "
                        f"Please set up OAuth2 credentials for Gmail API."
                    )
        else:
            if os.path.exists(credentials_file):
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_file, scopes
                )
                creds = flow.run_local_server(port=0)
            else:
                raise FileNotFoundError(
                    f"Credentials file {credentials_file} not found. "
                    f"Please set up OAuth2 credentials for Gmail API."
                )

        # Save the credentials for the next run
        with open(token_file, 'w') as token:
            token.write(creds.to_json())
        print("New token file created successfully.")

    # Build the Gmail API service
    service = build('gmail', 'v1', credentials=creds)

    try:
        # Get the authenticated user's email
        profile = service.users().getProfile(userId='me').execute()
        sender_email = profile.get('emailAddress', 'me')

        # Create the email message
        message = _create_message(sender_email, to_email, subject, body)

        # Send the email
        result = service.users().messages().send(
            userId='me',
            body=message
        ).execute()

        print(f"Email sent successfully to {to_email}")
        print(f"Message ID: {result['id']}")
        return True

    except HttpError as error:
        print(f"HTTP error occurred while sending email: {error}")
        return False
    except Exception as e:
        print(f"Error sending email to {to_email}: {str(e)}")
        return False


def main():
    """
    Send a reply to mahabrizwan@gmail.com
    """
    to_email = "mahabrizwan@gmail.com"
    subject = "Re: Your Recent Email"
    body = """Hello,

Thank you for your email. This is an automated response from my AI system.
I will review your message shortly.

Best regards,
Ali"""

    success = send_email_to_address(to_email, subject, body)

    if success:
        print("Auto-reply sent successfully to mahabrizwan@gmail.com")
    else:
        print("Failed to send auto-reply to mahabrizwan@gmail.com")


if __name__ == "__main__":
    main()