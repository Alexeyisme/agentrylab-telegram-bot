#!/usr/bin/env python3
"""
Simple test runner to bypass pytest-asyncio issues.
"""

import sys
import os
import unittest
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def run_tests():
    """Run all tests."""
    print("🧪 Running AgentryLab Telegram Bot Tests...")
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
    print("=" * 50)
    print(f"📊 Test Summary:")
    print(f"Total Tests: {total_tests}")
    print(f"Failures: {total_failures}")
    print(f"Errors: {total_errors}")
    print(f"Success Rate: {((total_tests - total_failures - total_errors) / max(total_tests, 1) * 100):.1f}%")
    
    if total_failures == 0 and total_errors == 0:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(run_tests())
