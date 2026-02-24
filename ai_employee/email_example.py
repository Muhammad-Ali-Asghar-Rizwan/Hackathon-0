#!/usr/bin/env python3
"""
Example usage of the Gmail Email Sender
"""

from email_sender import send_email, GmailSender


def example_usage():
    """Example of how to use the email sender functions."""

    print("Gmail Email Sender - Usage Examples")
    print("=" * 40)

    # Example 1: Using the convenience function
    print("\n1. Using the send_email() convenience function:")
    print("   success = send_email('recipient@example.com', 'Subject', 'Message body')")

    # Example 2: Using the GmailSender class directly
    print("\n2. Using the GmailSender class directly:")
    print("   sender = GmailSender()")
    print("   success = sender.send_email('recipient@example.com', 'Subject', 'Message body')")

    # Example 3: Sending HTML email
    print("\n3. Sending HTML email:")
    print("   success = sender.send_email('recipient@example.com', 'Subject', '<html><body>HTML content</body></html>', 'html')")

    # Example 4: Complete example with error handling
    print("\n4. Complete example with error handling:")
    print("""
    try:
        success = send_email('recipient@example.com', 'Test Subject', 'Test message')
        if success:
            print("Email sent successfully!")
        else:
            print("Failed to send email")
    except Exception as e:
        print(f"Error: {e}")
    """)

    print("\nNote: On first run, the script will use existing token.json for authentication.")
    print("If token.json is invalid or expired, it may attempt to refresh or require re-authentication.")
    print("\nThe email logs will be saved in the Logs/ directory as JSON files.")


def main():
    """Main function for the example."""
    example_usage()

    # Uncomment the lines below to actually send a test email
    # print("\n" + "="*40)
    # print("Sending test email...")
    # success = send_email("test@example.com", "Test Subject", "This is a test email.")
    # print(f"Email sent: {success}")


if __name__ == "__main__":
    main()