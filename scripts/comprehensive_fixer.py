#!/usr/bin/env python3
"""
Comprehensive Documentation Fixer
=================================

This script addresses ALL remaining validation errors including:
1. Missing frontmatter fields (title, description)
2. Invalid version formats
3. Code block syntax errors
4. Broken links, especially temp_reorg links

Usage:
    python comprehensive_fixer.py [--dry-run]
"""

import os
import re
import sys
import glob
import logging
import argparse
from pathlib import Path
import shutil
import yaml
from datetime import datetime
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("comprehensive_fix_log.log")
    ]
)
logger = logging.getLogger(__name__)

# Constants
REPO_ROOT = Path(__file__).parent.parent
TODAY = datetime.now().strftime("%Y-%m-%d")
OUTPUT_FILE = REPO_ROOT / "comprehensive_fix_results.log"

# Validation Rules
REQUIRED_FRONTMATTER_FIELDS = ['title', 'description', 'author', 'created_at', 'updated_at', 'version']
VALID_VERSION_FORMAT = r'^\d+\.\d+\.\d+$'  # Format: X.Y.Z (e.g., 1.0.0)

class ComprehensiveFixer:
    """Main class for comprehensive fixing of documentation issues."""
    
    def __init__(self, repo_root=REPO_ROOT, dry_run=False):
        """Initialize with repository root path and dry run flag."""
        self.repo_root = Path(repo_root)
        self.dry_run = dry_run
        self.fixed_files = 0
        self.errors = 0
        self.skipped = 0
        
        # Track what was fixed
        self.frontmatter_fixed = 0
        self.version_fixed = 0
        self.syntax_fixed = 0
        self.links_fixed = 0
        
        # Build file index for link fixing
        self.file_index = {}
    
    def run(self):
        """Run the comprehensive fixer."""
        logger.info(f"Starting comprehensive fixer on {self.repo_root}")
        logger.info("Dry run mode: %s", "ON" if self.dry_run else "OFF")
        
        # Build file index for link fixing
        self._build_file_index()
        
        # Process all markdown files
        markdown_files = list(self.repo_root.glob('**/*.md'))
        logger.info(f"Found {len(markdown_files)} markdown files to process")
        
        with open(OUTPUT_FILE, "w", encoding="utf-8") as log:
            log.write(f"=== Comprehensive Fix Results ===\n\n")
            log.write(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            log.write(f"Total files found: {len(markdown_files)}\n\n")
            
            for file_path in markdown_files:
                rel_path = file_path.relative_to(self.repo_root)
                log_msg = f"Processing: {rel_path}"
                logger.info(log_msg)
                log.write(f"{log_msg}\n")
                
                try:
                    # Read the content
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                    
                    # Apply fixes
                    new_content = self._fix_frontmatter(content, file_path)
                    new_content = self._fix_code_blocks(new_content, file_path)
                    new_content = self._fix_links(new_content, file_path)
                    
                    # Write changes if content was modified
                    if content != new_content and not self.dry_run:
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(new_content)
                        self.fixed_files += 1
                        log.write(f"  ✓ Fixed file: {rel_path}\n")
                    elif content != new_content:
                        log.write(f"  ✓ Would fix file (dry run): {rel_path}\n")
                    else:
                        log.write(f"  - No changes needed: {rel_path}\n")
                        self.skipped += 1
                    
                except Exception as e:
                    self.errors += 1
                    error_msg = f"  ✗ Error processing {rel_path}: {str(e)}"
                    logger.error(error_msg)
                    log.write(f"{error_msg}\n")
            
            # Write summary
            summary = f"""
=== Summary ===
Total files processed: {len(markdown_files)}
Files fixed: {self.fixed_files}
Files with errors: {self.errors}
Files skipped: {self.skipped}

Specific fixes applied:
- Frontmatter fields added: {self.frontmatter_fixed}
- Version format fixed: {self.version_fixed}
- Code block syntax fixed: {self.syntax_fixed}
- Links fixed: {self.links_fixed}
"""
            log.write(summary)
            logger.info(summary)
            
            log.write(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return {
            'total': len(markdown_files),
            'fixed': self.fixed_files,
            'errors': self.errors,
            'skipped': self.skipped,
            'frontmatter_fixed': self.frontmatter_fixed,
            'version_fixed': self.version_fixed,
            'syntax_fixed': self.syntax_fixed,
            'links_fixed': self.links_fixed
        }
    
    def _build_file_index(self):
        """Build an index of all files in the repository for link resolution."""
        logger.info("Building file index for link resolution...")
        for root, _, files in os.walk(self.repo_root):
            for file in files:
                abs_path = Path(os.path.join(root, file))
                rel_path = abs_path.relative_to(self.repo_root)
                
                # Index by various forms of the path
                self.file_index[str(rel_path).lower()] = rel_path
                self.file_index[file.lower()] = rel_path
                
                # Also index without extension for README.md files
                if file.lower() == "readme.md":
                    dir_name = os.path.basename(root)
                    self.file_index[dir_name.lower()] = rel_path
        
        logger.info(f"File index built with {len(self.file_index)} entries")
    
    def _fix_frontmatter(self, content, file_path):
        """Fix missing frontmatter fields and invalid version format."""
        # Check if content has frontmatter
        has_frontmatter = content.startswith('---')
        frontmatter = {}
        body = content
        
        if has_frontmatter:
            # Extract frontmatter
            parts = content.split('---', 2)
            if len(parts) >= 3:
                try:
                    frontmatter = yaml.safe_load(parts[1]) or {}
                    body = '---' + parts[2]
                except yaml.YAMLError:
                    # Invalid YAML, create new frontmatter
                    frontmatter = {}
                    body = content
                    has_frontmatter = False
            else:
                # Invalid frontmatter format
                frontmatter = {}
                body = content
                has_frontmatter = False
        
        # Generate sensible frontmatter fields based on file path
        rel_path = file_path.relative_to(self.repo_root)
        filename = file_path.name
        parent_dir = file_path.parent.name
        
        # Generate title from filename
        if 'title' not in frontmatter:
            if filename.lower() == "readme.md":
                if parent_dir:
                    title = f"{parent_dir.replace('_', ' ').title()} Documentation"
                else:
                    title = "Knowledge Base Documentation"
            elif filename.lower() == "related_resource.md":
                title = f"Related Resources for {parent_dir.replace('_', ' ').title()}"
            else:
                title = filename.replace('.md', '').replace('_', ' ').title()
            
            frontmatter['title'] = title
            self.frontmatter_fixed += 1
        
        # Generate description
        if 'description' not in frontmatter:
            if filename.lower() == "readme.md":
                description = f"Documentation and guides for the {parent_dir.replace('_', ' ').title()} module."
            elif filename.lower() == "related_resource.md":
                description = f"Related resources and reference materials for {parent_dir.replace('_', ' ').title()}."
            else:
                description = f"Documentation for {filename.replace('.md', '').replace('_', ' ').title()} in the Knowledge Base."
                
            frontmatter['description'] = description
            self.frontmatter_fixed += 1
        
        # Ensure other required fields
        if 'author' not in frontmatter:
            frontmatter['author'] = "Knowledge Base Team"
            self.frontmatter_fixed += 1
            
        if 'created_at' not in frontmatter:
            frontmatter['created_at'] = TODAY
            self.frontmatter_fixed += 1
            
        if 'updated_at' not in frontmatter:
            frontmatter['updated_at'] = TODAY
            self.frontmatter_fixed += 1
        
        # Fix version format if needed
        if 'version' not in frontmatter:
            frontmatter['version'] = "1.0.0"
            self.version_fixed += 1
        elif not re.match(VALID_VERSION_FORMAT, str(frontmatter['version'])):
            # Convert to proper semver
            current = str(frontmatter['version']).strip()
            if current == "1.0":
                frontmatter['version'] = "1.0.0"
            elif current == "1":
                frontmatter['version'] = "1.0.0"
            elif re.match(r'^\d+\.\d+$', current):
                frontmatter['version'] = f"{current}.0"
            else:
                # Just set to 1.0.0 if it's not parseable
                frontmatter['version'] = "1.0.0"
            self.version_fixed += 1
        
        # Rebuild the content with fixed frontmatter
        frontmatter_yaml = yaml.dump(frontmatter, default_flow_style=False, sort_keys=False)
        new_content = f"---\n{frontmatter_yaml}---\n\n{body.lstrip('---').lstrip()}"
        
        return new_content
    
    def _fix_code_blocks(self, content, file_path):
        """Fix syntax errors in code blocks."""
        lines = content.split('\n')
        new_lines = []
        in_code_block = False
        code_block_content = []
        code_block_language = ""
        fixed_blocks = 0
        
        for i, line in enumerate(lines):
            # Track code blocks
            if line.startswith("```") and not in_code_block:
                in_code_block = True
                code_block_content = []
                code_block_language = line[3:].strip()
                
                # Fix missing language specifier
                if not code_block_language:
                    # Detect likely language based on context
                    if any("import " in lines[j] for j in range(i+1, min(i+5, len(lines)))):
                        code_block_language = "python"
                    elif any("function" in lines[j] for j in range(i+1, min(i+5, len(lines)))):
                        code_block_language = "javascript"
                    elif any("class" in lines[j] and "{" in lines[j] for j in range(i+1, min(i+5, len(lines)))):
                        code_block_language = "java"
                    else:
                        code_block_language = "python"  # Default to Python
                    
                    new_lines.append(f"```{code_block_language}")
                    fixed_blocks += 1
                    self.syntax_fixed += 1
                else:
                    new_lines.append(line)
                    
            elif line.startswith("```") and in_code_block:
                in_code_block = False
                
                # Fix common syntax errors based on language
                fixed_content = self._fix_syntax_for_language(code_block_content, code_block_language)
                if fixed_content != code_block_content:
                    fixed_blocks += 1
                    self.syntax_fixed += 1
                
                # Add the fixed content
                new_lines.extend(fixed_content)
                new_lines.append(line)
                
            elif in_code_block:
                code_block_content.append(line)
            else:
                new_lines.append(line)
        
        # Handle unterminated code block
        if in_code_block:
            # Fix the content and close the block
            fixed_content = self._fix_syntax_for_language(code_block_content, code_block_language)
            if fixed_content != code_block_content:
                fixed_blocks += 1
                self.syntax_fixed += 1
            
            new_lines.extend(fixed_content)
            new_lines.append("```")
        
        if fixed_blocks > 0:
            logger.info(f"Fixed {fixed_blocks} code blocks in {file_path.name}")
        
        return '\n'.join(new_lines)
    
    def _fix_syntax_for_language(self, lines, language):
        """Fix syntax errors based on programming language."""
        if not lines:
            return lines
            
        # Convert to a single string for easier processing
        content = '\n'.join(lines)
        
        if language.lower() in ["python", "py"]:
            # Fix unclosed quotes
            content = self._fix_unclosed_quotes(content)
            
            # Fix missing colons in Python
            content = re.sub(r'(def\s+\w+\([^)]*\))\s*$', r'\1:', content, flags=re.MULTILINE)
            content = re.sub(r'(class\s+\w+(?:\([^)]*\))?)\s*$', r'\1:', content, flags=re.MULTILINE)
            content = re.sub(r'(if\s+[^:]+)\s*$', r'\1:', content, flags=re.MULTILINE)
            content = re.sub(r'(elif\s+[^:]+)\s*$', r'\1:', content, flags=re.MULTILINE)
            content = re.sub(r'(else)\s*$', r'\1:', content, flags=re.MULTILINE)
            content = re.sub(r'(for\s+[^:]+)\s*$', r'\1:', content, flags=re.MULTILINE)
            content = re.sub(r'(while\s+[^:]+)\s*$', r'\1:', content, flags=re.MULTILINE)
            content = re.sub(r'(try)\s*$', r'\1:', content, flags=re.MULTILINE)
            content = re.sub(r'(except(?:\s+[^:]+)?)\s*$', r'\1:', content, flags=re.MULTILINE)
            content = re.sub(r'(finally)\s*$', r'\1:', content, flags=re.MULTILINE)
            
            # Fix indentation issues - this is tricky to do programmatically
            # Just normalize to 4-space indentation
            lines = content.split('\n')
            for i in range(len(lines)):
                # Replace tabs with spaces
                if lines[i].startswith('\t'):
                    lines[i] = lines[i].replace('\t', '    ')
            
            return lines
            
        elif language.lower() in ["javascript", "js", "typescript", "ts"]:
            # Fix unclosed quotes
            content = self._fix_unclosed_quotes(content)
            
            # Fix missing semicolons in JavaScript
            content = re.sub(r'(var|let|const)\s+(\w+)\s*=\s*([^;]+)$', r'\1 \2 = \3;', content, flags=re.MULTILINE)
            
            # Fix missing braces
            lines = content.split('\n')
            brace_stack = []
            for i in range(len(lines)):
                # Count opening and closing braces
                open_braces = lines[i].count('{')
                close_braces = lines[i].count('}')
                
                # Update the stack
                for _ in range(open_braces):
                    brace_stack.append('{')
                for _ in range(close_braces):
                    if brace_stack and brace_stack[-1] == '{':
                        brace_stack.pop()
            
            # Add missing closing braces at the end if needed
            if brace_stack:
                for _ in range(brace_stack.count('{')):
                    lines.append('}')
            
            return lines
            
        elif language.lower() in ["json"]:
            # Try to fix JSON syntax issues
            try:
                # Replace missing commas in JSON objects
                content = re.sub(r'(\"\s*:\s*\"[^\"]+\")\s+\"', r'\1, "', content)
                
                # Fix trailing commas
                content = re.sub(r',(\s*})', r'\1', content)
                content = re.sub(r',(\s*])', r'\1', content)
            except Exception:
                pass
            
            return content.split('\n')
        
        return lines
    
    def _fix_unclosed_quotes(self, content):
        """Fix unclosed quote issues in code."""
        lines = content.split('\n')
        for i in range(len(lines)):
            # Fix unclosed double quotes
            if lines[i].count('"') % 2 == 1:
                # Add closing quote at the end
                lines[i] += '"'
            
            # Fix unclosed single quotes
            if lines[i].count("'") % 2 == 1:
                # Add closing quote at the end
                lines[i] += "'"
        
        return '\n'.join(lines)
    
    def _fix_links(self, content, file_path):
        """Fix broken links, especially temp_reorg links."""
        # Extract all markdown links [text](url)
        links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
        
        # Keep track of original links and their replacements
        replacements = {}
        
        for link_text, link_url in links:
            # Skip external links and anchors
            if link_url.startswith(('http://', 'https://', 'mailto:', '#')):
                continue
            
            # Fix temp_reorg links
            if 'temp_reorg/' in link_url:
                # Remove temp_reorg part
                fixed_url = link_url.replace('temp_reorg/', '')
                target_path = self._find_best_target(fixed_url)
                
                if target_path:
                    # Calculate relative path from current file to target
                    rel_path = self._calculate_relative_path(file_path, target_path)
                    replacements[link_url] = rel_path
                    self.links_fixed += 1
            elif '../unified-ai-system/' in link_url:
                # Fix unified-ai-system links (these appear to be common based on errors)
                fixed_url = link_url.replace('../unified-ai-system/', '../ai/')
                target_path = self._find_best_target(fixed_url)
                
                if target_path:
                    rel_path = self._calculate_relative_path(file_path, target_path)
                    replacements[link_url] = rel_path
                    self.links_fixed += 1
            else:
                # Check if the link is broken and try to fix it
                if not self._link_exists(link_url, file_path):
                    target_path = self._find_best_target(link_url)
                    
                    if target_path:
                        rel_path = self._calculate_relative_path(file_path, target_path)
                        replacements[link_url] = rel_path
                        self.links_fixed += 1
        
        # Apply all replacements
        new_content = content
        for old_url, new_url in replacements.items():
            # Replace the URL but keep the link text
            old_pattern = re.escape(old_url)
            new_content = re.sub(r'\[([^\]]+)\]\(' + old_pattern + r'\)', r'[\1](' + new_url + ')', new_content)
        
        return new_content
    
    def _link_exists(self, link_url, source_file):
        """Check if a link target exists relative to source file."""
        # Handle absolute and relative paths
        if link_url.startswith('/'):
            target_path = self.repo_root / link_url.lstrip('/')
        else:
            target_path = source_file.parent / link_url
        
        # Normalize path
        try:
            target_path = target_path.resolve()
            return target_path.exists()
        except Exception:
            return False
    
    def _find_best_target(self, link_url):
        """Find the best target file for a broken link."""
        # Extract the file part without any anchor
        parts = link_url.split('#')
        file_part = parts[0]
        
        # Try different variations to find a match
        variations = [
            file_part,
            file_part.lstrip('/'),
            os.path.basename(file_part),
            os.path.basename(file_part).lower()
        ]
        
        # If there's no extension, try with .md
        if not any(file_part.endswith(ext) for ext in ['.md', '.txt', '.py', '.js']):
            variations.extend([
                f"{file_part}.md",
                f"{file_part.lstrip('/')}.md",
                f"{os.path.basename(file_part)}.md"
            ])
        
        # Check each variation
        for var in variations:
            if var.lower() in self.file_index:
                return self.file_index[var.lower()]
        
        # Try to find a similar file
        filename = os.path.basename(file_part)
        best_match = None
        best_score = 0
        
        for indexed_file in self.file_index.values():
            indexed_name = indexed_file.name
            
            # Calculate similarity score (simple for now)
            if filename.lower() in indexed_name.lower():
                score = len(filename) / len(indexed_name) if len(indexed_name) > 0 else 0
                if score > best_score:
                    best_score = score
                    best_match = indexed_file
        
        return best_match
    
    def _calculate_relative_path(self, source_file, target_path):
        """Calculate the relative path from source file to target path."""
        # Ensure we have Path objects
        source_file = Path(source_file)
        target_path = Path(target_path)
        
        try:
            # Get relative path from source directory to target file
            rel_path = os.path.relpath(self.repo_root / target_path, source_file.parent)
            # Normalize path separators for links
            rel_path = rel_path.replace('\\', '/')
            return rel_path
        except ValueError:
            # If paths are on different drives, use the plain path
            return str(target_path).replace('\\', '/')


def main():
    """Main function to run the script."""
    parser = argparse.ArgumentParser(description='Comprehensive documentation fixer')
    parser.add_argument('--dry-run', action='store_true', help='Do not make actual changes')
    parser.add_argument('--repo-root', default=REPO_ROOT, help='Path to repository root')
    args = parser.parse_args()
    
    logger.info("=" * 80)
    logger.info("COMPREHENSIVE DOCUMENTATION FIXER STARTING")
    logger.info("=" * 80)
    
    fixer = ComprehensiveFixer(repo_root=args.repo_root, dry_run=args.dry_run)
    results = fixer.run()
    
    logger.info("=" * 80)
    logger.info(f"FIXER COMPLETE! Fixed {results['fixed']} files")
    logger.info(f"Frontmatter fields added: {results['frontmatter_fixed']}")
    logger.info(f"Version formats fixed: {results['version_fixed']}")
    logger.info(f"Syntax errors fixed: {results['syntax_fixed']}")
    logger.info(f"Links fixed: {results['links_fixed']}")
    logger.info("=" * 80)
    
    # Run validation script to verify fixes
    try:
        logger.info("Running validation script to verify fixes...")
        validation_script = os.path.join(args.repo_root, 'scripts', 'validate_docs.py')
        
        if os.path.exists(validation_script):
            result = subprocess.run([sys.executable, validation_script], capture_output=True, text=True)
            
            # Check if validation succeeded
            if "Documentation validation passed" in result.stdout or "Documentation validation passed" in result.stderr:
                logger.info("✅ Validation PASSED! All issues have been fixed.")
            else:
                logger.warning("⚠️ Validation still has issues. Check validation_results.log for details.")
        else:
            logger.warning(f"Validation script not found at {validation_script}")
    except Exception as e:
        logger.error(f"Error running validation script: {str(e)}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
