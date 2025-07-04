"""
Import Patcher Script
====================

This script modifies Python files to handle missing dependencies gracefully.
It specifically adds try/except blocks around problematic imports and substitutes
mock modules when the real ones aren't available.
"""

import os
import re
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("patch_imports.log", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("import-patcher")

# Constants
REPO_ROOT = Path(__file__).parent.parent
SRC_DIR = REPO_ROOT / "src"
TESTS_DIR = REPO_ROOT / "tests"
MOCK_MODULES_DIR = SRC_DIR / "mock_modules"

# Dependencies to patch
DEPENDENCIES_TO_PATCH = [
    "tensorflow",
    "cv2",
    "qiskit",
    "speech_recognition",
    "librosa",
    "torch",
]

# Mapping from real modules to mock modules
MOCK_MODULE_MAP = {
    "tensorflow": "src.mock_modules.tensorflow",
}

def find_py_files(directory):
    """Find all Python files in a directory recursively."""
    py_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                py_files.append(os.path.join(root, file))
    return py_files

def patch_imports(file_path):
    """Patch import statements in a file to handle missing dependencies."""
    logger.info(f"Patching imports in {file_path}")
    
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        
        original_content = content
        patched = False
        
        # Look for direct imports of dependencies to patch
        for dependency in DEPENDENCIES_TO_PATCH:
            # Pattern for simple import statements
            pattern1 = rf"^import\s+{dependency}(?:\s+as\s+(\w+))?(.*)$"
            # Pattern for from ... import statements
            pattern2 = rf"^from\s+{dependency}(?:\.\w+)?\s+import\s+(.*)$"
            
            # Process simple imports
            for match in re.finditer(pattern1, content, re.MULTILINE):
                alias = match.group(1) or dependency
                rest_of_line = match.group(2) or ""
                
                # Create a try/except block
                if dependency in MOCK_MODULE_MAP:
                    replacement = f"""try:
    import {dependency}{' as ' + alias if alias != dependency else ''}{rest_of_line}
except (ImportError, ModuleNotFoundError):
    import sys
    from pathlib import Path
    # Add mock modules to path
    mock_path = Path(__file__).parent.parent / "src" / "mock_modules"
    if mock_path.exists() and str(mock_path) not in sys.path:
        sys.path.insert(0, str(mock_path))
    import {dependency}{' as ' + alias if alias != dependency else ''}{rest_of_line}
    print(f"Using mock {dependency} module")
"""
                else:
                    replacement = f"""try:
    import {dependency}{' as ' + alias if alias != dependency else ''}{rest_of_line}
except (ImportError, ModuleNotFoundError):
    print(f"Warning: {dependency} module not available. Some functionality may be limited.")
    {alias} = None{rest_of_line}
"""
                
                content = content.replace(match.group(0), replacement)
                patched = True
            
            # Process from ... import statements
            for match in re.finditer(pattern2, content, re.MULTILINE):
                imports = match.group(1)
                
                # Create a try/except block
                if dependency in MOCK_MODULE_MAP:
                    replacement = f"""try:
    from {dependency} import {imports}
except (ImportError, ModuleNotFoundError):
    import sys
    from pathlib import Path
    # Add mock modules to path
    mock_path = Path(__file__).parent.parent / "src" / "mock_modules"
    if mock_path.exists() and str(mock_path) not in sys.path:
        sys.path.insert(0, str(mock_path))
    from {dependency} import {imports}
    print(f"Using mock {dependency} module")
"""
                else:
                    replacement = f"""try:
    from {dependency} import {imports}
except (ImportError, ModuleNotFoundError):
    print(f"Warning: {dependency} module not available. Some functionality may be limited.")
    # Creating empty placeholder objects for imported items
    import types
    {', '.join([f'{item.strip()} = types.SimpleNamespace()' for item in imports.split(',')])}
"""
                
                content = content.replace(match.group(0), replacement)
                patched = True
        
        # Add mock modules setup at the top of test files if they import patched dependencies
        if any(f"import {dep}" in content or f"from {dep}" in content for dep in DEPENDENCIES_TO_PATCH):
            if "import sys" not in content.split("\n")[:10]:
                setup_code = """import sys
from pathlib import Path

# Add mock modules to path if available
mock_path = Path(__file__).parent.parent / "src" / "mock_modules"
if mock_path.exists() and str(mock_path) not in sys.path:
    sys.path.insert(0, str(mock_path))

"""
                # Insert after any module docstrings or shebang lines
                doc_end = content.find('"""', content.find('"""') + 3) if '"""' in content else -1
                if doc_end > 0:
                    insert_point = content.find('\n', doc_end) + 1
                    content = content[:insert_point] + setup_code + content[insert_point:]
                else:
                    # Insert at the beginning, respecting any shebang
                    if content.startswith('#!'):
                        first_newline = content.find('\n') + 1
                        content = content[:first_newline] + '\n' + setup_code + content[first_newline:]
                    else:
                        content = setup_code + content
                patched = True
        
        # Save the file if it was modified
        if patched and content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            logger.info(f"✓ Patched imports in {file_path}")
            return True
        else:
            logger.info(f"No imports needed patching in {file_path}")
            return False
    
    except Exception as e:
        logger.error(f"Error patching {file_path}: {e}")
        return False

def main():
    """Main function."""
    logger.info("Starting import patching")
    
    # Make sure mock modules directory exists
    MOCK_MODULES_DIR.mkdir(exist_ok=True)
    
    # Patch all Python files in tests
    patched_count = 0
    
    for file_path in find_py_files(TESTS_DIR):
        if patch_imports(file_path):
            patched_count += 1
    
    logger.info(f"Patched imports in {patched_count} files")
    return patched_count

if __name__ == "__main__":
    main()
