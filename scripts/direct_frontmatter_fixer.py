"""
Direct Front Matter Fixer
========================

This script directly fixes front matter in all related_resource.md files with
verbose output and debugging information.
"""

import os
import sys
import glob
from pathlib import Path
from datetime import datetime

# Constants
REPO_ROOT = Path(__file__).parent.parent
TODAY = datetime.now().strftime("%Y-%m-%d")
OUTPUT_FILE = REPO_ROOT / "frontmatter_fix_results.log"

def fix_related_resource_files():
    """Fix front matter in all related_resource.md files."""
    print(f"Searching for related_resource.md files in: {REPO_ROOT}")
    # Use glob to find all related_resource.md files
    pattern = os.path.join(REPO_ROOT, "**", "related_resource.md")
    files = glob.glob(pattern, recursive=True)
    
    print(f"Found {len(files)} related_resource.md files")
    
    # Open log file for writing
    with open(OUTPUT_FILE, "w", encoding="utf-8") as log:
        log.write(f"=== Front Matter Fix Results ===\n\n")
        log.write(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        log.write(f"Total files found: {len(files)}\n\n")
        
        fixed_count = 0
        error_count = 0
        skipped_count = 0
        
        # Process each file
        for file_path in files:
            rel_path = os.path.relpath(file_path, REPO_ROOT)
            log_msg = f"Processing: {rel_path}"
            print(log_msg)
            log.write(f"{log_msg}\n")
            
            try:
                # Read the content
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                
                # Prepare new front matter
                front_matter = (
                    "---\n"
                    "author: Knowledge Base Team\n"
                    f"created_at: {TODAY}\n"
                    f"updated_at: {TODAY}\n"
                    "version: 1.0\n"
                    "---\n\n"
                )
                
                # If file already has front matter, replace it
                if content.startswith("---"):
                    # Find end of front matter
                    second_marker = content.find("---", 3)
                    if second_marker > 0:
                        # Replace front matter
                        new_content = front_matter + content[second_marker+3:].lstrip()
                        log_msg = f"  Replacing front matter in {rel_path}"
                    else:
                        # Invalid front matter, add new one
                        new_content = front_matter + content
                        log_msg = f"  Invalid front matter in {rel_path}, adding new one"
                else:
                    # No front matter, add new one
                    new_content = front_matter + content
                    log_msg = f"  No front matter in {rel_path}, adding new one"
                
                # Write the updated content
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                
                fixed_count += 1
                print(log_msg)
                log.write(f"{log_msg} ✓\n")
                
            except Exception as e:
                error_count += 1
                log_msg = f"  ERROR fixing {rel_path}: {str(e)}"
                print(log_msg)
                log.write(f"{log_msg}\n")
        
        # Write summary
        summary = f"""
=== Summary ===
Total files processed: {len(files)}
Files fixed: {fixed_count}
Files with errors: {error_count}
Files skipped: {skipped_count}
"""
        log.write(summary)
        print(summary)
        
        log.write(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print(f"Results written to {OUTPUT_FILE}")
    return fixed_count

def fix_syntax_errors():
    """Fix common syntax errors in specific files."""
    files_to_fix = [
        # Virtual assistant files
        os.path.join(REPO_ROOT, "docs", "virtual_assistant_cross_platform.md"),
        # AI README
        os.path.join(REPO_ROOT, "docs", "ai", "README.md"),
        # API files
        os.path.join(REPO_ROOT, "docs", "api", "narrow_ai_api.md"),
        # Deployment README
        os.path.join(REPO_ROOT, "docs", "deployment", "README.md"),
        # Quantum computing
        os.path.join(REPO_ROOT, "docs", "quantum_computing", "virtual_quantum_computer.md"),
        # Robotics files
        os.path.join(REPO_ROOT, "docs", "robotics", "advanced_system", "sanskrit_style_reorganization.md"),
        os.path.join(REPO_ROOT, "docs", "robotics", "advanced_system", "security", "README.md"),
        os.path.join(REPO_ROOT, "docs", "robotics", "advanced_system", "software", "README.md"),
        # Machine learning files
        os.path.join(REPO_ROOT, "docs", "machine_learning", "multimodal", "unified_recognition_guide.md"),
        # AI Vision files
        os.path.join(REPO_ROOT, "docs", "ai", "vision", "multi_category_object_recognition.md"),
        # Emotional intelligence files
        os.path.join(REPO_ROOT, "docs", "ai", "emotional_intelligence", "EMOTION_REGULATION.md"),
        # Web system design
        os.path.join(REPO_ROOT, "docs", "web", "system_design", "load_balancer.md"),
    ]
    
    fixed_count = 0
    
    with open(OUTPUT_FILE, "a", encoding="utf-8") as log:
        log.write("\n\n=== Syntax Error Fix Results ===\n\n")
        
        for file_path in files_to_fix:
            if not os.path.exists(file_path):
                rel_path = os.path.relpath(file_path, REPO_ROOT) if os.path.isabs(file_path) else file_path
                log_msg = f"File not found: {rel_path}"
                print(log_msg)
                log.write(f"{log_msg}\n")
                continue
            
            rel_path = os.path.relpath(file_path, REPO_ROOT)
            log_msg = f"Processing: {rel_path}"
            print(log_msg)
            log.write(f"{log_msg}\n")
            
            try:
                # Read the content
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                
                # Fix common syntax errors
                modified = False
                
                # Fix 1: Unterminated string literals
                lines = content.split('\n')
                for i in range(len(lines)):
                    if lines[i].count('"') % 2 == 1:  # Odd number of quotes
                        lines[i] += '"'
                        modified = True
                
                # Fix 2: Fix code blocks with missing language
                new_content = '\n'.join(lines)
                new_content = new_content.replace("```\n", "```python\n")
                if new_content != content:
                    modified = True
                
                # Fix 3: Fix invalid syntax in Python code blocks
                # Fix missing commas in dictionaries
                import re
                new_content = re.sub(r'(\w+": "[^"]*")\s+(")', r'\1, \2', new_content)
                if new_content != content:
                    modified = True
                
                # Write the updated content
                if modified:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    
                    fixed_count += 1
                    log_msg = f"  Fixed syntax errors in {rel_path}"
                    print(log_msg)
                    log.write(f"{log_msg} ✓\n")
                else:
                    log_msg = f"  No syntax errors fixed in {rel_path}"
                    print(log_msg)
                    log.write(f"{log_msg}\n")
                
            except Exception as e:
                log_msg = f"  ERROR fixing {rel_path}: {str(e)}"
                print(log_msg)
                log.write(f"{log_msg}\n")
        
        # Write summary
        summary = f"\n=== Syntax Errors Summary ===\nFiles with syntax errors fixed: {fixed_count}\n"
        log.write(summary)
        print(summary)
    
    return fixed_count

def main():
    """Main function."""
    print("=" * 80)
    print("DIRECT FRONT MATTER FIXER STARTING")
    print("=" * 80)
    
    frontmatter_count = fix_related_resource_files()
    syntax_count = fix_syntax_errors()
    
    print("=" * 80)
    print(f"DIRECT FIXER COMPLETE! Fixed {frontmatter_count} front matter files and {syntax_count} syntax files")
    print("=" * 80)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
