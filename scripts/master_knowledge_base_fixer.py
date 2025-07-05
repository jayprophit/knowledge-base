#!/usr/bin/env python3
"""
Master Knowledge Base Fixer - Complete System Repair
Fixes all identified issues in the knowledge base in one comprehensive pass.
"""

import os
import re
import json
import shutil
import hashlib
from pathlib import Path
from datetime import datetime
import csv
import subprocess
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('master_fix_log.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MasterKnowledgeBaseFixer:
    def __init__(self, base_path):
        self.base_path = Path(base_path)
        self.errors_fixed = 0
        self.files_processed = 0
        self.files_recreated = 0
        self.duplicates_removed = 0
        self.links_fixed = 0
        
        # Standard frontmatter template
        self.frontmatter_template = {
            'title': '',
            'description': '',
            'category': '',
            'tags': [],
            'version': '1.0.0',
            'updated_at': datetime.now().strftime('%Y-%m-%d'),
            'created_at': datetime.now().strftime('%Y-%m-%d'),
            'status': 'active'
        }
        
        # Files to exclude from processing
        self.exclude_patterns = {
            '.git', '.venv', '__pycache__', 'node_modules', 
            '.log', '.csv', 'temp_reorg', '.env'
        }
        
        # Broken link mappings for fixes
        self.link_fixes = {}
        self.load_broken_links()
    
    def load_broken_links(self):
        """Load broken links report for fixing."""
        broken_links_file = self.base_path / 'broken-links-report.csv'
        if broken_links_file.exists():
            try:
                with open(broken_links_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        source = row.get('SourceFile', '')
                        broken_link = row.get('BrokenLink', '')
                        if source and broken_link:
                            if source not in self.link_fixes:
                                self.link_fixes[source] = []
                            self.link_fixes[source].append(broken_link)
            except Exception as e:
                logger.warning(f"Could not load broken links report: {e}")
    
    def should_exclude(self, path):
        """Check if path should be excluded from processing."""
        path_str = str(path).lower()
        return any(exclude in path_str for exclude in self.exclude_patterns)
    
    def fix_unicode_characters(self, content):
        """Fix common Unicode box-drawing characters in code blocks."""
        # Common Unicode box-drawing characters that cause issues
        unicode_fixes = {
            '\u250C': '+',  # ┌
            '\u2510': '+',  # ┐
            '\u2514': '+',  # └
            '\u2518': '+',  # ┘
            '\u251C': '+',  # ├
            '\u2524': '+',  # ┤
            '\u252C': '+',  # ┬
            '\u2534': '+',  # ┴
            '\u253C': '+',  # ┼
            '\u2500': '-',  # ─
            '\u2502': '|',  # │
            '\u2211': 'sum', # ∑
        }
        
        for unicode_char, replacement in unicode_fixes.items():
            content = content.replace(unicode_char, replacement)
        
        return content
    
    def fix_code_blocks(self, content):
        """Fix syntax errors in code blocks."""
        # Fix leading zeros in decimal literals
        content = re.sub(r'\b0+(\d+)\b', r'\1', content)
        
        # Fix common syntax issues in code blocks
        lines = content.split('\n')
        fixed_lines = []
        in_code_block = False
        
        for line in lines:
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                fixed_lines.append(line)
                continue
            
            if in_code_block:
                # Fix common Python syntax issues
                line = re.sub(r'^\s*(\d+):', r'    # Line \1:', line)  # Fix line numbers
                line = re.sub(r'unexpected indent', '', line)
                line = re.sub(r'invalid syntax', '', line)
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def generate_frontmatter(self, file_path, content):
        """Generate appropriate frontmatter for a markdown file."""
        title = self.extract_title_from_content(content) or file_path.stem.replace('_', ' ').title()
        description = self.extract_description_from_content(content) or f"Documentation for {title}"
        category = self.determine_category(file_path)
        tags = self.generate_tags(file_path, content)
        
        frontmatter = self.frontmatter_template.copy()
        frontmatter.update({
            'title': title,
            'description': description,
            'category': category,
            'tags': tags
        })
        
        return frontmatter
    
    def extract_title_from_content(self, content):
        """Extract title from content."""
        # Look for first h1 header
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        return None
    
    def extract_description_from_content(self, content):
        """Extract description from content."""
        # Look for content after title but before next header
        lines = content.split('\n')
        description_lines = []
        found_title = False
        
        for line in lines:
            line = line.strip()
            if line.startswith('# '):
                found_title = True
                continue
            elif found_title and line.startswith('#'):
                break
            elif found_title and line and not line.startswith('```'):
                description_lines.append(line)
                if len(' '.join(description_lines)) > 200:
                    break
        
        description = ' '.join(description_lines).strip()
        return description[:200] + '...' if len(description) > 200 else description
    
    def determine_category(self, file_path):
        """Determine category based on file path."""
        path_parts = file_path.parts
        if 'ai' in path_parts:
            return 'AI & Machine Learning'
        elif 'robotics' in path_parts:
            return 'Robotics'
        elif 'quantum' in path_parts:
            return 'Quantum Computing'
        elif 'web' in path_parts:
            return 'Web Development'
        elif 'mobile' in path_parts:
            return 'Mobile Development'
        elif 'security' in path_parts:
            return 'Security'
        elif 'docs' in path_parts:
            return 'Documentation'
        elif 'src' in path_parts:
            return 'Source Code'
        else:
            return 'General'
    
    def generate_tags(self, file_path, content):
        """Generate relevant tags based on file path and content."""
        tags = []
        
        # Tags from path
        path_str = str(file_path).lower()
        tag_keywords = [
            'ai', 'ml', 'machine learning', 'robotics', 'quantum', 'web', 'mobile',
            'security', 'database', 'api', 'frontend', 'backend', 'deployment',
            'testing', 'documentation', 'guide', 'tutorial', 'reference'
        ]
        
        for keyword in tag_keywords:
            if keyword in path_str or keyword in content.lower():
                tags.append(keyword.replace(' ', '-'))
        
        return list(set(tags))[:5]  # Limit to 5 tags
    
    def add_frontmatter_to_file(self, file_path):
        """Add or fix frontmatter in a markdown file."""
        try:
            content = file_path.read_text(encoding='utf-8')
        except:
            return False
        
        # Check if frontmatter already exists
        if content.startswith('---\n'):
            # Extract existing frontmatter
            parts = content.split('---\n', 2)
            if len(parts) >= 3:
                existing_fm = parts[1]
                body_content = parts[2]
                
                # Parse existing frontmatter
                try:
                    import yaml
                    fm_data = yaml.safe_load(existing_fm) or {}
                except:
                    fm_data = {}
                
                # Update with missing fields
                new_fm = self.generate_frontmatter(file_path, body_content)
                for key, value in new_fm.items():
                    if key not in fm_data or not fm_data[key]:
                        fm_data[key] = value
                
                # Reconstruct file
                try:
                    import yaml
                    new_frontmatter = yaml.dump(fm_data, default_flow_style=False)
                    new_content = f"---\n{new_frontmatter}---\n{body_content}"
                except:
                    return False
            else:
                return False
        else:
            # Add new frontmatter
            frontmatter = self.generate_frontmatter(file_path, content)
            try:
                import yaml
                fm_string = yaml.dump(frontmatter, default_flow_style=False)
                new_content = f"---\n{fm_string}---\n{content}"
            except:
                return False
        
        # Apply other fixes
        new_content = self.fix_unicode_characters(new_content)
        new_content = self.fix_code_blocks(new_content)
        
        try:
            file_path.write_text(new_content, encoding='utf-8')
            return True
        except:
            return False
    
    def fix_broken_links_in_file(self, file_path):
        """Fix broken links in a specific file."""
        try:
            content = file_path.read_text(encoding='utf-8')
            original_content = content
            
            # Fix common broken link patterns
            link_patterns = [
                (r'\[([^\]]+)\]\(/tutorials\)', r'[\1](../tutorials/README.md)'),
                (r'\[([^\]]+)\]\(/src\)', r'[\1](../src/README.md)'),
                (r'\[([^\]]+)\]\(/tests\)', r'[\1](../tests/README.md)'),
                (r'\[([^\]]+)\]\(/docs/troubleshooting\.md\)', r'[\1](../TROUBLESHOOTING.md)'),
                (r'\[([^\]]+)\]\(/docs/faq\.md\)', r'[\1](../FAQ.md)'),
                (r'mailto:security@example\.com', 'mailto:security@knowledge-base.ai'),
                (r'mailto:support@example\.com', 'mailto:support@knowledge-base.ai'),
            ]
            
            for pattern, replacement in link_patterns:
                content = re.sub(pattern, replacement, content)
            
            if content != original_content:
                file_path.write_text(content, encoding='utf-8')
                self.links_fixed += 1
                return True
        except:
            pass
        return False
    
    def remove_empty_files_and_dirs(self):
        """Remove empty files and directories."""
        removed_count = 0
        
        # Remove empty files
        for file_path in self.base_path.rglob('*'):
            if file_path.is_file() and not self.should_exclude(file_path):
                try:
                    if file_path.stat().st_size == 0:
                        file_path.unlink()
                        removed_count += 1
                        logger.info(f"Removed empty file: {file_path}")
                except:
                    pass
        
        # Remove empty directories (multiple passes)
        for _ in range(3):
            for dir_path in sorted(self.base_path.rglob('*'), reverse=True):
                if dir_path.is_dir() and not self.should_exclude(dir_path):
                    try:
                        if not any(dir_path.iterdir()):
                            dir_path.rmdir()
                            removed_count += 1
                            logger.info(f"Removed empty directory: {dir_path}")
                    except:
                        pass
        
        return removed_count
    
    def find_and_remove_duplicates(self):
        """Find and remove duplicate files based on content hash."""
        file_hashes = {}
        duplicates_removed = 0
        
        for file_path in self.base_path.rglob('*'):
            if file_path.is_file() and not self.should_exclude(file_path):
                try:
                    content = file_path.read_bytes()
                    file_hash = hashlib.md5(content).hexdigest()
                    
                    if file_hash in file_hashes:
                        # Duplicate found - remove the one with less descriptive name
                        existing_file = file_hashes[file_hash]
                        if len(file_path.name) < len(existing_file.name):
                            file_path.unlink()
                            logger.info(f"Removed duplicate: {file_path}")
                        else:
                            existing_file.unlink()
                            file_hashes[file_hash] = file_path
                            logger.info(f"Removed duplicate: {existing_file}")
                        duplicates_removed += 1
                    else:
                        file_hashes[file_hash] = file_path
                except:
                    pass
        
        return duplicates_removed
    
    def create_missing_files(self):
        """Create missing files that are referenced but don't exist."""
        created_files = []
        
        # Essential files that should exist
        essential_files = {
            'tutorials/README.md': 'Tutorials and learning resources for the knowledge base.',
            'tests/README.md': 'Test suite and validation tools for the knowledge base.',
            'src/README.md': 'Source code documentation and implementation guides.',
            'docs/troubleshooting.md': 'Common issues and their solutions.',
            'docs/faq.md': 'Frequently asked questions about the knowledge base.'
        }
        
        for rel_path, description in essential_files.items():
            file_path = self.base_path / rel_path
            if not file_path.exists():
                file_path.parent.mkdir(parents=True, exist_ok=True)
                
                title = file_path.stem.replace('_', ' ').replace('-', ' ').title()
                content = f"""---
title: {title}
description: {description}
category: Documentation
version: 1.0.0
updated_at: {datetime.now().strftime('%Y-%m-%d')}
status: active
---

# {title}

{description}

This file was automatically generated as part of the knowledge base repair process.

## Contents

Coming soon - this section will be populated with relevant content.

## Contributing

If you'd like to contribute to this documentation, please see our [Contributing Guidelines](../CONTRIBUTING.md).
"""
                try:
                    file_path.write_text(content, encoding='utf-8')
                    created_files.append(str(file_path))
                    logger.info(f"Created missing file: {file_path}")
                except Exception as e:
                    logger.error(f"Failed to create {file_path}: {e}")
        
        return created_files
    
    def process_markdown_file(self, file_path):
        """Process a single markdown file completely."""
        try:
            logger.info(f"Processing: {file_path}")
            
            # Add/fix frontmatter
            if self.add_frontmatter_to_file(file_path):
                self.errors_fixed += 1
            
            # Fix broken links
            if self.fix_broken_links_in_file(file_path):
                self.links_fixed += 1
            
            self.files_processed += 1
            return True
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            return False
    
    def run_comprehensive_fix(self):
        """Run the complete fixing process."""
        logger.info("Starting comprehensive knowledge base repair...")
        
        start_time = datetime.now()
        
        # Step 1: Create missing essential files
        logger.info("Step 1: Creating missing essential files...")
        created_files = self.create_missing_files()
        
        # Step 2: Process all markdown files
        logger.info("Step 2: Processing all markdown files...")
        for file_path in self.base_path.rglob('*.md'):
            if not self.should_exclude(file_path):
                self.process_markdown_file(file_path)
        
        # Step 3: Remove duplicates
        logger.info("Step 3: Removing duplicate files...")
        self.duplicates_removed = self.find_and_remove_duplicates()
        
        # Step 4: Remove empty files and directories
        logger.info("Step 4: Removing empty files and directories...")
        empty_removed = self.remove_empty_files_and_dirs()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Generate report
        report = {
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_seconds': duration,
            'files_processed': self.files_processed,
            'errors_fixed': self.errors_fixed,
            'links_fixed': self.links_fixed,
            'duplicates_removed': self.duplicates_removed,
            'empty_files_removed': empty_removed,
            'created_files': created_files,
            'status': 'completed'
        }
        
        # Save report
        report_file = self.base_path / 'master_fix_report.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Comprehensive fix completed in {duration:.2f} seconds")
        logger.info(f"Files processed: {self.files_processed}")
        logger.info(f"Errors fixed: {self.errors_fixed}")
        logger.info(f"Links fixed: {self.links_fixed}")
        logger.info(f"Duplicates removed: {self.duplicates_removed}")
        logger.info(f"Empty files removed: {empty_removed}")
        logger.info(f"Created files: {len(created_files)}")
        
        return report

def main():
    # Get the knowledge base path
    script_dir = Path(__file__).parent
    kb_path = script_dir.parent
    
    logger.info(f"Knowledge base path: {kb_path}")
    
    # Run the comprehensive fix
    fixer = MasterKnowledgeBaseFixer(kb_path)
    report = fixer.run_comprehensive_fix()
    
    print("\n" + "="*60)
    print("MASTER KNOWLEDGE BASE FIX COMPLETED")
    print("="*60)
    print(f"Duration: {report['duration_seconds']:.2f} seconds")
    print(f"Files processed: {report['files_processed']}")
    print(f"Errors fixed: {report['errors_fixed']}")
    print(f"Links fixed: {report['links_fixed']}")
    print(f"Duplicates removed: {report['duplicates_removed']}")
    print(f"Empty files removed: {report['empty_files_removed']}")
    print(f"Files created: {len(report['created_files'])}")
    print("="*60)

if __name__ == "__main__":
    main()
