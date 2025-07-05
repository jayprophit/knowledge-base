#!/usr/bin/env python3
"""
Targeted Manual Fixer for Persistent Documentation Code Block Issues
===================================================================

This script addresses specific persistent syntax errors in identified problematic files
through manual, targeted fixes. Rather than applying generic rules, it contains
hand-crafted fixes for each problematic file based on the specific error patterns.

Usage:
    python targeted_manual_fixer.py [--dry-run]
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
        logging.FileHandler("targeted_manual_fix_log.log")
    ]
)
logger = logging.getLogger(__name__)

# Constants
REPO_ROOT = Path(__file__).parent.parent
OUTPUT_FILE = REPO_ROOT / "targeted_manual_fix_results.log"

# Define specific file fixes
FILE_SPECIFIC_FIXES = {
    # Format: 
    # 'relative/path/to/file.md': {
    #     'block_index': block_index,
    #     'error': 'error description',
    #     'fix_function': function_to_apply_fix
    # }
    'docs/ai/emotional_intelligence/SELF_AWARENESS.md': [
        {
            'block_index': 2,
            'error': 'unterminated string literal',
            'fix': lambda content: re.sub(r'([^\\])"([^"]*?)$', r'\1"\2"', content)
        },
        {
            'block_index': 4,
            'error': 'unterminated string literal',
            'fix': lambda content: re.sub(r'([^\\])"([^"]*?)$', r'\1"\2"', content)
        },
        {
            'block_index': 5,
            'error': 'invalid syntax',
            'fix': lambda content: content.replace('if emotion_detected', 'if emotion_detected:')
                                          .replace('elif self_aware', 'elif self_aware:')
        }
    ],
    'docs/ai/guides/multilingual_understanding.md': [
        {
            'block_index': 6,
            'error': 'unterminated string literal',
            'fix': lambda content: re.sub(r'([^\\])"([^"]*?)$', r'\1"\2"', content)
        }
    ],
    'docs/ai/guides/multimodal_integration.md': [
        {
            'block_index': 2,
            'error': 'invalid syntax',
            'fix': lambda content: content.replace('def process_multimodal_data(', 'def process_multimodal_data(visual_data, audio_data, text_data):')
        },
        {
            'block_index': 5,
            'error': 'invalid syntax',
            'fix': lambda content: content.replace('class MultimodalFusion', 'class MultimodalFusion:')
        }
    ],
    'docs/ai/multidisciplinary/integration.md': [
        {
            'block_index': 1,
            'error': 'invalid syntax',
            'fix': lambda content: content.replace('def integrate_disciplines(', 'def integrate_disciplines(disciplines):')
        }
    ],
    'docs/ai/virtual_brain/02_cognitive_functions.md': [
        {
            'block_index': 1,
            'error': 'invalid syntax',
            'fix': lambda content: content.replace('class CognitiveArchitecture', 'class CognitiveArchitecture:')
        },
        {
            'block_index': 2,
            'error': 'invalid syntax',
            'fix': lambda content: content.replace('def process_sensory_input(', 'def process_sensory_input(self, input_data):')
        },
        {
            'block_index': 3,
            'error': 'invalid syntax',
            'fix': lambda content: content.replace('def working_memory(', 'def working_memory(self, items):')
        },
        {
            'block_index': 4,
            'error': 'invalid syntax',
            'fix': lambda content: content.replace('def long_term_memory_store(', 'def long_term_memory_store(self, memory):')
        },
        {
            'block_index': 5,
            'error': 'invalid syntax',
            'fix': lambda content: content.replace('def decision_making(', 'def decision_making(self, options):')
        }
    ],
    'docs/ai/virtual_brain/03_python_implementation.md': [
        {
            'block_index': 1,
            'error': 'invalid syntax',
            'fix': lambda content: content.replace('class NeuralNetwork', 'class NeuralNetwork:')
        }
    ]
}

class TargetedManualFixer:
    """Manually fix specific problematic files with custom fixes."""
    
    def __init__(self, repo_root=REPO_ROOT, dry_run=False):
        """Initialize with repository root path and dry run flag."""
        self.repo_root = Path(repo_root)
        self.dry_run = dry_run
        self.files_fixed = 0
        self.blocks_fixed = 0
        self.errors = 0
        self.skipped = 0
    
    def run(self):
        """Run the targeted manual fixer."""
        logger.info(f"Starting targeted manual fixer on {self.repo_root}")
        logger.info("Dry run mode: %s", "ON" if self.dry_run else "OFF")
        
        with open(OUTPUT_FILE, "w", encoding="utf-8") as log:
            log.write(f"=== Targeted Manual Fix Results ===\n\n")
            
            # Process each file with known issues
            for rel_path, fixes in FILE_SPECIFIC_FIXES.items():
                file_path = self.repo_root / rel_path
                
                if not file_path.exists():
                    error_msg = f"File not found: {file_path}"
                    logger.error(error_msg)
                    log.write(f"{error_msg}\n")
                    self.errors += 1
                    continue
                
                log.write(f"Processing: {file_path}\n")
                logger.info(f"Processing: {file_path}")
                
                try:
                    # Read file content
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                    
                    # Apply all fixes for this file
                    updated_content = content
                    blocks_fixed = 0
                    
                    for fix_info in fixes:
                        block_index = fix_info['block_index']
                        error_type = fix_info['error']
                        fix_function = fix_info['fix']
                        
                        log.write(f"  - Block: {block_index}, Error: {error_type}\n")
                        logger.info(f"  - Block: {block_index}, Error: {error_type}")
                        
                        # Extract code blocks
                        code_blocks = self._extract_code_blocks(updated_content)
                        
                        if not code_blocks or block_index > len(code_blocks):
                            log.write(f"  ✗ Block {block_index} not found\n")
                            logger.warning(f"Block {block_index} not found in {file_path}")
                            self.skipped += 1
                            continue
                        
                        # Get the code block to fix
                        code_block = code_blocks[block_index - 1]
                        
                        # Apply the custom fix function
                        fixed_block = fix_function(code_block)
                        
                        if fixed_block == code_block:
                            log.write(f"  ✗ No changes needed\n")
                            logger.info(f"No changes needed for block {block_index} in {file_path}")
                            self.skipped += 1
                            continue
                        
                        # Replace the code block in the content
                        updated_content = self._replace_code_block(updated_content, code_block, fixed_block, block_index)
                        blocks_fixed += 1
                        self.blocks_fixed += 1
                        
                        log.write(f"  ✓ Fixed\n")
                        logger.info(f"Fixed block {block_index} in {file_path}")
                    
                    # Write back to file if not in dry run mode and something was fixed
                    if blocks_fixed > 0:
                        if not self.dry_run:
                            with open(file_path, "w", encoding="utf-8") as f:
                                f.write(updated_content)
                            log.write(f"  ✓ File updated with {blocks_fixed} fixes\n")
                            logger.info(f"File {file_path} updated with {blocks_fixed} fixes")
                            self.files_fixed += 1
                        else:
                            log.write(f"  ✓ Would update file with {blocks_fixed} fixes (dry run)\n")
                            logger.info(f"Would update file {file_path} with {blocks_fixed} fixes (dry run)")
                    else:
                        log.write(f"  ✗ No blocks fixed in this file\n")
                        logger.info(f"No blocks fixed in {file_path}")
                        self.skipped += 1
                
                except Exception as e:
                    self.errors += 1
                    error_msg = f"  ✗ Error processing {file_path}: {str(e)}"
                    logger.error(error_msg)
                    log.write(f"{error_msg}\n")
            
            # Write summary
            summary = f"""
=== Summary ===
Files with known issues: {len(FILE_SPECIFIC_FIXES)}
Files fixed: {self.files_fixed}
Files with errors: {self.errors}
Files skipped: {self.skipped}
Total code blocks fixed: {self.blocks_fixed}
"""
            log.write(summary)
            logger.info(summary)
        
        return {
            'total_files': len(FILE_SPECIFIC_FIXES),
            'files_fixed': self.files_fixed,
            'errors': self.errors,
            'skipped': self.skipped,
            'blocks_fixed': self.blocks_fixed
        }
    
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


def main():
    """Main function to run the script."""
    parser = argparse.ArgumentParser(description='Targeted manual fixer for persistent documentation code block issues')
    parser.add_argument('--dry-run', action='store_true', help='Do not make actual changes')
    parser.add_argument('--repo-root', default=REPO_ROOT, help='Path to repository root')
    args = parser.parse_args()
    
    logger.info("=" * 80)
    logger.info("TARGETED MANUAL FIXER STARTING")
    logger.info("=" * 80)
    
    fixer = TargetedManualFixer(repo_root=args.repo_root, dry_run=args.dry_run)
    results = fixer.run()
    
    logger.info("=" * 80)
    logger.info(f"TARGETED MANUAL FIXER COMPLETE! Fixed {results['files_fixed']} files with {results['blocks_fixed']} code blocks")
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
                
                # Extract count of remaining errors
                error_match = re.search(r'ERROR: Found (\d+) errors', result.stdout or result.stderr or "")
                if error_match:
                    remaining_errors = int(error_match.group(1))
                    logger.warning(f"Remaining errors: {remaining_errors}")
                    
                    # If we've made progress, acknowledge it
                    if remaining_errors < len(sum([fixes for fixes in FILE_SPECIFIC_FIXES.values()], [])):
                        logger.info(f"Progress made! Fixed some errors, but {remaining_errors} still remain.")
        else:
            logger.warning(f"Validation script not found at {validation_script}")
    except Exception as e:
        logger.error(f"Error running validation script: {str(e)}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
