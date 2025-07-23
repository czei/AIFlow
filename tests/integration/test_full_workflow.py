#!/usr/bin/env python3
"""
Integration tests for complete workflow automation.

Tests the full integration of commands, hooks, and state management
through a simulated 6-step workflow.
"""

import json
import os
import subprocess
import sys
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timezone

# Add src to path
sys.path.append(str(Path(__file__).parent.parent.parent / 'src'))

from state_manager import StateManager
from project_builder import ProjectBuilder


class WorkflowIntegrationTest:
    """Test complete workflow integration."""
    
    def __init__(self):
        self.test_dir = None
        self.project_name = "test-integration"
        self.passed = 0
        self.failed = 0
        
    def setup(self):
        """Create test environment."""
        # Create temporary directory
        self.test_dir = tempfile.mkdtemp(prefix="claude_integration_")
        print(f"✅ Created test directory: {self.test_dir}")
        
        # Initialize git repo
        subprocess.run(['git', 'init'], cwd=self.test_dir, check=True, capture_output=True)
        subprocess.run(['git', 'config', 'user.email', 'test@example.com'], cwd=self.test_dir, capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'Test User'], cwd=self.test_dir, capture_output=True)
        
        # Create initial commit
        Path(self.test_dir, 'README.md').write_text('# Test Project\n')
        subprocess.run(['git', 'add', '.'], cwd=self.test_dir, capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'Initial commit'], cwd=self.test_dir, capture_output=True)
        print("✅ Initialized git repository")
        
    def cleanup_state(self):
        """Remove state file if it exists."""
        state_file = Path(self.test_dir) / '.project-state.json'
        if state_file.exists():
            state_file.unlink()
        
    def teardown(self):
        """Clean up test environment."""
        if self.test_dir and os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
            print("✅ Cleaned up test directory")
            
    def run_hook(self, hook_name: str, event_data: dict) -> dict:
        """Run a hook and return its response."""
        hook_path = Path(__file__).parent.parent.parent / 'src' / 'hooks' / f'{hook_name}.py'
        
        # Run hook as subprocess
        proc = subprocess.run(
            [sys.executable, str(hook_path)],
            input=json.dumps(event_data),
            capture_output=True,
            text=True,
            cwd=self.test_dir
        )
        
        if proc.returncode != 0:
            print(f"Hook error: {proc.stderr}")
            
        # Parse response
        try:
            return json.loads(proc.stdout) if proc.stdout else {}
        except json.JSONDecodeError:
            return {}
            
    def test_project_setup(self):
        """Test project setup and initialization."""
        print("\n🧪 Testing project setup...")
        
        # Test ProjectBuilder with explicit path
        builder = ProjectBuilder(self.project_name, self.test_dir)
        builder.create_structure()
        
        # Verify directories created
        phases_dir = Path(self.test_dir) / 'phases'
        assert phases_dir.exists(), f"Expected phases directory at {phases_dir} but it doesn't exist"
        
        claude_dir = Path(self.test_dir) / '.claude'
        assert claude_dir.exists(), f"Expected .claude directory at {claude_dir} but it doesn't exist"
        
        logs_dir = Path(self.test_dir) / 'logs'
        assert logs_dir.exists(), f"Expected logs directory at {logs_dir} but it doesn't exist"
        
        docs_dir = Path(self.test_dir) / 'docs'
        assert docs_dir.exists(), f"Expected docs directory at {docs_dir} but it doesn't exist"
        
        # Verify phase files created
        planning_file = Path(self.test_dir) / 'phases' / '01-planning.md'
        assert planning_file.exists(), f"Expected planning phase file at {planning_file} but it doesn't exist"
        
        # Initialize state
        state_manager = StateManager(self.test_dir)
        state_manager.create(self.project_name)
        
        # Verify state file
        state = state_manager.read()
        assert state['project_name'] == self.project_name, \
            f"Expected project_name to be '{self.project_name}' but got '{state.get('project_name')}'"
        assert state['status'] == 'setup', \
            f"Expected initial status to be 'setup' but got '{state.get('status')}'"
        assert state['workflow_step'] == 'planning', \
            f"Expected initial workflow_step to be 'planning' but got '{state.get('workflow_step')}'"
        
        print("✅ Project setup successful with ProjectBuilder")
        self.passed += 1
        
    def test_workflow_enforcement(self):
        """Test workflow rule enforcement through hooks."""
        print("\n🧪 Testing workflow enforcement...")
        
        # Clean up any existing state
        self.cleanup_state()
        
        # Setup state
        state_manager = StateManager(self.test_dir)
        state_manager.create(self.project_name)
        state_manager.update({
            'automation_active': True,
            'workflow_step': 'planning'
        })
        
        # Test 1: Planning phase blocks Write
        event = {
            "cwd": self.test_dir,
            "tool": "Write",
            "input": {"file_path": "test.py", "content": "print('hello')"}
        }
        response = self.run_hook('pre_tool_use', event)
        assert response.get('decision') == 'block', \
            f"Planning phase should block Write tool but got decision='{response.get('decision')}'"
        print("  ✓ Planning phase blocks Write tool")
        
        # Test 2: Planning phase allows Read
        event['tool'] = 'Read'
        event['input'] = {"file_path": "README.md"}
        response = self.run_hook('pre_tool_use', event)
        assert response.get('decision') == 'allow', \
            f"Planning phase should allow Read tool but got decision='{response.get('decision')}'"
        print("  ✓ Planning phase allows Read tool")
        
        # Test 3: Implementation phase allows Write
        state_manager.update({'workflow_step': 'implementation'})
        event['tool'] = 'Write'
        response = self.run_hook('pre_tool_use', event)
        assert response.get('decision') == 'allow', \
            f"Implementation phase should allow Write tool but got decision='{response.get('decision')}'"
        print("  ✓ Implementation phase allows Write tool")
        
        print("✅ Workflow enforcement working correctly")
        self.passed += 1
        
    def test_progress_tracking(self):
        """Test progress tracking through PostToolUse hook."""
        print("\n🧪 Testing progress tracking...")
        
        # Clean up any existing state
        self.cleanup_state()
        
        # Setup state
        state_manager = StateManager(self.test_dir)
        state_manager.create(self.project_name)
        state_manager.update({
            'automation_active': True,
            'workflow_step': 'implementation'
        })
        
        # Simulate Write tool execution
        event = {
            "cwd": self.test_dir,
            "tool": "Write",
            "input": {"file_path": "src/main.py", "content": "def main():\n    pass"},
            "exit_code": 0
        }
        
        # Create the file first (simulating actual Write)
        os.makedirs(os.path.join(self.test_dir, 'src'), exist_ok=True)
        Path(self.test_dir, 'src', 'main.py').write_text("def main():\n    pass")
        
        # Run PostToolUse hook
        self.run_hook('post_tool_use', event)
        
        # Check state was updated
        state = state_manager.read()
        files_modified = state.get('files_modified', [])
        assert 'src/main.py' in files_modified, \
            f"Expected 'src/main.py' to be in files_modified but got {files_modified}"
        print("  ✓ File modifications tracked")
        
        # Simulate test execution
        event = {
            "cwd": self.test_dir,
            "tool": "Bash",
            "input": {"command": "pytest tests/"},
            "exit_code": 0
        }
        
        self.run_hook('post_tool_use', event)
        
        # Check quality gate
        state = state_manager.read()
        progress = state.get('workflow_progress', {})
        if isinstance(progress, dict) and progress.get('implementation'):
            assert progress['implementation'].get('tests_run', False), "Tests should be marked as run"
        
        print("✅ Progress tracking working correctly")
        self.passed += 1
        
    def test_workflow_advancement(self):
        """Test automatic workflow advancement through Stop hook."""
        print("\n🧪 Testing workflow advancement...")
        
        # Clean up any existing state
        self.cleanup_state()
        
        # Setup state with completed planning
        state_manager = StateManager(self.test_dir)
        state_manager.create(self.project_name)
        state_manager.update({
            'automation_active': True,
            'workflow_step': 'planning',
            'workflow_progress': {
                'planning': {
                    'planning_complete': True,
                    'tools_used': ['TodoWrite']
                }
            }
        })
        
        # Run Stop hook
        event = {
            "cwd": self.test_dir,
            "response": "Planning complete"
        }
        
        self.run_hook('stop', event)
        
        # Check workflow advanced
        state = state_manager.read()
        current_step = state.get('workflow_step')
        assert current_step == 'implementation', \
            f"Expected workflow to advance to 'implementation' but got '{current_step}'"
        print("  ✓ Workflow advances from planning to implementation")
        
        # Test implementation -> validation advancement
        state_manager.update({
            'workflow_step': 'implementation',
            'workflow_progress': {
                'implementation': {
                    'files_modified': ['src/main.py', 'src/utils.py']
                }
            }
        })
        
        self.run_hook('stop', event)
        
        state = state_manager.read()
        assert state.get('workflow_step') == 'validation', "Should advance to validation"
        print("  ✓ Workflow advances from implementation to validation")
        
        print("✅ Workflow advancement working correctly")
        self.passed += 1
        
    def test_pause_resume(self):
        """Test pause and resume functionality."""
        print("\n🧪 Testing pause/resume...")
        
        # Clean up any existing state
        self.cleanup_state()
        
        # Setup active automation
        state_manager = StateManager(self.test_dir)
        state_manager.create(self.project_name)
        state_manager.update({
            'automation_active': True,
            'workflow_step': 'implementation'
        })
        
        # Test pause
        state_manager.update({'automation_active': False})
        
        # Verify hooks don't enforce when paused
        event = {
            "cwd": self.test_dir,
            "tool": "Write",
            "input": {"file_path": "test.py", "content": "# test"}
        }
        response = self.run_hook('pre_tool_use', event)
        assert response.get('decision') == 'allow', "Should allow all when paused"
        print("  ✓ Automation paused - all tools allowed")
        
        # Test resume
        state_manager.update({'automation_active': True})
        
        # Move to planning to test enforcement
        state_manager.update({'workflow_step': 'planning'})
        response = self.run_hook('pre_tool_use', event)
        assert response.get('decision') == 'block', "Should enforce when resumed"
        print("  ✓ Automation resumed - rules enforced")
        
        print("✅ Pause/resume working correctly")
        self.passed += 1
        
    def test_emergency_override(self):
        """Test emergency override functionality."""
        print("\n🧪 Testing emergency override...")
        
        # Clean up any existing state
        self.cleanup_state()
        
        # Setup state in planning (normally blocks Write)
        state_manager = StateManager(self.test_dir)
        state_manager.create(self.project_name)
        state_manager.update({
            'automation_active': True,
            'workflow_step': 'planning'
        })
        
        # Test emergency override
        event = {
            "cwd": self.test_dir,
            "tool": "Bash",
            "input": {"command": "EMERGENCY: fix critical bug"}
        }
        
        response = self.run_hook('pre_tool_use', event)
        assert response.get('decision') == 'allow', "Emergency should override rules"
        print("  ✓ Emergency override allows restricted operations")
        
        # Verify metrics updated
        state = state_manager.read()
        metrics = state.get('metrics', {})
        assert metrics.get('emergency_overrides', 0) > 0, "Should track overrides"
        print("  ✓ Emergency overrides tracked in metrics")
        
        print("✅ Emergency override working correctly")
        self.passed += 1
        
    def test_quality_gates(self):
        """Test quality gate enforcement."""
        print("\n🧪 Testing quality gates...")
        
        # Clean up any existing state
        self.cleanup_state()
        
        # Setup state
        state_manager = StateManager(self.test_dir)
        state_manager.create(self.project_name)
        state_manager.update({
            'automation_active': True,
            'workflow_step': 'validation'
        })
        
        # Simulate successful test run
        event = {
            "cwd": self.test_dir,
            "tool": "Bash",
            "input": {"command": "pytest tests/"},
            "exit_code": 0
        }
        
        self.run_hook('post_tool_use', event)
        
        # Check quality gate passed
        state = state_manager.read()
        gates = state.get('quality_gates_passed', [])
        assert 'existing_tests' in gates, "Test gate should be marked"
        print("  ✓ Test quality gate tracked")
        
        # Simulate build success
        event['input']['command'] = 'make build'
        self.run_hook('post_tool_use', event)
        
        state = state_manager.read()
        gates = state.get('quality_gates_passed', [])
        assert 'compilation' in gates, "Build gate should be marked"
        print("  ✓ Build quality gate tracked")
        
        print("✅ Quality gates working correctly")
        self.passed += 1
        
    def test_error_recovery(self):
        """Test error handling and recovery."""
        print("\n🧪 Testing error recovery...")
        
        # Test 1: Missing state file
        event = {
            "cwd": "/nonexistent/path",
            "tool": "Write",
            "input": {"file_path": "test.py", "content": "test"}
        }
        
        response = self.run_hook('pre_tool_use', event)
        assert response.get('decision') == 'allow', "Should allow when no state"
        print("  ✓ Handles missing state gracefully")
        
        # Test 2: Corrupt state file
        state_path = Path(self.test_dir) / '.project-state.json'
        state_path.write_text('{"invalid": json')
        
        event['cwd'] = self.test_dir
        response = self.run_hook('pre_tool_use', event)
        assert 'decision' in response, "Should still return a decision"
        print("  ✓ Handles corrupt state gracefully")
        
        print("✅ Error recovery working correctly")
        self.passed += 1
        
    def run_all_tests(self):
        """Run all integration tests."""
        print("\n" + "="*60)
        print("🚀 Running Workflow Integration Tests")
        print("="*60)
        
        tests = [
            self.test_project_setup,
            self.test_workflow_enforcement,
            self.test_progress_tracking,
            self.test_workflow_advancement,
            self.test_pause_resume,
            self.test_emergency_override,
            self.test_quality_gates,
            self.test_error_recovery
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
    test = WorkflowIntegrationTest()
    
    try:
        test.setup()
        success = test.run_all_tests()
        test.teardown()
        
        if success:
            print("\n✅ All integration tests passed!")
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