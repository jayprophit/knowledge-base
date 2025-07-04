"""
Documentation Validation Script

This script validates the documentation in the knowledge base to ensure:
1. All code examples are syntactically correct
2. All internal links are valid
3. All required sections are present
4. Documentation follows the style guide
"""

import os
import re
import ast
import glob
import yaml
import traceback
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import markdown
from bs4 import BeautifulSoup
import nbformat
from nbconvert import PythonExporter

# Set up log file
LOG_FILE = Path(__file__).parent.parent / 'validation_results.log'

# Configuration
DOCS_DIR = Path(__file__).parent.parent / 'docs'
REQUIRED_SECTIONS = [
    'title', 'description', 'author', 'created_at', 'updated_at', 'version'
]
REQUIRED_TAGS = ['ai', 'quantum_computing', 'security', 'tutorial', 'api']

class DocValidator:
    """Validate documentation files."""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.link_cache: Dict[Path, List[str]] = {}
    
    def validate_all(self) -> bool:
        """Validate all documentation files."""
        with open(LOG_FILE, 'a', encoding='ascii', errors='replace') as f:
            f.write("\nStarting validation of all documentation files...\n")
            
            # Find all markdown files
            try:
                md_files = list(DOCS_DIR.rglob('*.md'))
                f.write(f"Found {len(md_files)} markdown files.\n")
                # Log the first few files for debugging
                for i, file in enumerate(md_files[:5]):
                    f.write(f"  - {file}\n")
                if len(md_files) > 5:
                    f.write(f"  ... and {len(md_files) - 5} more\n")
            except Exception as e:
                f.write(f"ERROR finding markdown files: {str(e)}\n")
                md_files = []
            
            # Find all Jupyter notebooks
            try:
                ipynb_files = list(DOCS_DIR.rglob('*.ipynb'))
                f.write(f"Found {len(ipynb_files)} Jupyter notebook files.\n")
            except Exception as e:
                f.write(f"ERROR finding notebook files: {str(e)}\n")
                ipynb_files = []
                
            f.write("\nStarting validation of markdown files...\n")
            # Validate markdown files
            for file_path in md_files:
                try:
                    f.write(f"Validating {file_path}\n")
                    self.validate_markdown_file(file_path)
                except Exception as e:
                    f.write(f"EXCEPTION validating {file_path}: {str(e)}\n")
                    self.errors.append(f"Exception processing {file_path}: {str(e)}")
            
            f.write("\nStarting validation of Jupyter notebooks...\n")
            # Validate Jupyter notebooks
            for file_path in ipynb_files:
                try:
                    f.write(f"Validating {file_path}\n")
                    self.validate_notebook(file_path)
                except Exception as e:
                    f.write(f"EXCEPTION validating {file_path}: {str(e)}\n")
                    self.errors.append(f"Exception processing {file_path}: {str(e)}")
            
            f.write("\nChecking for broken links...\n")
            # Check for broken links
            try:
                self.check_broken_links()
            except Exception as e:
                f.write(f"EXCEPTION checking links: {str(e)}\n")
                self.errors.append(f"Exception checking links: {str(e)}")
            
            # Report results
            f.write("\nGenerating validation report...\n")
        
        self._report_validation_results()
        
        return len(self.errors) == 0
    
    def validate_markdown_file(self, file_path: Path):
        """Validate a single markdown file."""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Check front matter
            if content.startswith('---'):
                self._validate_front_matter(file_path, content)
            
            # Check code blocks
            self._validate_code_blocks(file_path, content)
            
            # Check for TODOs
            if 'TODO' in content:
                self.warnings.append(f"TODO found in {file_path}")
            
            # Cache links for later validation
            self._cache_links(file_path, content)
            
        except Exception as e:
            self.errors.append(f"Error processing {file_path}: {str(e)}")
    
    def validate_notebook(self, file_path: Path):
        """Validate a Jupyter notebook."""
        try:
            # Read the notebook
            with open(file_path, 'r', encoding='utf-8') as f:
                nb = nbformat.read(f, as_version=4)
            
            # Convert to Python to check syntax
            exporter = PythonExporter()
            python_code, _ = exporter.from_notebook_node(nb)
            
            # Check Python syntax
            try:
                ast.parse(python_code)
            except SyntaxError as e:
                self.errors.append(
                    f"Syntax error in {file_path}, cell {e.lineno}: {e.msg}"
                )
            
            # Check for empty cells
            for i, cell in enumerate(nb.cells):
                if cell.cell_type == 'code' and not cell.source.strip():
                    self.warnings.append(
                        f"Empty code cell in {file_path}, cell {i+1}"
                    )
            
            # Check for long-running cells
            for i, cell in enumerate(nb.cells):
                if cell.cell_type == 'code' and 'time.sleep(' in cell.source:
                    self.warnings.append(
                        f"Potential long-running code in {file_path}, cell {i+1}"
                    )
            
        except Exception as e:
            self.errors.append(f"Error processing notebook {file_path}: {str(e)}")
    
    def _validate_front_matter(self, file_path: Path, content: str):
        """Validate front matter in markdown files."""
        try:
            # Extract front matter
            front_matter = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
            if not front_matter:
                self.errors.append(f"Malformed front matter in {file_path}")
                return
            
            # Parse YAML
            try:
                metadata = yaml.safe_load(front_matter.group(1))
            except yaml.YAMLError as e:
                self.errors.append(f"Invalid YAML in {file_path}: {str(e)}")
                return
            
            # Check required fields
            for field in REQUIRED_SECTIONS:
                if field not in metadata:
                    self.errors.append(f"Missing required field '{field}' in {file_path}")
            
            # Check tags
            if 'tags' in metadata:
                for tag in metadata['tags']:
                    if not isinstance(tag, str):
                        self.errors.append(f"Invalid tag format in {file_path}")
                    if tag not in REQUIRED_TAGS:
                        self.warnings.append(f"Non-standard tag '{tag}' in {file_path}")
            
            # Check version format
            if 'version' in metadata:
                if not re.match(r'^\d+\.\d+\.\d+$', str(metadata['version'])):
                    self.errors.append(
                        f"Invalid version format in {file_path}: {metadata['version']}"
                    )
            
        except Exception as e:
            self.errors.append(f"Error validating front matter in {file_path}: {str(e)}")
    
    def _validate_code_blocks(self, file_path: Path, content: str):
        """Validate code blocks in markdown."""
        # Find all code blocks
        code_blocks = re.findall(r'```(?:python)?\n(.*?)\n```', content, re.DOTALL)
        
        for i, code in enumerate(code_blocks, 1):
            try:
                # Skip empty code blocks
                if not code.strip():
                    continue
                    
                # Check Python syntax
                ast.parse(code)
                
            except SyntaxError as e:
                self.errors.append(
                    f"Syntax error in {file_path}, code block {i}: {e.msg}"
                )
    
    def _cache_links(self, file_path: Path, content: str):
        """Cache links for later validation."""
        # Convert markdown to HTML
        html = markdown.markdown(content)
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find all links
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            
            # Skip external links
            if href.startswith(('http://', 'https://', 'mailto:')):
                continue
                
            # Handle relative paths
            if href.startswith('/'):
                target_path = Path(DOCS_DIR) / href.lstrip('/')
            else:
                target_path = file_path.parent / href
            
            links.append((str(href), str(target_path)))
        
        self.link_cache[file_path] = links
    
    def check_broken_links(self):
        """Check for broken internal links."""
        for file_path, links in self.link_cache.items():
            for href, target_path in links:
                target_path = Path(target_path)
                
                # Handle anchor links
                if '#' in str(target_path):
                    path_part, anchor = str(target_path).split('#', 1)
                    target_path = Path(path_part)
                
                # Check if target exists
                if not target_path.exists():
                    # Check with .md extension
                    if not target_path.with_suffix('.md').exists():
                        self.errors.append(
                            f"Broken link in {file_path}: {href} (target not found)"
                        )
    
    def _report_validation_results(self):
        """Write validation results to log file."""
        with open(LOG_FILE, 'w', encoding='ascii', errors='replace') as f:
            f.write("\n=== Documentation Validation Results ===\n\n")
            
            if self.errors:
                f.write(f"ERROR: Found {len(self.errors)} errors:\n")
                for error in self.errors:
                    f.write(f"  - {error}\n")
            else:
                f.write("OK: No errors found!\n")
            
            if self.warnings:
                f.write(f"\nWARNING: Found {len(self.warnings)} warnings:\n")
                for warning in self.warnings[:10]:  # Show first 10 warnings
                    f.write(f"  - {warning}\n")
                if len(self.warnings) > 10:
                    f.write(f"  ... and {len(self.warnings) - 10} more warnings\n")
            
            f.write("\n=== Validation Complete ===\n")
            
        # Also print to console
        print(f"Results written to {LOG_FILE}")


def main():
    """Run the documentation validator."""
    try:
        # Write initial log entry
        with open(LOG_FILE, 'w', encoding='ascii', errors='replace') as f:
            f.write("Starting documentation validation...\n")
            
        validator = DocValidator()
        success = validator.validate_all()
        
        if not success:
            with open(LOG_FILE, 'a', encoding='ascii', errors='replace') as f:
                f.write("\nERROR: Documentation validation failed!\n")
            return 1
        
        with open(LOG_FILE, 'a', encoding='ascii', errors='replace') as f:
            f.write("\nOK: All documentation is valid!\n")
        return 0
    except Exception as e:
        # Catch any unexpected errors
        with open(LOG_FILE, 'a', encoding='ascii', errors='replace') as f:
            f.write(f"\nFATAL ERROR: Unhandled exception in validator:\n{str(e)}\n")
            f.write(traceback.format_exc())
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
