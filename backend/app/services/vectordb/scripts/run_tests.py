#!/usr/bin/env python3
"""
Test runner script for vectordb service
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))


def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}")
    print(f"Running: {' '.join(cmd)}")

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"✅ {description} - SUCCESS")
        if result.stdout:
            print(result.stdout)
    else:
        print(f"❌ {description} - FAILED")
        if result.stderr:
            print("Error:", result.stderr)
        if result.stdout:
            print("Output:", result.stdout)
        return False

    return True


def main():
    parser = argparse.ArgumentParser(description="Run vectordb service tests")
    parser.add_argument("--unit", action="store_true", help="Run only unit tests")
    parser.add_argument(
        "--integration", action="store_true", help="Run only integration tests"
    )
    parser.add_argument(
        "--coverage", action="store_true", help="Generate coverage report"
    )
    parser.add_argument(
        "--html", action="store_true", help="Generate HTML coverage report"
    )
    parser.add_argument("--parallel", action="store_true", help="Run tests in parallel")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--fast", action="store_true", help="Skip slow tests")
    parser.add_argument("--watch", action="store_true", help="Watch for file changes")
    parser.add_argument("--specific", help="Run specific test file or function")

    args = parser.parse_args()

    # Change to the vectordb service directory
    vectordb_dir = Path(__file__).resolve().parent.parent
    os.chdir(vectordb_dir)

    print(f"🧪 Running vectordb service tests from: {vectordb_dir}")

    # Base pytest command
    cmd = ["python", "-m", "pytest"]

    # Add test markers based on arguments
    if args.unit:
        cmd.extend(["-m", "unit"])
    elif args.integration:
        cmd.extend(["-m", "integration"])

    # Add coverage options
    if args.coverage or args.html:
        cmd.extend(["--cov=backend.app.services.vectordb"])
        cmd.extend(["--cov-report=term-missing"])

        if args.html:
            cmd.extend(["--cov-report=html:htmlcov"])

    # Add parallel execution
    if args.parallel:
        cmd.extend(["-n", "auto"])

    # Add verbose output
    if args.verbose:
        cmd.append("-v")
    else:
        cmd.append("-q")

    # Skip slow tests if requested
    if args.fast:
        cmd.extend(["-m", "not slow"])

    # Run specific test
    if args.specific:
        cmd.append(args.specific)
    else:
        cmd.append("tests/")

    # Watch mode
    if args.watch:
        try:
            import pytest_watch

            cmd = ["ptw"] + cmd[2:]  # Replace pytest with ptw
        except ImportError:
            print(
                "❌ pytest-watch not installed. Install with: pip install pytest-watch"
            )
            return False

    # Run the tests
    success = run_command(cmd, "Running vectordb service tests")

    if success and (args.coverage or args.html):
        print(f"\n📊 Coverage report generated")
        if args.html:
            html_path = vectordb_dir / "htmlcov" / "index.html"
            print(f"HTML coverage report: file://{html_path}")

    # Summary
    if success:
        print(f"\n🎉 All tests completed successfully!")
    else:
        print(f"\n💥 Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
