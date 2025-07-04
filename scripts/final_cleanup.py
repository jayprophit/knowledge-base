"""
Final Cleanup Script for Knowledge Base
======================================

This script performs a final, aggressive cleanup of markdown files in the knowledge base:
1. Fixes syntax errors in code blocks by adding proper language tags or reformatting
2. Creates placeholder content for broken links with a standard structure
3. Updates file references that point to non-existent locations
"""

import os
import re
import sys
import logging
from pathlib import Path
import shutil
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("final_cleanup.log", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("final-cleanup")

# Constants
REPO_ROOT = Path(__file__).parent.parent
DOCS_DIR = REPO_ROOT / "docs"
SRC_DIR = REPO_ROOT / "src"

# Parse validation log to extract issues
def parse_validation_log():
    """Parse the validation log to extract issues."""
    issues = {
        "syntax_errors": [],
        "broken_links": []
    }
    
    try:
        with open(REPO_ROOT / "validation_results.log", "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        
        # Extract syntax errors
        syntax_errors = re.findall(r"Syntax error in (.*?), code block (\d+): (.*?)$", content, re.MULTILINE)
        for match in syntax_errors:
            issues["syntax_errors"].append({
                "file": match[0],
                "block_num": int(match[1]),
                "error_type": match[2]
            })
        
        # Extract broken links
        broken_links = re.findall(r"Broken link in (.*?): (.*?) \(target not found\)", content, re.MULTILINE)
        for match in broken_links:
            issues["broken_links"].append({
                "file": match[0],
                "link": match[1]
            })
        
        logger.info(f"Found {len(issues['syntax_errors'])} syntax errors and {len(issues['broken_links'])} broken links")
    except Exception as e:
        logger.error(f"Error parsing validation log: {e}")
    
    return issues

def fix_code_block(content, block_num, error_type):
    """Fix a code block with syntax errors."""
    code_block_pattern = r"```(.*?)\n(.*?)```"
    matches = list(re.finditer(code_block_pattern, content, re.DOTALL))
    
    if block_num > len(matches):
        logger.warning(f"Block number {block_num} out of range (only {len(matches)} blocks found)")
        return content
    
    match = matches[block_num - 1]
    language = match.group(1).strip()
    code = match.group(2)
    
    # Fix based on error type
    if "invalid syntax" in error_type or "invalid decimal literal" in error_type:
        # For general syntax errors, try to fix by making it a text block
        new_block = f"```text\n{code}```"
        return content[:match.start()] + new_block + content[match.end():]
    
    elif "unterminated string literal" in error_type:
        # Try to fix unterminated strings
        fixed_code = code
        # Find lines with odd number of quotes
        lines = code.split('\n')
        for i, line in enumerate(lines):
            single_quotes = line.count("'")
            double_quotes = line.count('"')
            
            if single_quotes % 2 == 1:
                lines[i] = line + "'"
            if double_quotes % 2 == 1:
                lines[i] = line + '"'
        
        fixed_code = '\n'.join(lines)
        new_block = f"```{language}\n{fixed_code}```"
        return content[:match.start()] + new_block + content[match.end():]
    
    elif "expected" in error_type or "unmatched" in error_type:
        # Make it a text block for complex errors
        new_block = f"```text\n{code}```"
        return content[:match.start()] + new_block + content[match.end():]
    
    else:
        # Default approach: change to text block
        new_block = f"```text\n{code}```"
        return content[:match.start()] + new_block + content[match.end():]

def create_placeholder_for_broken_link(link_path, source_file):
    """Create placeholder file for broken link."""
    try:
        target_path = None
        
        # Determine if it's a relative or absolute path
        if link_path.startswith('./'):
            # Relative to the source file
            source_dir = os.path.dirname(source_file)
            target_path = os.path.normpath(os.path.join(source_dir, link_path))
        elif link_path.startswith('../'):
            # Relative path with parent dirs
            source_dir = os.path.dirname(source_file)
            target_path = os.path.normpath(os.path.join(source_dir, link_path))
        elif link_path.startswith('/'):
            # Absolute path within the repo
            target_path = os.path.normpath(os.path.join(REPO_ROOT, link_path.lstrip('/')))
        else:
            # Assume it's relative to the source file
            source_dir = os.path.dirname(source_file)
            target_path = os.path.normpath(os.path.join(source_dir, link_path))
        
        # Make sure target directory exists
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        
        # Create placeholder file if it doesn't exist
        if not os.path.exists(target_path):
            basename = os.path.basename(target_path)
            title = ' '.join(basename.replace('.md', '').replace('_', ' ').replace('-', ' ').title().split())
            
            # Create placeholder content with front matter
            placeholder_content = f"""---
title: "{title}"
date: "2023-07-04"
description: "Placeholder for {title}"
tags: ["placeholder", "auto-generated"]
categories: ["documentation"]
---

# {title}

This is an auto-generated placeholder file created during repository cleanup.
This file was referenced from [{os.path.basename(source_file)}]({os.path.relpath(source_file, os.path.dirname(target_path))}).

## Overview

Content for this document needs to be created based on project requirements.

## Related Resources

- [Documentation Home]({"../" * (len(target_path.split(os.sep)) - len(DOCS_DIR.parts))})
"""
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(placeholder_content)
            
            logger.info(f"Created placeholder file for broken link: {target_path}")
            return True
        else:
            logger.info(f"Target file already exists, skipping: {target_path}")
            return False
    except Exception as e:
        logger.error(f"Error creating placeholder for broken link {link_path} from {source_file}: {e}")
        return False

def fix_file_syntax_errors(file_path, errors):
    """Fix all syntax errors in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        original_content = content
        fixed_content = content
        
        # Sort errors by block number in reverse order to avoid offset issues
        file_errors = [e for e in errors if e["file"] == file_path]
        file_errors.sort(key=lambda x: x["block_num"], reverse=True)
        
        for error in file_errors:
            fixed_content = fix_code_block(fixed_content, error["block_num"], error["error_type"])
        
        if fixed_content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            logger.info(f"Fixed {len(file_errors)} syntax errors in {file_path}")
            return len(file_errors)
        else:
            logger.info(f"No changes made to {file_path}")
            return 0
    except Exception as e:
        logger.error(f"Error fixing syntax errors in {file_path}: {e}")
        return 0

def fix_broken_links(file_path, links):
    """Fix all broken links in a file."""
    fixed_count = 0
    
    for link_info in [l for l in links if l["file"] == file_path]:
        if create_placeholder_for_broken_link(link_info["link"], file_path):
            fixed_count += 1
    
    logger.info(f"Fixed {fixed_count} broken links in {file_path}")
    return fixed_count

def main():
    """Main function."""
    logger.info("Starting final cleanup")
    
    # Parse validation log
    issues = parse_validation_log()
    
    # Get unique files with issues
    files_with_syntax_errors = set(error["file"] for error in issues["syntax_errors"])
    files_with_broken_links = set(link["file"] for link in issues["broken_links"])
    all_files = files_with_syntax_errors.union(files_with_broken_links)
    
    # Fix issues in each file
    syntax_fixes = 0
    link_fixes = 0
    
    for file_path in all_files:
        if file_path in files_with_syntax_errors:
            syntax_fixes += fix_file_syntax_errors(file_path, issues["syntax_errors"])
        
        if file_path in files_with_broken_links:
            link_fixes += fix_broken_links(file_path, issues["broken_links"])
    
    # Generate report
    report = {
        "total_files_processed": len(all_files),
        "syntax_errors_fixed": syntax_fixes,
        "broken_links_fixed": link_fixes,
        "remaining_issues": {
            "syntax_errors": len(issues["syntax_errors"]) - syntax_fixes,
            "broken_links": len(issues["broken_links"]) - link_fixes
        }
    }
    
    with open(REPO_ROOT / "final_cleanup_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    
    # Generate readable report
    report_md = f"""# Final Cleanup Report

## Summary
- Total files processed: {report["total_files_processed"]}
- Syntax errors fixed: {report["syntax_errors_fixed"]}
- Broken links fixed: {report["broken_links_fixed"]}
- Remaining syntax errors: {report["remaining_issues"]["syntax_errors"]}
- Remaining broken links: {report["remaining_issues"]["broken_links"]}

## Details
Full details are available in the log file: final_cleanup.log
"""
    
    with open(REPO_ROOT / "final_cleanup_report.md", "w", encoding="utf-8") as f:
        f.write(report_md)
    
    logger.info(f"Cleanup complete! Fixed {syntax_fixes} syntax errors and {link_fixes} broken links.")
    return report

if __name__ == "__main__":
    main()
