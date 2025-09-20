#!/usr/bin/env python3
"""
Simple test script to verify project setup without external dependencies.
"""

import sys
from pathlib import Path

def test_project_structure():
    """Test that all required files and directories exist."""
    required_files = [
        "README.md",
        "requirements.txt", 
        "config.py",
        "config.example.py",
        "setup.py",
        "install.sh",
        ".gitignore",
        "bot/__init__.py",
        "bot/main.py",
        "bot/handlers/__init__.py",
        "bot/keyboards/__init__.py", 
        "bot/states/__init__.py",
        "bot/utils/__init__.py",
        "tests/__init__.py",
        "tests/test_bot.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    
    print("✅ All required files exist")
    return True

def test_config_loading():
    """Test that configuration can be loaded."""
    try:
        from config import BOT_TOKEN, BOT_USERNAME, POLLING
        print("✅ Configuration loads successfully")
        return True
    except Exception as e:
        print(f"❌ Configuration loading failed: {e}")
        return False

def test_bot_structure():
    """Test that bot modules can be imported (without external deps)."""
    try:
        # Test that we can import the bot module structure
        import bot
        import bot.handlers
        import bot.keyboards
        import bot.states
        import bot.utils
        print("✅ Bot module structure is correct")
        return True
    except Exception as e:
        print(f"❌ Bot module structure test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing AgentryLab Telegram Bot setup...")
    print()
    
    tests = [
        ("Project Structure", test_project_structure),
        ("Configuration", test_config_loading),
        ("Bot Structure", test_bot_structure),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"Testing {test_name}...")
        if test_func():
            passed += 1
        print()
    
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Project setup is correct.")
        print()
        print("Next steps:")
        print("1. Run: ./install.sh")
        print("2. Edit config.py with your bot token")
        print("3. Run: python bot/main.py")
        return 0
    else:
        print("❌ Some tests failed. Please check the setup.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
