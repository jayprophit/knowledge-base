"""
Related Resource Front Matter Fixer
==================================

This script specifically targets related_resource.md files with missing front matter fields.
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Constants
REPO_ROOT = Path(__file__).parent.parent
TODAY = datetime.now().strftime("%Y-%m-%d")
REQUIRED_FIELDS = ['author', 'created_at', 'updated_at', 'version']

def find_related_resource_files():
    """Find all related_resource.md files in the repository."""
    result_files = []
    
    print(f"Searching for related_resource.md files in {REPO_ROOT}...")
    
    for root, _, files in os.walk(REPO_ROOT):
        # Skip .git directory
        if '.git' in root.split(os.sep):
            continue
            
        for file in files:
            if file == "related_resource.md":
                full_path = os.path.join(root, file)
                result_files.append(full_path)
    
    print(f"Found {len(result_files)} related_resource.md files")
    return result_files

def fix_front_matter(file_path):
    """Fix front matter in a related_resource.md file."""
    try:
        print(f"Processing {file_path}")
        
        # Read the file content
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Check for front matter
        if content.startswith('---'):
            # Extract existing front matter
            lines = content.split('\n')
            front_matter_end = -1
            for i, line in enumerate(lines[1:], 1):
                if line == '---':
                    front_matter_end = i
                    break
            
            # If front matter is found
            if front_matter_end != -1:
                # Extract existing fields
                front_matter_lines = lines[1:front_matter_end]
                front_matter = {}
                for line in front_matter_lines:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        front_matter[key.strip()] = value.strip()
                
                # Add missing required fields
                modified = False
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
                
                if modified:
                    # Create new front matter string
                    front_matter_str = '---\n'
                    for key, value in front_matter.items():
                        front_matter_str += f"{key}: {value}\n"
                    front_matter_str += '---\n'
                    
                    # Combine with content after front matter
                    new_content = front_matter_str + '\n'.join(lines[front_matter_end+1:])
                    
                    # Write the updated content
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    return True, "Updated missing front matter fields"
                
                return False, "Front matter already complete"
            
        # If no front matter or improperly formatted
        else:
            # Create new front matter
            front_matter = {
                'author': 'Knowledge Base Team',
                'created_at': TODAY,
                'updated_at': TODAY,
                'version': '1.0'
            }
            
            front_matter_str = '---\n'
            for key, value in front_matter.items():
                front_matter_str += f"{key}: {value}\n"
            front_matter_str += '---\n\n'
            
            # Add front matter to content
            new_content = front_matter_str + content
            
            # Write the updated content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return True, "Added new front matter"
    
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False, f"Error: {str(e)}"

def main():
    """Main function."""
    print(f"Starting Related Resource Front Matter Fixer from {REPO_ROOT}")
    
    # Find all related_resource.md files
    files = find_related_resource_files()
    
    # Track changes
    fixed_count = 0
    errors = []
    fixed_files = []
    
    # Process each file
    for file_path in files:
        try:
            modified, message = fix_front_matter(file_path)
            rel_path = os.path.relpath(file_path, REPO_ROOT)
            
            if modified:
                fixed_count += 1
                fixed_files.append(f"{rel_path}: {message}")
                print(f"✓ Fixed {rel_path}: {message}")
            else:
                print(f"- Skipped {rel_path}: {message}")
        except Exception as e:
            errors.append(f"Error processing {file_path}: {e}")
            print(f"✗ Error processing {file_path}: {e}")
    
    # Generate report
    report = f"""# Related Resource Fixer Report

## Summary
- Total related_resource.md files: {len(files)}
- Files fixed: {fixed_count}
- Errors: {len(errors)}

## Fixed Files
"""
    
    for fix in fixed_files:
        report += f"- {fix}\n"
    
    if errors:
        report += "\n## Errors\n"
        for error in errors:
            report += f"- {error}\n"
    
    # Save report
    report_path = REPO_ROOT / "related_resource_fixer_report.md"
    with open(report_path, "w", encoding='utf-8') as f:
        f.write(report)
    
    print(f"\nReport saved to {report_path}")
    print(f"Fixed {fixed_count} out of {len(files)} related_resource.md files")
    
    # Return success if all files were processed without errors
    return len(errors) == 0

if __name__ == "__main__":
    main()
