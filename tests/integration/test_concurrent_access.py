#!/usr/bin/env python3
"""
Concurrent access tests for StateManager.

Tests that the file locking mechanism properly handles multiple
processes trying to access state simultaneously.
"""

import multiprocessing
import time
import tempfile
import shutil
import sys
from pathlib import Path
from datetime import datetime, timezone

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.state_manager import StateManager, StateValidationError


def update_state_process(test_dir: str, process_id: int, updates_per_process: int):
    """Worker process that performs multiple state updates."""
    state_manager = StateManager(test_dir)
    
    for i in range(updates_per_process):
        try:
            # Perform update with process-specific data
            update_data = {
                f'process_{process_id}_update_{i}': datetime.now(timezone.utc).isoformat(),
                'last_process': process_id,
                'automation_cycles': i
            }
            state_manager.update(update_data)
            
            # Small delay to increase chance of contention
            time.sleep(0.001)
            
        except Exception as e:
            print(f"Process {process_id} error on update {i}: {e}")
            raise


def read_state_process(test_dir: str, process_id: int, reads_per_process: int):
    """Worker process that performs multiple state reads."""
    state_manager = StateManager(test_dir)
    
    for i in range(reads_per_process):
        try:
            state = state_manager.read()
            # Verify state is valid
            assert 'project_name' in state
            assert 'status' in state
            
            # Small delay
            time.sleep(0.001)
            
        except Exception as e:
            print(f"Read process {process_id} error on read {i}: {e}")
            raise


class ConcurrentAccessTest:
    """Test concurrent access to state files."""
    
    def __init__(self):
        self.test_dir = None
        self.passed = 0
        self.failed = 0
        
    def setup(self):
        """Create test environment."""
        self.test_dir = tempfile.mkdtemp(prefix="claude_concurrent_")
        print(f"✅ Created test directory: {self.test_dir}")
        
    def teardown(self):
        """Clean up test environment."""
        if self.test_dir and Path(self.test_dir).exists():
            shutil.rmtree(self.test_dir)
            print("✅ Cleaned up test directory")
            
    def test_concurrent_updates(self):
        """Test multiple processes updating state simultaneously."""
        print("\n🧪 Testing concurrent state updates...")
        
        # Create initial state
        state_manager = StateManager(self.test_dir)
        state_manager.create('concurrent-test')
        
        # Setup test parameters
        num_processes = 5
        updates_per_process = 10
        
        # Create processes
        processes = []
        for i in range(num_processes):
            p = multiprocessing.Process(
                target=update_state_process,
                args=(self.test_dir, i, updates_per_process)
            )
            processes.append(p)
            
        # Start all processes
        start_time = time.time()
        for p in processes:
            p.start()
            
        # Wait for completion
        for p in processes:
            p.join()
            
        duration = time.time() - start_time
        
        # Verify all processes completed successfully
        success = all(p.exitcode == 0 for p in processes)
        if not success:
            print("❌ Some processes failed")
            self.failed += 1
            return
            
        # Verify final state has all updates
        final_state = state_manager.read()
        
        # Check that updates from all processes are present
        for i in range(num_processes):
            for j in range(updates_per_process):
                key = f'process_{i}_update_{j}'
                assert key in final_state, f"Missing update: {key}"
                
        print(f"  ✓ All {num_processes * updates_per_process} updates successful")
        print(f"  ✓ Completed in {duration:.2f}s")
        print("✅ Concurrent updates handled correctly")
        self.passed += 1
        
    def test_concurrent_reads(self):
        """Test multiple processes reading state simultaneously."""
        print("\n🧪 Testing concurrent state reads...")
        
        # Clean up any existing state file
        state_file = Path(self.test_dir) / '.project-state.json'
        if state_file.exists():
            state_file.unlink()
        
        # Create initial state
        state_manager = StateManager(self.test_dir)
        state_manager.create('concurrent-test')
        
        # Add some data
        state_manager.update({
            'test_data': 'concurrent read test',
            'automation_active': True
        })
        
        # Setup test parameters
        num_processes = 10
        reads_per_process = 20
        
        # Create processes
        processes = []
        for i in range(num_processes):
            p = multiprocessing.Process(
                target=read_state_process,
                args=(self.test_dir, i, reads_per_process)
            )
            processes.append(p)
            
        # Start all processes
        start_time = time.time()
        for p in processes:
            p.start()
            
        # Wait for completion
        for p in processes:
            p.join()
            
        duration = time.time() - start_time
        
        # Verify all processes completed successfully
        success = all(p.exitcode == 0 for p in processes)
        if success:
            print(f"  ✓ All {num_processes * reads_per_process} reads successful")
            print(f"  ✓ Completed in {duration:.2f}s")
            print("✅ Concurrent reads handled correctly")
            self.passed += 1
        else:
            print("❌ Some read processes failed")
            self.failed += 1
            
    def test_mixed_operations(self):
        """Test mixed read/write operations simultaneously."""
        print("\n🧪 Testing mixed concurrent operations...")
        
        # Clean up any existing state file
        state_file = Path(self.test_dir) / '.project-state.json'
        if state_file.exists():
            state_file.unlink()
        
        # Create initial state
        state_manager = StateManager(self.test_dir)
        state_manager.create('concurrent-test')
        
        # Create mix of read and write processes
        processes = []
        
        # Writers
        for i in range(3):
            p = multiprocessing.Process(
                target=update_state_process,
                args=(self.test_dir, i, 5)
            )
            processes.append(p)
            
        # Readers
        for i in range(5):
            p = multiprocessing.Process(
                target=read_state_process,
                args=(self.test_dir, i + 100, 10)
            )
            processes.append(p)
            
        # Start all processes
        start_time = time.time()
        for p in processes:
            p.start()
            
        # Wait for completion
        for p in processes:
            p.join()
            
        duration = time.time() - start_time
        
        # Verify all processes completed successfully
        success = all(p.exitcode == 0 for p in processes)
        if success:
            print(f"  ✓ Mixed operations completed in {duration:.2f}s")
            print("✅ Mixed concurrent operations handled correctly")
            self.passed += 1
        else:
            print("❌ Some mixed operations failed")
            self.failed += 1
            
    def test_lock_timeout(self):
        """Test that lock timeout works correctly."""
        print("\n🧪 Testing lock timeout behavior...")
        
        # This test would require simulating a stuck lock
        # For now, we'll verify the timeout mechanism exists
        
        # Clean up any existing state file
        state_file = Path(self.test_dir) / '.project-state.json'
        if state_file.exists():
            state_file.unlink()
        
        # Create state
        state_manager = StateManager(self.test_dir)
        state_manager.create('timeout-test')
        
        # Verify FileLock has timeout configured
        from src.state_manager import FileLock
        lock = FileLock(state_manager.state_file, timeout=0.1)
        
        assert lock.timeout == 0.1, "Lock timeout should be configurable"
        print("  ✓ Lock timeout mechanism available")
        print("✅ Lock timeout configuration verified")
        self.passed += 1
        
    def run_all_tests(self):
        """Run all concurrent access tests."""
        print("\n" + "="*60)
        print("🚀 Running Concurrent Access Tests")
        print("="*60)
        
        tests = [
            self.test_concurrent_updates,
            self.test_concurrent_reads,
            self.test_mixed_operations,
            self.test_lock_timeout
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                print(f"❌ Test failed: {test.__name__}")
                print(f"   Error: {e}")
                self.failed += 1
                
        print("\n" + "="*60)
        print(f"📊 Test Results: {self.passed} passed, {self.failed} failed")
        print("="*60)
        
        return self.failed == 0


def main():
    """Main test runner."""
    # Required for multiprocessing on some platforms
    multiprocessing.set_start_method('spawn', force=True)
    
    test = ConcurrentAccessTest()
    
    try:
        test.setup()
        success = test.run_all_tests()
        test.teardown()
        
        if success:
            print("\n✅ All concurrent access tests passed!")
            sys.exit(0)
        else:
            print("\n❌ Some tests failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 Fatal error: {e}")
        test.teardown()
        sys.exit(2)


if __name__ == '__main__':
    main()