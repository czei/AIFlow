#!/usr/bin/env python3
"""
Unit tests for Claude Code hooks.

Tests the PreToolUse, PostToolUse, and Stop hooks with various scenarios.
"""

import json
import subprocess
import sys
import tempfile
import os
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.state_manager import StateManager


class TestHooks:
    """Test suite for Claude Code hooks."""
    
    def setup_method(self):
        """Create temporary directory and state for tests."""
        self.temp_dir = tempfile.mkdtemp()
        self.state_manager = StateManager(self.temp_dir)
        
    def teardown_method(self):
        """Clean up temporary directory."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def run_hook(self, hook_name: str, event_data: dict) -> dict:
        """Run a hook and return its response."""
        hook_path = Path(__file__).parent.parent.parent / 'src' / 'hooks' / f'{hook_name}.py'
        
        # Run hook as subprocess
        proc = subprocess.run(
            [sys.executable, str(hook_path)],
            input=json.dumps(event_data),
            capture_output=True,
            text=True
        )
        
        if proc.returncode != 0:
            print(f"Hook stderr: {proc.stderr}")
            
        # Parse response
        try:
            return json.loads(proc.stdout)
        except json.JSONDecodeError:
            print(f"Hook stdout: {proc.stdout}")
            return {}
    
    def test_pre_tool_use_no_state(self):
        """Test PreToolUse hook when no state file exists."""
        event = {
            "cwd": self.temp_dir,
            "tool": "Write",
            "input": {"file_path": "test.py", "content": "print('hello')"}
        }
        
        response = self.run_hook('pre_tool_use', event)
        assert response.get('decision') == 'allow'
    
    def test_pre_tool_use_automation_inactive(self):
        """Test PreToolUse hook when automation is not active."""
        # Create state with automation inactive
        self.state_manager.create('test-project')
        
        event = {
            "cwd": self.temp_dir,
            "tool": "Write",
            "input": {"file_path": "test.py", "content": "print('hello')"}
        }
        
        response = self.run_hook('pre_tool_use', event)
        assert response.get('decision') == 'allow'
    
    def test_pre_tool_use_planning_blocks_write(self):
        """Test PreToolUse hook blocks Write tool during planning sprint."""
        # Create state with automation active and planning sprint
        self.state_manager.create('test-project')
        self.state_manager.update({
            'automation_active': True,
            'workflow_step': 'planning'
        })
        
        event = {
            "cwd": self.temp_dir,
            "tool": "Write",
            "input": {"file_path": "test.py", "content": "print('hello')"}
        }
        
        response = self.run_hook('pre_tool_use', event)
        assert response.get('decision') == 'block'
        assert 'Planning sprint' in response.get('reason', '')
    
    def test_pre_tool_use_planning_allows_read(self):
        """Test PreToolUse hook allows Read tool during planning sprint."""
        # Create state with automation active and planning sprint
        self.state_manager.create('test-project')
        self.state_manager.update({
            'automation_active': True,
            'workflow_step': 'planning'
        })
        
        event = {
            "cwd": self.temp_dir,
            "tool": "Read",
            "input": {"file_path": "test.py"}
        }
        
        response = self.run_hook('pre_tool_use', event)
        assert response.get('decision') == 'allow'
    
    def test_pre_tool_use_implementation_allows_all(self):
        """Test PreToolUse hook allows all tools during implementation."""
        # Create state with implementation sprint
        self.state_manager.create('test-project')
        self.state_manager.update({
            'automation_active': True,
            'workflow_step': 'implementation'
        })
        
        event = {
            "cwd": self.temp_dir,
            "tool": "Write",
            "input": {"file_path": "test.py", "content": "print('hello')"}
        }
        
        response = self.run_hook('pre_tool_use', event)
        assert response.get('decision') == 'allow'
    
    def test_post_tool_use_tracks_progress(self):
        """Test PostToolUse hook tracks workflow progress."""
        # Create state
        self.state_manager.create('test-project')
        self.state_manager.update({
            'automation_active': True,
            'workflow_step': 'implementation'
        })
        
        event = {
            "cwd": self.temp_dir,
            "tool": "Write",
            "input": {"file_path": "test.py", "content": "print('hello')"},
            "exit_code": 0
        }
        
        # Run hook as subprocess directly (PostToolUse doesn't return JSON)
        hook_path = Path(__file__).parent.parent.parent / 'src' / 'hooks' / 'post_tool_use.py'
        proc = subprocess.run(
            [sys.executable, str(hook_path)],
            input=json.dumps(event),
            capture_output=True,
            text=True,
            cwd=self.temp_dir
        )
        
        # PostToolUse should exit with 0
        assert proc.returncode == 0
        
        # Check state was updated
        state = self.state_manager.read()
        
        # The hook should track file modifications at the state level
        assert 'test.py' in state.get('files_modified', [])
        
        # And workflow_progress should indicate completion
        progress = state.get('workflow_progress', {})
        if progress.get('complete'):
            # Step was marked complete
            assert progress.get('step') == 'implementation'
            assert 'Implementation complete' in progress.get('message', '')
        else:
            # Or check nested structure if not complete
            impl_progress = progress.get('implementation', {})
            assert 'test.py' in impl_progress.get('files_modified', [])
            assert 'Write' in impl_progress.get('tools_used', [])
    
    def test_pre_tool_use_validation_blocks_write(self):
        """Test PreToolUse hook blocks Write tool during validation sprint."""
        # Create state with validation sprint
        self.state_manager.create('test-project')
        self.state_manager.update({
            'automation_active': True,
            'workflow_step': 'validation'
        })
        
        event = {
            "cwd": self.temp_dir,
            "tool": "Write",
            "input": {"file_path": "new_test.py", "content": "print('test')"}
        }
        
        response = self.run_hook('pre_tool_use', event)
        assert response.get('decision') == 'block'
        assert 'Validation sprint' in response.get('reason', '')
    
    def test_pre_tool_use_emergency_override(self):
        """Test PreToolUse hook allows emergency overrides."""
        # Create state with planning sprint (normally blocks Write)
        self.state_manager.create('test-project')
        self.state_manager.update({
            'automation_active': True,
            'workflow_step': 'planning'
        })
        
        event = {
            "cwd": self.temp_dir,
            "tool": "Bash",
            "input": {"command": "EMERGENCY: fix production bug"}
        }
        
        response = self.run_hook('pre_tool_use', event)
        assert response.get('decision') == 'allow'
    
    def test_stop_hook_workflow_advancement(self):
        """Test Stop hook advances workflow when step is complete."""
        # Create state with implementation sprint and completion indicators
        self.state_manager.create('test-project')
        self.state_manager.update({
            'automation_active': True,
            'workflow_step': 'implementation',
            'workflow_progress': {
                'implementation': {
                    'files_modified': ['app.py', 'test_app.py'],
                    'tools_used': ['Write', 'Edit']
                }
            }
        })
        
        event = {
            "cwd": self.temp_dir,
            "response": "Implementation complete"
        }
        
        # Run stop hook
        hook_path = Path(__file__).parent.parent.parent / 'src' / 'hooks' / 'stop.py'
        proc = subprocess.run(
            [sys.executable, str(hook_path)],
            input=json.dumps(event),
            capture_output=True,
            text=True,
            cwd=self.temp_dir
        )
        
        # Should succeed
        assert proc.returncode == 0
        
        # Check workflow advanced
        state = self.state_manager.read()
        assert state.get('workflow_step') == 'validation'


def run_tests():
    """Run all tests and report results."""
    test_suite = TestHooks()
    test_methods = [m for m in dir(test_suite) if m.startswith('test_')]
    
    passed = 0
    failed = 0
    
    for test_name in test_methods:
        test_suite.setup_method()
        try:
            getattr(test_suite, test_name)()
            print(f"✅ {test_name}")
            passed += 1
        except Exception as e:
            print(f"❌ {test_name}: {e}")
            failed += 1
        finally:
            test_suite.teardown_method()
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)