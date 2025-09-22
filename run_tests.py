#!/usr/bin/env python3
"""
Comprehensive test runner including unit tests, code quality, and security checks.
"""

import sys
import os
import unittest
import subprocess
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def run_command(command, description, check_output=False):
    """Run a command and return success status."""
    print(f"🔍 {description}...")
    try:
        if check_output:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=project_root)
            if result.returncode == 0:
                print(f"✅ {description} passed")
                return True
            else:
                print(f"❌ {description} failed")
                if result.stdout:
                    print("STDOUT:", result.stdout)
                if result.stderr:
                    print("STDERR:", result.stderr)
                return False
        else:
            result = subprocess.run(command, shell=True, cwd=project_root)
            if result.returncode == 0:
                print(f"✅ {description} passed")
                return True
            else:
                print(f"❌ {description} failed")
                return False
    except Exception as e:
        print(f"❌ Error running {description}: {e}")
        return False


def run_unit_tests():
    """Run unit tests."""
    print("🧪 Running Unit Tests...")
    print()
    
    # Test modules to run
    test_modules = [
        "tests.test_validation",
        "tests.test_keyboards", 
        "tests.test_conversation_state",
        "tests.test_integration"
    ]
    
    total_tests = 0
    total_failures = 0
    total_errors = 0
    
    for module_name in test_modules:
        print(f"Testing {module_name}...")
        try:
            # Import the test module
            test_module = __import__(module_name, fromlist=[''])
            
            # Create a test suite
            loader = unittest.TestLoader()
            suite = loader.loadTestsFromModule(test_module)
            
            # Run the tests
            runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
            result = runner.run(suite)
            
            # Count results
            total_tests += result.testsRun
            total_failures += len(result.failures)
            total_errors += len(result.errors)
            
            print(f"✅ {module_name}: {result.testsRun} tests, {len(result.failures)} failures, {len(result.errors)} errors")
            print()
            
        except Exception as e:
            print(f"❌ Error running {module_name}: {e}")
            print()
            total_errors += 1
    
    # Summary
    print("=" * 30)
    print(f"📊 Unit Test Summary:")
    print(f"Total Tests: {total_tests}")
    print(f"Failures: {total_failures}")
    print(f"Errors: {total_errors}")
    print(f"Success Rate: {((total_tests - total_failures - total_errors) / max(total_tests, 1) * 100):.1f}%")
    print()
    
    return total_failures == 0 and total_errors == 0


def run_quality_checks():
    """Run code quality checks."""
    print("🔍 Running Code Quality Checks...")
    print()
    
    checks_passed = 0
    total_checks = 3
    
    # Black formatting check
    if run_command("black --check bot/", "Black code formatting check", check_output=True):
        checks_passed += 1
    
    # MyPy type checking
    if run_command("mypy bot/ --ignore-missing-imports", "MyPy type checking", check_output=True):
        checks_passed += 1
    
    # Bandit security check
    if run_command("bandit -r bot/", "Bandit security check", check_output=True):
        checks_passed += 1
    
    print("=" * 30)
    print(f"📊 Quality Check Summary:")
    print(f"Checks Passed: {checks_passed}/{total_checks}")
    print(f"Success Rate: {(checks_passed / total_checks * 100):.1f}%")
    print()
    
    return checks_passed == total_checks


def run_tests():
    """Run all tests and quality checks."""
    print("🚀 Running AgentryLab Telegram Bot Comprehensive Tests...")
    print("=" * 60)
    print()
    
    # Run unit tests
    unit_tests_passed = run_unit_tests()
    
    # Run quality checks
    quality_checks_passed = run_quality_checks()
    
    # Overall summary
    print("=" * 60)
    print("🎯 OVERALL SUMMARY:")
    print(f"Unit Tests: {'✅ PASSED' if unit_tests_passed else '❌ FAILED'}")
    print(f"Quality Checks: {'✅ PASSED' if quality_checks_passed else '❌ FAILED'}")
    print()
    
    if unit_tests_passed and quality_checks_passed:
        print("🎉 ALL TESTS AND CHECKS PASSED!")
        print("🚀 Your code is ready for deployment!")
        return 0
    else:
        print("❌ Some tests or checks failed.")
        print("🔧 Please fix the issues above before deploying.")
        return 1

if __name__ == "__main__":
    sys.exit(run_tests())
