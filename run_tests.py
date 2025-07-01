#!/usr/bin/env python3
"""
Test runner for the knowledge base project.
"""

import unittest
import sys
import os
from pathlib import Path

def run_tests():
    """Run all tests in the tests directory."""
    # Add the project root to the Python path
    project_root = str(Path(__file__).parent)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    # Discover and run tests
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover(
        start_dir=os.path.join(project_root, 'tests'),
        pattern='test_*.py',
        top_level_dir=project_root
    )
    
    # Run the tests
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    # Return appropriate exit code
    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
    sys.exit(run_tests())
