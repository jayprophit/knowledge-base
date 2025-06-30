#!/usr/bin/env python3
"""
Script: auto_update_docs.py
Description: Automatically updates README.md and changelog.md in one script
Author: Knowledge Base Maintainer
Date: 2025-06-30
"""

import os
import sys
import logging
import subprocess
from datetime import datetime, timedelta

# Add the scripts directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the individual update scripts
import update_readme
import update_changelog

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/auto_update_docs.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_git_command(command, cwd=None):
    """Run a git command and return the output."""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            cwd=cwd
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logger.error(f"Git command failed: {e}")
        return None

def commit_changes():
    """Commit changes to README.md and changelog.md if they've been modified."""
    # Check if files have been modified
    status = run_git_command(["git", "status", "--porcelain", "README.md", "changelog.md"])
    
    if not status:
        logger.info("No changes to commit")
        return True
    
    try:
        # Add the files
        run_git_command(["git", "add", "README.md", "changelog.md"])
        
        # Commit the changes
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        run_git_command(["git", "commit", "-m", f"Auto-update docs: {timestamp}"])
        
        logger.info("Changes committed successfully")
        return True
    except Exception as e:
        logger.error(f"Error committing changes: {str(e)}")
        return False

def push_changes():
    """Push committed changes to the remote repository."""
    try:
        run_git_command(["git", "push"])
        logger.info("Changes pushed successfully")
        return True
    except Exception as e:
        logger.error(f"Error pushing changes: {str(e)}")
        return False

def main():
    """Main function."""
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Update README
    logger.info("Updating README.md...")
    readme_result = update_readme.update_readme()
    
    # Update changelog
    logger.info("Updating changelog.md...")
    changelog_result = update_changelog.update_changelog()
    
    # Commit and push changes if requested
    if len(sys.argv) > 1 and sys.argv[1].lower() == '--commit':
        if readme_result or changelog_result:
            commit_result = commit_changes()
            if commit_result and len(sys.argv) > 2 and sys.argv[2].lower() == '--push':
                push_changes()
    
    # Return appropriate exit code
    return 0 if (readme_result and changelog_result) else 1

if __name__ == "__main__":
    print("Starting automatic documentation update...")
    exit_code = main()
    print(f"Documentation update completed with exit code: {exit_code}")
    sys.exit(exit_code)
