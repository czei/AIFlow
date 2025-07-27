#!/usr/bin/env python3
"""
Focused unit tests for post_tool_use hook based on actual behavior.
"""

import pytest
import json
import os
from pathlib import Path
import sys
import subprocess

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tests.unit.hook_test_base import SubprocessHookTestBase


class TestPostToolUseHookFocused(SubprocessHookTestBase):
    """Focused tests for post_tool_use hook based on actual behavior."""
    
    def run_post_tool_hook(self, event):
        """Run post_tool_use hook and return result."""
        result = subprocess.run(
            [sys.executable, str(self.post_tool_use_hook)],
            input=json.dumps(event),
            capture_output=True,
            text=True,
            cwd=str(self.project_dir),
            env={**os.environ, 'PYTHONPATH': str(Path(__file__).parent.parent.parent)}
        )
        return result
    
    def test_hook_handles_missing_state_gracefully(self):
        """Test hook exits cleanly when no state file exists."""
        event = {
            'cwd': str(self.project_dir),
            'tool': 'Read',
            'input': {'file_path': 'test.py'},
            'exit_code': 0
        }
        
        result = self.run_post_tool_hook(event)
        assert result.returncode == 0
    
    def test_planning_completion_via_todowrite(self):
        """Test that TodoWrite in planning step marks it complete."""
        # Create state in planning
        state = self.default_state()
        state['workflow_step'] = 'planning'
        self.create_state_file(state)
        
        # Use TodoWrite
        event = {
            'cwd': str(self.project_dir),
            'tool': 'TodoWrite',
            'input': {
                'todos': [
                    {'content': 'Implement feature', 'status': 'pending', 'priority': 'high', 'id': '1'}
                ]
            },
            'exit_code': 0
        }
        
        result = self.run_post_tool_hook(event)
        assert result.returncode == 0
        
        # Check workflow_progress shows completion
        after_state = self.read_state_file()
        progress = after_state.get('workflow_progress', {})
        assert progress.get('complete') == True
        assert progress.get('step') == 'planning'
        assert 'Planning complete' in progress.get('message', '')
        assert progress.get('ready_for_next') == 'implementation'
        
        # Check output
        assert 'Planning complete' in result.stdout
    
    def test_review_completion_via_codereview(self):
        """Test that codereview tool in review step marks it complete."""
        # Create state in review
        state = self.default_state()
        state['workflow_step'] = 'review'
        self.create_state_file(state)
        
        # Use codereview tool
        event = {
            'cwd': str(self.project_dir),
            'tool': 'mcp__zen__codereview',
            'input': {},
            'exit_code': 0
        }
        
        result = self.run_post_tool_hook(event)
        assert result.returncode == 0
        
        # Check workflow_progress shows completion
        after_state = self.read_state_file()
        progress = after_state.get('workflow_progress', {})
        assert progress.get('complete') == True
        assert progress.get('step') == 'review'
        
        # Also check quality gate
        assert 'review' in after_state.get('acceptance_criteria_passed', [])
    
    def test_test_execution_updates_quality_gates(self):
        """Test that successful test execution updates acceptance criteria."""
        # Create state in validation
        state = self.default_state()
        state['workflow_step'] = 'validation'
        self.create_state_file(state)
        
        # Run tests
        event = {
            'cwd': str(self.project_dir),
            'tool': 'Bash',
            'input': {'command': 'pytest tests/'},
            'exit_code': 0
        }
        
        result = self.run_post_tool_hook(event)
        assert result.returncode == 0
        
        # Check quality gates
        after_state = self.read_state_file()
        assert 'existing_tests' in after_state.get('acceptance_criteria_passed', [])
        
        # Check output
        assert 'Quality gate passed' in result.stdout
    
    def test_build_success_updates_compilation_gate(self):
        """Test that successful build updates compilation gate."""
        # Create state
        state = self.default_state()
        state['workflow_step'] = 'validation'
        self.create_state_file(state)
        
        # Run build
        event = {
            'cwd': str(self.project_dir),
            'tool': 'Bash',
            'input': {'command': 'npm run build'},
            'exit_code': 0
        }
        
        result = self.run_post_tool_hook(event)
        assert result.returncode == 0
        
        # Check quality gates
        after_state = self.read_state_file()
        assert 'compilation' in after_state.get('acceptance_criteria_passed', [])
    
    def test_file_modifications_tracked_globally(self):
        """Test that file modifications are tracked at top level."""
        # Create state
        state = self.default_state()
        state['workflow_step'] = 'implementation'
        self.create_state_file(state)
        
        # Write a file
        event = {
            'cwd': str(self.project_dir),
            'tool': 'Write',
            'input': {
                'file_path': 'feature.py',
                'content': 'def feature(): pass'
            },
            'exit_code': 0
        }
        
        result = self.run_post_tool_hook(event)
        assert result.returncode == 0
        
        # Check file tracked at top level
        after_state = self.read_state_file()
        assert 'feature.py' in after_state.get('files_modified', [])
    
    def test_validation_completion_when_tests_pass(self):
        """Test validation step completion when tests pass."""
        # Create state in validation
        state = self.default_state()
        state['workflow_step'] = 'validation'
        self.create_state_file(state)
        
        # Run passing tests
        event = {
            'cwd': str(self.project_dir),
            'tool': 'Bash',
            'input': {'command': 'pytest'},
            'exit_code': 0,
            'output': '====== 10 passed ======'
        }
        
        result = self.run_post_tool_hook(event)
        assert result.returncode == 0
        
        # Check completion
        after_state = self.read_state_file()
        progress = after_state.get('workflow_progress', {})
        assert progress.get('complete') == True
        assert progress.get('step') == 'validation'
        assert 'Validation complete' in progress.get('message', '')
    
    def test_automation_inactive_prevents_updates(self):
        """Test that no updates occur when automation is inactive."""
        # Create state with automation disabled
        state = self.default_state()
        state['automation_active'] = False
        original_state = state.copy()
        self.create_state_file(state)
        
        # Try various operations
        event = {
            'cwd': str(self.project_dir),
            'tool': 'Write',
            'input': {
                'file_path': 'test.py',
                'content': 'print("test")'
            },
            'exit_code': 0
        }
        
        result = self.run_post_tool_hook(event)
        assert result.returncode == 0
        
        # Check no changes were made
        after_state = self.read_state_file()
        # Only last_updated should change
        assert after_state.get('files_modified', []) == original_state.get('files_modified', [])
        assert after_state.get('workflow_progress', {}) == original_state.get('workflow_progress', {})
    
    def test_invalid_event_exits_gracefully(self):
        """Test graceful handling of invalid events."""
        # Create state
        self.create_state_file()
        
        # Invalid event (missing required fields)
        event = {'tool': 'Bash'}
        
        result = self.run_post_tool_hook(event)
        assert result.returncode == 0
        assert "Invalid event" in result.stdout
    
    def test_corrupted_state_returns_error(self):
        """Test handling of corrupted state files."""
        # Create corrupted state
        state_file = self.project_dir / ".project-state.json"
        state_file.write_text("{ invalid json")
        
        event = {
            'cwd': str(self.project_dir),
            'tool': 'Read',
            'input': {'file_path': 'test.py'},
            'exit_code': 0
        }
        
        result = self.run_post_tool_hook(event)
        assert result.returncode == 0
        # Should output error JSON
        output = json.loads(result.stdout.strip())
        assert output.get('status') == 'error'
        assert 'Unexpected error' in output.get('message', '')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])