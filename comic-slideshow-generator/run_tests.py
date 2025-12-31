"""
Test runner script for Comic Slideshow Generator
Runs pytest with coverage reporting
"""
import subprocess
import sys
from pathlib import Path


def run_tests(coverage: bool = True, verbose: bool = True):
    """
    Run test suite with optional coverage
    
    Args:
        coverage: Generate coverage report
        verbose: Verbose output
    
    Returns:
        Exit code from pytest
    """
    args = ["pytest"]
    
    if verbose:
        args.append("-v")
    
    if coverage:
        args.extend([
            "--cov=src",
            "--cov-report=html",
            "--cov-report=term",
            "--cov-fail-under=80"
        ])
    
    # Add test directory
    args.append("tests/")
    
    print(f"Running: {' '.join(args)}")
    print("=" * 60)
    
    result = subprocess.run(args, cwd=Path(__file__).parent)
    
    if coverage:
        print("\n" + "=" * 60)
        print("Coverage report generated: htmlcov/index.html")
        print("=" * 60)
    
    return result.returncode


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Run Comic Slideshow Generator tests"
    )
    parser.add_argument(
        "--no-coverage",
        action="store_true",
        help="Disable coverage reporting"
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Quiet output"
    )
    parser.add_argument(
        "-k", "--keyword",
        help="Only run tests matching keyword"
    )
    
    args = parser.parse_args()
    
    # Build pytest arguments
    pytest_args = ["pytest"]
    
    if not args.quiet:
        pytest_args.append("-v")
    
    if not args.no_coverage:
        pytest_args.extend([
            "--cov=src",
            "--cov-report=html",
            "--cov-report=term"
        ])
    
    if args.keyword:
        pytest_args.extend(["-k", args.keyword])
    
    pytest_args.append("tests/")
    
    # Run tests
    result = subprocess.run(pytest_args, cwd=Path(__file__).parent)
    
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
