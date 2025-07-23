#!/usr/bin/env python3
"""
Performance tests for hook execution times.

Measures the execution time of hooks to ensure they don't
slow down Claude Code operations.
"""

import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from statistics import mean, stdev

# Add src to path
sys.path.append(str(Path(__file__).parent.parent.parent / 'src'))

from state_manager import StateManager


class HookPerformanceTest:
    """Test hook performance and execution times."""
    
    def __init__(self):
        self.iterations = 10  # Number of times to run each test
        self.max_allowed_ms = 100  # Maximum allowed time in milliseconds
        
    def measure_hook_time(self, hook_name: str, event_data: dict, test_dir: str) -> float:
        """Measure execution time of a single hook call in milliseconds."""
        hook_path = Path(__file__).parent.parent.parent / 'src' / 'hooks' / f'{hook_name}.py'
        
        start_time = time.perf_counter()
        
        proc = subprocess.run(
            [sys.executable, str(hook_path)],
            input=json.dumps(event_data),
            capture_output=True,
            text=True,
            cwd=test_dir
        )
        
        end_time = time.perf_counter()
        
        if proc.returncode != 0:
            print(f"Hook error: {proc.stderr}")
            
        return (end_time - start_time) * 1000  # Convert to milliseconds
        
    def test_pre_tool_use_performance(self):
        """Test PreToolUse hook performance."""
        print("\n🧪 Testing PreToolUse hook performance...")
        
        with tempfile.TemporaryDirectory() as test_dir:
            # Setup state
            state_manager = StateManager(test_dir)
            state_manager.create('perf-test')
            state_manager.update({
                'automation_active': True,
                'workflow_step': 'planning'
            })
            
            # Test event
            event = {
                "cwd": test_dir,
                "tool": "Write",
                "input": {"file_path": "test.py", "content": "print('test')"}
            }
            
            # Warm up
            self.measure_hook_time('pre_tool_use', event, test_dir)
            
            # Measure
            times = []
            for i in range(self.iterations):
                time_ms = self.measure_hook_time('pre_tool_use', event, test_dir)
                times.append(time_ms)
                
            avg_time = mean(times)
            std_dev = stdev(times) if len(times) > 1 else 0
            
            print(f"  Average time: {avg_time:.2f}ms ± {std_dev:.2f}ms")
            print(f"  Min: {min(times):.2f}ms, Max: {max(times):.2f}ms")
            
            if avg_time > self.max_allowed_ms:
                print(f"  ⚠️  WARNING: Average time exceeds {self.max_allowed_ms}ms limit")
                return False
            else:
                print(f"  ✅ Performance within {self.max_allowed_ms}ms limit")
                return True
                
    def test_post_tool_use_performance(self):
        """Test PostToolUse hook performance."""
        print("\n🧪 Testing PostToolUse hook performance...")
        
        with tempfile.TemporaryDirectory() as test_dir:
            # Setup state
            state_manager = StateManager(test_dir)
            state_manager.create('perf-test')
            state_manager.update({
                'automation_active': True,
                'workflow_step': 'implementation'
            })
            
            # Test event
            event = {
                "cwd": test_dir,
                "tool": "Write",
                "input": {"file_path": "test.py", "content": "print('test')"},
                "exit_code": 0
            }
            
            # Warm up
            self.measure_hook_time('post_tool_use', event, test_dir)
            
            # Measure
            times = []
            for i in range(self.iterations):
                time_ms = self.measure_hook_time('post_tool_use', event, test_dir)
                times.append(time_ms)
                
            avg_time = mean(times)
            std_dev = stdev(times) if len(times) > 1 else 0
            
            print(f"  Average time: {avg_time:.2f}ms ± {std_dev:.2f}ms")
            print(f"  Min: {min(times):.2f}ms, Max: {max(times):.2f}ms")
            
            if avg_time > self.max_allowed_ms:
                print(f"  ⚠️  WARNING: Average time exceeds {self.max_allowed_ms}ms limit")
                return False
            else:
                print(f"  ✅ Performance within {self.max_allowed_ms}ms limit")
                return True
                
    def test_stop_hook_performance(self):
        """Test Stop hook performance."""
        print("\n🧪 Testing Stop hook performance...")
        
        with tempfile.TemporaryDirectory() as test_dir:
            # Setup state
            state_manager = StateManager(test_dir)
            state_manager.create('perf-test')
            state_manager.update({
                'automation_active': True,
                'workflow_step': 'planning',
                'workflow_progress': {
                    'planning': {
                        'planning_complete': True
                    }
                }
            })
            
            # Test event
            event = {
                "cwd": test_dir,
                "response": "Planning complete"
            }
            
            # Warm up
            self.measure_hook_time('stop', event, test_dir)
            
            # Measure
            times = []
            for i in range(self.iterations):
                # Reset state for consistent testing
                state_manager.update({'workflow_step': 'planning'})
                time_ms = self.measure_hook_time('stop', event, test_dir)
                times.append(time_ms)
                
            avg_time = mean(times)
            std_dev = stdev(times) if len(times) > 1 else 0
            
            print(f"  Average time: {avg_time:.2f}ms ± {std_dev:.2f}ms")
            print(f"  Min: {min(times):.2f}ms, Max: {max(times):.2f}ms")
            
            if avg_time > self.max_allowed_ms:
                print(f"  ⚠️  WARNING: Average time exceeds {self.max_allowed_ms}ms limit")
                return False
            else:
                print(f"  ✅ Performance within {self.max_allowed_ms}ms limit")
                return True
                
    def test_state_operations_performance(self):
        """Test StateManager operations performance."""
        print("\n🧪 Testing StateManager operations performance...")
        
        with tempfile.TemporaryDirectory() as test_dir:
            state_manager = StateManager(test_dir)
            state_manager.create('perf-test')
            
            # Test read performance
            read_times = []
            for i in range(self.iterations * 10):  # More iterations for quick operations
                start = time.perf_counter()
                state = state_manager.read()
                end = time.perf_counter()
                read_times.append((end - start) * 1000)
                
            # Test update performance
            update_times = []
            for i in range(self.iterations * 10):
                update_data = {
                    'test_counter': i,
                    'last_updated': f'test-{i}'
                }
                start = time.perf_counter()
                state_manager.update(update_data)
                end = time.perf_counter()
                update_times.append((end - start) * 1000)
                
            avg_read = mean(read_times)
            avg_update = mean(update_times)
            
            print(f"  Read average: {avg_read:.2f}ms")
            print(f"  Update average: {avg_update:.2f}ms")
            
            if avg_read < 10 and avg_update < 10:
                print(f"  ✅ State operations are fast (<10ms)")
                return True
            else:
                print(f"  ⚠️  WARNING: State operations may be slow")
                return False
                
    def run_all_tests(self):
        """Run all performance tests."""
        print("\n" + "="*60)
        print("🚀 Running Hook Performance Tests")
        print("="*60)
        
        all_passed = True
        
        tests = [
            self.test_pre_tool_use_performance,
            self.test_post_tool_use_performance,
            self.test_stop_hook_performance,
            self.test_state_operations_performance
        ]
        
        for test in tests:
            try:
                passed = test()
                if not passed:
                    all_passed = False
            except Exception as e:
                print(f"❌ Test failed: {test.__name__}")
                print(f"   Error: {e}")
                all_passed = False
                
        print("\n" + "="*60)
        print("📊 Performance Test Summary")
        print("="*60)
        
        if all_passed:
            print("✅ All hooks perform within acceptable limits")
            print(f"✅ Target: <{self.max_allowed_ms}ms per hook execution")
        else:
            print("⚠️  Some performance issues detected")
            print("Consider optimizing slow operations")
            
        return all_passed


def main():
    """Main test runner."""
    test = HookPerformanceTest()
    success = test.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()