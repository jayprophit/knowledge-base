"""
Enhanced Duplicate File Finder
=============================

This script identifies duplicate files in the repository based on content hash,
with improved error handling and verbose output.
"""

import os
import sys
import hashlib
import traceback
from pathlib import Path
from collections import defaultdict
import time

# Constants
REPO_ROOT = Path(__file__).parent.parent
print(f"Repository root: {REPO_ROOT}")

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
    except Exception as e:
        print(f"Error hashing file {filepath}: {e}")
        return None

def find_duplicates():
    """Find duplicate files in the repository."""
    print("Scanning repository for duplicate files...")
    start_time = time.time()
    
    # Dictionary to store file hashes and their paths
    file_hashes = defaultdict(list)
    
    # Track progress
    file_count = 0
    
    try:
        # Walk through repository
        for root, dirs, files in os.walk(REPO_ROOT):
            # Skip ignored directories
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            
            print(f"Scanning directory: {root}")
            
            for filename in files:
                # Skip ignored extensions
                if any(filename.endswith(ext) for ext in IGNORE_EXTENSIONS):
                    continue
                
                filepath = os.path.join(root, filename)
                file_hash = get_file_hash(filepath)
                
                if file_hash:
                    file_hashes[file_hash].append(filepath)
                
                file_count += 1
                if file_count % 100 == 0:
                    print(f"Processed {file_count} files...")
        
        end_time = time.time()
        print(f"Finished scanning {file_count} files in {end_time - start_time:.2f} seconds")
        
        # Filter for duplicates only
        duplicates = {h: paths for h, paths in file_hashes.items() if len(paths) > 1}
        
        return duplicates
    
    except Exception as e:
        print(f"Error scanning for duplicates: {e}")
        traceback.print_exc()
        return {}

def generate_report(duplicates):
    """Generate a report of duplicate files."""
    try:
        total_duplicates = sum(len(paths) - 1 for paths in duplicates.values())
        
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
        print(f"Writing report to {report_path}")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)
        
        print(f"Report saved to {report_path}")
        return report_path
    
    except Exception as e:
        print(f"Error generating report: {e}")
        traceback.print_exc()
        
        # Try to save a simple report
        try:
            report_path = REPO_ROOT / "duplicate_files_report.md"
            with open(report_path, "w", encoding="utf-8") as f:
                f.write("# Duplicate Files Report\n\n## Error\nAn error occurred while generating the full report.\n")
            return report_path
        except Exception as e2:
            print(f"Failed to save even a simple error report: {e2}")
            return None

def main():
    """Main function."""
    try:
        print(f"Starting duplicate file search in {REPO_ROOT}...")
        
        duplicates = find_duplicates()
        report_path = generate_report(duplicates)
        
        if duplicates:
            print(f"\nFound {len(duplicates)} sets of duplicate files.")
            print(f"Total duplicate files: {sum(len(paths) - 1 for paths in duplicates.values())}")
            print(f"See {report_path} for details.")
        else:
            print("\nNo duplicate files found! The repository is already deduplicated.")
        
        return len(duplicates) == 0
    
    except Exception as e:
        print(f"Unhandled error in main: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main()
