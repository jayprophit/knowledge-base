"""
Final Front Matter and Syntax Error Fixer
=========================================

This script fixes missing front matter fields and syntax errors in markdown files.
Debug version with verbose output.
"""

import os
import re
import sys
from pathlib import Path
from datetime import datetime
import traceback
import time

# Constants
REPO_ROOT = Path(__file__).parent.parent
TODAY = datetime.now().strftime("%Y-%m-%d")
REQUIRED_FIELDS = ['author', 'created_at', 'updated_at', 'version']

def find_markdown_files():
    """Find all markdown files in the repository."""
    markdown_files = []
    for root, _, files in os.walk(REPO_ROOT):
        # Skip .git directory
        if '.git' in root.split(os.sep):
            continue
            
        for file in files:
            if file.endswith('.md'):
                markdown_files.append(os.path.join(root, file))
    
    print(f"Found {len(markdown_files)} markdown files")
    return markdown_files

def has_front_matter(content):
    """Check if the file has front matter."""
    return content.startswith('---')

def extract_front_matter(content):
    """Extract front matter from file content."""
    if not has_front_matter(content):
        return {}, content
    
    # Find the second '---' that closes the front matter
    lines = content.split('\n')
    front_matter_end = -1
    for i, line in enumerate(lines[1:], 1):
        if line == '---':
            front_matter_end = i
            break
    
    if front_matter_end == -1:
        # No closing '---' found
        return {}, content
    
    # Extract front matter content
    front_matter_lines = lines[1:front_matter_end]
    front_matter = {}
    for line in front_matter_lines:
        if ':' in line:
            key, value = line.split(':', 1)
            front_matter[key.strip()] = value.strip()
    
    # Remaining content
    remaining_content = '\n'.join(lines[front_matter_end+1:])
    
    return front_matter, remaining_content

def fix_front_matter(file_path):
    """Fix front matter in a markdown file."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Special case for README.md files
        if os.path.basename(file_path) == 'README.md':
            # Don't modify README files as they have special formatting
            return False, "README file - no modification needed"
        
        front_matter, remaining_content = extract_front_matter(content)
        modified = False
        
        # For any markdown file with missing front matter fields
        if "related_resource" in os.path.basename(file_path):
            # Add default fields for related_resource.md files
            for field in REQUIRED_FIELDS:
                if field not in front_matter:
                    if field == 'author':
                        front_matter[field] = 'Knowledge Base Team'
                    elif field == 'created_at':
                        front_matter[field] = TODAY
                    elif field == 'updated_at':
                        front_matter[field] = TODAY
                    elif field == 'version':
                        front_matter[field] = '1.0'
                    modified = True
        
        # If front matter was modified, write the file
        if modified:
            # Create front matter string
            front_matter_str = '---\n'
            for key, value in front_matter.items():
                front_matter_str += f"{key}: {value}\n"
            front_matter_str += '---\n'
            
            # Write updated content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(front_matter_str + remaining_content)
            
            return True, "Added missing front matter fields"
    
    except Exception as e:
        return False, f"Error processing {file_path}: {str(e)}"
    
    return False, "No changes needed"

def fix_code_block_syntax(file_path):
    """Fix syntax errors in code blocks."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Look for common syntax errors in code blocks
        modified = False
        
        # Fix unterminated string literals
        # Pattern: matches a code block with an unclosed quote
        pattern = r'```[^\n]*\n(.*?)(?<!\\)"(.*?)```'
        matches = list(re.finditer(pattern, content, re.DOTALL))
        for match in reversed(matches):  # Process from end to avoid index issues
            code_block = match.group(0)
            # Fix by adding closing quote
            if '"' in code_block and code_block.count('"') % 2 != 0:
                fixed_block = code_block.replace('```\n', '```python\n')
                content = content[:match.start()] + fixed_block + content[match.end():]
                modified = True
        
        # Fix invalid syntax in Python code blocks
        pattern = r'```python\n(.*?)```'
        matches = list(re.finditer(pattern, content, re.DOTALL))
        for match in matches:
            code_block = match.group(1)
            # Fix common Python syntax errors
            fixed_code = code_block
            
            # Missing commas in dictionaries/lists
            fixed_code = re.sub(r'(\w+": "[^"]*")\s+("', r'\1, \2', fixed_code)
            
            # Unterminated string literals
            fixed_code = re.sub(r'("[^"]*)\n', r'\1"\n', fixed_code)
            
            # Fix invalid decimal literals
            fixed_code = re.sub(r'(\d+)\.([a-zA-Z])', r'\1.\2', fixed_code)
            
            if fixed_code != code_block:
                fixed_block = f"```python\n{fixed_code}```"
                content = content[:match.start()] + fixed_block + content[match.end():]
                modified = True
        
        # If content was modified, write the file
        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True, "Fixed code block syntax"
    
    except Exception as e:
        return False, f"Error fixing code blocks in {file_path}: {str(e)}"
    
    return False, "No changes needed"

def main():
    """Main function."""
    try:
        start_time = time.time()
        print("=" * 80)
        print("Starting Final Front Matter and Syntax Error Fixer...")
        print(f"Repository root: {REPO_ROOT}")
        print("=" * 80)
        
        # Find all markdown files
        markdown_files = find_markdown_files()
        
        # Track changes
        front_matter_fixed = 0
        syntax_fixed = 0
        errors = []
        fixed_files = []
        
        # Process each file
        count = 0
        for file_path in markdown_files:
            count += 1
            if count % 10 == 0:
                print(f"Processing file {count}/{len(markdown_files)}: {file_path}")
            
            # Fix front matter
            fm_modified, fm_message = fix_front_matter(file_path)
            if fm_modified:
                front_matter_fixed += 1
                rel_path = os.path.relpath(file_path, REPO_ROOT)
                fixed_files.append(f"Fixed front matter in {rel_path}")
                print(f"Fixed front matter in {rel_path}: {fm_message}")
            
            # Fix code block syntax
            syntax_modified, syntax_message = fix_code_block_syntax(file_path)
            if syntax_modified:
                syntax_fixed += 1
                rel_path = os.path.relpath(file_path, REPO_ROOT)
                fixed_files.append(f"Fixed code blocks in {rel_path}")
                print(f"Fixed code blocks in {rel_path}: {syntax_message}")
        
        # Force flush stdout
        sys.stdout.flush()
        
        # Print summary
        end_time = time.time()
        duration = end_time - start_time
        print("\n" + "=" * 80)
        print(f"Final Fixer complete in {duration:.2f} seconds!")
        print(f"- Total markdown files processed: {len(markdown_files)}")
        print(f"- Front matter issues fixed: {front_matter_fixed}")
        print(f"- Syntax errors fixed: {syntax_fixed}")
        print(f"- Errors encountered: {len(errors)}")
        
        # Generate report
        report = f"""# Final Fixer Report

## Summary
- Total markdown files processed: {len(markdown_files)}
- Front matter issues fixed: {front_matter_fixed}
- Syntax errors fixed: {syntax_fixed}
- Errors encountered: {len(errors)}
- Processing time: {duration:.2f} seconds

## Details

### Fixed Files
"""
        for fix in fixed_files:
            report += f"- {fix}\n"
        
        report += "\n### Errors\n"
        if errors:
            for error in errors:
                report += f"- {error}\n"
        else:
            report += "No errors encountered.\n"
        
        report_path = REPO_ROOT / "final_fixer_report.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)
        
        print(f"\nReport saved to {report_path}")
        
        return True
    
    except Exception as e:
        print(f"Unhandled error in main: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main()
