#!/usr/bin/env python3
"""
Script: sync_brain_plan.py
Description: Synchronizes the brain plan with the knowledge base plan
Author: Knowledge Base Maintainer
Date: 2025-06-30
"""

import os
import re
import argparse
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/sync_brain_plan.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
CONFIG = {
    'brain_plan_path': os.environ.get('BRAIN_PLAN_PATH', 'c:/Users/jpowe/.codeium/windsurf/brain/336ae3cb-b35b-448d-9568-57688ea99ee5/plan.md'),
    'kb_plan_path': 'plan.md',
    'backup_dir': 'backups/',
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
        os.makedirs(CONFIG['backup_dir'], exist_ok=True)
        
        # Create backup filename with timestamp
        filename = os.path.basename(filepath)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(CONFIG['backup_dir'], f"{filename}.{timestamp}")
        
        # Copy the file
        content = read_file(filepath)
        write_file(backup_path, content)
        
        logger.info(f"Backup created: {backup_path}")
        return True
    except Exception as e:
        logger.error(f"Error backing up file {filepath}: {str(e)}")
        return False

def sync_plans():
    """Synchronize the brain plan with the knowledge base plan."""
    # Read the brain plan
    brain_plan = read_file(CONFIG['brain_plan_path'])
    if brain_plan is None:
        logger.error("Could not read brain plan")
        return False
    
    # Read the knowledge base plan
    kb_plan = read_file(CONFIG['kb_plan_path'])
    if kb_plan is None:
        logger.warning("Could not read knowledge base plan - creating new one")
        kb_plan = "# Knowledge Base Plan\n\n"
    
    # Backup the knowledge base plan
    backup_file(CONFIG['kb_plan_path'])
    
    # Update the knowledge base plan with the brain plan content
    write_file(CONFIG['kb_plan_path'], brain_plan)
    
    logger.info("Plan synchronization completed successfully")
    return True

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Synchronize brain plan with knowledge base plan')
    parser.add_argument('--brain-plan', type=str, help='Path to the brain plan')
    parser.add_argument('--kb-plan', type=str, help='Path to the knowledge base plan')
    return parser.parse_args()

def main():
    """Main function."""
    args = parse_args()
    
    # Update configuration with command line arguments
    if args.brain_plan:
        CONFIG['brain_plan_path'] = args.brain_plan
    if args.kb_plan:
        CONFIG['kb_plan_path'] = args.kb_plan
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Perform synchronization
    result = sync_plans()
    
    # Return appropriate exit code
    return 0 if result else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
