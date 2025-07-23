#!/usr/bin/env python3
"""
Compare test runner v1 and v2 outputs to ensure compatibility.
"""

import subprocess
import json
from pathlib import Path


def run_test_runner(script):
    """Run a test runner and capture output"""
    result = subprocess.run(
        ['python3', script],
        capture_output=True,
        text=True
    )
    return result.stdout, result.stderr, result.returncode


def main():
    print("Comparing Test Runner v1 and v2...")
    print("=" * 60)
    
    # Run both versions
    print("\nRunning original test runner...")
    v1_out, v1_err, v1_code = run_test_runner('test_runner.py')
    
    print("\nRunning new test runner v2...")
    v2_out, v2_err, v2_code = run_test_runner('test_runner_v2.py')
    
    # Compare exit codes
    print(f"\nExit codes: v1={v1_code}, v2={v2_code}")
    if v1_code == v2_code:
        print("✅ Exit codes match")
    else:
        print("❌ Exit codes differ")
    
    # Compare test detection
    v1_tests = v1_out.count("Running:")
    v2_tests = v2_out.count("Running:")
    print(f"\nTests found: v1={v1_tests}, v2={v2_tests}")
    if v1_tests == v2_tests:
        print("✅ Same number of tests discovered")
    else:
        print("❌ Different number of tests")
    
    # Check JSON report format compatibility
    print("\nChecking JSON report format...")
    latest_reports = sorted(Path("test_results").glob("test_report_*.json"))
    if len(latest_reports) >= 2:
        # Compare structure of last two reports
        with open(latest_reports[-2]) as f:
            report1 = json.load(f)
        with open(latest_reports[-1]) as f:
            report2 = json.load(f)
        
        # Check same keys in summary
        if set(report1["summary"].keys()) == set(report2["summary"].keys()):
            print("✅ JSON summary structure matches")
        else:
            print("❌ JSON summary structure differs")
    
    print("\n" + "="*60)
    print("Key improvements in v2:")
    print("- ✅ Automatic test discovery (no hardcoding)")
    print("- ✅ Interactive tests handled properly") 
    print("- ✅ Clear permission error messages")
    print("- ✅ Plugin architecture for future layers")
    print("- ✅ Configuration file support")


if __name__ == "__main__":
    main()