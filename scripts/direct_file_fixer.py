#!/usr/bin/env python3
"""
Direct File Fixer for Persistent Syntax Errors
=============================================

This script directly modifies specific problematic files with custom fixes
for each file. Rather than trying to parse code blocks generically, it applies
file-specific transformations to address the exact syntax issues identified
in the validation results.

Usage:
    python direct_file_fixer.py
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
        logging.FileHandler("direct_file_fix_log.log")
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

# File-specific fix functions
def fix_python_implementation(content):
    """Fix PYTHON_IMPLEMENTATION.md syntax errors."""
    # Replace invalid class declarations
    content = re.sub(r'class\s+(\w+)\s*(?=\n)', r'class \1:', content)
    
    # Replace invalid function declarations
    content = re.sub(r'def\s+(\w+)\s*\(\s*(?=\n)', r'def \1(self):\n    ', content)
    
    # Fix missing colons in if statements
    content = re.sub(r'if\s+([^:]+?)(?=\n)', r'if \1:', content)
    
    # Fix unterminated string literals
    content = re.sub(r'([^\\])"([^"]*?)$', r'\1"\2"', content, flags=re.MULTILINE)
    content = re.sub(r'([^\\])\'([^\']*?)$', r'\1\'\2\'', content, flags=re.MULTILINE)
    
    return content

def fix_self_awareness(content):
    """Fix SELF_AWARENESS.md syntax errors."""
    # Replace invalid code blocks with fixed versions
    code_blocks = extract_code_blocks(content)
    
    if len(code_blocks) >= 3:
        # Fix block 2: unterminated string literal
        block2 = code_blocks[1]
        fixed_block2 = re.sub(r'([^\\])"([^"]*?)$', r'\1"\2"', block2, flags=re.MULTILINE)
        content = replace_code_block_content(content, block2, fixed_block2)
        
        # Fix block 3: invalid syntax
        block3 = extract_code_blocks(content)[2]  # Re-extract after previous fix
        fixed_block3 = block3.replace('if emotion_detected', 'if emotion_detected:')
        fixed_block3 = fixed_block3.replace('elif self_aware', 'elif self_aware:')
        fixed_block3 = fixed_block3.replace('else', 'else:')
        content = replace_code_block_content(content, block3, fixed_block3)
    
    return content

def fix_multilingual_understanding(content):
    """Fix multilingual_understanding.md syntax errors."""
    # Fix block 6: unterminated string literal
    code_blocks = extract_code_blocks(content)
    
    if len(code_blocks) >= 6:
        block6 = code_blocks[5]
        fixed_block6 = re.sub(r'([^\\])"([^"]*?)$', r'\1"\2"', block6, flags=re.MULTILINE)
        fixed_block6 = re.sub(r'([^\\])\'([^\']*?)$', r'\1\'\2\'', fixed_block6, flags=re.MULTILINE)
        content = replace_code_block_content(content, block6, fixed_block6)
    
    return content

def fix_multimodal_integration(content):
    """Fix multimodal_integration.md syntax errors."""
    # Fix syntax errors in blocks 2 and 5
    code_blocks = extract_code_blocks(content)
    
    if len(code_blocks) >= 2:
        # Fix block 2: invalid function declaration
        block2 = code_blocks[1]
        if 'def process_multimodal_data(' in block2 and not 'def process_multimodal_data(' + ')' in block2:
            fixed_block2 = block2.replace(
                'def process_multimodal_data(',
                'def process_multimodal_data(visual_data, audio_data, text_data):'
            )
            content = replace_code_block_content(content, block2, fixed_block2)
    
    if len(code_blocks) >= 5:
        # Fix block 5: invalid class declaration
        block5 = code_blocks[4]
        if 'class MultimodalFusion' in block5 and not 'class MultimodalFusion:' in block5:
            fixed_block5 = block5.replace('class MultimodalFusion', 'class MultimodalFusion:')
            content = replace_code_block_content(content, block5, fixed_block5)
    
    return content

def fix_integration(content):
    """Fix integration.md syntax errors."""
    # Fix block 1: invalid function declaration
    code_blocks = extract_code_blocks(content)
    
    if len(code_blocks) >= 1:
        block1 = code_blocks[0]
        if 'def integrate_disciplines(' in block1:
            fixed_block1 = block1.replace(
                'def integrate_disciplines(',
                'def integrate_disciplines(disciplines):'
            )
            content = replace_code_block_content(content, block1, fixed_block1)
    
    return content

def fix_cognitive_functions(content):
    """Fix 02_cognitive_functions.md syntax errors."""
    # Fix all blocks with syntax errors
    code_blocks = extract_code_blocks(content)
    
    if len(code_blocks) >= 1:
        # Fix block 1: class declaration
        block1 = code_blocks[0]
        fixed_block1 = block1.replace('class CognitiveArchitecture', 'class CognitiveArchitecture:')
        content = replace_code_block_content(content, block1, fixed_block1)
    
    if len(code_blocks) >= 2:
        # Fix block 2: function declaration
        block2 = extract_code_blocks(content)[1]  # Re-extract after previous fix
        fixed_block2 = block2.replace(
            'def process_sensory_input(',
            'def process_sensory_input(self, input_data):'
        )
        content = replace_code_block_content(content, block2, fixed_block2)
    
    if len(code_blocks) >= 3:
        # Fix block 3: function declaration
        block3 = extract_code_blocks(content)[2]  # Re-extract after previous fixes
        fixed_block3 = block3.replace('def working_memory(', 'def working_memory(self, items):')
        content = replace_code_block_content(content, block3, fixed_block3)
    
    if len(code_blocks) >= 4:
        # Fix block 4: function declaration
        block4 = extract_code_blocks(content)[3]  # Re-extract after previous fixes
        fixed_block4 = block4.replace(
            'def long_term_memory_store(',
            'def long_term_memory_store(self, memory):'
        )
        content = replace_code_block_content(content, block4, fixed_block4)
    
    if len(code_blocks) >= 5:
        # Fix block 5: function declaration
        block5 = extract_code_blocks(content)[4]  # Re-extract after previous fixes
        fixed_block5 = block5.replace('def decision_making(', 'def decision_making(self, options):')
        content = replace_code_block_content(content, block5, fixed_block5)
    
    return content

def fix_python_implementation_vb(content):
    """Fix 03_python_implementation.md syntax errors."""
    # Fix block 1: class declaration
    code_blocks = extract_code_blocks(content)
    
    if len(code_blocks) >= 1:
        block1 = code_blocks[0]
        fixed_block1 = block1.replace('class NeuralNetwork', 'class NeuralNetwork:')
        content = replace_code_block_content(content, block1, fixed_block1)
    
    return content

# Helper functions
def extract_code_blocks(content):
    """Extract all code blocks from markdown content."""
    code_block_pattern = r'```[a-zA-Z]*\s*\n(.*?)```'
    code_blocks = []
    
    for match in re.finditer(code_block_pattern, content, re.DOTALL):
        code_blocks.append(match.group(1))
    
    return code_blocks

def replace_code_block_content(content, old_block, new_block):
    """Replace a specific code block in content."""
    # Escape special regex characters in old_block
    old_block_escaped = re.escape(old_block)
    
    # Replace the old block with the new block
    # Look for the old block surrounded by code block markers
    pattern = r'```[a-zA-Z]*\s*\n' + old_block_escaped + r'```'
    replacement = '```python\n' + new_block + '```'
    
    # Use re.sub to replace the first occurrence only
    new_content = re.sub(pattern, replacement, content, count=1, flags=re.DOTALL)
    
    return new_content

def fix_file(file_path):
    """Apply file-specific fixes to a markdown file."""
    logger.info(f"Processing {file_path}")
    
    try:
        # Read file content
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Apply file-specific fixes
        original_content = content
        
        # Choose fix function based on file path
        if "PYTHON_IMPLEMENTATION.md" in str(file_path) and "emotional_intelligence" in str(file_path):
            content = fix_python_implementation(content)
        elif "SELF_AWARENESS.md" in str(file_path):
            content = fix_self_awareness(content)
        elif "multilingual_understanding.md" in str(file_path):
            content = fix_multilingual_understanding(content)
        elif "multimodal_integration.md" in str(file_path):
            content = fix_multimodal_integration(content)
        elif "integration.md" in str(file_path) and "multidisciplinary" in str(file_path):
            content = fix_integration(content)
        elif "02_cognitive_functions.md" in str(file_path):
            content = fix_cognitive_functions(content)
        elif "03_python_implementation.md" in str(file_path) and "virtual_brain" in str(file_path):
            content = fix_python_implementation_vb(content)
        
        # Check if content was modified
        if content != original_content:
            # Write back modified content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"✅ Fixed {file_path}")
            return True
        else:
            logger.info(f"⚠️ No changes made to {file_path}")
            return False
    
    except Exception as e:
        logger.error(f"❌ Error fixing {file_path}: {str(e)}")
        return False

def main():
    """Main function to run the script."""
    logger.info("=" * 80)
    logger.info("DIRECT FILE FIXER STARTING")
    logger.info("=" * 80)
    
    fixed_count = 0
    
    # Process each problematic file
    for file_path in PROBLEMATIC_FILES:
        if fix_file(file_path):
            fixed_count += 1
    
    logger.info("=" * 80)
    logger.info(f"DIRECT FILE FIXER COMPLETE! Fixed {fixed_count} out of {len(PROBLEMATIC_FILES)} files")
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
        else:
            logger.warning(f"Validation script not found at {validation_script}")
    except Exception as e:
        logger.error(f"Error running validation script: {str(e)}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
