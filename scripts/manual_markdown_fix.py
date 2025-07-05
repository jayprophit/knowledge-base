#!/usr/bin/env python3
"""
Manual Markdown Fix for Persistent Code Block Issues
===================================================

This script directly addresses specific markdown formatting issues that
are causing syntax validation errors, particularly focused on:
1. Malformed code block markers
2. Unterminated string literals
3. Incorrect indentation or missing colons

Usage:
    python manual_markdown_fix.py
"""

import os
import re
import sys
import logging
from pathlib import Path
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("manual_markdown_fix_log.log")
    ]
)
logger = logging.getLogger(__name__)

# Constants
REPO_ROOT = Path(__file__).parent.parent

# List of problematic files with their absolute paths
PROBLEMATIC_FILES = [
    REPO_ROOT / "docs/ai/emotional_intelligence/PYTHON_IMPLEMENTATION.md",
    REPO_ROOT / "docs/ai/emotional_intelligence/SELF_AWARENESS.md",
    REPO_ROOT / "docs/ai/guides/multilingual_understanding.md",
    REPO_ROOT / "docs/ai/guides/multimodal_integration.md",
    REPO_ROOT / "docs/ai/multidisciplinary/integration.md",
    REPO_ROOT / "docs/ai/virtual_brain/02_cognitive_functions.md",
    REPO_ROOT / "docs/ai/virtual_brain/03_python_implementation.md",
]

def fix_file(file_path):
    """Fix specific markdown formatting issues in a file."""
    logger.info(f"Processing {file_path}")
    
    try:
        # Read file content
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Store original content to check if changes were made
        original_content = content
        
        # Fix 1: Correct malformed code block markers
        # Pattern: `````` or ```[language]``` or other variations
        content = re.sub(r'```\s*```+', '```\n\n```', content)
        content = re.sub(r'```(\w+)\s*```', r'```\1\n\n```', content)
        
        # Fix specifically the pattern from SELF_AWARENESS.md
        content = re.sub(r'```\s*```(\w+)', r'```\n\n```\1', content)
        
        # Fix 2: Fix unterminated string literals in docstrings
        content = re.sub(r'"""([^"]*?)""""', r'"""\1"""', content)
        content = re.sub(r"'''([^']*?)''''", r"'''\1'''", content)
        
        # Fix 3: General code block cleanup - normalize indentation and fix common syntax errors
        # Extract all code blocks
        code_blocks = []
        in_code_block = False
        code_block_content = ""
        code_block_language = ""
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Check for code block start
            start_match = re.match(r'^```(\w*)$', line.strip())
            if start_match and not in_code_block:
                in_code_block = True
                code_block_language = start_match.group(1) or "python"  # Default to python if no language specified
                code_block_content = ""
                fixed_lines.append(f"```{code_block_language}")
                continue
            
            # Check for code block end
            if line.strip() == "```" and in_code_block:
                in_code_block = False
                
                # Apply fixes to the code block content
                fixed_code = fix_code_block(code_block_content, code_block_language)
                fixed_lines.extend(fixed_code.split('\n'))
                fixed_lines.append("```")
                continue
            
            if in_code_block:
                # Collect lines within the code block
                code_block_content += line + "\n"
            else:
                # Pass through non-code block lines
                fixed_lines.append(line)
        
        # Reassemble the content
        fixed_content = '\n'.join(fixed_lines)
        
        # Write back if changes were made
        if fixed_content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            logger.info(f"✅ Fixed {file_path}")
            return True
        else:
            logger.info(f"⚠️ No changes needed for {file_path}")
            return False
        
    except Exception as e:
        logger.error(f"❌ Error fixing {file_path}: {str(e)}")
        return False

def fix_code_block(code_block, language):
    """Apply language-specific fixes to a code block."""
    
    if language.lower() in ["python", "py", ""]:
        return fix_python_code_block(code_block)
    elif language.lower() in ["javascript", "js"]:
        return fix_js_code_block(code_block)
    else:
        # For other languages, just normalize trailing quotes
        code_block = re.sub(r'([^\\])"([^"]*?)$', r'\1"\2"', code_block, flags=re.MULTILINE)
        code_block = re.sub(r"([^\\])'([^']*?)$", r"\1'\2'", code_block, flags=re.MULTILINE)
        return code_block

def fix_python_code_block(code_block):
    """Fix Python-specific syntax issues."""
    # Fix docstrings
    code_block = re.sub(r'"""([^"]*?)""""', r'"""\1"""', code_block)
    code_block = re.sub(r"'''([^']*?)''''", r"'''\1'''", code_block)
    
    # Fix missing colons in control structures and definitions
    lines = code_block.split('\n')
    fixed_lines = []
    
    for line in lines:
        # Fix missing colons in control structures
        if re.match(r'^\s*(if|elif|else|for|while|try|except|finally)\s+.+\s*$', line) and not line.rstrip().endswith(':'):
            line = line.rstrip() + ':'
        
        # Fix missing colons in definitions
        if re.match(r'^\s*(def|class)\s+\w+\s*\(.+\)\s*$', line) and not line.rstrip().endswith(':'):
            line = line.rstrip() + ':'
        
        # Fix incomplete function parameters
        if re.match(r'^\s*def\s+\w+\s*\(\s*$', line):
            line = line.rstrip() + '):'
            
        # Fix unterminated string literals (single and double quotes)
        if line.count('"') % 2 == 1 and not re.search(r'\\"\s*$', line):
            line = line.rstrip() + '"'
        if line.count("'") % 2 == 1 and not re.search(r"\\'\s*$", line):
            line = line.rstrip() + "'"
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def fix_js_code_block(code_block):
    """Fix JavaScript-specific syntax issues."""
    # Fix missing semicolons
    lines = code_block.split('\n')
    fixed_lines = []
    
    for line in lines:
        # Add missing semicolons to statement-ending lines
        if (re.search(r'(var|let|const)\s+\w+\s*=\s*.+[^;]$', line.rstrip()) or
            re.search(r'\w+\s*=\s*.+[^;]$', line.rstrip()) or
            re.search(r'\w+\(\)$', line.rstrip())):
            line = line.rstrip() + ';'
        
        # Fix unterminated string literals (single and double quotes)
        if line.count('"') % 2 == 1 and not re.search(r'\\"\s*$', line):
            line = line.rstrip() + '"'
        if line.count("'") % 2 == 1 and not re.search(r"\\'\s*$", line):
            line = line.rstrip() + "'"
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def main():
    """Main function to run the script."""
    logger.info("=" * 80)
    logger.info("MANUAL MARKDOWN FIXER STARTING")
    logger.info("=" * 80)
    
    fixed_count = 0
    
    # Process each problematic file
    for file_path in PROBLEMATIC_FILES:
        if fix_file(file_path):
            fixed_count += 1
    
    logger.info("=" * 80)
    logger.info(f"MANUAL MARKDOWN FIXER COMPLETE! Fixed {fixed_count} out of {len(PROBLEMATIC_FILES)} files")
    logger.info("=" * 80)
    
    # Run validation script to verify fixes
    try:
        logger.info("Running validation script to verify fixes...")
        validation_script = REPO_ROOT / 'scripts' / 'validate_docs.py'
        
        if validation_script.exists():
            result = subprocess.run([sys.executable, str(validation_script)], capture_output=True, text=True)
            
            # Check if validation succeeded
            if "Documentation validation passed" in result.stdout or "Documentation validation passed" in result.stderr:
                logger.info("✅ Validation PASSED! All issues have been fixed.")
            else:
                logger.warning("⚠️ Validation still has issues. Check validation_results.log for details.")
                
                # Extract count of remaining errors
                error_match = re.search(r'ERROR: Found (\d+) errors', result.stdout or result.stderr or "")
                if error_match:
                    remaining_errors = int(error_match.group(1))
                    logger.warning(f"Remaining errors: {remaining_errors}")
                    
                    # If we've made progress, acknowledge it
                    if remaining_errors < 13:  # We had 13 errors before
                        logger.info(f"Progress made! Fixed some errors, but {remaining_errors} still remain.")
        else:
            logger.warning(f"Validation script not found at {validation_script}")
    except Exception as e:
        logger.error(f"Error running validation script: {str(e)}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
