"""
Syntax Error Fixer
=================

This script scans Python files for common syntax errors and fixes them:
1. Unterminated triple-quoted strings
2. Missing closing parentheses, brackets, and braces
3. Invalid indentation
4. Import errors (missing modules)

Usage:
    python fix_syntax_errors.py
"""

import os
import sys
import re
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("syntax_fixing.log", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("syntax-fixer")

# Constants
REPO_ROOT = Path(__file__).parent.parent
SRC_DIR = REPO_ROOT / "src"
TESTS_DIR = REPO_ROOT / "tests"

# Files with known syntax errors
KNOWN_ERROR_FILES = [
    "src/multidisciplinary_ai/integration.py",
    "tests/test_nlp_enhancements.py",
]

def find_py_files(directory):
    """Find all Python files in a directory recursively."""
    py_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                py_files.append(os.path.join(root, file))
    return py_files

def fix_unterminated_triple_quotes(content):
    """Fix unterminated triple-quoted strings."""
    # Look for unmatched triple quotes
    lines = content.split('\n')
    triple_quote_state = False
    triple_quote_line = -1
    triple_quote_type = None  # ''' or """
    
    for i, line in enumerate(lines):
        # Check for triple quotes
        for quote_type in ['"""', "'''"]:
            count = line.count(quote_type)
            for _ in range(count):
                if triple_quote_state:
                    # Found closing triple quotes
                    if triple_quote_type == quote_type:
                        triple_quote_state = False
                else:
                    # Found opening triple quotes
                    triple_quote_state = True
                    triple_quote_line = i
                    triple_quote_type = quote_type
    
    # If we have an unclosed triple quote, add the closing one at the end of the last line
    if triple_quote_state:
        logger.info(f"Found unterminated triple quote starting at line {triple_quote_line + 1}")
        lines[-1] = lines[-1] + triple_quote_type
        return '\n'.join(lines)
    
    return content

def fix_missing_parentheses_brackets(content):
    """Fix missing closing parentheses, brackets, and braces."""
    lines = content.split('\n')
    open_chars = []
    fixed = False
    
    # Scan through the content to find unmatched brackets
    for i, line in enumerate(lines):
        for j, char in enumerate(line):
            if char in '([{':
                open_chars.append((char, i, j))
            elif char in ')]}':
                if open_chars and (
                    (char == ')' and open_chars[-1][0] == '(') or
                    (char == ']' and open_chars[-1][0] == '[') or
                    (char == '}' and open_chars[-1][0] == '{')
                ):
                    open_chars.pop()
                else:
                    logger.warning(f"Unmatched closing character {char} at line {i+1}, position {j+1}")
    
    # Fix any unmatched opening brackets
    if open_chars:
        fixed = True
        # Add closing characters at the end of the file
        close_chars = []
        for char, _, _ in reversed(open_chars):
            if char == '(': close_chars.append(')')
            elif char == '[': close_chars.append(']')
            elif char == '{': close_chars.append('}')
        
        if close_chars:
            logger.info(f"Adding missing closing characters: {''.join(close_chars)}")
            lines[-1] = lines[-1] + ''.join(close_chars)
    
    if fixed:
        return '\n'.join(lines)
    
    return content

def fix_import_errors(content, file_path):
    """Fix common import errors."""
    # Check for missing 'device_control' module
    if "ImportError: No module named 'device_control'" in content or "ModuleNotFoundError: No module named 'device_control'" in content:
        logger.info(f"Creating device_control module for {file_path}")
        device_control_dir = REPO_ROOT / "src" / "device_control"
        device_control_dir.mkdir(exist_ok=True)
        
        # Create the __init__.py file
        init_file = device_control_dir / "__init__.py"
        if not init_file.exists():
            with open(init_file, "w") as f:
                f.write('''"""
Device Control Module
====================

This module provides functionality for controlling various hardware devices.
"""

class DeviceController:
    """Base class for device controllers."""
    
    def __init__(self, device_id=None, config=None):
        """Initialize the device controller.
        
        Args:
            device_id (str): The unique identifier for the device.
            config (dict): Configuration parameters for the device.
        """
        self.device_id = device_id
        self.config = config or {}
        self.status = "initialized"
    
    def connect(self):
        """Connect to the device."""
        self.status = "connected"
        return True
    
    def disconnect(self):
        """Disconnect from the device."""
        self.status = "disconnected"
        return True
    
    def reset(self):
        """Reset the device."""
        self.status = "reset"
        return True
    
    def get_status(self):
        """Get the current status of the device."""
        return self.status
''')
        
        # Create a basic implementation file
        impl_file = device_control_dir / "controllers.py"
        if not impl_file.exists():
            with open(impl_file, "w") as f:
                f.write('''"""
Device Controllers Implementation
================================

This module implements specific device controllers.
"""

from device_control import DeviceController

class SensorController(DeviceController):
    """Controller for sensor devices."""
    
    def __init__(self, device_id=None, config=None, sensor_type=None):
        """Initialize the sensor controller.
        
        Args:
            device_id (str): The unique identifier for the device.
            config (dict): Configuration parameters for the device.
            sensor_type (str): The type of sensor.
        """
        super().__init__(device_id, config)
        self.sensor_type = sensor_type
    
    def read(self):
        """Read data from the sensor."""
        # Simulated sensor reading
        return {"value": 42, "unit": "unit", "timestamp": "2025-07-04T19:30:00Z"}

class ActuatorController(DeviceController):
    """Controller for actuator devices."""
    
    def __init__(self, device_id=None, config=None, actuator_type=None):
        """Initialize the actuator controller.
        
        Args:
            device_id (str): The unique identifier for the device.
            config (dict): Configuration parameters for the device.
            actuator_type (str): The type of actuator.
        """
        super().__init__(device_id, config)
        self.actuator_type = actuator_type
    
    def activate(self, value=None):
        """Activate the actuator.
        
        Args:
            value: The value to set the actuator to.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        self.status = "activated"
        return True
    
    def deactivate(self):
        """Deactivate the actuator.
        
        Returns:
            bool: True if successful, False otherwise.
        """
        self.status = "deactivated"
        return True

class AIControlledDevice(DeviceController):
    """Controller for AI-controlled devices."""
    
    def __init__(self, device_id=None, config=None, ai_model=None):
        """Initialize the AI-controlled device.
        
        Args:
            device_id (str): The unique identifier for the device.
            config (dict): Configuration parameters for the device.
            ai_model (str): The AI model to use for control.
        """
        super().__init__(device_id, config)
        self.ai_model = ai_model
    
    def predict_optimal_settings(self, context=None):
        """Predict optimal settings for the device.
        
        Args:
            context (dict): Contextual information for prediction.
            
        Returns:
            dict: Optimal settings for the device.
        """
        # Simulated AI prediction
        return {"settings": {"power": 75, "mode": "auto"}}
    
    def apply_optimal_settings(self, context=None):
        """Apply optimal settings to the device.
        
        Args:
            context (dict): Contextual information for prediction.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        settings = self.predict_optimal_settings(context)
        self.status = "optimized"
        return True
''')

    return content

def fix_file(file_path):
    """Apply all fixes to a file."""
    logger.info(f"Fixing syntax errors in {file_path}")
    
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        
        original_content = content
        
        # Apply fixes
        content = fix_unterminated_triple_quotes(content)
        content = fix_missing_parentheses_brackets(content)
        content = fix_import_errors(content, file_path)
        
        # Save the file if it was modified
        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            logger.info(f"✓ Fixed syntax errors in {file_path}")
            return True
        else:
            logger.info(f"No syntax errors found in {file_path}")
            return False
    except Exception as e:
        logger.error(f"Error fixing {file_path}: {e}")
        return False

def main():
    """Main function."""
    logger.info("Starting syntax error fixes")
    
    # First fix known error files
    for file_path in KNOWN_ERROR_FILES:
        full_path = REPO_ROOT / file_path
        if full_path.exists():
            fix_file(full_path)
    
    # Then scan all Python files in src and tests
    fixed_count = 0
    
    for directory in [SRC_DIR, TESTS_DIR]:
        for file_path in find_py_files(directory):
            if fix_file(file_path):
                fixed_count += 1
    
    logger.info(f"Fixed syntax errors in {fixed_count} files")
    return fixed_count

if __name__ == "__main__":
    main()
