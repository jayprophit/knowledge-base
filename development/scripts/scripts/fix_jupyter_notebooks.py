#!/usr/bin/env python3
"""
Jupyter Notebook Fixer

This script fixes malformed Jupyter notebook files by ensuring they have valid JSON structure.
It checks for missing closing brackets/braces and adds them as needed.
"""

import os
import json
import sys
from pathlib import Path


def fix_notebook(notebook_path):
    """
    Fix a potentially malformed Jupyter notebook by ensuring it has valid JSON structure.
    
    Args:
        notebook_path: Path to the notebook file
    
    Returns:
        bool: True if fixed, False if no fix needed or couldn't fix
    """
    try:
        # Try to load as JSON first to check if it's already valid
        with open(notebook_path, 'r', encoding='utf-8') as f:
            content = f.read()
            try:
                json.loads(content)
                print(f"Notebook {notebook_path} is already valid JSON. No fix needed.")
                return False
            except json.JSONDecodeError as e:
                print(f"Found JSON error in {notebook_path}: {e}")
                
                # Create a backup of the original file
                backup_path = f"{notebook_path}.bak"
                with open(backup_path, 'w', encoding='utf-8') as backup:
                    backup.write(content)
                print(f"Created backup at {backup_path}")
                
                # Simple fix: Count opening and closing braces/brackets
                open_braces = content.count('{')
                close_braces = content.count('}')
                open_brackets = content.count('[')
                close_brackets = content.count(']')
                
                # Add missing closing structures
                fixed_content = content
                
                # Add missing closing brackets
                if close_brackets < open_brackets:
                    missing_brackets = open_brackets - close_brackets
                    print(f"Adding {missing_brackets} missing closing brackets ']'")
                    fixed_content += ']' * missing_brackets
                
                # Add missing closing braces
                if close_braces < open_braces:
                    missing_braces = open_braces - close_braces
                    print(f"Adding {missing_braces} missing closing braces '}}'")
                    fixed_content += '}' * missing_braces
                    
                # Validate the fixed content
                try:
                    json.loads(fixed_content)
                    # Write the fixed content
                    with open(notebook_path, 'w', encoding='utf-8') as f:
                        f.write(fixed_content)
                    print(f"Successfully fixed {notebook_path}")
                    return True
                except json.JSONDecodeError as e2:
                    print(f"Couldn't automatically fix JSON structure: {e2}")
                    print(f"Original file preserved, see backup for attempts.")
                    # Restore the original file
                    with open(notebook_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    return False
                
    except Exception as e:
        print(f"Error processing {notebook_path}: {e}")
        return False


def find_and_fix_notebooks(directory):
    """
    Find all Jupyter notebook files in the directory and fix them if needed.
    
    Args:
        directory: Root directory to search
    
    Returns:
        tuple: (fixed_count, total_count)
    """
    fixed_count = 0
    total_count = 0
    
    for path in Path(directory).rglob("*.ipynb"):
        total_count += 1
        print(f"Checking {path}...")
        if fix_notebook(path):
            fixed_count += 1
    
    return fixed_count, total_count


if __name__ == "__main__":
    if len(sys.argv) > 1:
        directory = sys.argv[1]
    else:
        directory = os.getcwd()
    
    print(f"Searching for Jupyter notebooks in {directory}...")
    fixed, total = find_and_fix_notebooks(directory)
    
    print(f"\nSummary: Fixed {fixed} out of {total} notebooks")
    if fixed > 0:
        print("Successfully fixed notebooks with proper JSON structure.")
