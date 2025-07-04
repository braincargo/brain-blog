#!/usr/bin/env python3
"""
Test runner for Brain Blog Generator unit tests.

This script discovers and runs all unit tests, provides coverage reports,
and can be used in CI/CD pipelines.
"""

import unittest
import sys
import os
from typing import List

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def discover_tests() -> unittest.TestSuite:
    """
    Discover all test modules in the tests directory.
    
    Returns:
        TestSuite containing all discovered tests
    """
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(__file__)
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    return suite


def run_tests_with_coverage() -> int:
    """
    Run tests with coverage reporting.
    
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    try:
        import coverage
        
        # Initialize coverage
        cov = coverage.Coverage(
            source=['config', 'pipeline', 'providers'],
            omit=['*/tests/*', '*/test_*', '*/__pycache__/*']
        )
        cov.start()
        
        # Run tests
        suite = discover_tests()
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        # Stop coverage and generate report
        cov.stop()
        cov.save()
        
        print("\n" + "="*60)
        print("COVERAGE REPORT")
        print("="*60)
        cov.report()
        
        # Generate HTML coverage report
        try:
            cov.html_report(directory='tests/coverage_html')
            print(f"\nHTML coverage report generated in: tests/coverage_html/index.html")
        except Exception as e:
            print(f"Could not generate HTML report: {e}")
        
        return 0 if result.wasSuccessful() else 1
        
    except ImportError:
        print("Coverage module not available. Running tests without coverage...")
        return run_tests_simple()


def run_tests_simple() -> int:
    """
    Run tests without coverage reporting.
    
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    suite = discover_tests()
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1


def run_specific_test_module(module_name: str) -> int:
    """
    Run tests from a specific module.
    
    Args:
        module_name: Name of the test module (e.g., 'test_config')
        
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    try:
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromName(module_name)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return 0 if result.wasSuccessful() else 1
        
    except Exception as e:
        print(f"Error running test module '{module_name}': {e}")
        return 1


def list_test_modules() -> List[str]:
    """
    List all available test modules.
    
    Returns:
        List of test module names
    """
    test_dir = os.path.dirname(__file__)
    modules = []
    
    for filename in os.listdir(test_dir):
        if filename.startswith('test_') and filename.endswith('.py'):
            module_name = filename[:-3]  # Remove .py extension
            modules.append(module_name)
    
    return sorted(modules)


def main():
    """Main test runner function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run Brain Blog Generator tests')
    parser.add_argument(
        '--module', '-m',
        help='Run tests from a specific module (e.g., test_config)'
    )
    parser.add_argument(
        '--list', '-l',
        action='store_true',
        help='List available test modules'
    )
    parser.add_argument(
        '--no-coverage',
        action='store_true',
        help='Skip coverage reporting'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    if args.list:
        modules = list_test_modules()
        print("Available test modules:")
        for module in modules:
            print(f"  - {module}")
        return 0
    
    if args.module:
        print(f"Running tests from module: {args.module}")
        return run_specific_test_module(args.module)
    
    print("Discovering and running all tests...")
    print("="*60)
    
    if args.no_coverage:
        return run_tests_simple()
    else:
        return run_tests_with_coverage()


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code) 