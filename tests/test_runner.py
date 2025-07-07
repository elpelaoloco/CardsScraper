#!/usr/bin/env python3

import subprocess
import sys
import argparse
from pathlib import Path
from datetime import datetime


def run_pytest_command(args):
    cmd = ["python", "-m", "pytest"]

    if args.verbose:
        cmd.append("-v")

    if args.s:
        cmd.append("-s")

    cmd.extend(["--tb", args.tb])

    if not args.no_coverage:
        cmd.extend([
            "--cov=src",
            "--cov-report=html:htmlcov",
            "--cov-report=term-missing",
            "--cov-report=xml:coverage.xml",
            f"--cov-fail-under={args.coverage_threshold}"
        ])

    if args.unit_only:
        cmd.extend(["-m", "unit"])
    elif args.integration_only:
        cmd.extend(["-m", "integration"])
    elif args.markers:
        cmd.extend(["-m", args.markers])

    if args.include_slow:
        cmd.append("--runslow")

    if args.test_paths:
        cmd.extend(args.test_paths)
    else:
        tests_dir = Path("tests")
        if tests_dir.exists():
            cmd.append("tests/")
        else:
            test_files = list(Path(".").glob("test_*.py"))
            if test_files:
                cmd.extend([str(f) for f in test_files])
            else:
                tests_dir.mkdir(exist_ok=True)
                (tests_dir / "__init__.py").touch()
    return cmd


def main():
    parser = argparse.ArgumentParser(description="Test Runner")

    parser.add_argument("test_paths", nargs="*", help="Specific test paths")
    parser.add_argument("--unit-only", action="store_true", help="Run only unit tests")
    parser.add_argument("--integration-only", action="store_true",
                        help="Run only integration tests")
    parser.add_argument("--markers", "-m", help="Run tests with specific markers")
    parser.add_argument("--include-slow", action="store_true",
                        help="Include slow tests")

    parser.add_argument("--no-coverage", action="store_true", help="Disable coverage")
    parser.add_argument("--coverage-threshold", type=int,
                        default=80, help="Coverage threshold")

    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("-s", action="store_true", help="Don't capture output")
    parser.add_argument(
        "--tb",
        choices=[
            "short",
            "long",
            "line",
            "native"],
        default="short",
        help="Traceback style")

    args = parser.parse_args()

    print("TEST RUNNER")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Current working directory: {Path.cwd()}")
    print(f"Script location: {Path(__file__).parent}")
    print("=" * 60)

    cmd = run_pytest_command(args)
    print(f"Running: {' '.join(cmd)}")
    print("-" * 60)

    try:
        result = subprocess.run(cmd, cwd=Path(__file__).parent)
        print("-" * 60)
        print(f"✅ Tests completed with exit code: {result.returncode}")
        return result.returncode
    except KeyboardInterrupt:
        print("\n⚠️  Test execution interrupted")
        return 1
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
