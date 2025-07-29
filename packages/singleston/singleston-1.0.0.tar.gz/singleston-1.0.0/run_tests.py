# Test runner script for C++ Exporter
# Provides an alternative way to run tests with additional options

import sys
import unittest
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def run_tests(pattern='test_*.py', verbosity=2, failfast=False):
    """Run the test suite with specified options."""
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = str(project_root / 'tests')
    suite = loader.discover(start_dir, pattern=pattern)

    runner = unittest.TextTestRunner(
        verbosity=verbosity,
        failfast=failfast,
        buffer=True  # Capture stdout/stderr
    )

    result = runner.run(suite)
    return result.wasSuccessful()


def main():
    """Main entry point for test runner."""
    import argparse

    parser = argparse.ArgumentParser(description='Run C++ Exporter tests')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Verbose output')
    parser.add_argument('-f', '--failfast', action='store_true',
                        help='Stop on first failure')
    parser.add_argument('-p', '--pattern', default='test_*.py',
                        help='Test file pattern (default: test_*.py)')
    parser.add_argument('--list', action='store_true',
                        help='List available tests')

    args = parser.parse_args()

    if args.list:
        # List all test files
        test_dir = project_root / 'tests'
        test_files = list(test_dir.glob(args.pattern))
        print("Available test files:")
        for test_file in sorted(test_files):
            print(f"  {test_file.name}")
        return True

    verbosity = 2 if args.verbose else 1
    success = run_tests(
        pattern=args.pattern,
        verbosity=verbosity,
        failfast=args.failfast
    )

    return success


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
