#!/usr/bin/env python3
"""
Enhanced Syntax Fixer for Documentation Code Blocks
==================================================

This script specifically targets complex syntax errors in documentation code blocks
that weren't fixed by previous attempts. It directly processes files listed in
the validation results log and applies targeted fixes for specific error types.

Usage:
    python enhanced_syntax_fixer.py [--dry-run]
"""

import os
import re
import sys
import logging
import argparse
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("enhanced_syntax_fix_log.log")
    ]
)
logger = logging.getLogger(__name__)

# Constants
REPO_ROOT = Path(__file__).parent.parent
VALIDATION_LOG = REPO_ROOT / "validation_results.log"
OUTPUT_FILE = REPO_ROOT / "enhanced_syntax_fix_results.log"

class EnhancedSyntaxFixer:
    """Enhanced fixer for complex syntax errors in documentation code blocks."""
    
    def __init__(self, repo_root=REPO_ROOT, dry_run=False):
        """Initialize with repository root path and dry run flag."""
        self.repo_root = Path(repo_root)
        self.dry_run = dry_run
        self.files_fixed = 0
        self.blocks_fixed = 0
        self.errors = 0
        self.skipped = 0
        
        # Cache of fixed files to avoid redundant processing
        self.fixed_files = set()
    
    def run(self):
        """Run the enhanced syntax fixer."""
        logger.info(f"Starting enhanced syntax fixer on {self.repo_root}")
        logger.info("Dry run mode: %s", "ON" if self.dry_run else "OFF")
        
        # Extract files with syntax errors from validation log
        error_files = self._parse_validation_log()
        
        if not error_files:
            logger.warning("No syntax errors found in validation log.")
            return
        
        with open(OUTPUT_FILE, "w", encoding="utf-8") as log:
            log.write(f"=== Enhanced Syntax Fix Results ===\n\n")
            log.write(f"Files with errors: {len(error_files)}\n\n")
            
            # Process each file with errors
            for file_info in error_files:
                file_path = file_info['file']
                block_index = file_info['block_index']
                error_type = file_info['error_type']
                
                # Skip already processed files
                if file_path in self.fixed_files:
                    continue
                
                # Process the file
                try:
                    log.write(f"Processing: {file_path}\n")
                    log.write(f"  - Block: {block_index}, Error: {error_type}\n")
                    
                    fixed = self._fix_file(file_path, file_info)
                    
                    if fixed:
                        self.files_fixed += 1
                        self.blocks_fixed += 1
                        log.write(f"  ✓ Fixed\n")
                        self.fixed_files.add(file_path)
                    else:
                        log.write(f"  ✗ Could not fix\n")
                        self.skipped += 1
                except Exception as e:
                    self.errors += 1
                    error_msg = f"  ✗ Error processing {file_path}: {str(e)}"
                    logger.error(error_msg)
                    log.write(f"{error_msg}\n")
            
            # Write summary
            summary = f"""
=== Summary ===
Files with errors: {len(error_files)}
Files fixed: {self.files_fixed}
Files with errors: {self.errors}
Files skipped: {self.skipped}
Total code blocks fixed: {self.blocks_fixed}
"""
            log.write(summary)
            logger.info(summary)
        
        return {
            'total_files': len(error_files),
            'files_fixed': self.files_fixed,
            'errors': self.errors,
            'skipped': self.skipped,
            'blocks_fixed': self.blocks_fixed
        }
    
    def _parse_validation_log(self):
        """Parse validation log to extract files with syntax errors."""
        if not os.path.exists(VALIDATION_LOG):
            logger.error(f"Validation log not found: {VALIDATION_LOG}")
            return []
        
        with open(VALIDATION_LOG, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        
        # Extract syntax errors from validation log
        error_files = []
        error_pattern = r"Syntax error in ([^,]+), code block (\d+): (.+)"
        
        for match in re.finditer(error_pattern, content):
            file_path, block_index, error_message = match.groups()
            
            error_files.append({
                'file': file_path,
                'block_index': int(block_index),
                'error_type': error_message,
                'line': self._extract_line_number(error_message)
            })
        
        return error_files
    
    def _extract_line_number(self, error_message):
        """Extract line number from error message if available."""
        line_match = re.search(r'detected at line (\d+)', error_message)
        if line_match:
            return int(line_match.group(1))
        return None
    
    def _fix_file(self, file_path, error_info):
        """Fix syntax errors in a file."""
        # Read file content
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        
        # Extract code blocks
        code_blocks = self._extract_code_blocks(content)
        
        if not code_blocks:
            logger.warning(f"No code blocks found in {file_path}")
            return False
        
        # Get the target code block
        block_index = error_info['block_index']
        if block_index > len(code_blocks):
            logger.warning(f"Block index out of range: {block_index}, max: {len(code_blocks)}")
            return False
        
        # Get the code block to fix
        code_block = code_blocks[block_index - 1]
        error_type = error_info['error_type']
        error_line = error_info['line']
        
        # Apply targeted fixes based on error type
        fixed_block = self._apply_targeted_fix(code_block, error_type, error_line)
        
        if fixed_block == code_block:
            logger.info(f"No changes needed for block {block_index} in {file_path}")
            return False
        
        # Replace the code block in the content
        new_content = self._replace_code_block(content, code_block, fixed_block, block_index)
        
        # Write back to file if not in dry run mode
        if not self.dry_run:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            logger.info(f"Fixed block {block_index} in {file_path}")
        else:
            logger.info(f"Would fix block {block_index} in {file_path} (dry run)")
        
        return True
    
    def _extract_code_blocks(self, content):
        """Extract code blocks from markdown content."""
        # Split by code block markers
        parts = re.split(r'```[a-zA-Z]*\s*\n', content)
        
        if len(parts) <= 1:
            return []
        
        # Get all blocks between markers
        code_blocks = []
        for i in range(1, len(parts), 2):
            if i < len(parts):
                # Find the end marker
                block = parts[i].split('```', 1)[0] if '```' in parts[i] else parts[i]
                code_blocks.append(block)
        
        return code_blocks
    
    def _replace_code_block(self, content, original_block, fixed_block, block_index):
        """Replace a specific code block in content."""
        # Find the position of the code block
        parts = re.split(r'```[a-zA-Z]*\s*\n', content)
        
        if block_index >= len(parts):
            return content
        
        # Reconstruct content with replaced block
        new_content = parts[0]
        count = 0
        
        for i in range(1, len(parts), 2):
            if i < len(parts):
                language = ""
                # Extract language if present
                lang_match = re.search(r'```([a-zA-Z]*)\s*\n', content)
                if lang_match:
                    language = lang_match.group(1)
                
                # Increment code block counter
                count += 1
                
                if count == block_index:
                    # Replace this block
                    new_content += f"```{language}\n{fixed_block}```"
                else:
                    # Keep original
                    block = parts[i].split('```', 1)[0] if '```' in parts[i] else parts[i]
                    new_content += f"```{language}\n{block}```"
                
                # Add text between code blocks
                if i + 1 < len(parts):
                    between_text = parts[i].split('```', 1)[1] if '```' in parts[i] else ""
                    new_content += between_text
        
        return new_content
    
    def _apply_targeted_fix(self, code_block, error_type, error_line):
        """Apply targeted fix based on error type."""
        lines = code_block.split('\n')
        
        # Handle different error types
        if "unterminated string literal" in error_type:
            return self._fix_unterminated_string(lines, error_line)
        elif "invalid decimal literal" in error_type:
            return self._fix_decimal_literal(lines)
        elif "invalid syntax" in error_type:
            # Try multiple fixes in sequence
            fixed = self._fix_general_syntax(lines)
            if fixed != code_block:
                return fixed
            
            # Try other fixes if the general one didn't help
            fixed = self._fix_missing_colons(lines)
            if fixed != code_block:
                return fixed
            
            fixed = self._fix_missing_commas(lines)
            if fixed != code_block:
                return fixed
            
            # More aggressive syntax cleaning as a last resort
            return self._aggressive_syntax_clean(lines)
        
        # Default: return original if no specific fix applied
        return code_block
    
    def _fix_unterminated_string(self, lines, error_line):
        """Fix unterminated string literals."""
        if error_line and 0 < error_line <= len(lines):
            # Fix specific line
            target_line = lines[error_line - 1]
            
            # Check for unterminated quotes
            single_quotes = target_line.count("'")
            double_quotes = target_line.count('"')
            
            if single_quotes % 2 == 1:
                # Odd number of single quotes - add one at the end
                lines[error_line - 1] = target_line + "'"
            elif double_quotes % 2 == 1:
                # Odd number of double quotes - add one at the end
                lines[error_line - 1] = target_line + '"'
        else:
            # Check all lines
            for i in range(len(lines)):
                line = lines[i]
                single_quotes = line.count("'")
                double_quotes = line.count('"')
                
                if single_quotes % 2 == 1:
                    # Odd number of single quotes - add one at the end
                    lines[i] = line + "'"
                elif double_quotes % 2 == 1:
                    # Odd number of double quotes - add one at the end
                    lines[i] = line + '"'
        
        return '\n'.join(lines)
    
    def _fix_decimal_literal(self, lines):
        """Fix invalid decimal literals (e.g., leading zeros)."""
        fixed_lines = []
        
        for line in lines:
            # Replace patterns like "01" with "1", but not in strings
            in_string = False
            quote_char = None
            fixed_line = ""
            
            i = 0
            while i < len(line):
                # Handle string boundaries
                if not in_string and (line[i] == '"' or line[i] == "'"):
                    in_string = True
                    quote_char = line[i]
                    fixed_line += line[i]
                elif in_string and line[i] == quote_char and (i == 0 or line[i-1] != '\\'):
                    in_string = False
                    fixed_line += line[i]
                # Fix decimal literals outside strings
                elif not in_string and i + 1 < len(line) and line[i] == '0' and line[i+1].isdigit():
                    # Check if this is part of a valid construct (like 0.5 or 0x5)
                    if i + 2 < len(line) and line[i+1] == '.' and line[i+2].isdigit():
                        # This is a valid decimal like 0.5
                        fixed_line += line[i]
                    elif i + 2 < len(line) and line[i+1] in ['x', 'b', 'o']:
                        # This is a hex/binary/octal literal
                        fixed_line += line[i]
                    else:
                        # This is an invalid decimal with leading 0
                        # Skip the 0 and just use the digit
                        fixed_line += ""
                else:
                    fixed_line += line[i]
                
                i += 1
            
            fixed_lines.append(fixed_line)
        
        return '\n'.join(fixed_lines)
    
    def _fix_general_syntax(self, lines):
        """Fix common syntax errors."""
        # Join lines to handle multi-line issues
        code = '\n'.join(lines)
        
        # 1. Fix unclosed parentheses, brackets, and braces
        paren_count = code.count('(') - code.count(')')
        bracket_count = code.count('[') - code.count(']')
        brace_count = code.count('{') - code.count('}')
        
        # Add missing closing symbols
        if paren_count > 0:
            code += ')' * paren_count
        if bracket_count > 0:
            code += ']' * bracket_count
        if brace_count > 0:
            code += '}' * brace_count
        
        # 2. Fix common syntax issues with imports
        code = re.sub(r'import\s+([a-zA-Z0-9_]+)\s+([a-zA-Z0-9_]+)', r'import \1 as \2', code)
        
        # 3. Fix missing semicolons in JS/Java code
        if any(keyword in code for keyword in ['var ', 'let ', 'const ', 'function ', 'class ']):
            lines = code.split('\n')
            for i in range(len(lines)):
                # Add semicolons to statement-ending lines
                if (re.search(r'(var|let|const)\s+\w+\s*=\s*.+[^;]$', lines[i]) or
                    re.search(r'\w+\s*=\s*.+[^;]$', lines[i]) or
                    re.search(r'\w+\(\)$', lines[i])):
                    lines[i] += ';'
            code = '\n'.join(lines)
        
        return code
    
    def _fix_missing_colons(self, lines):
        """Fix missing colons in Python code blocks."""
        fixed_lines = []
        
        for line in lines:
            # Check for Python control structures without colons
            if re.match(r'^\s*(if|elif|else|for|while|def|class|try|except|finally)\b.*\S+\s*$', line) and not line.rstrip().endswith(':'):
                # Add colon at the end
                fixed_lines.append(line + ':')
            else:
                fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def _fix_missing_commas(self, lines):
        """Fix missing commas in lists, dictionaries, and function calls."""
        fixed_lines = lines.copy()
        in_container = False
        container_type = None
        
        for i in range(len(fixed_lines) - 1):
            current_line = fixed_lines[i].rstrip()
            next_line = fixed_lines[i + 1].strip()
            
            # Detect container context
            for char in current_line:
                if char in '([{':
                    in_container = True
                    container_type = char
                elif char in ')]}':
                    if (container_type == '(' and char == ')') or \
                       (container_type == '[' and char == ']') or \
                       (container_type == '{' and char == '}'):
                        in_container = False
                        container_type = None
            
            # Check if comma needed
            if in_container and current_line and next_line and \
               not current_line.endswith((',', ':', '[', '{', '(', '.')) and \
               not next_line.startswith((')', ']', '}', ',')):
                fixed_lines[i] = current_line + ','
        
        return '\n'.join(fixed_lines)
    
    def _aggressive_syntax_clean(self, lines):
        """Aggressively clean syntax as a last resort."""
        # Join all lines
        code = '\n'.join(lines)
        
        # Replace problematic characters and patterns
        code = re.sub(r'([^\\])"([^"]*?)([^\\])"', r'\1"\2\3"', code)  # Fix double quotes
        code = re.sub(r"([^\\])'([^']*?)([^\\])'", r"\1'\2\3'", code)  # Fix single quotes
        
        # Remove any remaining syntax error triggers
        code = re.sub(r'([^\w\s])(\s*)(\1+)', r'\1', code)  # Remove repeated symbols
        
        # Normalize operators
        code = re.sub(r'\s+([=+\-*/])\s+', r' \1 ', code)
        
        # Ensure proper spacing around operators
        code = re.sub(r'([a-zA-Z0-9_])([\+\-\*/=])([a-zA-Z0-9_])', r'\1 \2 \3', code)
        
        # Fix common Python syntax issues
        code = re.sub(r'print\s+([^(].*)', r'print(\1)', code)  # Add parentheses to print
        
        # Add missing colons to all potential block starters
        lines = code.split('\n')
        for i in range(len(lines)):
            if re.match(r'^\s*(if|elif|else|for|while|def|class|try|except|finally)\b.*\S+\s*$', lines[i]) and not lines[i].rstrip().endswith(':'):
                lines[i] = lines[i] + ':'
        
        return '\n'.join(lines)


def main():
    """Main function to run the script."""
    parser = argparse.ArgumentParser(description='Enhanced syntax fixer for documentation code blocks')
    parser.add_argument('--dry-run', action='store_true', help='Do not make actual changes')
    parser.add_argument('--repo-root', default=REPO_ROOT, help='Path to repository root')
    args = parser.parse_args()
    
    logger.info("=" * 80)
    logger.info("ENHANCED SYNTAX FIXER STARTING")
    logger.info("=" * 80)
    
    fixer = EnhancedSyntaxFixer(repo_root=args.repo_root, dry_run=args.dry_run)
    results = fixer.run()
    
    logger.info("=" * 80)
    logger.info(f"ENHANCED FIXER COMPLETE! Fixed {results['files_fixed']} files with {results['blocks_fixed']} code blocks")
    logger.info("=" * 80)
    
    # Run validation script to verify fixes
    try:
        logger.info("Running validation script to verify fixes...")
        validation_script = os.path.join(args.repo_root, 'scripts', 'validate_docs.py')
        
        if os.path.exists(validation_script):
            import subprocess
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
