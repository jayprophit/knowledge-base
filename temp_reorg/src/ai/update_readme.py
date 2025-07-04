#!/usr/bin/env python3
"""
Script: update_readme.py
Description: Automatically updates the README.md file with current repository structure
Author: Knowledge Base Maintainer
Date: 2025-06-30
"""

import os
import re
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/update_readme.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Constants
README_PATH = "README.md"
BACKUP_DIR = "backups/"
DIRECTORY_EMOJI_MAP = {
    "docs": "📚",
    "templates": "📋",
    "process": "🔄",
    "automation": "⚙️",
    "meta": "🔍",
    "maintenance": "🛠️",
    "assets": "🖼️",
    "scripts": "📜",
    "anthropic": "🧠",
    "mcp": "🤖",
    "backups": "💾",
    "logs": "📊"
}

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

def get_directory_structure(rootdir='.', max_depth=3, excluded_dirs=None):
    """Generate a markdown tree of the directory structure."""
    if excluded_dirs is None:
        excluded_dirs = ['.git', '__pycache__', 'venv', 'env', 'node_modules', BACKUP_DIR]
    
    lines = []
    
    for root, dirs, files in os.walk(rootdir):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in excluded_dirs]
        
        # Calculate depth
        depth = root.count(os.sep)
        if depth > max_depth:
            continue
        
        # Skip the root directory itself
        if root == '.':
            continue
        
        # Get relative path
        rel_path = root.replace('./', '')
        if rel_path.startswith('./'):
            rel_path = rel_path[2:]
        
        # Get directory name
        dirname = os.path.basename(root)
        
        # Add emoji if available
        emoji = DIRECTORY_EMOJI_MAP.get(dirname, "📁")
        
        # Add to lines
        indent = "  " * (depth - 1)
        lines.append(f"{indent}- {emoji} **{dirname}/**")
    
    return "\n".join(lines)

def get_recent_files(rootdir='.', max_files=5, excluded_dirs=None):
    """Get a list of recently modified files."""
    if excluded_dirs is None:
        excluded_dirs = ['.git', '__pycache__', 'venv', 'env', 'node_modules', BACKUP_DIR]
    
    files_with_time = []
    
    for root, dirs, files in os.walk(rootdir):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in excluded_dirs]
        
        for file in files:
            if file.endswith(('.md', '.py')):
                file_path = os.path.join(root, file)
                try:
                    mtime = os.path.getmtime(file_path)
                    files_with_time.append((file_path, mtime))
                except:
                    pass
    
    # Sort by modification time, newest first
    files_with_time.sort(key=lambda x: x[1], reverse=True)
    
    # Return formatted list of recent files
    recent_files = []
    for file_path, mtime in files_with_time[:max_files]:
        rel_path = file_path.replace('./', '')
        date = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
        recent_files.append(f"- [{rel_path}]({rel_path.replace(' ', '%20')}) - *Updated: {date}*")
    
    return "\n".join(recent_files)

def update_readme():
    """Update the README.md file with current repository information."""
    # Backup current README
    backup_file(README_PATH)
    
    # Read current README
    current_readme = read_file(README_PATH) or ""
    
    # Generate directory structure
    directory_structure = get_directory_structure()
    
    # Get recent files
    recent_files = get_recent_files()
    
    # Update directory structure section
    dir_section_pattern = r"## Directory Structure\s+```(?:.|\n)*?```"
    dir_section_replacement = "## Directory Structure\n\n" + directory_structure
    
    if re.search(dir_section_pattern, current_readme):
        updated_readme = re.sub(dir_section_pattern, dir_section_replacement, current_readme)
    else:
        # If section doesn't exist, add it
        updated_readme = current_readme + "\n\n" + dir_section_replacement
    
    # Update recent updates section
    updates_section_pattern = r"## Recent Updates\s+(?:.|\n)*?(?:\n\n|\Z)"
    updates_section_replacement = "## Recent Updates\n\n" + recent_files + "\n\n"
    
    if re.search(updates_section_pattern, updated_readme):
        updated_readme = re.sub(updates_section_pattern, updates_section_replacement, updated_readme)
    else:
        # If section doesn't exist, add it
        updated_readme = updated_readme + "\n\n" + updates_section_replacement
    
    # Add last updated timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    timestamp_pattern = r"_Last updated: .*?_"
    timestamp_replacement = f"_Last updated: {timestamp}_"
    
    if re.search(timestamp_pattern, updated_readme):
        updated_readme = re.sub(timestamp_pattern, timestamp_replacement, updated_readme)
    else:
        # If timestamp doesn't exist, add it at the end
        updated_readme = updated_readme + f"\n\n{timestamp_replacement}"
    
    # Write updated README
    success = write_file(README_PATH, updated_readme)
    
    if success:
        logger.info("README.md updated successfully")
    else:
        logger.error("Failed to update README.md")
    
    return success

def main():
    """Main function."""
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Update README
    result = update_readme()
    
    # Return appropriate exit code
    return 0 if result else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
