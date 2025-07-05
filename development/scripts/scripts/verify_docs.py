#!/usr/bin/env python3
"""
Documentation verification script.
Checks for broken links, missing files, and documentation structure issues.
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Configuration
DOCS_DIR = Path(__file__).parent.parent
MAIN_DOCS = [
    'README.md',
    'ARCHITECTURE.md',
    'CHANGELOG.md',
    'CODE_OF_CONDUCT.md',
    'CONTRIBUTING.md',
    'FAQ.md',
    'GOVERNANCE.md',
    'MEMORIES.md',
    'METHOD.md',
    'PLAN.md',
    'ROLLBACK.md',
    'SECURITY.md',
    'SUPPORT.md',
    'SYSTEM_DESIGN.md',
    'TROUBLESHOOTING.md'
]

class DocLink:
    def __init__(self, file_path: str, line_num: int, link_text: str, link_target: str):
        self.file_path = file_path
        self.line_num = line_num
        self.link_text = link_text
        self.link_target = link_target

    def __str__(self) -> str:
        return f"{self.file_path}:{self.line_num} - [{self.link_text}]({self.link_target})"

def find_markdown_files(directory: Path) -> List[Path]:
    """Find all markdown files in the given directory."""
    return list(directory.glob('**/*.md'))

def extract_links(file_path: Path) -> List[DocLink]:
    """Extract all markdown links from a file."""
    links = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            # Match markdown links [text](url)
            for match in re.finditer(r'\[([^\]]+)\]\(([^)]+)\)', line):
                link_text = match.group(1)
                link_target = match.group(2)
                links.append(DocLink(
                    str(file_path),
                    line_num,
                    link_text,
                    link_target
                ))
    return links

def verify_links(links: List[DocLink]) -> Tuple[List[DocLink], List[DocLink]]:
    """Verify that all links point to existing files or anchors."""
    broken_links = []
    valid_links = []
    
    for link in links:
        # Skip external links
        if link.link_target.startswith(('http://', 'https://', 'mailto:')):
            valid_links.append(link)
            continue
            
        # Handle anchor links
        if '#' in link.link_target:
            file_part, anchor = link.link_target.split('#', 1)
            if not file_part:  # Same-file anchor
                file_part = os.path.basename(link.file_path)
        else:
            file_part = link.link_target
            anchor = None
            
        # Check if file exists
        file_path = os.path.join(os.path.dirname(link.file_path), file_part)
        if not os.path.exists(file_path):
            broken_links.append(link)
            continue
            
        # If there's an anchor, check if it exists in the file
        if anchor:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().lower()
                # Simple check for heading with the same text
                if f'# {anchor.lower().replace("-", " ")}' not in content:
                    broken_links.append(link)
                    continue
                    
        valid_links.append(link)
        
    return valid_links, broken_links

def check_documentation_structure() -> bool:
    """Check the overall documentation structure."""
    success = True
    
    # Check for missing main documentation files
    for doc_file in MAIN_DOCS:
        if not os.path.exists(os.path.join(DOCS_DIR, doc_file)):
            print(f"❌ Missing documentation file: {doc_file}")
            success = False
    
    # Check for broken links in all markdown files
    markdown_files = find_markdown_files(DOCS_DIR)
    all_links = []
    
    for md_file in markdown_files:
        all_links.extend(extract_links(md_file))
    
    valid_links, broken_links = verify_links(all_links)
    
    if broken_links:
        print("\n❌ Found broken links:")
        for link in broken_links:
            print(f"  - {link}")
        success = False
    
    # Check for orphaned files (files not linked from anywhere)
    linked_files = set()
    for link in valid_links:
        if not link.link_target.startswith(('http://', 'https://', 'mailto:')):
            linked_files.add(os.path.normpath(os.path.join(os.path.dirname(link.file_path), link.link_target)))
    
    orphaned_files = []
    for md_file in markdown_files:
        if str(md_file.resolve()) not in linked_files and md_file.name != 'README.md':
            orphaned_files.append(str(md_file))
    
    if orphaned_files:
        print("\n⚠️  Found potentially orphaned files (not linked from anywhere):")
        for file_path in orphaned_files:
            print(f"  - {file_path}")
    
    return success

def main() -> int:
    print("🔍 Verifying documentation structure...\n")
    
    if not check_documentation_structure():
        print("\n❌ Documentation verification failed.")
        return 1
    
    print("\n✅ Documentation verification passed!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
