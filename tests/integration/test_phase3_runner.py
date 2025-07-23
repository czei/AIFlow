#!/usr/bin/env python3
"""
Sprint 3 Test Runner - Run all end-to-end integration tests.

Executes the minimal test suite for proof-of-concept validation.
"""

import sys
import time
from pathlib import Path

# Import all test modules
sys.path.append(str(Path(__file__).parent))

from test_command_execution import CommandExecutionTest
from test_workflow_enforcement import WorkflowEnforcementTest
from test_workflow_progression import WorkflowProgressionTest
from test_complete_workflow import CompleteWorkflowTest
from test_performance import HookPerformanceTest


class Sprint3TestRunner:
    """Run all Sprint 3 integration tests."""
    
    def __init__(self):
        self.total_passed = 0
        self.total_failed = 0
        self.test_results = []
        
    def run_test_suite(self, test_class, test_name: str):
        """Run a test suite and track results."""
        print(f"\n{'='*70}")
        print(f"Running {test_name}")
        print(f"{'='*70}")
        
        start_time = time.time()
        
        try:
            test = test_class()
            
            # Setup if available
            if hasattr(test, 'setup'):
                test.setup()
                
            # Run tests
            if hasattr(test, 'run_all_tests'):
                success = test.run_all_tests()
            else:
                success = test.run_tests()
                
            # Teardown if available
            if hasattr(test, 'teardown'):
                test.teardown()
                
            # Track results
            if hasattr(test, 'passed') and hasattr(test, 'failed'):
                self.total_passed += test.passed
                self.total_failed += test.failed
            elif success:
                self.total_passed += 1
            else:
                self.total_failed += 1
                
            duration = time.time() - start_time
            self.test_results.append({
                'name': test_name,
                'success': success,
                'duration': duration,
                'passed': getattr(test, 'passed', 1 if success else 0),
                'failed': getattr(test, 'failed', 0 if success else 1)
            })
            
            return success
            
        except Exception as e:
            print(f"\n💥 Fatal error in {test_name}: {e}")
            import traceback
            traceback.print_exc()
            
            self.total_failed += 1
            self.test_results.append({
                'name': test_name,
                'success': False,
                'duration': time.time() - start_time,
                'passed': 0,
                'failed': 1,
                'error': str(e)
            })
            
            return False
            
    def print_summary(self):
        """Print test execution summary."""
        print("\n" + "="*70)
        print("PHASE 3 TEST SUMMARY")
        print("="*70)
        
        for result in self.test_results:
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            duration = f"{result['duration']:.1f}s"
            details = f"({result['passed']} passed, {result['failed']} failed)"
            
            print(f"{status} {result['name']:<35} {duration:>8} {details}")
            
            if 'error' in result:
                print(f"     Error: {result['error']}")
                
        print("-"*70)
        
        total_tests = self.total_passed + self.total_failed
        if total_tests > 0:
            pass_rate = (self.total_passed / total_tests) * 100
        else:
            pass_rate = 0
            
        print(f"Total: {total_tests} tests")
        print(f"Passed: {self.total_passed} ({pass_rate:.1f}%)")
        print(f"Failed: {self.total_failed}")
        
        total_duration = sum(r['duration'] for r in self.test_results)
        print(f"Duration: {total_duration:.1f}s")
        
        print("="*70)
        
    def run_all_tests(self):
        """Run all Sprint 3 tests."""
        print("\n" + "#"*70)
        print("# PHASE 3 END-TO-END INTEGRATION TESTS")
        print("# Minimal test suite for proof-of-concept validation")
        print("#"*70)
        
        start_time = time.time()
        
        # Define test suites in execution order
        test_suites = [
            (CommandExecutionTest, "Command Execution Tests"),
            (WorkflowEnforcementTest, "Workflow Enforcement Tests"),
            (WorkflowProgressionTest, "Workflow Progression Tests"),
            (CompleteWorkflowTest, "Complete Workflow Tests"),
            (HookPerformanceTest, "Performance Tests")
        ]
        
        # Run each test suite
        all_passed = True
        for test_class, test_name in test_suites:
            success = self.run_test_suite(test_class, test_name)
            if not success:
                all_passed = False
                
        # Print summary
        self.print_summary()
        
        total_duration = time.time() - start_time
        
        print(f"\nTotal execution time: {total_duration:.1f}s")
        
        if all_passed:
            print("\n🎉 ALL PHASE 3 TESTS PASSED! 🎉")
            print("The automated development system is working correctly.")
            print("\nNext steps:")
            print("- Run on real projects for alpha testing")
            print("- Gather performance metrics")
            print("- Document any edge cases found")
        else:
            print("\n❌ SOME TESTS FAILED")
            print("Please fix the failing tests before proceeding.")
            print("\nDebugging tips:")
            print("- Check individual test output above")
            print("- Run failing tests individually")
            print("- Verify all dependencies are installed")
            
        return all_passed


def main():
    """Main entry point."""
    runner = Sprint3TestRunner()
    success = runner.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()