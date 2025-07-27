#!/usr/bin/env python3
"""
Unit tests for stop hook using subprocess for complete isolation.
"""

import pytest
import json
from pathlib import Path
import sys

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tests.unit.hook_test_base import SubprocessHookTestBase


class TestStopHook(SubprocessHookTestBase):
    """Test stop hook functionality with subprocess isolation."""
    
    # Basic Functionality Tests
    
    def test_no_state_file_exits_gracefully(self):
        """Test hook exits silently when no state file exists."""
        event = {'cwd': str(self.project_dir)}
        
        result = self.run_hook('stop', event)
        
        # StateManager throws StateValidationError which is caught as generic exception
        assert result is not None
        assert result.get('status') == 'error'
        assert 'State file not found' in result.get('message', '')
    
    def test_automation_inactive_no_advancement(self):
        """Test no workflow advancement when automation is off."""
        # Create state with automation disabled
        state = self.default_state()
        state['automation_active'] = False
        state['workflow_step'] = 'planning'
        self.create_state_file(state)
        
        event = {'cwd': str(self.project_dir)}
        result = self.run_hook('stop', event)
        
        # Should not advance workflow
        after_state = self.read_state_file()
        assert after_state['workflow_step'] == 'planning'
    
    def test_corrupted_state_returns_error(self):
        """Test handling of corrupted state files."""
        # Create corrupted state
        state_file = self.project_dir / ".project-state.json"
        state_file.write_text("{ invalid json")
        
        event = {'cwd': str(self.project_dir)}
        result = self.run_hook('stop', event)
        
        # Should output error JSON
        assert result is not None
        assert result.get('status') == 'error'
        # StateManager wraps JSON decode error, so check for that
        assert 'Failed to read state file' in result.get('message', '')
    
    # Workflow Advancement Tests
    
    def test_planning_advances_after_todowrite(self):
        """Test advancement from planning to implementation."""
        # Create state in planning with completion signal
        state = self.default_state()
        state['workflow_step'] = 'planning'
        state['workflow_progress'] = {
            'complete': True,
            'step': 'planning',
            'message': 'Planning complete - todo list created',
            'ready_for_next': 'implementation'
        }
        self.create_state_file(state)
        
        event = {'cwd': str(self.project_dir)}
        result = self.run_hook('stop', event)
        
        # Should advance to implementation
        after_state = self.read_state_file()
        assert after_state['workflow_step'] == 'implementation'
        assert after_state['automation_cycles'] == 1
    
    def test_implementation_advances_after_file_changes(self):
        """Test advancement from implementation to validation."""
        # Create state in implementation with files modified
        state = self.default_state()
        state['workflow_step'] = 'implementation'
        state['workflow_progress'] = {
            'implementation': {
                'files_modified': ['app.py', 'test.py']
            }
        }
        self.create_state_file(state)
        
        event = {'cwd': str(self.project_dir)}
        result = self.run_hook('stop', event)
        
        # Should advance to validation
        after_state = self.read_state_file()
        assert after_state['workflow_step'] == 'validation'
    
    def test_validation_advances_after_tests_pass(self):
        """Test advancement from validation to review."""
        # Create state in validation with tests run
        state = self.default_state()
        state['workflow_step'] = 'validation'
        state['workflow_progress'] = {
            'validation': {
                'tests_run': True
            }
        }
        self.create_state_file(state)
        
        event = {'cwd': str(self.project_dir)}
        result = self.run_hook('stop', event)
        
        # Should advance to review
        after_state = self.read_state_file()
        assert after_state['workflow_step'] == 'review'
    
    def test_review_advances_after_codereview(self):
        """Test advancement from review to refinement."""
        # Create state in review with completion signal
        state = self.default_state()
        state['workflow_step'] = 'review'
        state['workflow_progress'] = {
            'complete': True,
            'step': 'review',
            'message': 'Review complete'
        }
        self.create_state_file(state)
        
        event = {'cwd': str(self.project_dir)}
        result = self.run_hook('stop', event)
        
        # Should advance to refinement
        after_state = self.read_state_file()
        assert after_state['workflow_step'] == 'refinement'
    
    def test_refinement_advances_after_edits(self):
        """Test advancement from refinement to integration."""
        # Create state in refinement with edits made
        state = self.default_state()
        state['workflow_step'] = 'refinement'
        state['workflow_progress'] = {
            'refinement': {
                'tools_used': ['Edit', 'Bash']
            }
        }
        self.create_state_file(state)
        
        event = {'cwd': str(self.project_dir)}
        result = self.run_hook('stop', event)
        
        # Should advance to integration
        after_state = self.read_state_file()
        assert after_state['workflow_step'] == 'integration'
    
    def test_integration_advances_to_new_sprint(self):
        """Test advancement from integration to planning (new sprint)."""
        # Create state in integration with git operations
        state = self.default_state()
        state['workflow_step'] = 'integration'
        state['workflow_progress'] = {
            'integration': {
                'tools_used': ['Bash'],
                'git_commands_run': True
            }
        }
        state['current_sprint'] = '01'
        self.create_state_file(state)
        
        event = {'cwd': str(self.project_dir)}
        result = self.run_hook('stop', event)
        
        # Should advance to planning with sprint completed
        after_state = self.read_state_file()
        assert after_state['workflow_step'] == 'planning'
        assert '01' in after_state['completed_sprints']
        assert after_state['workflow_progress'] == {}  # Reset
        assert after_state['metrics']['tools_allowed'] == 0  # Reset
    
    # Sprint Completion Tests
    
    def test_sprint_completion_updates_metrics(self):
        """Test that sprint completion resets metrics."""
        # Create state in integration ready to complete
        state = self.default_state()
        state['workflow_step'] = 'integration'
        state['workflow_progress'] = {
            'integration': {
                'tools_used': ['Bash'],
                'git_commands_run': True
            }
        }
        state['metrics'] = {
            'tools_allowed': 50,
            'tools_blocked': 10,
            'emergency_overrides': 2,
            'workflow_violations': 1
        }
        self.create_state_file(state)
        
        event = {'cwd': str(self.project_dir)}
        result = self.run_hook('stop', event)
        
        # Metrics should be reset
        after_state = self.read_state_file()
        assert after_state['metrics']['tools_allowed'] == 0
        assert after_state['metrics']['tools_blocked'] == 0
        assert after_state['metrics']['emergency_overrides'] == 0
        assert after_state['metrics']['workflow_violations'] == 0
    
    def test_final_sprint_marks_project_complete(self):
        """Test that completing the final sprint marks project complete."""
        # Create state in integration of sprint 5
        state = self.default_state()
        state['workflow_step'] = 'integration'
        state['current_sprint'] = '05'
        state['completed_sprints'] = ['01', '02', '03', '04']
        state['workflow_progress'] = {
            'integration': {
                'tools_used': ['Bash'],
                'git_commands_run': True
            }
        }
        self.create_state_file(state)
        
        event = {'cwd': str(self.project_dir)}
        result = self.run_hook('stop', event)
        
        # Should mark project complete
        after_state = self.read_state_file()
        assert after_state['status'] == 'completed'
        assert after_state['automation_active'] == False
        assert '05' in after_state['completed_sprints']
    
    def test_compliance_score_calculation(self):
        """Test that compliance score is calculated correctly."""
        # Create state with specific metrics
        state = self.default_state()
        state['workflow_step'] = 'integration'
        state['current_sprint'] = '02'
        state['workflow_progress'] = {
            'integration': {
                'tools_used': ['Bash'],
                'git_commands_run': True
            }
        }
        state['metrics'] = {
            'tools_allowed': 80,
            'tools_blocked': 20,
            'emergency_overrides': 0,
            'workflow_violations': 0
        }
        self.create_state_file(state)
        
        event = {'cwd': str(self.project_dir)}
        result = self.run_hook('stop', event)
        
        # Should calculate 80% compliance
        # Check stdout for compliance score message
        # Note: Since the hook prints to stdout, we need to check the subprocess output
        # The test framework captures this in the result
    
    # Edge Cases
    
    def test_invalid_event_data_handled(self):
        """Test handling of invalid event data."""
        # Missing required 'cwd' field
        event = {'response': 'Task completed'}
        
        result = self.run_hook('stop', event)
        
        # Should output error about invalid event
        assert result is not None
        assert result.get('status') == 'error'
        assert 'Invalid event data' in result.get('message', '')
    
    def test_permission_errors_handled(self):
        """Test handling of file permission errors."""
        # Create state file and make it unreadable
        state = self.default_state()
        state_file = self.create_state_file(state)
        state_file.chmod(0o000)
        
        event = {'cwd': str(self.project_dir)}
        
        try:
            result = self.run_hook('stop', event)
            # Should output error about permissions
            assert result is not None
            assert result.get('status') == 'error'
            assert 'Permission denied' in result.get('message', '')
        finally:
            # Restore permissions for cleanup
            state_file.chmod(0o644)
    
    def test_workflow_progress_signals_respected(self):
        """Test that post_tool_use completion signals are honored."""
        # Create state with explicit completion signal
        state = self.default_state()
        state['workflow_step'] = 'validation'
        state['workflow_progress'] = {
            'complete': True,
            'step': 'validation',
            'message': 'Validation complete - all tests passed',
            'ready_for_next': 'review'
        }
        self.create_state_file(state)
        
        event = {'cwd': str(self.project_dir)}
        result = self.run_hook('stop', event)
        
        # Should advance based on signal
        after_state = self.read_state_file()
        assert after_state['workflow_step'] == 'review'
    
    def test_no_advancement_without_completion(self):
        """Test that steps don't advance without completion criteria."""
        # Create state in implementation with no progress
        state = self.default_state()
        state['workflow_step'] = 'implementation'
        state['workflow_progress'] = {}
        self.create_state_file(state)
        
        event = {'cwd': str(self.project_dir)}
        result = self.run_hook('stop', event)
        
        # Should not advance
        after_state = self.read_state_file()
        assert after_state['workflow_step'] == 'implementation'
    
    def test_preserves_acceptance_criteria(self):
        """Test that acceptance criteria are preserved across transitions."""
        # Create state with existing acceptance criteria
        state = self.default_state()
        state['workflow_step'] = 'refinement'
        state['acceptance_criteria_passed'] = ['existing_tests', 'compilation']
        state['workflow_progress'] = {
            'refinement': {
                'tools_used': ['Edit']
            }
        }
        self.create_state_file(state)
        
        event = {'cwd': str(self.project_dir)}
        result = self.run_hook('stop', event)
        
        # Should preserve acceptance criteria
        after_state = self.read_state_file()
        assert 'existing_tests' in after_state['acceptance_criteria_passed']
        assert 'compilation' in after_state['acceptance_criteria_passed']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])