"""
Repository Cleanup Script
========================

This script removes temporary and utility files that have completed their purpose,
including fixer scripts, PowerShell scripts, and other temporary files.
"""

import os
import sys
import shutil
from pathlib import Path

# Constants
REPO_ROOT = Path(__file__).parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"

# Files to keep (essential files that shouldn't be removed)
ESSENTIAL_SCRIPTS = [
    "cleanup_temp_files.py",  # This script
    "validate_docs.py",       # Main validation script
    "__init__.py",            # Package indicators
    "README.md",              # Documentation
    "requirements.txt",       # Dependencies
]

def list_files_to_remove():
    """List all temporary files that can be removed."""
    to_remove = []
    
    # Find PowerShell scripts
    ps1_files = []
    for root, _, files in os.walk(REPO_ROOT):
        for file in files:
            if file.endswith('.ps1'):
                ps1_files.append(os.path.join(root, file))
    
    # Find fixer scripts in scripts directory
    fixer_scripts = []
    for file in os.listdir(SCRIPTS_DIR):
        if (file.endswith('.py') and 
            ('fix' in file.lower() or 
             'patch' in file.lower() or 
             'clean' in file.lower()) and 
            file not in ESSENTIAL_SCRIPTS):
            fixer_scripts.append(os.path.join(SCRIPTS_DIR, file))
    
    # Find temporary report files
    temp_reports = []
    for file in os.listdir(REPO_ROOT):
        if (file.endswith('.md') and 
            ('report' in file.lower() or 
             'log' in file.lower() or 
             'temp' in file.lower()) and
            file != "README.md" and
            file != "PROJECT_SUMMARY.md" and
            file != "PRODUCTION_READINESS_REPORT.md" and
            file != "checklist.md"):
            temp_reports.append(os.path.join(REPO_ROOT, file))
    
    # Combine all lists
    to_remove = ps1_files + fixer_scripts + temp_reports
    
    return to_remove

def remove_files(file_list):
    """Remove files from the given list and log the results."""
    removed = []
    errors = []
    
    for file_path in file_list:
        try:
            os.remove(file_path)
            removed.append(file_path)
            print(f"Removed: {file_path}")
        except Exception as e:
            errors.append((file_path, str(e)))
            print(f"Error removing {file_path}: {e}")
    
    return removed, errors

def generate_report(removed, errors):
    """Generate a report of removed files."""
    report_content = f"""# Temporary File Cleanup Report

## Summary
- Total files removed: {len(removed)}
- Errors encountered: {len(errors)}

## Files Removed
"""
    
    for file_path in removed:
        report_content += f"- {file_path}\n"
    
    if errors:
        report_content += "\n## Errors\n"
        for file_path, error in errors:
            report_content += f"- {file_path}: {error}\n"
    
    report_path = REPO_ROOT / "cleanup_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)
    
    print(f"Report saved to {report_path}")
    return report_path

def main():
    print("Starting repository cleanup...")
    
    # List files to remove
    files_to_remove = list_files_to_remove()
    
    # Confirm with user if running interactively
    if sys.stdout.isatty():
        print(f"\nFound {len(files_to_remove)} files to remove:")
        for file in files_to_remove:
            print(f"- {file}")
        
        confirm = input("\nDo you want to proceed? (y/n): ")
        if confirm.lower() != 'y':
            print("Cleanup canceled.")
            return
    
    # Remove files
    removed, errors = remove_files(files_to_remove)
    
    # Generate report
    report_path = generate_report(removed, errors)
    
    print(f"\nCleanup complete! Removed {len(removed)} files with {len(errors)} errors.")
    print(f"See {report_path} for details.")
    
    # Return success
    return len(errors) == 0

if __name__ == "__main__":
    main()
