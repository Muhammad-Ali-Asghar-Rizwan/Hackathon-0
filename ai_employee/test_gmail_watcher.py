import os
import sys
from pathlib import Path

# Add the current directory to path to import gmail_api_watcher
sys.path.insert(0, str(Path(__file__).parent))

from gmail_api_watcher import GmailWatcher


def test_imports():
    """Test that all required modules can be imported."""
    try:
        import google.auth.transport.requests
        import google_auth_oauthlib.flow
        import googleapiclient.discovery
        import googleapiclient.errors
        import dotenv
        print("+ All required modules imported successfully")
        return True
    except ImportError as e:
        print(f"- Import error: {e}")
        return False


def test_environment():
    """Test that environment is properly set up."""
    vault_path = os.getenv('VAULT_PATH', 'Needs_Action')
    print(f"+ VAULT_PATH is set to: {vault_path}")

    # Check if client_secret.json exists
    if os.path.exists('client_secret.json'):
        print("+ client_secret.json found")
    else:
        print("! client_secret.json not found - this is required for Gmail API")

    return True


def test_vault_directory_creation():
    """Test that the vault directory can be created."""
    vault_path = os.getenv('VAULT_PATH', 'Needs_Action')
    vault_dir = Path(vault_path)

    try:
        vault_dir.mkdir(parents=True, exist_ok=True)
        print(f"+ Vault directory '{vault_path}' created/accessed successfully")
        return True
    except Exception as e:
        print(f"- Error creating vault directory: {e}")
        return False


def main():
    """Run basic tests to verify the setup."""
    print("Running basic tests for Gmail API Watcher...\n")

    all_tests_passed = True

    print("1. Testing imports...")
    if not test_imports():
        all_tests_passed = False

    print("\n2. Testing environment...")
    if not test_environment():
        all_tests_passed = False

    print("\n3. Testing vault directory creation...")
    if not test_vault_directory_creation():
        all_tests_passed = False

    print(f"\n{'='*50}")
    if all_tests_passed:
        print("+ All basic tests passed! The environment is ready.")
        print("\nTo run the Gmail watcher:")
        print("1. Make sure you have client_secret.json in the project directory")
        print("2. Run: python gmail_api_watcher.py")
    else:
        print("- Some tests failed. Please check the error messages above.")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()