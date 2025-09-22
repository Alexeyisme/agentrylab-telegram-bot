#!/usr/bin/env python3
"""
Run individual code quality checks.
Usage: python run_quality_checks.py [black|mypy|bandit|all]
"""

import sys
import subprocess
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def run_command(command, description):
    """Run a command and return success status."""
    print(f"🔍 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=project_root)
        if result.returncode == 0:
            print(f"✅ {description} passed")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print(f"❌ {description} failed")
            if result.stdout:
                print("STDOUT:", result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error running {description}: {e}")
        return False


def run_black_check():
    """Run Black formatting check."""
    return run_command("black --check bot/", "Black code formatting check")


def run_black_format():
    """Run Black formatting (fix issues)."""
    return run_command("black bot/", "Black code formatting (fix)")


def run_mypy_check():
    """Run MyPy type checking."""
    return run_command("mypy bot/ --ignore-missing-imports", "MyPy type checking")


def run_bandit_check():
    """Run Bandit security check."""
    return run_command("bandit -r bot/", "Bandit security check")


def run_all_checks():
    """Run all quality checks."""
    print("🔍 Running All Code Quality Checks...")
    print("=" * 50)
    print()
    
    checks = [
        ("Black formatting check", run_black_check),
        ("MyPy type checking", run_mypy_check),
        ("Bandit security check", run_bandit_check),
    ]
    
    passed = 0
    total = len(checks)
    
    for name, check_func in checks:
        if check_func():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Quality Check Summary:")
    print(f"Checks Passed: {passed}/{total}")
    print(f"Success Rate: {(passed / total * 100):.1f}%")
    
    if passed == total:
        print("🎉 All quality checks passed!")
        return 0
    else:
        print("❌ Some quality checks failed.")
        return 1


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python run_quality_checks.py [black|black-fix|mypy|bandit|all]")
        print()
        print("Commands:")
        print("  black      - Check code formatting with Black")
        print("  black-fix  - Fix code formatting with Black")
        print("  mypy       - Run MyPy type checking")
        print("  bandit     - Run Bandit security check")
        print("  all        - Run all quality checks")
        return 1
    
    command = sys.argv[1].lower()
    
    if command == "black":
        return 0 if run_black_check() else 1
    elif command == "black-fix":
        return 0 if run_black_format() else 1
    elif command == "mypy":
        return 0 if run_mypy_check() else 1
    elif command == "bandit":
        return 0 if run_bandit_check() else 1
    elif command == "all":
        return run_all_checks()
    else:
        print(f"Unknown command: {command}")
        print("Use 'python run_quality_checks.py' to see available commands.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
