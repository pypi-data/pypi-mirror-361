#!/usr/bin/env python3
"""
Simple tests for the yfinance MCP server
"""

import sys
import subprocess
import time

def test_import():
    """Test that the main module can be imported"""
    try:
        import main
        print("✅ Import test passed")
        return True
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

def test_server_startup():
    """Test that the server can start up (skip in CI)"""
    import os
    if os.environ.get('CI'):
        print("⏭️  Server startup test skipped in CI environment")
        return True
        
    try:
        # Start the server process
        proc = subprocess.Popen(
            [sys.executable, 'main.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a bit for startup
        time.sleep(3)
        
        # Check if process is still running
        if proc.poll() is None:
            print("✅ Server startup test passed")
            proc.terminate()
            proc.wait()
            return True
        else:
            stdout, stderr = proc.communicate()
            print(f"❌ Server startup test failed")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Server startup test failed: {e}")
        return False

def test_fastmcp_import():
    """Test that FastMCP can be imported"""
    try:
        import fastmcp
        print("✅ FastMCP import test passed")
        return True
    except Exception as e:
        print(f"❌ FastMCP import test failed: {e}")
        return False

def test_yfinance_import():
    """Test that yfinance can be imported"""
    try:
        import yfinance
        print("✅ yfinance import test passed")
        return True
    except Exception as e:
        print(f"❌ yfinance import test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Running yfinance MCP server tests...")
    print("=" * 50)
    
    tests = [
        test_fastmcp_import,
        test_yfinance_import,
        test_import,
        test_server_startup
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 