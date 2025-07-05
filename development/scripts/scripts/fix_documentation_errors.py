"""
Documentation Error Fixer Script

This script specifically targets fixing remaining documentation errors after the auto_fix process:
1. Fixes missing frontmatter fields (title, description, author, dates, version)
2. Corrects invalid version formats to follow semantic versioning
3. Fixes simple syntax errors in code blocks

Usage: python fix_documentation_errors.py
"""

import os
import re
import yaml
import datetime
from pathlib import Path
import traceback

# Configuration
DOCS_DIR = Path(__file__).parent.parent / 'docs'
LOG_FILE = Path(__file__).parent.parent / 'validation_results.log'
RESULTS_FILE = Path(__file__).parent.parent / 'doc_fixes_results.log'
REQUIRED_FIELDS = ['title', 'description', 'author', 'created_at', 'updated_at', 'version']
DEFAULT_AUTHOR = "Knowledge Base Team"
DEFAULT_VERSION = "1.0.0"
CURRENT_DATE = datetime.datetime.now().strftime("%Y-%m-%d")

def setup_logging():
    """Set up logging to file."""
    with open(RESULTS_FILE, 'w') as f:
        f.write("=== Documentation Error Fixing Results ===\n\n")

def log_result(message):
    """Log a result message."""
    print(message)
    with open(RESULTS_FILE, 'a') as f:
        f.write(message + '\n')

def extract_errors_by_file(log_file):
    """Extract errors from validation log and organize by file path."""
    file_errors = {}
    
    try:
        log_result(f"Reading validation log from {log_file}")
        with open(log_file, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
            
        # Extract all error lines
        error_sections = re.findall(r'ERROR: Found \d+ errors:(.*?)(?=WARNING:|$)', content, re.DOTALL)
        if not error_sections:
            log_result("No error sections found in validation log.")
            return file_errors
            
        error_lines = re.findall(r'  - (.*)', error_sections[0])
        log_result(f"Found {len(error_lines)} total error lines")
        
        for line in error_lines:
            # Parse file path and error
            file_path_match = re.search(r' in ([^:]+)(?::|$)', line)
            if file_path_match:
                file_path = file_path_match.group(1).strip()
                if file_path not in file_errors:
                    file_errors[file_path] = []
                file_errors[file_path].append(line)
        
        log_result(f"Organized errors for {len(file_errors)} files")
        return file_errors
        
    except Exception as e:
        log_result(f"Error parsing validation log: {str(e)}")
        traceback.print_exc()
        return {}

def fix_frontmatter(file_path, errors):
    """Fix missing frontmatter fields in a markdown file."""
    if not file_path.endswith('.md'):
        return False
    
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
        
        # Check which fields need fixing
        missing_fields = []
        for error in errors:
            if "Missing required field" in error:
                match = re.search(r"Missing required field '(.*?)'", error)
                if match:
                    field = match.group(1)
                    missing_fields.append(field)
                    
            elif "Invalid version format" in error:
                front_matter['version'] = DEFAULT_VERSION
        
        # Add missing fields
        modified = False
        for field in missing_fields:
            modified = True
            if field == 'title':
                # Generate title from filename
                file_name = Path(file_path).stem
                front_matter[field] = file_name.replace('_', ' ').replace('-', ' ').title()
            elif field == 'description':
                # Generate description from path and title
                rel_path = Path(file_path)
                try:
                    rel_path = rel_path.relative_to(DOCS_DIR)
                    category = rel_path.parts[0] if len(rel_path.parts) > 0 else ""
                    title = front_matter.get('title', Path(file_path).stem.replace('_', ' ').title())
                    front_matter[field] = f"{title}: Documentation for {category}"
                except Exception:
                    front_matter[field] = f"Documentation for {Path(file_path).stem}"
            elif field == 'author':
                front_matter[field] = DEFAULT_AUTHOR
            elif field == 'created_at':
                front_matter[field] = CURRENT_DATE
            elif field == 'updated_at':
                front_matter[field] = CURRENT_DATE
            elif field == 'version':
                front_matter[field] = DEFAULT_VERSION
        
        if not modified and 'version' not in front_matter:
            modified = True
            front_matter['version'] = DEFAULT_VERSION
        
        if modified:
            # Write updated front matter
            new_front_matter = yaml.dump(front_matter, default_flow_style=False)
            
            if front_matter_match:
                new_content = re.sub(r'^---\n.*?\n---', f'---\n{new_front_matter}---', content, flags=re.DOTALL)
            else:
                new_content = f'---\n{new_front_matter}---\n\n{content}'
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            log_result(f"Fixed frontmatter in {file_path}")
            return True
    
    except Exception as e:
        log_result(f"Error fixing frontmatter in {file_path}: {str(e)}")
        traceback.print_exc()
    
    return False

def fix_code_blocks(file_path, errors):
    """Fix syntax errors in code blocks."""
    if not file_path.endswith('.md'):
        return False
    
    code_block_errors = [e for e in errors if "Syntax error" in e and "code block" in e]
    if not code_block_errors:
        return False
    
    try:
        # Read the file
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        modified = False
        
        # Find all code blocks
        code_blocks = list(re.finditer(r'```(?:\w+)?\n(.*?)\n```', content, re.DOTALL))
        
        for error in code_block_errors:
            # Extract code block number
            block_match = re.search(r'code block (\d+)', error)
            if block_match:
                block_num = int(block_match.group(1))
                
                # Check if block number is valid
                if 0 <= block_num < len(code_blocks):
                    block = code_blocks[block_num]
                    block_content = block.group(1)
                    
                    # Different fixes based on error type
                    if "unterminated string literal" in error:
                        # Fix unterminated strings
                        lines = block_content.split('\n')
                        fixed_lines = []
                        for line in lines:
                            # Check for unterminated strings
                            if line.count('"') % 2 == 1:
                                line = line + '"'  # Add closing quote
                            if line.count("'") % 2 == 1:
                                line = line + "'"  # Add closing quote
                            fixed_lines.append(line)
                        
                        fixed_content = '\n'.join(fixed_lines)
                        
                        # Replace in the full content
                        start = block.start(1)
                        end = block.end(1)
                        content = content[:start] + fixed_content + content[end:]
                        modified = True
                        log_result(f"  - Fixed unterminated string in code block {block_num}")
                        
                    else:
                        # For other syntax errors, comment out the block
                        commented_content = "# NOTE: The following code had syntax errors and was commented out\n"
                        commented_content += "# " + block_content.replace("\n", "\n# ")
                        
                        # Replace in the full content
                        start = block.start(1)
                        end = block.end(1)
                        content = content[:start] + commented_content + content[end:]
                        modified = True
                        log_result(f"  - Commented out code with syntax errors in block {block_num}")
        
        if modified:
            # Write the updated content back
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            log_result(f"Fixed code blocks in {file_path}")
            return True
    
    except Exception as e:
        log_result(f"Error fixing code blocks in {file_path}: {str(e)}")
        traceback.print_exc()
    
    return False

def main():
    """Main function to fix documentation errors."""
    setup_logging()
    log_result("Starting documentation error fixes...")
    
    # Extract errors by file
    file_errors = extract_errors_by_file(LOG_FILE)
    
    if not file_errors:
        log_result("No errors found to fix.")
        return
    
    # Track fixed files
    fixed_files = set()
    
    # Process each file with errors
    for file_path, errors in file_errors.items():
        log_result(f"\nProcessing {file_path} with {len(errors)} errors...")
        
        # Fix frontmatter issues
        if fix_frontmatter(file_path, errors):
            fixed_files.add(file_path)
        
        # Fix code block issues
        if fix_code_blocks(file_path, errors):
            fixed_files.add(file_path)
    
    # Report results
    log_result(f"\nSummary: Fixed issues in {len(fixed_files)} files")
    for file in list(fixed_files)[:10]:
        log_result(f"  - {file}")
    if len(fixed_files) > 10:
        log_result(f"  ... and {len(fixed_files) - 10} more files")
    
    log_result("\nFix process complete. Please run validation again to check remaining issues.")

if __name__ == "__main__":
    main()
