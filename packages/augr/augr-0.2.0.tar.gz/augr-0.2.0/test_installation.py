#!/usr/bin/env python3
"""
Test script to verify AUGR installation works correctly
"""

import os
import sys


def test_basic_import():
    """Test that the package can be imported"""
    try:
        import augr
        print("✅ Package import successful")
        return True
    except ImportError as e:
        print(f"❌ Package import failed: {e}")
        return False

def test_cli_import():
    """Test that the CLI module can be imported"""
    try:
        from augr.cli import main
        print("✅ CLI import successful")
        return True
    except ImportError as e:
        print(f"❌ CLI import failed: {e}")
        return False

def test_ai_client_import():
    """Test that the AI client can be imported"""
    try:
        from augr.ai_client import create_ai
        print("✅ AI client import successful")
        return True
    except ImportError as e:
        print(f"❌ AI client import failed: {e}")
        return False

def test_config_system():
    """Test configuration system"""
    try:
        # Set a test API key
        os.environ['BRAINTRUST_API_KEY'] = 'test-key-12345'
        
        from augr.config import get_project_api_key, AugrConfig
        
        # Test that the config class can be instantiated
        config = AugrConfig()
        
        # Test that the API key function works with environment variable
        api_key = get_project_api_key("test-project")
        
        if api_key == 'test-key-12345':
            print("✅ Configuration system works")
            return True
        else:
            print(f"❌ Configuration system failed: got {api_key}")
            return False
    except Exception as e:
        print(f"❌ Configuration system failed: {e}")
        return False
    finally:
        # Clean up
        if 'BRAINTRUST_API_KEY' in os.environ:
            del os.environ['BRAINTRUST_API_KEY']

def test_entry_point():
    """Test that the entry point script exists"""
    try:
        import subprocess
        result = subprocess.run([sys.executable, '-c', 'import augr.cli; print("Entry point accessible")'],
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Entry point accessible")
            return True
        else:
            print(f"❌ Entry point test failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Entry point test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing AUGR Installation")
    print("=" * 30)

    tests = [
        test_basic_import,
        test_cli_import,
        test_ai_client_import,
        test_config_system,
        test_entry_point,
    ]

    results = []
    for test in tests:
        results.append(test())
        print()

    # Summary
    passed = sum(results)
    total = len(results)

    print("📊 Test Summary")
    print("-" * 15)
    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("🎉 All tests passed! AUGR is ready to use.")
        return 0
    else:
        print("❌ Some tests failed. Please check the installation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
