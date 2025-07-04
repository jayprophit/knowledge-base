#!/usr/bin/env python3
"""
Updated Fix Broken Links Script

This script automatically fixes broken links in documentation files by:
1. Reading the broken-links-report.csv with the correct column format
2. Searching for the correct target files
3. Updating the links in the source files
4. Generating a report of fixed and unfixable links
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
        try:
            with open(self.report_file, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Map the actual CSV columns to the expected format
                    source_file = row.get('SourceFile', '')
                    
                    # Fix path if it uses F: drive
                    if source_file.startswith("F:"):
                        source_file = source_file.replace("F:\\github\\knowledge-base", 
                                                         str(self.repo_root))
                    
                    broken_links.append({
                        'source_file': source_file,
                        'line_number': 0,  # Not provided in the actual CSV
                        'broken_link': row.get('BrokenLink', ''),
                        'link_text': row.get('LinkText', ''),
                        'relative_path': row.get('RelativePath', ''),
                        'link_type': self._determine_link_type(row.get('BrokenLink', '')),
                    })
                    
                    logger.debug(f"Found broken link: {row.get('BrokenLink', '')} in {source_file}")
        except Exception as e:
            logger.error(f"Error reading broken links report: {e}")
        
        return broken_links
    
    def _determine_link_type(self, link: str) -> str:
        """Determine the type of link based on the link text."""
        if link.startswith('http://') or link.startswith('https://'):
            return 'external'
        elif link.startswith('mailto:'):
            return 'mailto'
        elif link.endswith('.md') or '.md#' in link or link.startswith('#'):
            return 'markdown'
        elif link.endswith('.py') or link.endswith('.js'):
            return 'code'
        elif link.startswith('/'):
            return 'absolute'
        else:
            return 'relative'
    
    def _find_best_target(self, link_info: Dict) -> Optional[Path]:
        """Find the best target for a broken link.
        
        Args:
            link_info: Dictionary with broken link information
            
        Returns:
            Path to the best matching file or None if not found
        """
        broken_link = link_info['broken_link']
        relative_path = link_info['relative_path']
        source_file = link_info['source_file']
        
        if not broken_link or broken_link.startswith(('http://', 'https://', 'mailto:')):
            logger.info(f"Skipping external or mailto link: {broken_link}")
            return None
        
        # Clean up the link to get just the file part
        target_file = broken_link.split('#')[0]  # Remove any anchors
        target_file = target_file.split('?')[0]  # Remove any query parameters
        
        # Handle absolute paths
        if target_file.startswith('/'):
            target_file = target_file.lstrip('/')
        
        # Try to find the exact file
        if target_file in self.file_index:
            return self.file_index[target_file]
        
        # Try to find the file by just the filename
        filename = os.path.basename(target_file)
        if filename in self.file_index:
            return self.file_index[filename]
        
        # Try to resolve relative to source file
        if source_file:
            source_dir = os.path.dirname(source_file)
            abs_target = os.path.normpath(os.path.join(source_dir, target_file))
            rel_abs_target = str(Path(abs_target).relative_to(self.repo_root))
            
            if rel_abs_target.lower() in self.file_index:
                return self.file_index[rel_abs_target.lower()]
        
        # For markdown links, try adding .md extension
        if not target_file.endswith(tuple(DOC_EXTENSIONS)) and not target_file.endswith(tuple(CODE_EXTENSIONS)):
            with_md_ext = f"{target_file}.md"
            if with_md_ext in self.file_index:
                return self.file_index[with_md_ext]
            
            # Try with just the filename
            filename_with_md = f"{filename}.md"
            if filename_with_md in self.file_index:
                return self.file_index[filename_with_md]
        
        logger.warning(f"Could not find target file for {broken_link}")
        return None
    
    def _fix_link(self, link_info: Dict):
        """Fix a broken link.
        
        Args:
            link_info: Dictionary with broken link information
        """
        source_file = link_info['source_file']
        broken_link = link_info['broken_link']
        link_type = link_info['link_type']
        link_text = link_info.get('link_text', '')
        
        # Skip if source file doesn't exist
        if not os.path.exists(source_file):
            logger.warning(f"Source file not found: {source_file}")
            self.unfixable_links.append({**link_info, 'reason': 'Source file not found'})
            return
        
        # Find target file
        target = self._find_best_target(link_info)
        if not target:
            logger.warning(f"Target not found for {broken_link} in {source_file}")
            self.unfixable_links.append({**link_info, 'reason': 'Target not found'})
            return
        
        # Determine the relative path from source to target
        source_path = Path(source_file)
        target_path = self.repo_root / target
        
        try:
            # Get relative path from source directory to target file
            source_dir = source_path.parent
            rel_path = os.path.relpath(target_path, source_dir)
            rel_path = rel_path.replace('\\', '/')  # Normalize path separators for links
            
            # Fix relative paths that go up from root
            if rel_path.startswith('../..') and not target_path.is_relative_to(source_dir):
                # Use a path from the root
                rel_path = str(target_path.relative_to(self.repo_root))
                rel_path = rel_path.replace('\\', '/')
        except ValueError:
            # If paths are on different drives, use absolute path
            rel_path = str(target_path)
            rel_path = rel_path.replace('\\', '/')
            logger.warning(f"Using absolute path for {source_file} -> {rel_path}")
            self.unfixable_links.append({**link_info, 'reason': 'Paths on different drives'})
            return
        
        # Read the source file
        try:
            with open(source_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Error reading source file {source_file}: {e}")
            self.unfixable_links.append({**link_info, 'reason': f'Error reading source file: {e}'})
            return
        
        # Build the replacement pattern and replacement text
        if link_type == 'markdown':
            # Format: [link text](link)
            if link_text:
                replacement = f"[{link_text}]({rel_path})"
                pattern = r'\[' + re.escape(link_text) + r'\]\(' + re.escape(broken_link) + r'\)'
            else:
                # We don't have link text info from the CSV, try to find it in the content
                md_match = re.search(r'\[([^\]]+)\]\(' + re.escape(broken_link) + r'\)', content)
                if md_match:
                    link_text = md_match.group(1)
                    replacement = f"[{link_text}]({rel_path})"
                    pattern = r'\[' + re.escape(link_text) + r'\]\(' + re.escape(broken_link) + r'\)'
                else:
                    # Can't find the link in markdown format
                    logger.warning(f"Could not find markdown link pattern for {broken_link} in {source_file}")
                    self.unfixable_links.append({**link_info, 'reason': 'Could not find markdown link pattern'})
                    return
        elif link_type == 'html':
            # Format: <a href="link">text</a>
            pattern = r'<a\s+href="' + re.escape(broken_link) + r'"[^>]*>(.*?)</a>'
            html_match = re.search(pattern, content)
            if html_match:
                link_text = html_match.group(1) if not link_text else link_text
                replacement = f'<a href="{rel_path}">{link_text}</a>'
            else:
                # Can't find the link in HTML format
                logger.warning(f"Could not find HTML link pattern for {broken_link} in {source_file}")
                self.unfixable_links.append({**link_info, 'reason': 'Could not find HTML link pattern'})
                return
        elif link_type == 'mailto':
            # Skip mailto links
            logger.info(f"Skipping mailto link: {broken_link}")
            self.unfixable_links.append({**link_info, 'reason': 'mailto link, not fixable automatically'})
            return
        elif link_type == 'external':
            # Skip external links
            logger.info(f"Skipping external link: {broken_link}")
            self.unfixable_links.append({**link_info, 'reason': 'External link, not fixable automatically'})
            return
        else:
            # Just replace the raw link
            pattern = re.escape(broken_link)
            replacement = rel_path
        
        # Make the replacement
        new_content = re.sub(pattern, replacement, content)
        
        if content == new_content:
            logger.warning(f"No changes made to {source_file} for {broken_link}")
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
    
    def generate_report(self, output_file: str = "updated-link-fixing-report.csv"):
        """Generate a report of fixed and unfixable links.
        
        Args:
            output_file: Path to the output report file
        """
        report_path = self.repo_root / output_file
        with open(report_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['source_file', 'line_number', 'broken_link', 'link_type',
                          'link_text', 'relative_path', 'new_link', 'status', 'reason']
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
    parser.add_argument('--output-file', default='updated-link-fixing-report.csv', help='Path to output report CSV')
    parser.add_argument('--dry-run', action='store_true', help='Do not make actual changes')
    args = parser.parse_args()
    
    logger.info(f"Starting link fixer with repo_root={args.repo_root}, report_file={args.report_file}")
    
    fixer = LinkFixer(args.repo_root, args.report_file, args.dry_run)
    fixer.run()
    fixer.generate_report(args.output_file)


if __name__ == "__main__":
    main()
