"""
Find Duplicate Files
===================

This script identifies duplicate files in the repository based on content hash.
"""

import os
import sys
import hashlib
from pathlib import Path
from collections import defaultdict

# Constants
REPO_ROOT = Path(__file__).parent.parent
IGNORE_DIRS = ['.git', '__pycache__', 'node_modules']
IGNORE_EXTENSIONS = ['.pyc', '.pyo', '.pyd', '.git']

def get_file_hash(filepath):
    """Calculate MD5 hash of file contents."""
    h = hashlib.md5()
    try:
        with open(filepath, 'rb') as f:
            # Read in chunks for large files
            for chunk in iter(lambda: f.read(4096), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None

def find_duplicates():
    """Find duplicate files in the repository."""
    print("Scanning repository for duplicate files...")
    
    # Dictionary to store file hashes and their paths
    file_hashes = defaultdict(list)
    
    # Walk through repository
    for root, dirs, files in os.walk(REPO_ROOT):
        # Skip ignored directories
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        for filename in files:
            # Skip ignored extensions
            if any(filename.endswith(ext) for ext in IGNORE_EXTENSIONS):
                continue
            
            filepath = os.path.join(root, filename)
            file_hash = get_file_hash(filepath)
            
            if file_hash:
                file_hashes[file_hash].append(filepath)
    
    # Filter for duplicates only
    duplicates = {h: paths for h, paths in file_hashes.items() if len(paths) > 1}
    
    return duplicates

def generate_report(duplicates):
    """Generate a report of duplicate files."""
    total_duplicates = sum(len(paths) for paths in duplicates.values()) - len(duplicates)
    
    report = f"""# Duplicate Files Report

## Summary
- Total duplicate files found: {total_duplicates}
- Total sets of duplicates: {len(duplicates)}

## Details
"""
    
    if duplicates:
        for i, (file_hash, paths) in enumerate(duplicates.items(), 1):
            report += f"\n### Duplicate Set #{i}\n"
            for path in paths:
                rel_path = os.path.relpath(path, REPO_ROOT)
                report += f"- `{rel_path}`\n"
    else:
        report += "\nNo duplicate files found! The repository is already deduplicated."
    
    report_path = REPO_ROOT / "duplicate_files_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"Report saved to {report_path}")
    return report_path

def main():
    """Main function."""
    duplicates = find_duplicates()
    report_path = generate_report(duplicates)
    
    if duplicates:
        print(f"\nFound {len(duplicates)} sets of duplicate files.")
        print(f"See {report_path} for details.")
    else:
        print("\nNo duplicate files found! The repository is already deduplicated.")
    
    return len(duplicates) == 0

if __name__ == "__main__":
    main()
