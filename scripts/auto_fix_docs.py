"""
Documentation Auto-Fix Script

This script automatically fixes common issues found in documentation:
1. Missing front matter fields
2. Simple syntax errors in code blocks
3. Basic broken links (generating stub files)

The script uses the validation results to identify issues and applies fixes.
"""

import os
import re
import yaml
import sys
import datetime
from pathlib import Path
import shutil
import traceback

# Configuration
DOCS_DIR = Path(__file__).parent.parent / 'docs'
LOG_FILE = Path(__file__).parent.parent / 'validation_results.log'
REQUIRED_FIELDS = ['title', 'description', 'author', 'created_at', 'updated_at', 'version']
DEFAULT_AUTHOR = "Knowledge Base Automation System"
DEFAULT_VERSION = "1.0.0"
CURRENT_DATE = datetime.datetime.now().strftime("%Y-%m-%d")

class DocFixer:
    """Automatically fix documentation issues."""
    
    def __init__(self):
        self.fixed_files = []
        self.error_log = self._parse_validation_log()
        
    def _parse_validation_log(self):
        """Parse the validation log to get errors by file."""
        file_errors = {}
        
        try:
            print("Parsing validation log file...")
            with open(LOG_FILE, 'r', encoding='ascii', errors='replace') as f:
                content = f.read()
                
                # Extract all error lines
                error_lines = re.findall(r'  - (.*)', content)
                print(f"Found {len(error_lines)} total error lines")
                
                for line in error_lines:
                    # Parse file path and error
                    match = re.match(r'(.*?) in (.*?):', line)
                    if match:
                        error_type = match.group(1)
                        file_path = match.group(2)
                        if file_path not in file_errors:
                            file_errors[file_path] = []
                        file_errors[file_path].append(line)
                    else:
                        # Handle broken links differently
                        match = re.match(r'Broken link in (.*?):', line)
                        if match:
                            file_path = match.group(1)
                            if file_path not in file_errors:
                                file_errors[file_path] = []
                            file_errors[file_path].append(line)
            
            print(f"Organized errors for {len(file_errors)} files")
            return file_errors
            
        except Exception as e:
            print(f"Error parsing validation log: {str(e)}")
            return {}
    
    def fix_all(self):
        """Apply fixes to all identified issues."""
        print("Starting automatic documentation fixes...")
        
        # Fix missing front matter
        self._fix_missing_front_matter()
        
        # Fix code block syntax errors
        self._fix_code_block_syntax_errors()
        
        # Fix broken links
        self._fix_broken_links()
        
        # Report results
        print(f"\nFixes applied to {len(self.fixed_files)} files:")
        for file in self.fixed_files[:10]:
            print(f"  - {file}")
        if len(self.fixed_files) > 10:
            print(f"  ... and {len(self.fixed_files) - 10} more files")
    
    def _fix_missing_front_matter(self):
        """Fix missing front matter fields in markdown files."""
        print("\nFixing missing front matter fields...")
        
        for file_path, errors in self.error_log.items():
            if not file_path.lower().endswith('.md'):
                continue
                
            # Check if it has front matter errors
            front_matter_errors = [e for e in errors if "Missing required field" in e]
            if not front_matter_errors:
                continue
                
            # Extract missing fields
            missing_fields = []
            for error in front_matter_errors:
                match = re.search(r"Missing required field '(.*?)'", error)
                if match:
                    missing_fields.append(match.group(1))
            
            if missing_fields:
                self._add_missing_front_matter(file_path, missing_fields)
    
    def _add_missing_front_matter(self, file_path, missing_fields):
        """Add missing front matter to a markdown file."""
        try:
            # Read the file
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            # Extract existing front matter if any
            front_matter = {}
            front_matter_match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
            
            if front_matter_match:
                # Update existing front matter
                try:
                    front_matter = yaml.safe_load(front_matter_match.group(1)) or {}
                except Exception:
                    front_matter = {}
                
                # Generate new front matter
                for field in missing_fields:
                    if field == 'title':
                        front_matter[field] = self._generate_title(file_path)
                    elif field == 'description':
                        front_matter[field] = self._generate_description(file_path)
                    elif field == 'author':
                        front_matter[field] = DEFAULT_AUTHOR
                    elif field == 'created_at':
                        front_matter[field] = CURRENT_DATE
                    elif field == 'updated_at':
                        front_matter[field] = CURRENT_DATE
                    elif field == 'version':
                        front_matter[field] = DEFAULT_VERSION
                
                # Replace old front matter with new one
                new_front_matter = yaml.dump(front_matter, default_flow_style=False)
                new_content = re.sub(r'^---\n.*?\n---', f'---\n{new_front_matter}---', content, flags=re.DOTALL)
                
            else:
                # Create new front matter
                for field in REQUIRED_FIELDS:
                    if field == 'title':
                        front_matter[field] = self._generate_title(file_path)
                    elif field == 'description':
                        front_matter[field] = self._generate_description(file_path)
                    elif field == 'author':
                        front_matter[field] = DEFAULT_AUTHOR
                    elif field == 'created_at':
                        front_matter[field] = CURRENT_DATE
                    elif field == 'updated_at':
                        front_matter[field] = CURRENT_DATE
                    elif field == 'version':
                        front_matter[field] = DEFAULT_VERSION
                
                # Add front matter at the beginning of the file
                new_front_matter = yaml.dump(front_matter, default_flow_style=False)
                new_content = f'---\n{new_front_matter}---\n\n{content}'
            
            # Write the updated content back
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            self.fixed_files.append(file_path)
            print(f"Fixed front matter in {file_path}")
            
        except Exception as e:
            print(f"Error fixing front matter in {file_path}: {str(e)}")
    
    def _generate_title(self, file_path):
        """Generate a title based on the file name."""
        file_name = Path(file_path).stem
        title = file_name.replace('_', ' ').title()
        return title
    
    def _generate_description(self, file_path):
        """Generate a description based on the file path."""
        # Extract directory structure
        rel_path = Path(file_path).relative_to(DOCS_DIR)
        category = rel_path.parts[0] if len(rel_path.parts) > 1 else ""
        subcategory = rel_path.parts[1] if len(rel_path.parts) > 2 else ""
        
        # Format title
        title = self._generate_title(file_path)
        
        if category and subcategory:
            return f"Documentation on {title} for {category}/{subcategory}"
        elif category:
            return f"Documentation on {title} for {category}"
        else:
            return f"Documentation on {title}"
            
    def _fix_code_block_syntax_errors(self):
        """Fix simple code block syntax errors in markdown files."""
        print("\nFixing code block syntax errors...")
        
        for file_path, errors in self.error_log.items():
            if not file_path.lower().endswith('.md'):
                continue
                
            # Check if it has code block errors
            code_block_errors = [e for e in errors if "Syntax error" in e and "code block" in e]
            if not code_block_errors:
                continue
            
            print(f"Attempting to fix {len(code_block_errors)} code block errors in {file_path}")
            self._fix_code_blocks_in_file(file_path, code_block_errors)
    
    def _fix_code_blocks_in_file(self, file_path, errors):
        """Fix code blocks in a specific file."""
        try:
            # Read the file
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            modified = False
            new_content = content
            
            # Find all code blocks
            code_blocks = list(re.finditer(r'```(?:python)?\n(.*?)\n```', content, re.DOTALL))
            
            for error in errors:
                # Extract code block number
                match = re.search(r'code block (\d+)', error)
                if match:
                    block_num = int(match.group(1))
                    
                    # Check if block number is valid
                    if 0 < block_num <= len(code_blocks):
                        # Extract error type
                        if "invalid character" in error:
                            # Replace Unicode characters with ASCII equivalent
                            block = code_blocks[block_num-1]
                            block_content = block.group(1)
                            cleaned_content = block_content.encode('ascii', errors='replace').decode('ascii')
                            
                            # Replace in the full content
                            start = block.start(1)
                            end = block.end(1)
                            new_content = new_content[:start] + cleaned_content + new_content[end:]
                            modified = True
                            print(f"  - Fixed invalid character in code block {block_num}")
                            
                        elif "invalid syntax" in error:
                            # For simple syntax errors, comment out the problematic code
                            block = code_blocks[block_num-1]
                            block_content = block.group(1)
                            commented_content = "# NOTE: The following code had syntax errors and was commented out\n"
                            commented_content += "# " + block_content.replace("\n", "\n# ")
                            
                            # Replace in the full content
                            start = block.start(1)
                            end = block.end(1)
                            new_content = new_content[:start] + commented_content + new_content[end:]
                            modified = True
                            print(f"  - Commented out code with syntax errors in block {block_num}")
            
            if modified:
                # Write the updated content back
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                if file_path not in self.fixed_files:
                    self.fixed_files.append(file_path)
                print(f"Fixed code blocks in {file_path}")
                
        except Exception as e:
            print(f"Error fixing code blocks in {file_path}: {str(e)}")
            traceback.print_exc()
    
    def _fix_broken_links(self):
        """Fix broken links by creating stub files."""
        print("\nFixing broken links...")
        
        fixed_links = 0
        
        for file_path, errors in self.error_log.items():
            # Check if it has broken link errors
            link_errors = [e for e in errors if "Broken link" in e]
            if not link_errors:
                continue
            
            print(f"Found {len(link_errors)} broken links in {file_path}")
            
            for error in link_errors:
                # Extract target path
                match = re.search(r'Broken link in .*?: (.*?) \(target not found\)', error)
                if match:
                    link_path = match.group(1)
                    
                    # Handle relative paths
                    if link_path.startswith('/'):  # Absolute path from docs root
                        target_path = DOCS_DIR / link_path.lstrip('/')
                    elif link_path.startswith('.'):  # Relative path
                        source_dir = Path(file_path).parent
                        target_path = source_dir / link_path
                    else:  # Path relative to current directory
                        source_dir = Path(file_path).parent
                        target_path = source_dir / link_path
                    
                    # Normalize and resolve path
                    try:
                        target_path = target_path.resolve()
                    except Exception:
                        # If resolve fails, just normalize
                        target_path = target_path.absolute()
                    
                    # Check if it's a markdown file or directory
                    if not target_path.suffix:
                        # Assume it's a directory
                        self._create_stub_directory(target_path)
                    else:
                        # Add .md extension if missing
                        if target_path.suffix != '.md':
                            target_path = target_path.with_suffix('.md')
                        self._create_stub_file(target_path)
                    
                    fixed_links += 1
                    print(f"  - Created stub for: {target_path}")
        
        print(f"Fixed {fixed_links} broken links total")
    
    def _create_stub_file(self, target_path):
        """Create a stub markdown file with front matter."""
        if target_path.exists():
            return  # Don't overwrite existing files
        
        try:
            # Create parent directories if they don't exist
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Generate front matter
            front_matter = {
                'title': self._generate_title(target_path),
                'description': f"Auto-generated stub for {target_path.name}",
                'author': DEFAULT_AUTHOR,
                'created_at': CURRENT_DATE,
                'updated_at': CURRENT_DATE,
                'version': DEFAULT_VERSION
            }
            
            # Create stub content
            yaml_front_matter = yaml.dump(front_matter, default_flow_style=False)
            content = f"---\n{yaml_front_matter}---\n\n# {front_matter['title']}\n\n*This is an auto-generated stub file created to fix a broken link.*\n\nTODO: Replace this stub with actual content.\n"
            
            # Write the stub file
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            if target_path not in self.fixed_files:
                self.fixed_files.append(str(target_path))
                
        except Exception as e:
            print(f"Error creating stub file {target_path}: {str(e)}")
            traceback.print_exc()
    
    def _create_stub_directory(self, target_path):
        """Create a stub directory with README.md."""
        if target_path.exists():
            return  # Don't create if directory exists
            
        try:
            # Create the directory
            target_path.mkdir(parents=True, exist_ok=True)
            
            # Create README.md inside it
            readme_path = target_path / "README.md"
            self._create_stub_file(readme_path)
            
        except Exception as e:
            print(f"Error creating stub directory {target_path}: {str(e)}")
            traceback.print_exc()


def main():
    """Run the documentation fixer."""
    doc_fixer = DocFixer()
    doc_fixer.fix_all()
    return 0


if __name__ == "__main__":
    # Add initial debug output
    print("=== Documentation Auto-Fix Script Starting ===\n")
    print(f"Looking for validation log at: {LOG_FILE}")
    
    if not os.path.exists(LOG_FILE):
        print(f"ERROR: Validation log file not found at {LOG_FILE}")
        sys.exit(1)
    
    print(f"Log file found: {os.path.getsize(LOG_FILE)} bytes")
    
    try:
        sys.exit(main())
    except Exception as e:
        print(f"ERROR: Unhandled exception in main: {str(e)}")
        traceback.print_exc()
        sys.exit(1)
