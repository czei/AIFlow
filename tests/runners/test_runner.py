#!/usr/bin/env python3
"""
Minimal test runner for AI Software Project Management System.
Wraps existing shell scripts and provides foundation for 4-layer testing architecture.
"""

import subprocess
import json
import sys
import time
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional


class TestResult:
    """Represents the result of a single test execution"""
    def __init__(self, name: str, success: bool, duration: float, 
                 output: str = "", error: str = "", metadata: Dict = None):
        self.name = name
        self.success = success
        self.duration = duration
        self.output = output
        self.error = error
        self.metadata = metadata or {}
        self.timestamp = datetime.now(timezone.utc).isoformat()


class TestRunner:
    """Main test orchestrator for the 4-layer testing architecture"""
    
    def __init__(self, results_dir: str = "test_results"):
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True)
        self.results: List[TestResult] = []
        
    def run_shell_test(self, script_path: str, timeout: int = 300) -> TestResult:
        """
        Wrap and execute existing shell script tests.
        
        Args:
            script_path: Path to the shell script
            timeout: Maximum execution time in seconds
            
        Returns:
            TestResult object with execution details
        """
        script_path = Path(script_path)
        if not script_path.exists():
            return TestResult(
                name=str(script_path),
                success=False,
                duration=0.0,
                error=f"Script not found: {script_path}"
            )
        
        print(f"\n{'='*60}")
        print(f"Running: {script_path.name}")
        print(f"{'='*60}")
        
        start_time = time.time()
        try:
            # Make script executable if needed
            script_path.chmod(0o755)
            
            # Run the script
            result = subprocess.run(
                [str(script_path.absolute())],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(Path.cwd()),
                input=""  # Prevent hanging on interactive prompts
            )
            
            duration = time.time() - start_time
            
            test_result = TestResult(
                name=script_path.name,
                success=(result.returncode == 0),
                duration=duration,
                output=result.stdout,
                error=result.stderr,
                metadata={
                    "exit_code": result.returncode,
                    "script_path": str(script_path)
                }
            )
            
            # Print summary
            status = "✅ PASSED" if test_result.success else "❌ FAILED"
            print(f"\n{status} - {script_path.name} ({duration:.2f}s)")
            
            if result.stderr and not test_result.success:
                print(f"\nErrors:\n{result.stderr}")
                
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            test_result = TestResult(
                name=script_path.name,
                success=False,
                duration=duration,
                error=f"Test timed out after {timeout} seconds"
            )
            print(f"\n⏱️  TIMEOUT - {script_path.name} ({timeout}s)")
            
        except Exception as e:
            duration = time.time() - start_time
            test_result = TestResult(
                name=script_path.name,
                success=False,
                duration=duration,
                error=f"Unexpected error: {str(e)}"
            )
            print(f"\n🚨 ERROR - {script_path.name}: {str(e)}")
        
        self.results.append(test_result)
        return test_result
    
    def run_python_test(self, test_module: str) -> TestResult:
        """
        Run Python-based tests (placeholder for future layers).
        
        Args:
            test_module: Python module path (e.g., 'tests.unit.test_state_management')
            
        Returns:
            TestResult object
        """
        # TODO: Implement pytest integration
        return TestResult(
            name=test_module,
            success=True,
            duration=0.0,
            output="Python test runner not yet implemented"
        )
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate a comprehensive test report"""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.success)
        failed_tests = total_tests - passed_tests
        total_duration = sum(r.duration for r in self.results)
        
        report = {
            "summary": {
                "total": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "success_rate": f"{(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%",
                "total_duration": f"{total_duration:.2f}s",
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            "results": [
                {
                    "name": r.name,
                    "success": r.success,
                    "duration": f"{r.duration:.2f}s",
                    "timestamp": r.timestamp,
                    "metadata": r.metadata,
                    "error": r.error if r.error else None
                }
                for r in self.results
            ]
        }
        
        # Save report to file
        report_path = self.results_dir / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def print_summary(self):
        """Print a summary of test results"""
        report = self.generate_report()
        summary = report["summary"]
        
        print(f"\n{'='*60}")
        print("TEST SUMMARY")
        print(f"{'='*60}")
        print(f"Total Tests: {summary['total']}")
        print(f"Passed:      {summary['passed']} ✅")
        print(f"Failed:      {summary['failed']} ❌")
        print(f"Success Rate: {summary['success_rate']}")
        print(f"Total Time:   {summary['total_duration']}")
        print(f"{'='*60}")
        
        if summary['failed'] > 0:
            print("\nFailed Tests:")
            for result in self.results:
                if not result.success:
                    print(f"  ❌ {result.name}: {result.error}")
        
        print(f"\nDetailed report saved to: {self.results_dir}/")


def main():
    """Main entry point for test runner"""
    runner = TestRunner()
    
    # Define test suites
    shell_tests = [
        "tests/run_all_tests.sh",
        "tests/integration_test.sh",
        # Add more shell scripts as needed
    ]
    
    print("🧪 AI Software Project Management - Test Runner")
    print(f"Starting test execution at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run existing shell script tests
    for test_script in shell_tests:
        if Path(test_script).exists():
            runner.run_shell_test(test_script)
        else:
            print(f"⚠️  Skipping {test_script} - file not found")
    
    # Generate and display summary
    runner.print_summary()
    
    # Exit with appropriate code
    report = runner.generate_report()
    sys.exit(0 if report["summary"]["failed"] == 0 else 1)


if __name__ == "__main__":
    main()