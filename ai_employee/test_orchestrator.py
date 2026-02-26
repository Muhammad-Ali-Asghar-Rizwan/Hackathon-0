import os
import sys
from pathlib import Path
from linkedin_poster import post_to_linkedin
# Add the current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from orchestrator import Orchestrator


def test_imports():
    """Test that all required modules can be imported."""
    try:
        import json
        import re
        from datetime import datetime
        from pathlib import Path
        from typing import Dict, List, Optional
        from email_sender import send_email
        print("+ All required modules imported successfully")
        return True
    except ImportError as e:
        print(f"- Import error: {e}")
        return False


def test_directories():
    """Test that required directories exist."""
    directories = ['Needs_Action', 'Plans', 'Pending_Approval', 'Done', 'Approved']
    all_exist = True

    for directory in directories:
        dir_exists = os.path.exists(directory)
        print(f"+ {directory} directory exists: {'Yes' if dir_exists else 'No'}")
        if not dir_exists:
            all_exist = False

    return all_exist


def test_orchestrator_initialization():
    """Test that Orchestrator class can be initialized."""
    try:
        orchestrator = Orchestrator()
        print("+ Orchestrator class initialized successfully")

        # Check if all directories exist after initialization
        expected_dirs = ['Needs_Action', 'Plans', 'Pending_Approval', 'Done', 'Approved']
        for dir_name in expected_dirs:
            dir_path = Path(dir_name)
            if dir_path.exists():
                print(f"  + {dir_name} directory confirmed to exist")
            else:
                print(f"  - {dir_name} directory not found")

        return True
    except Exception as e:
        print(f"- Orchestrator initialization error: {e}")
        return False


def test_dashboard():
    """Test that Dashboard.md can be created/accessed."""
    try:
        # Initialize orchestrator to ensure dashboard path is set
        orchestrator = Orchestrator()

        # Test updating the dashboard
        orchestrator._update_dashboard("Test Action", "Test details")

        dashboard_exists = os.path.exists('Dashboard.md')
        print(f"+ Dashboard.md exists: {'Yes' if dashboard_exists else 'No'}")

        return True
    except Exception as e:
        print(f"- Dashboard test error: {e}")
        return False





def main():
    """Run basic tests for the orchestrator."""
    print("Testing Orchestrator Setup")
    print("=" * 30)

    all_tests_passed = True

    print("1. Testing imports...")
    if not test_imports():
        all_tests_passed = False

    print("\n2. Testing required directories...")
    if not test_directories():
        all_tests_passed = False

    print("\n3. Testing orchestrator initialization...")
    if not test_orchestrator_initialization():
        all_tests_passed = False

    print("\n4. Testing dashboard functionality...")
    if not test_dashboard():
        all_tests_passed = False

    print("\n" + "=" * 30)
    if all_tests_passed:
        print("+ All basic tests passed! Orchestrator is ready.")
        print("\nTo run the orchestrator, use:")
        print("python orchestrator.py")
    else:
        print("- Some tests failed. Please check the error messages above.")
    print("=" * 30)


if __name__ == "__main__":
    main()