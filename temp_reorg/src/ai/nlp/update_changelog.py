#!/usr/bin/env python3
"""
Script: update_changelog.py
Description: Automatically updates the changelog.md file with recent git changes
Author: Knowledge Base Maintainer
Date: 2025-06-30
"""

import os
import re
import logging
import subprocess
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/update_changelog.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Constants
CHANGELOG_PATH = "changelog.md"
BACKUP_DIR = "backups/"
DATE_FORMAT = "%Y-%m-%d"
CHANGELOG_HEADER = """# Changelog

All notable changes to the Knowledge Base will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

"""

def read_file(filepath):
    """Read the content of a file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        logger.error(f"Error reading file {filepath}: {str(e)}")
        return None

def write_file(filepath, content):
    """Write content to a file."""
    try:
        # Create directories if they don't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(content)
        return True
    except Exception as e:
        logger.error(f"Error writing file {filepath}: {str(e)}")
        return False

def backup_file(filepath):
    """Create a backup of the file."""
    if not os.path.exists(filepath):
        logger.warning(f"Cannot backup non-existent file: {filepath}")
        return False
    
    try:
        # Create backup directory if it doesn't exist
        os.makedirs(BACKUP_DIR, exist_ok=True)
        
        # Create backup filename with timestamp
        filename = os.path.basename(filepath)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(BACKUP_DIR, f"{filename}.{timestamp}")
        
        # Copy the file
        content = read_file(filepath)
        write_file(backup_path, content)
        
        logger.info(f"Backup created: {backup_path}")
        return True
    except Exception as e:
        logger.error(f"Error backing up file {filepath}: {str(e)}")
        return False

def run_git_command(command):
    """Run a git command and return the output."""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logger.error(f"Git command failed: {e}")
        return None

def get_recent_commits(days=7):
    """Get commits from the last X days."""
    date_since = datetime.now() - datetime.timedelta(days=days)
    date_str = date_since.strftime(DATE_FORMAT)
    
    command = [
        "git", "log", f"--since={date_str}", 
        "--pretty=format:%ad | %an | %s", "--date=short"
    ]
    
    return run_git_command(command)

def get_changed_files_since(date):
    """Get files that have changed since the specified date."""
    command = [
        "git", "diff", "--name-only", f"--since={date}"
    ]
    
    return run_git_command(command)

def categorize_changes(files):
    """Categorize changed files based on their type and location."""
    categories = {
        "Added": [],
        "Modified": [],
        "Documentation": [],
        "Automation": [],
        "Templates": [],
        "Structure": []
    }
    
    # Check if files exist currently
    for file in files.split('\n'):
        if not file:
            continue
        
        # Determine the category based on the file path and extension
        if file.endswith('.md'):
            if file.startswith('docs/'):
                categories["Documentation"].append(file)
            elif file.startswith('templates/'):
                categories["Templates"].append(file)
            else:
                categories["Documentation"].append(file)
        elif file.endswith('.py') or file.endswith('.sh') or file.endswith('.bat'):
            categories["Automation"].append(file)
        elif '/' in file and not os.path.exists(file):
            # This might be a deletion or rename, but we'll list as modified
            categories["Modified"].append(file)
        elif not os.path.exists(file):
            # New file that doesn't exist in repo yet
            categories["Added"].append(file)
        elif os.path.isdir(file):
            categories["Structure"].append(file)
        else:
            # Default to Modified
            categories["Modified"].append(file)
    
    return categories

def generate_changelog_entry(date=None):
    """Generate a changelog entry for changes since the given date."""
    if date is None:
        # Default to 7 days ago
        date = (datetime.now() - datetime.timedelta(days=7)).strftime(DATE_FORMAT)
    
    # Get changed files
    changed_files = get_changed_files_since(date)
    if not changed_files:
        logger.info(f"No files changed since {date}")
        return None
    
    # Categorize changes
    categories = categorize_changes(changed_files)
    
    # Format the entry
    today = datetime.now().strftime(DATE_FORMAT)
    entry = f"## [{today}]\n\n"
    
    for category, files in categories.items():
        if not files:
            continue
        
        entry += f"### {category}\n\n"
        for file in files:
            entry += f"- {file}\n"
        entry += "\n"
    
    return entry

def update_changelog():
    """Update the changelog file with recent changes."""
    # Backup current changelog
    if os.path.exists(CHANGELOG_PATH):
        backup_file(CHANGELOG_PATH)
    
    # Read current changelog
    current_changelog = read_file(CHANGELOG_PATH)
    
    # If changelog doesn't exist, create it
    if not current_changelog:
        current_changelog = CHANGELOG_HEADER
    
    # Generate new changelog entry
    new_entry = generate_changelog_entry()
    if not new_entry:
        logger.info("No new changes to add to changelog")
        return True
    
    # Find the position to insert the new entry (after the header, before the first entry)
    header_end = current_changelog.find("## [")
    if header_end == -1:
        # No existing entries, add after the header
        updated_changelog = current_changelog + "\n" + new_entry
    else:
        # Insert before the first entry
        updated_changelog = current_changelog[:header_end] + new_entry + current_changelog[header_end:]
    
    # Write updated changelog
    success = write_file(CHANGELOG_PATH, updated_changelog)
    
    if success:
        logger.info("changelog.md updated successfully")
    else:
        logger.error("Failed to update changelog.md")
    
    return success

def main():
    """Main function."""
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Update changelog
    result = update_changelog()
    
    # Return appropriate exit code
    return 0 if result else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
