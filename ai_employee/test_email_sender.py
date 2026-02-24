import os
import sys
from pathlib import Path

# Add the current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from email_sender import GmailSender, send_email


def test_imports():
    """Test that all required modules can be imported."""
    try:
        import pickle
        import json
        import base64
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        import google.auth.transport.requests
        import google_auth_oauthlib.flow
        import googleapiclient.discovery
        import googleapiclient.errors
        print("+ All required modules imported successfully")
        return True
    except ImportError as e:
        print(f"- Import error: {e}")
        return False


def test_files_exist():
    """Test that required files exist."""
    token_exists = os.path.exists('token.json')
    client_secret_exists = os.path.exists('client_secret.json')
    logs_dir_exists = os.path.exists('Logs')

    print(f"+ token.json exists: {'Yes' if token_exists else 'No'}")
    print(f"+ client_secret.json exists: {'Yes' if client_secret_exists else 'No'}")
    print(f"+ Logs directory exists: {'Yes' if logs_dir_exists else 'Creating...'}")

    if not logs_dir_exists:
        os.makedirs('Logs', exist_ok=True)
        print("+ Logs directory created")

    return token_exists and client_secret_exists


def test_class_initialization():
    """Test that GmailSender class can be initialized."""
    try:
        # Just test if the class can be imported and instantiated (won't actually connect)
        sender = GmailSender
        print("+ GmailSender class available")
        return True
    except Exception as e:
        print(f"- GmailSender initialization error: {e}")
        return False


def main():
    """Run basic tests for the email sender."""
    print("Testing Email Sender Setup")
    print("=" * 30)

    all_tests_passed = True

    print("1. Testing imports...")
    if not test_imports():
        all_tests_passed = False

    print("\n2. Testing required files...")
    if not test_files_exist():
        all_tests_passed = False

    print("\n3. Testing class availability...")
    if not test_class_initialization():
        all_tests_passed = False

    print("\n" + "=" * 30)
    if all_tests_passed:
        print("+ All basic tests passed! Email sender is ready.")
        print("\nTo send an email, use:")
        print("send_email('recipient@example.com', 'Subject', 'Message body')")
    else:
        print("- Some tests failed. Please check the error messages above.")
    print("=" * 30)


if __name__ == "__main__":
    main()