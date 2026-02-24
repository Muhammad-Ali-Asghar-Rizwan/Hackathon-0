# Gmail API Watcher

A production-ready Python script that monitors Gmail inbox and processes unread emails using the Gmail API.

## Features

- Uses Gmail API with OAuth authentication
- Loads credentials from `client_secret.json`
- Saves token to `token.json` after first authentication
- Automatically refreshes expired tokens
- Fetches unread emails
- Extracts subject and plain text body
- Saves each email as a .txt file in the `Needs_Action` folder
- Names files based on email subject
- Marks emails as read after processing
- Uses python-dotenv to load VAULT_PATH
- Proper error handling

## Prerequisites

1. Google Account with Gmail enabled
2. Google Cloud Project with Gmail API enabled
3. OAuth 2.0 credentials (client_secret.json)

## Setup

### 1. Enable Gmail API

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Gmail API
4. Create credentials (OAuth 2.0 Client IDs)
5. Download the credentials file and rename it to `client_secret.json`

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Create a `.env` file in the project root with the following content:

```
VAULT_PATH=Needs_Action
```

### 4. Run the Script

```bash
python gmail_api_watcher.py
```

On first run, the script will open a browser window for OAuth authentication. After successful authentication, it will save the credentials to `token.json` for future use.

## Usage

The script will:

1. Connect to your Gmail account using OAuth
2. Fetch all unread emails
3. Extract the subject and plain text body from each email
4. Save each email as a .txt file in the `Needs_Action` folder
5. Mark the email as read in Gmail

## File Naming

Email files are named based on the subject line with the following format:
```
{cleaned_subject}_{timestamp}.txt
```

If a file with the same name already exists, the script will append a counter to ensure uniqueness:
```
{cleaned_subject}_{timestamp}_(1).txt
```

## Error Handling

The script includes comprehensive error handling for:
- Authentication failures
- Network errors
- File system errors
- Gmail API errors

## Security

- Credentials are stored locally in `token.json`
- OAuth tokens are automatically refreshed
- All sensitive data is handled securely through Google's authentication system

## Folder Structure

```
project/
├── gmail_api_watcher.py
├── email_sender.py
├── requirements.txt
├── .env
├── client_secret.json (your credentials)
├── token.json (generated after first run)
├── Needs_Action/ (default output folder for watcher)
├── Logs/ (output folder for email logs)
└── test_email_sender.py (test script)
```

## Authentication Notes

The email sender requires the `https://www.googleapis.com/auth/gmail.send` scope.
If your existing `token.json` was created with different scopes, you may need to re-authenticate.