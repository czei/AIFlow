#!/usr/bin/env python3
"""
Unit tests for pre_tool_use hook using subprocess for complete isolation.
"""

import pytest
from pathlib import Path
import sys

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tests.unit.hook_test_base import SubprocessHookTestBase


class TestPreToolUseHook(SubprocessHookTestBase):
    """Test pre_tool_use hook functionality with subprocess isolation."""
    
    def test_hook_allows_when_no_state_file(self, event_fixtures):
        """Test hook allows all operations when no state file exists."""
        # Don't create state file
        event = event_fixtures['read_event']
        
        response = self.run_hook('pre_tool_use', event)
        
        self.assert_allowed(response)
        assert 'State read error' in response.get('message', '')
    
    def test_hook_allows_when_automation_inactive(self, event_fixtures):
        """Test hook allows all operations when automation is not active."""
        # Create state with automation_active = False
        state = self.default_state()
        state['automation_active'] = False
        self.create_state_file(state)
        
        event = event_fixtures['write_event']
        response = self.run_hook('pre_tool_use', event)
        
        self.assert_allowed(response)
    
    def test_planning_step_blocks_write_tools(self, event_fixtures):
        """Test planning step blocks write operations."""
        # Create state in planning step
        state = self.default_state()
        state['workflow_step'] = 'planning'
        self.create_state_file(state)
        
        event = event_fixtures['write_event']
        response = self.run_hook('pre_tool_use', event)
        
        self.assert_blocked(response)
        assert 'Planning sprint' in response['reason']
        self.assert_has_suggestions(response)
    
    def test_planning_step_allows_read_tools(self, event_fixtures):
        """Test planning step allows read operations."""
        # Create state in planning step
        state = self.default_state()
        state['workflow_step'] = 'planning'
        self.create_state_file(state)
        
        event = event_fixtures['read_event']
        response = self.run_hook('pre_tool_use', event)
        
        self.assert_allowed(response)
    
    def test_planning_step_allows_todo_write(self, event_fixtures):
        """Test planning step allows TodoWrite tool."""
        # Create state in planning step
        state = self.default_state()
        state['workflow_step'] = 'planning'
        self.create_state_file(state)
        
        event = event_fixtures['todo_event']
        response = self.run_hook('pre_tool_use', event)
        
        self.assert_allowed(response)
    
    def test_implementation_step_allows_all_tools(self, event_fixtures):
        """Test implementation step allows all tools."""
        # Create state in implementation step
        state = self.default_state()
        state['workflow_step'] = 'implementation'
        self.create_state_file(state)
        
        # Test write tool
        event = event_fixtures['write_event']
        response = self.run_hook('pre_tool_use', event)
        self.assert_allowed(response)
        
        # Test bash tool
        event = event_fixtures['bash_event']
        response = self.run_hook('pre_tool_use', event)
        self.assert_allowed(response)
    
    def test_emergency_override_allows_blocked_tool(self, event_fixtures):
        """Test emergency override allows normally blocked tools."""
        # Create state in planning step (write blocked)
        state = self.default_state()
        state['workflow_step'] = 'planning'
        self.create_state_file(state)
        
        # Use emergency bash command
        event = event_fixtures['emergency_bash']
        response = self.run_hook('pre_tool_use', event)
        
        self.assert_allowed(response)
        
        # Check metrics were updated
        after_state = self.read_state_file()
        assert after_state['metrics']['emergency_overrides'] == 1
    
    def test_metrics_update_on_allow(self, event_fixtures):
        """Test metrics are updated when tool is allowed."""
        # Create initial state
        state = self.default_state()
        state['workflow_step'] = 'planning'
        self.create_state_file(state)
        
        event = event_fixtures['read_event']
        response = self.run_hook('pre_tool_use', event)
        
        self.assert_allowed(response)
        
        # Check metrics
        after_state = self.read_state_file()
        assert after_state['metrics']['tools_allowed'] == 1
        assert after_state['metrics']['tools_blocked'] == 0
    
    def test_metrics_update_on_block(self, event_fixtures):
        """Test metrics are updated when tool is blocked."""
        # Create initial state
        state = self.default_state()
        state['workflow_step'] = 'planning'
        self.create_state_file(state)
        
        event = event_fixtures['write_event']
        response = self.run_hook('pre_tool_use', event)
        
        self.assert_blocked(response)
        
        # Check metrics
        after_state = self.read_state_file()
        assert after_state['metrics']['tools_allowed'] == 0
        assert after_state['metrics']['tools_blocked'] == 1
    
    def test_invalid_event_returns_error(self):
        """Test invalid event data returns error response."""
        # Create state
        self.create_state_file()
        
        # Invalid event (missing required fields)
        event = {'tool': 'Read'}  # Missing cwd and input
        response = self.run_hook('pre_tool_use', event)
        
        self.assert_allowed(response)  # Errors allow but log
        assert 'Invalid event data' in response.get('message', '')
    
    def test_state_read_error_allows_operation(self, event_fixtures):
        """Test state read errors allow operation but log warning."""
        # Create corrupted state file
        state_file = self.project_dir / ".project-state.json"
        state_file.write_text("{ invalid json")
        
        event = event_fixtures['read_event']
        response = self.run_hook('pre_tool_use', event)
        
        self.assert_allowed(response)
        assert 'State read error' in response.get('message', '')
    
    def test_validation_step_allows_minor_edits(self, event_fixtures):
        """Test validation step allows Edit but not Write."""
        # Create state in validation step
        state = self.default_state()
        state['workflow_step'] = 'validation'
        self.create_state_file(state)
        
        # Edit should be allowed
        edit_event = {
            'cwd': str(self.project_dir),
            'tool': 'Edit',
            'input': {
                'file_path': 'test.py',
                'old_string': 'bug',
                'new_string': 'fix'
            }
        }
        response = self.run_hook('pre_tool_use', edit_event)
        self.assert_allowed(response)
        
        # Write should be blocked
        write_event = event_fixtures['write_event']
        response = self.run_hook('pre_tool_use', write_event)
        self.assert_blocked(response)
    
    def test_refinement_step_blocks_new_files(self, event_fixtures):
        """Test refinement step allows edits but not new files."""
        # Create state in refinement step
        state = self.default_state()
        state['workflow_step'] = 'refinement'
        self.create_state_file(state)
        
        # MultiEdit should be allowed
        multi_edit_event = {
            'cwd': str(self.project_dir),
            'tool': 'MultiEdit',
            'input': {
                'file_path': 'test.py',
                'edits': [
                    {'old_string': 'a', 'new_string': 'b'}
                ]
            }
        }
        response = self.run_hook('pre_tool_use', multi_edit_event)
        self.assert_allowed(response)
        
        # Write should be blocked
        write_event = event_fixtures['write_event']
        response = self.run_hook('pre_tool_use', write_event)
        self.assert_blocked(response)
    
    def test_integration_step_allows_git_tools(self):
        """Test integration step allows git operations."""
        # Create state in integration step
        state = self.default_state()
        state['workflow_step'] = 'integration'
        self.create_state_file(state)
        
        # Git operations via Bash should be allowed
        git_event = {
            'cwd': str(self.project_dir),
            'tool': 'Bash',
            'input': {'command': 'git status'}
        }
        response = self.run_hook('pre_tool_use', git_event)
        self.assert_allowed(response)
    
    def test_emergency_patterns_in_different_contexts(self):
        """Test various emergency override patterns."""
        # Create state in planning (bash blocked)
        state = self.default_state()
        state['workflow_step'] = 'planning'
        self.create_state_file(state)
        
        emergency_commands = [
            'HOTFIX: critical bug in production',
            'CRITICAL: security vulnerability found',
            'production is down, need immediate fix',
            'OVERRIDE: emergency deployment needed'
        ]
        
        for command in emergency_commands:
            event = {
                'cwd': str(self.project_dir),
                'tool': 'Bash',
                'input': {'command': command}
            }
            response = self.run_hook('pre_tool_use', event)
            self.assert_allowed(response)
    
    def test_multiple_calls_maintain_isolation(self, event_fixtures):
        """Test that multiple hook calls maintain proper isolation."""
        # Create initial state
        state = self.default_state()
        state['workflow_step'] = 'planning'
        self.create_state_file(state)
        
        # First call - block write
        response1 = self.run_hook('pre_tool_use', event_fixtures['write_event'])
        self.assert_blocked(response1)
        
        # Second call - allow read
        response2 = self.run_hook('pre_tool_use', event_fixtures['read_event'])
        self.assert_allowed(response2)
        
        # Third call - block another write
        response3 = self.run_hook('pre_tool_use', event_fixtures['write_event'])
        self.assert_blocked(response3)
        
        # Check final metrics
        final_state = self.read_state_file()
        assert final_state['metrics']['tools_allowed'] == 1
        assert final_state['metrics']['tools_blocked'] == 2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])