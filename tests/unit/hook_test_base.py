#!/usr/bin/env python3
"""
Base test class for hook testing using subprocess for true isolation.

This approach ensures complete isolation between tests by running
hooks in separate processes.
"""

import json
import sys
import os
from pathlib import Path
import pytest
import subprocess
import tempfile
import shutil

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class SubprocessHookTestBase:
    """Base class for hook tests using subprocess for complete isolation."""
    
    @pytest.fixture(autouse=True)
    def setup_test_environment(self, tmp_path):
        """Set up isolated test environment."""
        # Create test directory
        self.test_dir = tmp_path / "hook_test"
        self.test_dir.mkdir()
        self.project_dir = self.test_dir / "project"
        self.project_dir.mkdir()
        
        # Store original cwd
        self.original_cwd = os.getcwd()
        
        # Get hook paths
        self.hooks_dir = Path(__file__).parent.parent.parent / 'src' / 'hooks'
        self.pre_tool_use_hook = self.hooks_dir / 'pre_tool_use.py'
        self.post_tool_use_hook = self.hooks_dir / 'post_tool_use.py'
        self.stop_hook = self.hooks_dir / 'stop.py'
        
        yield
        
        # Restore cwd
        os.chdir(self.original_cwd)
    
    def run_hook(self, hook_name, event_data):
        """Run a hook using subprocess and return the parsed response."""
        # Determine hook path
        if hook_name == 'pre_tool_use':
            hook_path = self.pre_tool_use_hook
        elif hook_name == 'post_tool_use':
            hook_path = self.post_tool_use_hook
        elif hook_name == 'stop':
            hook_path = self.stop_hook
        else:
            raise ValueError(f"Unknown hook: {hook_name}")
        
        # Run hook as subprocess
        result = subprocess.run(
            [sys.executable, str(hook_path)],
            input=json.dumps(event_data),
            capture_output=True,
            text=True,
            cwd=str(self.project_dir),
            env={**os.environ, 'PYTHONPATH': str(Path(__file__).parent.parent.parent)}
        )
        
        # Parse output
        if result.stdout.strip():
            try:
                return json.loads(result.stdout.strip())
            except json.JSONDecodeError:
                print(f"Failed to parse output: {result.stdout}")
                print(f"Stderr: {result.stderr}")
                return None
        return None
    
    def create_state_file(self, state_data=None):
        """Create a state file in the test directory."""
        if state_data is None:
            state_data = self.default_state()
        
        state_file = self.project_dir / ".project-state.json"
        state_file.write_text(json.dumps(state_data, indent=2))
        return state_file
    
    def read_state_file(self):
        """Read the current state file."""
        state_file = self.project_dir / ".project-state.json"
        if state_file.exists():
            return json.loads(state_file.read_text())
        return None
    
    def default_state(self):
        """Get default state for testing."""
        return {
            'project_name': 'test-project',
            'current_sprint': '01',
            'status': 'active',
            'automation_active': True,
            'workflow_step': 'planning',
            'current_user_story': None,
            'quality_gates_passed': [],
            'completed_sprints': [],
            'automation_cycles': 0,
            'started': '2024-01-01T00:00:00Z',
            'last_updated': '2024-01-01T00:00:00Z',
            'git_branch': None,
            'git_worktree': '.',
            'version': '1.0.0',
            'acceptance_criteria_passed': [],
            'metrics': {
                'tools_allowed': 0,
                'tools_blocked': 0,
                'emergency_overrides': 0,
                'workflow_violations': 0
            },
            'workflow_progress': {}
        }
    
    @pytest.fixture
    def basic_event(self):
        """Create a basic valid event."""
        return {
            'cwd': str(self.project_dir),
            'tool': 'Read',
            'input': {
                'file_path': 'test.py'
            }
        }
    
    @pytest.fixture
    def event_fixtures(self):
        """Collection of common event fixtures."""
        cwd = str(self.project_dir)
        return {
            'read_event': {
                'cwd': cwd,
                'tool': 'Read',
                'input': {'file_path': 'test.py'}
            },
            'write_event': {
                'cwd': cwd,
                'tool': 'Write',
                'input': {
                    'file_path': 'new.py',
                    'content': 'print("hello")'
                }
            },
            'bash_event': {
                'cwd': cwd,
                'tool': 'Bash',
                'input': {'command': 'python test.py'}
            },
            'emergency_bash': {
                'cwd': cwd,
                'tool': 'Bash',
                'input': {'command': 'EMERGENCY: fix production issue'}
            },
            'todo_event': {
                'cwd': cwd,
                'tool': 'TodoWrite',
                'input': {
                    'todos': [
                        {'content': 'Implement feature', 'status': 'pending', 'priority': 'high', 'id': '1'}
                    ]
                }
            },
            'post_tool_success': {
                'cwd': cwd,
                'tool': 'Bash',
                'input': {'command': 'python test.py'},
                'exit_code': 0,
                'output': 'Tests passed',
                'duration': 1.5
            },
            'post_tool_failure': {
                'cwd': cwd,
                'tool': 'Bash',
                'input': {'command': 'python test.py'},
                'exit_code': 1,
                'error': 'Tests failed',
                'duration': 2.0
            },
            'stop_event': {
                'cwd': cwd,
                'response': 'Task completed successfully'
            }
        }
    
    def assert_allowed(self, response):
        """Assert that the response allows the operation."""
        assert response is not None, "No response received"
        assert response.get('decision') == 'allow', f"Expected allow, got: {response}"
    
    def assert_blocked(self, response):
        """Assert that the response blocks the operation."""
        assert response is not None, "No response received"
        assert response.get('decision') == 'block', f"Expected block, got: {response}"
        assert 'reason' in response, "Block response missing reason"
    
    def assert_has_suggestions(self, response):
        """Assert that the response includes suggestions."""
        assert 'suggestions' in response, "Response missing suggestions"
        assert isinstance(response['suggestions'], list), "Suggestions not a list"
        assert len(response['suggestions']) > 0, "No suggestions provided"
    
    def assert_metrics_updated(self, before_state, after_state, expected_changes):
        """Assert that metrics were updated correctly."""
        before_metrics = before_state.get('metrics', {})
        after_metrics = after_state.get('metrics', {})
        
        for metric, expected_delta in expected_changes.items():
            before_val = before_metrics.get(metric, 0)
            after_val = after_metrics.get(metric, 0)
            actual_delta = after_val - before_val
            assert actual_delta == expected_delta, \
                f"{metric}: expected delta {expected_delta}, got {actual_delta}"