#!/usr/bin/env python3
"""
Update cross-links between main documentation files.
Ensures all main .md files in the root directory are properly cross-referenced.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set

# Main documentation files in the root directory
MAIN_FILES = [
    'README.md',
    'architecture.md',
    'changelog.md',
    'memories.md',
    'method.md',
    'plan.md',
    'rollback.md',
    'system_design.md',
]

# Mapping of file to its display name
FILE_NAMES = {
    'README.md': 'Project Overview',
    'architecture.md': 'System Architecture',
    'changelog.md': 'Changelog',
    'memories.md': 'System Memories',
    'method.md': 'Development Methodology',
    'plan.md': 'Implementation Plan',
    'rollback.md': 'Rollback Procedures',
    'system_design.md': 'System Design',
}

def get_existing_links(content: str) -> Set[str]:
    """Extract existing links from markdown content."""
    pattern = r'\[([^\]]+)\]\(([^)]+\.md)\)'
    return set(match[1] for match in re.findall(pattern, content))

def generate_links_section(files: List[str], current_file: str) -> str:
    """Generate a markdown section with links to other files."""
    lines = ['## Related Documentation', '']
    for file in sorted(files):
        if file != current_file:
            name = FILE_NAMES.get(file, file.replace('.md', '').replace('_', ' ').title())
            lines.append(f"- [{name}]({file})")
    return '\n'.join(lines) + '\n'

def update_file_links(filepath: str, all_files: List[str]):
    """Update a file to include links to all other main files."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Warning: {filepath} not found")
        return

    # Skip if this is a generated section
    if "## Related Documentation" in content:
        print(f"Skipping {filepath} - already has Related Documentation section")
        return

    # Add the section before any existing sections
    new_section = generate_links_section(all_files, os.path.basename(filepath))
    
    # Try to find a good place to insert the section
    insert_pos = content.find('## ')
    if insert_pos == -1:
        insert_pos = len(content)
    
    # Insert the new section
    updated_content = (
        content[:insert_pos].rstrip() + 
        '\n\n' + 
        new_section + 
        content[insert_pos:].lstrip()
    )

    # Write back the updated content
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print(f"Updated {filepath}")

def main():
    root_dir = Path(__file__).parent.parent
    os.chdir(root_dir)
    
    # Only process files that exist
    existing_files = [f for f in MAIN_FILES if os.path.exists(f)]
    
    for file in existing_files:
        update_file_links(file, existing_files)

if __name__ == "__main__":
    main()
