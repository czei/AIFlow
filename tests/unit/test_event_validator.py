#!/usr/bin/env python3
"""
Unit tests for EventValidator - validates Claude Code event data structures.
"""

import pytest
import sys
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.hooks.event_validator import EventValidator


class TestEventValidator:
    """Test the EventValidator class."""
    
    # Test PreToolUse Validation
    
    def test_validate_pre_tool_use_valid_event(self):
        """Test validation of a valid pre_tool_use event."""
        event = {
            'cwd': '/home/user/project',
            'tool': 'Read',
            'input': {
                'file_path': 'test.py'
            }
        }
        
        is_valid, error = EventValidator.validate_pre_tool_use(event)
        assert is_valid
        assert error is None
    
    def test_validate_pre_tool_use_missing_required_field(self):
        """Test validation fails when required field is missing."""
        # Missing 'tool' field
        event = {
            'cwd': '/home/user/project',
            'input': {'file_path': 'test.py'}
        }
        
        is_valid, error = EventValidator.validate_pre_tool_use(event)
        assert not is_valid
        assert 'Missing required field: tool' in error
        
        # Missing 'cwd' field
        event = {
            'tool': 'Read',
            'input': {'file_path': 'test.py'}
        }
        
        is_valid, error = EventValidator.validate_pre_tool_use(event)
        assert not is_valid
        assert 'Missing required field: cwd' in error
    
    def test_validate_pre_tool_use_wrong_type(self):
        """Test validation fails when field has wrong type."""
        event = {
            'cwd': '/home/user/project',
            'tool': 'Read',
            'input': 'not a dict'  # Should be dict
        }
        
        is_valid, error = EventValidator.validate_pre_tool_use(event)
        assert not is_valid
        assert 'Field input must be dict' in error
    
    def test_validate_pre_tool_use_tool_specific_validation(self):
        """Test tool-specific input validation."""
        # Valid Write tool
        event = {
            'cwd': '/home/user/project',
            'tool': 'Write',
            'input': {
                'file_path': 'new.py',
                'content': 'print("hello")'
            }
        }
        is_valid, error = EventValidator.validate_pre_tool_use(event)
        assert is_valid
        
        # Invalid Write tool (missing content)
        event = {
            'cwd': '/home/user/project',
            'tool': 'Write',
            'input': {
                'file_path': 'new.py'
            }
        }
        is_valid, error = EventValidator.validate_pre_tool_use(event)
        assert not is_valid
        assert 'Invalid input for Write' in error
    
    def test_validate_pre_tool_use_not_dict(self):
        """Test validation fails when event is not a dict."""
        is_valid, error = EventValidator.validate_pre_tool_use("not a dict")
        assert not is_valid
        assert 'Event data must be a dictionary' in error
    
    # Test PostToolUse Validation
    
    def test_validate_post_tool_use_valid_event(self):
        """Test validation of a valid post_tool_use event."""
        event = {
            'cwd': '/home/user/project',
            'tool': 'Bash',
            'input': {'command': 'python test.py'},
            'exit_code': 0,
            'output': 'Tests passed',
            'duration': 1.5
        }
        
        is_valid, error = EventValidator.validate_post_tool_use(event)
        assert is_valid
        assert error is None
    
    def test_validate_post_tool_use_missing_exit_code(self):
        """Test validation fails when exit_code is missing."""
        event = {
            'cwd': '/home/user/project',
            'tool': 'Bash',
            'input': {'command': 'python test.py'}
        }
        
        is_valid, error = EventValidator.validate_post_tool_use(event)
        assert not is_valid
        assert 'Missing required field: exit_code' in error
    
    def test_validate_post_tool_use_invalid_exit_code(self):
        """Test validation fails for invalid exit codes."""
        # Exit code too high
        event = {
            'cwd': '/home/user/project',
            'tool': 'Bash',
            'input': {'command': 'test'},
            'exit_code': 300
        }
        is_valid, error = EventValidator.validate_post_tool_use(event)
        assert not is_valid
        assert 'Invalid exit_code: 300' in error
        
        # Exit code too low
        event['exit_code'] = -300
        is_valid, error = EventValidator.validate_post_tool_use(event)
        assert not is_valid
        assert 'Invalid exit_code: -300' in error
        
        # Exit code not integer
        event['exit_code'] = "0"
        is_valid, error = EventValidator.validate_post_tool_use(event)
        assert not is_valid
        assert 'Field exit_code must be int' in error
    
    def test_validate_post_tool_use_duration_types(self):
        """Test validation accepts both int and float for duration."""
        event = {
            'cwd': '/home/user/project',
            'tool': 'Bash',
            'input': {'command': 'test'},
            'exit_code': 0,
            'duration': 1  # int
        }
        is_valid, error = EventValidator.validate_post_tool_use(event)
        assert is_valid
        
        event['duration'] = 1.5  # float
        is_valid, error = EventValidator.validate_post_tool_use(event)
        assert is_valid
        
        event['duration'] = "1.5"  # string (invalid)
        is_valid, error = EventValidator.validate_post_tool_use(event)
        assert not is_valid
        assert 'Field duration must be one of' in error
    
    # Test Stop Validation
    
    def test_validate_stop_valid_event(self):
        """Test validation of a valid stop event."""
        event = {
            'cwd': '/home/user/project',
            'response': 'Task completed successfully'
        }
        
        is_valid, error = EventValidator.validate_stop(event)
        assert is_valid
        assert error is None
    
    def test_validate_stop_minimal_event(self):
        """Test validation with minimal stop event."""
        event = {'cwd': '/home/user/project'}
        
        is_valid, error = EventValidator.validate_stop(event)
        assert is_valid
        assert error is None
    
    def test_validate_stop_missing_cwd(self):
        """Test validation fails when cwd is missing."""
        event = {'response': 'Done'}
        
        is_valid, error = EventValidator.validate_stop(event)
        assert not is_valid
        assert 'Missing required field: cwd' in error
    
    # Test Tool-Specific Input Schemas
    
    def test_edit_tool_validation(self):
        """Test Edit tool input validation."""
        # Valid Edit
        input_data = {
            'file_path': 'test.py',
            'old_string': 'foo',
            'new_string': 'bar',
            'replace_all': True
        }
        event = {
            'cwd': '/project',
            'tool': 'Edit',
            'input': input_data
        }
        is_valid, error = EventValidator.validate_pre_tool_use(event)
        assert is_valid
        
        # Missing required field
        del input_data['new_string']
        is_valid, error = EventValidator.validate_pre_tool_use(event)
        assert not is_valid
        assert 'Missing required field: new_string' in error
    
    def test_multi_edit_tool_validation(self):
        """Test MultiEdit tool input validation."""
        # Valid MultiEdit
        input_data = {
            'file_path': 'test.py',
            'edits': [
                {'old_string': 'foo', 'new_string': 'bar'},
                {'old_string': 'baz', 'new_string': 'qux'}
            ]
        }
        event = {
            'cwd': '/project',
            'tool': 'MultiEdit',
            'input': input_data
        }
        is_valid, error = EventValidator.validate_pre_tool_use(event)
        assert is_valid
        
        # Wrong type for edits
        input_data['edits'] = 'not a list'
        is_valid, error = EventValidator.validate_pre_tool_use(event)
        assert not is_valid
        assert 'Field edits must be list' in error
    
    def test_bash_tool_validation(self):
        """Test Bash tool input validation."""
        # Valid Bash with all fields
        input_data = {
            'command': 'python test.py',
            'timeout': 300,
            'description': 'Run tests'
        }
        event = {
            'cwd': '/project',
            'tool': 'Bash',
            'input': input_data
        }
        is_valid, error = EventValidator.validate_pre_tool_use(event)
        assert is_valid
        
        # Missing required command
        del input_data['command']
        is_valid, error = EventValidator.validate_pre_tool_use(event)
        assert not is_valid
        assert 'Missing required field: command' in error
    
    def test_todo_write_validation(self):
        """Test TodoWrite tool input validation."""
        # Valid TodoWrite
        input_data = {
            'todos': [
                {'content': 'Task 1', 'status': 'pending', 'priority': 'high', 'id': '1'},
                {'content': 'Task 2', 'status': 'completed', 'priority': 'low', 'id': '2'}
            ]
        }
        event = {
            'cwd': '/project',
            'tool': 'TodoWrite',
            'input': input_data
        }
        is_valid, error = EventValidator.validate_pre_tool_use(event)
        assert is_valid
        
        # Wrong type for todos
        input_data['todos'] = 'not a list'
        is_valid, error = EventValidator.validate_pre_tool_use(event)
        assert not is_valid
        assert 'Field todos must be list' in error
    
    def test_unknown_tool_validation(self):
        """Test validation passes for unknown tools."""
        event = {
            'cwd': '/project',
            'tool': 'UnknownTool',
            'input': {'some': 'data'}
        }
        
        # Should pass - no specific validation for unknown tools
        is_valid, error = EventValidator.validate_pre_tool_use(event)
        assert is_valid


if __name__ == '__main__':
    pytest.main([__file__, '-v'])