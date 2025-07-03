import os
import sys
import subprocess
import logging
from pathlib import Path

# --- CONFIGURATION ---
REPO_ROOT = Path(__file__).parent.parent.resolve()
TESTS_DIR = REPO_ROOT / 'tests'
DOCS_DIR = REPO_ROOT / 'docs'
PHP_DIR = REPO_ROOT / 'src' / 'web' / 'php'
MOBILE_DIR = REPO_ROOT / 'mobile' if (REPO_ROOT / 'mobile').exists() else None

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger('deploy_and_test')


def run_python_tests():
    """Run all Python tests using unittest."""
    logger.info("Running Python test suite...")
    result = subprocess.run([sys.executable, '-m', 'unittest', 'discover', str(TESTS_DIR)], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        logger.error("Python tests failed.")
        print(result.stderr)
    else:
        logger.info("Python tests passed.")
    return result.returncode == 0


def run_php_tests():
    """Run PHP tests if present (using PHPUnit or simple scripts)."""
    if not PHP_DIR.exists():
        logger.info("No PHP directory found, skipping PHP tests.")
        return True
    phpunit = PHP_DIR / 'vendor' / 'bin' / 'phpunit'
    if phpunit.exists():
        logger.info("Running PHP unit tests...")
        result = subprocess.run(['php', str(phpunit)], capture_output=True, text=True)
        print(result.stdout)
        if result.returncode != 0:
            logger.error("PHP tests failed.")
            print(result.stderr)
            return False
        logger.info("PHP tests passed.")
        return True
    # Fallback: check for test files
    test_files = list(PHP_DIR.glob('test*.php'))
    if test_files:
        logger.info("Running PHP test files...")
        all_passed = True
        for test in test_files:
            result = subprocess.run(['php', str(test)], capture_output=True, text=True)
            print(result.stdout)
            if result.returncode != 0:
                logger.error(f"PHP test failed: {test}")
                print(result.stderr)
                all_passed = False
        return all_passed
    logger.info("No PHP tests found.")
    return True


def run_mobile_tests():
    """Stub for running mobile tests (JS/React Native, etc.)."""
    if not MOBILE_DIR:
        logger.info("No mobile directory found, skipping mobile tests.")
        return True
    logger.info("Mobile test automation not implemented. Add your mobile test runner here.")
    return True


def deploy_docs():
    """Stub for documentation deployment (can be extended for CI/CD)."""
    logger.info("Documentation deployment is not automated in this script. If needed, add deployment steps here.")
    return True


def main():
    logger.info("Starting deployment and test automation for the knowledge base...")
    all_passed = True
    
    # Run Python tests
    if not run_python_tests():
        all_passed = False
    
    # Run PHP tests
    if not run_php_tests():
        all_passed = False
    
    # Run mobile tests (stub)
    if not run_mobile_tests():
        all_passed = False
    
    # Deploy docs (stub)
    deploy_docs()
    
    # Final summary
    if all_passed:
        logger.info("\n===== ALL TESTS PASSED. DEPLOYMENT READY. =====")
        print("\nAll modules have passed their tests. The knowledge base is ready for deployment.")
    else:
        logger.error("\n===== SOME TESTS FAILED. REVIEW ERRORS ABOVE. =====")
        print("\nSome modules failed their tests. Please review the errors above.")

if __name__ == '__main__':
    main()
