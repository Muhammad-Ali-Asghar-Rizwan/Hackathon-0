# Gmail API Integration: Watcher and Sender

This document describes how the two Gmail API scripts work together in your system.

## Components

### 1. Gmail API Watcher (`gmail_api_watcher.py`)
- Monitors Gmail inbox for unread emails
- Extracts subject and body content
- Saves emails as text files in the `Needs_Action` folder
- Marks processed emails as read
- Uses OAuth with read and modify permissions

### 2. Gmail Email Sender (`email_sender.py`)
- Sends emails via Gmail API
- Logs all sent emails to the `Logs` folder as JSON files
- Uses OAuth with send permissions (plus read for profile access)
- Provides both class-based and convenience function interfaces

## Authentication

Both scripts use the same:
- `client_secret.json` for OAuth credentials
- `token.json` for authenticated session (created after first authentication)

If you run both scripts, you'll need OAuth permissions for both reading/modifying and sending emails. The recommended approach is to authenticate with broader permissions that work for both scripts.

## Usage Examples

### Watching for emails:
```python
from gmail_api_watcher import GmailWatcher
watcher = GmailWatcher()
watcher.run()  # Processes all unread emails
```

### Sending emails:
```python
from email_sender import send_email
success = send_email('recipient@example.com', 'Subject', 'Message body')
```

Or using the class interface:
```python
from email_sender import GmailSender
sender = GmailSender()
success = sender.send_email('recipient@example.com', 'Subject', 'Message body')
```

## File Structure
```
project/
├── gmail_api_watcher.py      # Watch and process incoming emails
├── email_sender.py           # Send outgoing emails
├── client_secret.json        # OAuth credentials
├── token.json                # Authenticated token (shared)
├── Needs_Action/             # Incoming email storage
├── Logs/                     # Sent email logs
├── requirements.txt          # Dependencies
└── .env                      # Environment configuration
```

## Logging

- Incoming emails are saved as `.txt` files in `Needs_Action/`
- Sent emails are logged as `.json` files in `Logs/`
- Each log entry contains timestamp, recipient, subject, body, status, and error details if applicable

## Error Handling

Both scripts implement comprehensive error handling:
- Authentication failures
- Network errors
- API errors
- File system errors
- Invalid email content