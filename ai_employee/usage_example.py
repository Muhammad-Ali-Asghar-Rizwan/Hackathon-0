#!/usr/bin/env python3
"""
Usage example for Gmail API Watcher
"""

import os
import sys
from pathlib import Path

# Add the current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from gmail_api_watcher import GmailWatcher


def usage_example():
    """Example of how to use the GmailWatcher class."""

    print("Gmail API Watcher - Usage Example")
    print("=" * 40)

    print("\n1. Initialize GmailWatcher with default settings:")
    print("   watcher = GmailWatcher()")

    print("\n2. Or initialize with a custom client secret path:")
    print("   watcher = GmailWatcher('path/to/your/client_secret.json')")

    print("\n3. Process all unread emails:")
    print("   watcher.process_unread_emails()")

    print("\n4. Run the complete watch cycle:")
    print("   watcher.run()")

    print("\nNote: On first run, the script will open a browser for OAuth authentication.")
    print("After successful authentication, credentials will be saved to token.json")
    print("for future use, and the script will fetch and process unread emails.")

    print("\n" + "=" * 40)
    print("To run the Gmail Watcher now, execute:")
    print("python gmail_api_watcher.py")


def main():
    """Main function."""
    usage_example()


if __name__ == "__main__":
    main()