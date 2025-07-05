#!/usr/bin/env python3
"""
Create Missing Documentation Stubs

This script creates stub files for missing documentation that are referenced by other files
but don't yet exist. It ignores links in template files and example documentation.
"""

import os
import csv
import logging
from pathlib import Path
import re
import shutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# Directories and files to ignore (these are templates or example files)
IGNORE_DIRS = [
    'templates',
    'examples',
    'temp_reorg'
]

IGNORE_FILES = [
    'linking_standards.md',
    'contribution_guide.md',
    'document_template.md',
    'model_template.md',
    'workflow_template.md',
]

# Template for stub markdown files
STUB_TEMPLATE = """---
title: "{title}"
description: "Stub documentation for {title}"
type: "documentation"
category: "{category}"
related_resources:
  - name: "Related Resource 1"
    url: "#"
tags:
  - documentation
  - stub
---

# {title}

This is a stub document created to fix broken links in the knowledge base.

## Overview

This documentation needs to be expanded with actual content.

## References

- Reference 1
- Reference 2
"""

class MissingDocStubCreator:
    def __init__(self, repo_root, report_file='updated-link-fixing-report.csv'):
        self.repo_root = Path(repo_root)
        self.report_file = self.repo_root / report_file
        self.created_stubs = []
        self.skipped = []
        
    def run(self):
        """Run the stub creation process."""
        if not self.report_file.exists():
            logger.error(f"Report file not found: {self.report_file}")
            return False
        
        unfixed_links = self._read_unfixed_links()
        logger.info(f"Found {len(unfixed_links)} unfixed links to process")
        
        for link_info in unfixed_links:
            self._process_link(link_info)
            
        # Generate report
        self._generate_report()
        
        return True
    
    def _read_unfixed_links(self):
        """Read unfixed links from the report CSV."""
        unfixed_links = []
        try:
            with open(self.report_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Only process rows without a status (unfixed links)
                    if not row.get('status'):
                        unfixed_links.append(row)
        except Exception as e:
            logger.error(f"Error reading link fixing report: {e}")
        
        return unfixed_links
    
    def _process_link(self, link_info):
        """Process a single unfixed link."""
        source_file = link_info.get('source_file', '')
        broken_link = link_info.get('broken_link', '')
        link_text = link_info.get('link_text', '')
        
        # Skip if the source file is in an ignored directory or is an ignored file
        source_path = Path(source_file)
        if self._should_ignore(source_path):
            logger.info(f"Skipping link in ignored file: {source_file} -> {broken_link}")
            self.skipped.append({
                'source': source_file,
                'link': broken_link,
                'reason': 'Template or example file'
            })
            return
        
        # Skip external links, templates, or placeholders
        if not broken_link or broken_link.startswith(('http://', 'https://', 'mailto:')) or broken_link == 'URL':
            logger.info(f"Skipping external or placeholder link: {broken_link}")
            self.skipped.append({
                'source': source_file,
                'link': broken_link,
                'reason': 'External or placeholder link'
            })
            return
        
        # Create the stub file
        self._create_stub(source_file, broken_link, link_text)
    
    def _should_ignore(self, path):
        """Check if a path should be ignored."""
        path_str = str(path)
        
        # Check if path is in an ignored directory
        for ignored_dir in IGNORE_DIRS:
            if ignored_dir in path_str.split(os.sep):
                return True
        
        # Check if file is in the ignored list
        if path.name in IGNORE_FILES:
            return True
        
        return False
    
    def _create_stub(self, source_file, broken_link, link_text):
        """Create a stub file for a broken link."""
        try:
            # Determine the target path
            target_path = self._determine_target_path(source_file, broken_link)
            if not target_path:
                logger.warning(f"Could not determine target path for {broken_link} in {source_file}")
                self.skipped.append({
                    'source': source_file,
                    'link': broken_link,
                    'reason': 'Could not determine target path'
                })
                return
            
            # Create the directory if needed
            target_dir = target_path.parent
            if not target_dir.exists():
                os.makedirs(target_dir, exist_ok=True)
                logger.info(f"Created directory: {target_dir}")
            
            # Only create the file if it doesn't exist
            if target_path.exists():
                logger.info(f"File already exists: {target_path}")
                self.skipped.append({
                    'source': source_file,
                    'link': broken_link,
                    'reason': 'Target file already exists'
                })
                return
            
            # Determine the title and category
            title = link_text if link_text else target_path.stem.replace('_', ' ').title()
            category = self._determine_category(target_path)
            
            # Create the stub file
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(STUB_TEMPLATE.format(title=title, category=category))
            
            logger.info(f"Created stub file: {target_path}")
            self.created_stubs.append({
                'source': source_file,
                'link': broken_link,
                'target': str(target_path),
                'title': title
            })
            
        except Exception as e:
            logger.error(f"Error creating stub for {broken_link} in {source_file}: {e}")
            self.skipped.append({
                'source': source_file,
                'link': broken_link,
                'reason': f'Error: {str(e)}'
            })
    
    def _determine_target_path(self, source_file, broken_link):
        """Determine the target path for a broken link."""
        # Clean up the link (remove anchors and query parameters)
        clean_link = broken_link.split('#')[0].split('?')[0]
        
        # Handle absolute paths (starting with /)
        if clean_link.startswith('/'):
            return self.repo_root / clean_link.lstrip('/')
        
        # Handle relative paths
        source_path = Path(source_file)
        source_dir = source_path.parent
        
        # Check if it's missing a file extension
        if not os.path.splitext(clean_link)[1]:
            clean_link += '.md'
        
        # Build the absolute path
        try:
            # Handle paths like ../path/to/file.md
            target_path = (source_dir / clean_link).resolve()
            
            # Make sure the target path is within the repository
            if not str(target_path).startswith(str(self.repo_root)):
                # If it's outside the repo, place it in a logical location within the repo
                path_parts = clean_link.split('/')
                file_name = path_parts[-1]
                
                # Place it in a suitable directory
                if 'template' in file_name.lower():
                    target_dir = self.repo_root / 'templates'
                elif 'review' in file_name.lower():
                    target_dir = self.repo_root / 'maintenance'
                else:
                    target_dir = self.repo_root / 'docs'
                
                target_path = target_dir / file_name
            
            return target_path
            
        except Exception as e:
            logger.error(f"Error resolving path for {clean_link} from {source_file}: {e}")
            return None
    
    def _determine_category(self, path):
        """Determine a category for the document based on its path."""
        path_str = str(path)
        
        if 'docs/ai' in path_str:
            return "AI"
        elif 'docs/machine_learning' in path_str:
            return "Machine Learning"
        elif 'docs/robotics' in path_str:
            return "Robotics"
        elif 'docs/web' in path_str:
            return "Web Development"
        elif 'docs/blockchain' in path_str:
            return "Blockchain"
        elif 'docs/deployment' in path_str:
            return "Deployment"
        elif 'templates' in path_str:
            return "Templates"
        elif 'maintenance' in path_str:
            return "Maintenance"
        else:
            return "Documentation"
    
    def _generate_report(self):
        """Generate a report of created stubs and skipped links."""
        report_path = self.repo_root / 'stub_creation_report.md'
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# Documentation Stub Creation Report\n\n")
            
            f.write("## Created Stub Files\n\n")
            if self.created_stubs:
                f.write("| Source File | Broken Link | Created Stub | Title |\n")
                f.write("|-------------|------------|--------------|-------|\n")
                for stub in self.created_stubs:
                    f.write(f"| {stub['source']} | {stub['link']} | {stub['target']} | {stub['title']} |\n")
            else:
                f.write("No stub files were created.\n")
            
            f.write("\n## Skipped Links\n\n")
            if self.skipped:
                f.write("| Source File | Broken Link | Reason |\n")
                f.write("|-------------|------------|--------|\n")
                for skip in self.skipped:
                    f.write(f"| {skip['source']} | {skip['link']} | {skip['reason']} |\n")
            else:
                f.write("No links were skipped.\n")
        
        logger.info(f"Generated report at {report_path}")
        
        # Also create a CSV report
        csv_path = self.repo_root / 'stub_creation_report.csv'
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            # Create CSV writer for stubs
            stub_writer = csv.DictWriter(f, fieldnames=['source', 'link', 'target', 'title', 'type'])
            stub_writer.writeheader()
            
            # Write stubs
            for stub in self.created_stubs:
                stub_writer.writerow({**stub, 'type': 'created'})
            
            # Write skipped
            for skip in self.skipped:
                stub_writer.writerow({**skip, 'target': '', 'title': '', 'type': 'skipped'})
        
        logger.info(f"Generated CSV report at {csv_path}")


def main():
    # Use the current directory as the repository root
    repo_root = os.getcwd()
    
    logger.info(f"Starting missing documentation stub creator in {repo_root}")
    
    creator = MissingDocStubCreator(repo_root)
    creator.run()
    
    logger.info("Documentation stub creation complete")


if __name__ == "__main__":
    main()
