#!/usr/bin/env python3
"""
Fix Broken Links Script

This script automatically fixes broken links in documentation files by:
1. Reading the broken-links-report.csv to identify broken links
2. Searching for the correct target files
3. Updating the links in the source files
4. Generating a report of fixed and unfixable links

Usage:
    python fix_broken_links.py [--dry-run] [--report-file REPORT_FILE]
"""

import os
import csv
import re
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Set, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# File types to check
DOC_EXTENSIONS = {'.md', '.rst', '.txt'}
CODE_EXTENSIONS = {'.py', '.js', '.java', '.cpp', '.h', '.c', '.php', '.html'}

class LinkFixer:
    """Class for fixing broken documentation links."""
    
    def __init__(self, repo_root: str, report_file: str = 'broken-links-report.csv', dry_run: bool = False):
        """Initialize the link fixer.
        
        Args:
            repo_root: Path to the repository root
            report_file: Path to the broken links report CSV
            dry_run: If True, don't make actual changes
        """
        self.repo_root = Path(repo_root)
        self.report_file = self.repo_root / report_file
        self.dry_run = dry_run
        self.file_index = {}  # Cache of files in the repository
        self.fixed_links = []
        self.unfixable_links = []
    
    def run(self) -> Tuple[List[Dict], List[Dict]]:
        """Run the link fixing process.
        
        Returns:
            Tuple of (fixed_links, unfixable_links)
        """
        # Check if report file exists
        if not self.report_file.exists():
            logger.error(f"Report file not found: {self.report_file}")
            return [], []
        
        # Build file index
        logger.info("Building file index...")
        self._build_file_index()
        
        # Read broken links report
        broken_links = self._read_broken_links_report()
        logger.info(f"Found {len(broken_links)} broken links to fix")
        
        # Fix broken links
        for link_info in broken_links:
            self._fix_link(link_info)
        
        # Print summary
        logger.info(f"Fixed {len(self.fixed_links)} links")
        logger.info(f"Could not fix {len(self.unfixable_links)} links")
        
        return self.fixed_links, self.unfixable_links
    
    def _build_file_index(self):
        """Build an index of all files in the repository."""
        for root, _, files in os.walk(self.repo_root):
            rel_root = Path(root).relative_to(self.repo_root)
            for file in files:
                path = Path(rel_root) / file
                # Store by both full path and just filename
                self.file_index[str(path).lower()] = path
                self.file_index[file.lower()] = path
        
        logger.info(f"Indexed {len(self.file_index)} files")
    
    def _read_broken_links_report(self) -> List[Dict]:
        """Read the broken links report CSV.
        
        Returns:
            List of dictionaries with broken link information
        """
        broken_links = []
        with open(self.report_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                broken_links.append({
                    'source_file': row.get('source_file', ''),
                    'line_number': int(row.get('line_number', 0)) if row.get('line_number', '').isdigit() else 0,
                    'broken_link': row.get('broken_link', ''),
                    'link_type': row.get('link_type', ''),
                    'expected_target': row.get('expected_target', '')
                })
        
        return broken_links
    
    def _find_best_target(self, expected_target: str) -> Optional[Path]:
        """Find the best target for a broken link.
        
        Args:
            expected_target: The expected target file
            
        Returns:
            Path to the best matching file or None if not found
        """
        # Try direct match
        target_lower = expected_target.lower()
        if target_lower in self.file_index:
            return self.file_index[target_lower]
        
        # Try without leading directory
        filename = Path(expected_target).name.lower()
        if filename in self.file_index:
            return self.file_index[filename]
        
        # Try fuzzy matching by extension
        ext = Path(expected_target).suffix.lower()
        if not ext and Path(expected_target).name:
            # If no extension and not empty, try common extensions
            for try_ext in ['.md', '.py', '.js', '.html', '.txt']:
                test_path = f"{expected_target}{try_ext}".lower()
                if test_path in self.file_index:
                    return self.file_index[test_path]
        
        # Try target with common doc extensions if it's a doc link
        if ext not in DOC_EXTENSIONS and Path(expected_target).name:
            for try_ext in DOC_EXTENSIONS:
                name_without_ext = Path(expected_target).with_suffix('').name
                test_path = f"{name_without_ext}{try_ext}".lower()
                if test_path in self.file_index:
                    return self.file_index[test_path]
        
        return None
    
    def _fix_link(self, link_info: Dict):
        """Fix a broken link.
        
        Args:
            link_info: Dictionary with broken link information
        """
        source_file = self.repo_root / link_info['source_file']
        if not source_file.exists():
            logger.warning(f"Source file not found: {source_file}")
            self.unfixable_links.append({**link_info, 'reason': 'Source file not found'})
            return
        
        # Find the best target
        expected_target = link_info['expected_target']
        best_target = self._find_best_target(expected_target)
        
        if not best_target:
            logger.warning(f"Could not find target for: {expected_target}")
            self.unfixable_links.append({**link_info, 'reason': 'Target not found'})
            return
        
        # Calculate relative path from source to target
        source_dir = source_file.parent
        rel_source_dir = source_dir.relative_to(self.repo_root)
        rel_target = best_target.relative_to(self.repo_root)
        
        # Make target path relative to source
        try:
            rel_path = os.path.relpath(rel_target, rel_source_dir)
            # Always use forward slashes in links
            rel_path = rel_path.replace('\\', '/')
        except ValueError:
            logger.warning(f"Could not calculate relative path from {rel_source_dir} to {rel_target}")
            self.unfixable_links.append({**link_info, 'reason': 'Could not calculate relative path'})
            return
        
        # Read the source file
        try:
            with open(source_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Error reading source file {source_file}: {e}")
            self.unfixable_links.append({**link_info, 'reason': f'Error reading source file: {e}'})
            return
        
        # Replace the broken link
        broken_link = link_info['broken_link']
        link_type = link_info['link_type']
        
        if link_type == 'markdown':
            # Format: [text](link)
            pattern = re.escape(broken_link)
            # Extract text part if it's a markdown link
            md_match = re.search(r'\[(.*?)\]\((.*?)\)', broken_link)
            if md_match:
                link_text, _ = md_match.groups()
                replacement = f"[{link_text}]({rel_path})"
            else:
                replacement = f"[{rel_target.name}]({rel_path})"
                
        elif link_type == 'html':
            # Format: <a href="link">text</a>
            pattern = re.escape(broken_link)
            # Extract text part if it's an HTML link
            html_match = re.search(r'<a\s+href="(.*?)">(.*?)</a>', broken_link, re.IGNORECASE)
            if html_match:
                _, link_text = html_match.groups()
                replacement = f'<a href="{rel_path}">{link_text}</a>'
            else:
                replacement = f'<a href="{rel_path}">{rel_target.name}</a>'
                
        elif link_type == 'import' or link_type == 'require':
            # Format: import from "path" or require("path")
            pattern = re.escape(broken_link)
            replacement = broken_link.replace(link_info['broken_link'], rel_path)
            
        else:
            # Just replace the raw link
            pattern = re.escape(broken_link)
            replacement = rel_path
        
        # Make the replacement
        new_content = re.sub(pattern, replacement, content)
        
        if content == new_content:
            logger.warning(f"No changes made to {source_file}")
            self.unfixable_links.append({**link_info, 'reason': 'No changes made'})
            return
        
        # Write the changes
        if not self.dry_run:
            try:
                with open(source_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                logger.info(f"Fixed link in {source_file}: {broken_link} -> {rel_path}")
                self.fixed_links.append({
                    **link_info, 
                    'new_link': rel_path,
                    'status': 'fixed'
                })
            except Exception as e:
                logger.error(f"Error writing to source file {source_file}: {e}")
                self.unfixable_links.append({**link_info, 'reason': f'Error writing to source file: {e}'})
        else:
            logger.info(f"[DRY RUN] Would fix link in {source_file}: {broken_link} -> {rel_path}")
            self.fixed_links.append({
                **link_info, 
                'new_link': rel_path,
                'status': 'would_fix'
            })
    
    def generate_report(self, output_file: str = "link-fixing-report.csv"):
        """Generate a report of fixed and unfixable links.
        
        Args:
            output_file: Path to the output report file
        """
        report_path = self.repo_root / output_file
        with open(report_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['source_file', 'line_number', 'broken_link', 'link_type',
                          'expected_target', 'new_link', 'status', 'reason']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for link in self.fixed_links:
                writer.writerow(link)
                
            for link in self.unfixable_links:
                writer.writerow(link)
                
        logger.info(f"Generated report at {report_path}")


def main():
    """Main function to run the script."""
    parser = argparse.ArgumentParser(description='Fix broken links in documentation.')
    parser.add_argument('--repo-root', default='.', help='Path to repository root')
    parser.add_argument('--report-file', default='broken-links-report.csv', help='Path to broken links report CSV')
    parser.add_argument('--output-file', default='link-fixing-report.csv', help='Path to output report CSV')
    parser.add_argument('--dry-run', action='store_true', help='Do not make actual changes')
    args = parser.parse_args()
    
    fixer = LinkFixer(args.repo_root, args.report_file, args.dry_run)
    fixer.run()
    fixer.generate_report(args.output_file)


if __name__ == "__main__":
    main()
