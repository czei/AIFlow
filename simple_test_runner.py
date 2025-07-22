#!/usr/bin/env python3
"""
Simple test runner that executes the existing test suite
"""

import subprocess
import sys
from pathlib import Path

def run_test(test_path):
    """Run a single test and return success status"""
    print(f"\n{'='*60}")
    print(f"Running: {test_path}")
    print(f"{'='*60}")
    
    result = subprocess.run([str(test_path)], cwd=Path.cwd(), input="")
    
    if result.returncode == 0:
        print(f"✅ PASSED: {test_path}")
        return True
    else:
        print(f"❌ FAILED: {test_path} (exit code: {result.returncode})")
        return False

def main():
    """Run all tests"""
    print("🧪 Running existing test suite...")
    
    # Run the main test script
    success = run_test("tests/run_all_tests.sh")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()