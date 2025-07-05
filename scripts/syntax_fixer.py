#!/usr/bin/env python3
"""
Syntax Fixer for Code Blocks in Documentation
============================================

This script specifically addresses code block syntax errors identified by the validation script.
It parses the validation_results.log, identifies code blocks with syntax errors,
and applies advanced fixes to resolve them.

Usage:
    python syntax_fixer.py [--dry-run]
"""

import os
import re
import sys
import glob
import logging
import argparse
from pathlib import Path
import subprocess
import ast
import tempfile
import shutil
import tokenize
from io import BytesIO
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("syntax_fix_log.log")
    ]
)
logger = logging.getLogger(__name__)

# Constants
REPO_ROOT = Path(__file__).parent.parent
VALIDATION_LOG = REPO_ROOT / "validation_results.log"
OUTPUT_FILE = REPO_ROOT / "syntax_fix_results.log"

class CodeBlockSyntaxFixer:
    """Class for fixing syntax errors in documentation code blocks."""
    
    def __init__(self, repo_root=REPO_ROOT, dry_run=False):
        """Initialize with repository root path and dry run flag."""
        self.repo_root = Path(repo_root)
        self.dry_run = dry_run
        self.fixed_files = 0
        self.errors = 0
        self.skipped = 0
        self.total_fixed_blocks = 0
    
    def run(self):
        """Run the syntax fixer."""
        logger.info(f"Starting syntax fixer on {self.repo_root}")
        logger.info("Dry run mode: %s", "ON" if self.dry_run else "OFF")
        
        # Parse validation log for syntax errors
        syntax_errors = self._parse_validation_log()
        
        # Group errors by file for efficient processing
        files_to_fix = defaultdict(list)
        for error in syntax_errors:
            files_to_fix[error['file']].append(error)
        
        logger.info(f"Found {len(syntax_errors)} syntax errors in {len(files_to_fix)} files")
        
        with open(OUTPUT_FILE, "w", encoding="utf-8") as log:
            log.write(f"=== Syntax Fix Results ===\n\n")
            log.write(f"Started at: {os.path.basename(__file__)}\n")
            log.write(f"Total errors found: {len(syntax_errors)}\n")
            log.write(f"Total files to process: {len(files_to_fix)}\n\n")
            
            # Process each file with errors
            for file_path, errors in files_to_fix.items():
                rel_path = Path(file_path).relative_to(self.repo_root) if Path(file_path).is_absolute() else file_path
                log_msg = f"Processing: {rel_path} - {len(errors)} error(s)"
                logger.info(log_msg)
                log.write(f"{log_msg}\n")
                
                try:
                    # Read the file content
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                    
                    # Extract code blocks
                    original_code_blocks, markers = self._extract_code_blocks(content)
                    if not original_code_blocks:
                        log.write(f"  - No code blocks found in {rel_path}\n")
                        logger.warning(f"No code blocks found in {rel_path}")
                        self.skipped += 1
                        continue
                    
                    # Create a copy of the code blocks for modification
                    fixed_code_blocks = original_code_blocks.copy()
                    
                    # Track if any changes were made
                    changes_made = False
                    
                    # Fix syntax errors in each code block
                    for error in errors:
                        block_index = error['block_index'] - 1  # Convert to 0-based index
                        if 0 <= block_index < len(fixed_code_blocks):
                            original_block = fixed_code_blocks[block_index]
                            fixed_block = self._fix_syntax_error(original_block, error)
                            
                            if fixed_block != original_block:
                                fixed_code_blocks[block_index] = fixed_block
                                changes_made = True
                                self.total_fixed_blocks += 1
                                log.write(f"  ✓ Fixed code block {block_index + 1}: {error['error_type']}\n")
                        else:
                            log.write(f"  ✗ Block index out of range: {block_index + 1}\n")
                    
                    # Replace fixed code blocks in the original content
                    if changes_made:
                        new_content = self._replace_code_blocks(content, fixed_code_blocks, markers)
                        
                        # Write the changes to file
                        if not self.dry_run:
                            with open(file_path, "w", encoding="utf-8") as f:
                                f.write(new_content)
                            self.fixed_files += 1
                            log.write(f"  ✓ Fixed file: {rel_path}\n")
                        else:
                            log.write(f"  ✓ Would fix file (dry run): {rel_path}\n")
                    else:
                        log.write(f"  - No changes needed or could not fix: {rel_path}\n")
                        self.skipped += 1
                except Exception as e:
                    self.errors += 1
                    error_msg = f"  ✗ Error processing {rel_path}: {str(e)}"
                    logger.error(error_msg)
                    log.write(f"{error_msg}\n")
            
            # Write summary
            summary = f"""
=== Summary ===
Total files processed: {len(files_to_fix)}
Files fixed: {self.fixed_files}
Files with errors: {self.errors}
Files skipped: {self.skipped}
Total code blocks fixed: {self.total_fixed_blocks}
"""
            log.write(summary)
            logger.info(summary)
        
        return {
            'total_files': len(files_to_fix),
            'fixed_files': self.fixed_files,
            'errors': self.errors,
            'skipped': self.skipped,
            'total_fixed_blocks': self.total_fixed_blocks
        }
    
    def _parse_validation_log(self):
        """Parse the validation log to extract syntax errors."""
        if not os.path.exists(VALIDATION_LOG):
            logger.error(f"Validation log not found: {VALIDATION_LOG}")
            return []
        
        with open(VALIDATION_LOG, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        
        # Extract syntax errors from validation log
        syntax_errors = []
        error_pattern = r"Syntax error in ([^,]+), code block (\d+): (.+)"
        
        for match in re.finditer(error_pattern, content):
            file_path, block_index, error_message = match.groups()
            
            syntax_errors.append({
                'file': file_path,
                'block_index': int(block_index),
                'error_type': error_message,
                'error_details': self._parse_error_details(error_message)
            })
        
        return syntax_errors
    
    def _parse_error_details(self, error_message):
        """Extract detailed information from error messages."""
        details = {
            'line': None,
            'position': None,
            'missing_element': None
        }
        
        # Extract line number if available
        line_match = re.search(r'(detected at line (\d+))', error_message)
        if line_match:
            details['line'] = int(line_match.group(2))
        
        # Identify common error types
        if "unterminated string literal" in error_message:
            details['missing_element'] = 'quote'
        elif "invalid syntax. Perhaps you forgot a comma" in error_message:
            details['missing_element'] = 'comma'
        elif "invalid syntax" in error_message:
            # Generic syntax error
            pass
        elif "invalid decimal literal" in error_message:
            details['missing_element'] = 'numeric_format'
        
        return details
    
    def _extract_code_blocks(self, content):
        """Extract code blocks from markdown content."""
        # Find all code block markers
        code_block_pattern = r"```(\w*)\s*\n(.*?)\n```"
        markers = []
        
        for match in re.finditer(code_block_pattern, content, re.DOTALL):
            start = match.start()
            end = match.end()
            language = match.group(1)
            markers.append({
                'start': start,
                'end': end,
                'language': language
            })
        
        # Extract the code blocks
        code_blocks = []
        for marker in markers:
            block_content = content[marker['start']:marker['end']]
            # Remove the opening and closing backticks and language specifier
            clean_content = re.sub(r"```\w*\s*\n", "", block_content, count=1)
            clean_content = re.sub(r"\n```$", "", clean_content, count=1)
            code_blocks.append(clean_content)
        
        return code_blocks, markers
    
    def _replace_code_blocks(self, content, code_blocks, markers):
        """Replace code blocks in content with fixed versions."""
        # Create a list of content chunks
        chunks = []
        last_end = 0
        
        for i, marker in enumerate(markers):
            # Add text before the code block
            chunks.append(content[last_end:marker['start']])
            
            # Add the code block with backticks and language specifier
            language = marker['language']
            chunks.append(f"```{language}\n{code_blocks[i]}\n```")
            
            last_end = marker['end']
        
        # Add remaining content after the last code block
        chunks.append(content[last_end:])
        
        # Join all chunks
        return ''.join(chunks)
    
    def _fix_syntax_error(self, code_block, error):
        """Apply fixes to code block based on error type."""
        error_type = error['error_type']
        error_details = error['error_details']
        
        # Split code block into lines for easier processing
        lines = code_block.split('\n')
        
        # Apply different fixes based on error type
        if "unterminated string literal" in error_type:
            if error_details['line']:
                # Fix unterminated string in specific line
                line_idx = error_details['line'] - 1
                if 0 <= line_idx < len(lines):
                    lines[line_idx] = self._fix_unterminated_string(lines[line_idx])
            else:
                # Check all lines for unterminated strings
                for i in range(len(lines)):
                    lines[i] = self._fix_unterminated_string(lines[i])
        
        elif "invalid syntax. Perhaps you forgot a comma" in error_type:
            # Fix missing commas in code block
            fixed_lines = []
            for i, line in enumerate(lines):
                if i > 0 and line.strip() and fixed_lines and self._needs_comma(fixed_lines[-1], line):
                    # Add comma to the end of the previous line
                    fixed_lines[-1] = fixed_lines[-1] + ","
                fixed_lines.append(line)
            lines = fixed_lines
        
        elif "invalid decimal literal" in error_type:
            # Fix invalid decimal literals (e.g., 01, 02)
            for i in range(len(lines)):
                lines[i] = self._fix_invalid_decimal_literals(lines[i])
        
        else:  # Generic "invalid syntax" or other errors
            # Try various fixes
            
            # 1. Fix missing colons
            for i in range(len(lines)):
                if self._line_needs_colon(lines[i]):
                    lines[i] = lines[i] + ":"
            
            # 2. Fix unbalanced parentheses/brackets
            lines = self._fix_unbalanced_brackets('\n'.join(lines)).split('\n')
            
            # 3. Fix indentation issues
            lines = self._normalize_indentation(lines)
            
            # 4. Fix missing end quotes
            for i in range(len(lines)):
                lines[i] = self._fix_unterminated_string(lines[i])
        
        return '\n'.join(lines)
    
    def _fix_unterminated_string(self, line):
        """Fix unterminated string literals in a line."""
        # Count quotes to detect imbalance
        single_quotes = line.count("'")
        double_quotes = line.count('"')
        
        # If odd number of quotes, add the missing one
        if single_quotes % 2 == 1:
            # Find the position of the opening quote
            pos = line.find("'")
            if pos >= 0:
                # Check if there's another quote after it
                next_pos = line.find("'", pos + 1)
                if next_pos < 0:
                    # No closing quote, add it at the end
                    return line + "'"
        
        if double_quotes % 2 == 1:
            # Find the position of the opening quote
            pos = line.find('"')
            if pos >= 0:
                # Check if there's another quote after it
                next_pos = line.find('"', pos + 1)
                if next_pos < 0:
                    # No closing quote, add it at the end
                    return line + '"'
        
        return line
    
    def _needs_comma(self, prev_line, current_line):
        """Check if a comma is needed between lines (e.g., in lists, dicts)."""
        # Strip comments
        prev_line = re.sub(r'#.*$', '', prev_line).strip()
        current_line = current_line.strip()
        
        # Check if we're in a list or dict context
        in_container = False
        for char in prev_line:
            if char in '[{(':
                in_container = True
            elif char in ']})':
                in_container = False
        
        # If we're in a container and the current line doesn't start with a closing bracket
        if in_container and current_line and current_line[0] not in ']}),':
            # Check if prev_line doesn't already end with a comma or operator
            if prev_line and prev_line[-1] not in ',+-*/=:[]{}()':
                return True
        
        return False
    
    def _fix_invalid_decimal_literals(self, line):
        """Fix invalid decimal literals like 01, 02, etc."""
        # Find patterns like 0\d (not in a string)
        def replace_invalid_decimal(m):
            # Keep the digit without the leading 0
            return m.group(1)[1:]
        
        # Replace 0\d with \d, but not inside strings
        # This is a simplified approach - a proper parser would be better
        new_line = ""
        in_string = False
        quote_char = None
        i = 0
        
        while i < len(line):
            if not in_string and i + 1 < len(line) and line[i] == '0' and line[i+1].isdigit():
                # Found a potential invalid decimal literal
                if i == 0 or not line[i-1].isalnum():  # Make sure it's not part of a name
                    new_line += line[i+1]  # Skip the leading 0
                    i += 2
                    continue
            
            # Handle string detection
            if not in_string and (line[i] == "'" or line[i] == '"'):
                in_string = True
                quote_char = line[i]
            elif in_string and line[i] == quote_char and (i == 0 or line[i-1] != '\\'):
                in_string = False
            
            new_line += line[i]
            i += 1
        
        return new_line
    
    def _line_needs_colon(self, line):
        """Check if a line needs a colon at the end (e.g., for Python control structures)."""
        line = line.strip()
        
        # Common Python constructs that need a colon
        if re.match(r'^(if|elif|else|for|while|def|class|try|except|finally|with)\b.*[^:]$', line):
            # Check that the line doesn't already have a colon
            if not line.endswith(':'):
                # Make sure we're not in a line that shouldn't have a colon
                if not any(line.endswith(x) for x in [',', '.', ';', '+', '-', '*', '/', '=', '(', '[']):
                    return True
        
        return False
    
    def _fix_unbalanced_brackets(self, code):
        """Fix unbalanced brackets/parentheses/braces."""
        # Count opening and closing brackets
        brackets = {'(': ')', '[': ']', '{': '}'}
        stack = []
        
        # Find missing closing brackets
        for char in code:
            if char in brackets:
                stack.append(char)
            elif char in brackets.values():
                expected_opening = None
                for opening, closing in brackets.items():
                    if closing == char:
                        expected_opening = opening
                        break
                
                if stack and stack[-1] == expected_opening:
                    stack.pop()
                # If unexpected closing bracket, we don't handle it here
        
        # Add missing closing brackets at the end
        for opening_bracket in reversed(stack):
            code += brackets[opening_bracket]
        
        return code
    
    def _normalize_indentation(self, lines):
        """Normalize indentation to use 4 spaces per level."""
        # This is a simplified approach - a proper parser would be better
        fixed_lines = []
        for line in lines:
            # Replace tabs with spaces
            line = line.replace('\t', '    ')
            fixed_lines.append(line)
        
        return fixed_lines


def main():
    """Main function to run the script."""
    parser = argparse.ArgumentParser(description='Code block syntax fixer')
    parser.add_argument('--dry-run', action='store_true', help='Do not make actual changes')
    parser.add_argument('--repo-root', default=REPO_ROOT, help='Path to repository root')
    args = parser.parse_args()
    
    logger.info("=" * 80)
    logger.info("CODE BLOCK SYNTAX FIXER STARTING")
    logger.info("=" * 80)
    
    fixer = CodeBlockSyntaxFixer(repo_root=args.repo_root, dry_run=args.dry_run)
    results = fixer.run()
    
    logger.info("=" * 80)
    logger.info(f"FIXER COMPLETE! Fixed {results['fixed_files']} files with {results['total_fixed_blocks']} code blocks")
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
