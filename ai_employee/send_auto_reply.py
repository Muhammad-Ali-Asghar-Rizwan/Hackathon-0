import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_auto_reply(service, to_email, original_subject):
    """
    Sends an auto-reply email to the sender of an incoming email.

    Args:
        service: Gmail API service object
        to_email: Email address of the sender to reply to
        original_subject: Subject of the original email
    """
    # Create the reply subject with "Re:" prefix
    reply_subject = f"Re: {original_subject}"

    # Create the reply body
    reply_body = f"Hello! This is an automated reply to your email regarding '{original_subject}'."

    # Create a MIME message
    message = MIMEMultipart()
    message['to'] = to_email
    message['subject'] = reply_subject

    # Add the body to the message
    message.attach(MIMEText(reply_body, 'plain'))

    # Encode the message in base64
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

    # Send the email using Gmail API
    sent_message = service.users().messages().send(
        userId='me',
        body={
            'raw': raw_message
        }
    ).execute()

    return sent_message