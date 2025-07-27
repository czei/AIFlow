#!/usr/bin/env python3
"""
Unit tests for hook_utils.py - shared functions for all hooks.
"""

import pytest
import json
import sys
import os
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock
import tempfile

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.hooks.hook_utils import (
    HookConfig, HookLogger, EventParser, ResponseBuilder,
    format_time_delta, safe_state_update
)


class TestHookConfig:
    """Test the HookConfig class."""
    
    def test_load_default_config(self):
        """Test loading default config when file doesn't exist."""
        # Reset cached config
        HookConfig._config = None
        
        with patch('pathlib.Path.open', side_effect=FileNotFoundError):
            config = HookConfig.load()
        
        # Should return default config
        assert 'workflow_enforcement' in config
        assert config['workflow_enforcement']['mode'] == 'guided_flexibility'
        assert config['workflow_enforcement']['allow_emergency_override'] == True
        assert config['metrics']['track_compliance'] == True
    
    def test_load_config_from_file(self):
        """Test loading config from JSON file."""
        # Reset cached config
        HookConfig._config = None
        
        test_config = {
            'workflow_enforcement': {
                'mode': 'strict',
                'allow_emergency_override': False
            },
            'metrics': {
                'track_compliance': False
            }
        }
        
        # Need to mock builtins.open instead
        with patch('builtins.open', mock_open(read_data=json.dumps(test_config))):
            config = HookConfig.load()
        
        assert config['workflow_enforcement']['mode'] == 'strict'
        assert config['workflow_enforcement']['allow_emergency_override'] == False
    
    def test_load_config_cached(self):
        """Test that config is cached after first load."""
        # Reset cached config
        HookConfig._config = None
        
        # First load
        with patch('pathlib.Path.open', side_effect=FileNotFoundError):
            config1 = HookConfig.load()
        
        # Second load should return cached value
        with patch('pathlib.Path.open', side_effect=Exception("Should not be called")):
            config2 = HookConfig.load()
        
        assert config1 is config2  # Same object
    
    def test_load_emergency_overrides(self):
        """Test loading emergency override patterns."""
        # Reset cached overrides
        HookConfig._emergency_overrides = None
        
        test_overrides = {
            'patterns': ['URGENT:', 'CRITICAL:'],
            'context_patterns': ['production.*broken']
        }
        
        with patch('builtins.open', mock_open(read_data=json.dumps(test_overrides))):
            overrides = HookConfig.load_emergency_overrides()
        
        assert 'URGENT:' in overrides['patterns']
        assert 'production.*broken' in overrides['context_patterns']
    
    def test_load_emergency_overrides_default(self):
        """Test default emergency overrides when file missing."""
        # Reset cached overrides
        HookConfig._emergency_overrides = None
        
        with patch('builtins.open', side_effect=FileNotFoundError):
            overrides = HookConfig.load_emergency_overrides()
        
        assert overrides == {'patterns': [], 'context_patterns': []}


class TestHookLogger:
    """Test the HookLogger class."""
    
    def test_log_basic_message(self, capsys):
        """Test basic logging to stderr."""
        HookLogger.log("Test message", "INFO")
        
        captured = capsys.readouterr()
        assert "[INFO] Test message" in captured.err
        assert captured.out == ""  # Nothing to stdout
    
    def test_debug_log_when_enabled(self, capsys):
        """Test debug logging when HOOK_DEBUG is set."""
        with patch.dict(os.environ, {'HOOK_DEBUG': '1'}):
            HookLogger.debug("Debug message")
        
        captured = capsys.readouterr()
        assert "[DEBUG] Debug message" in captured.err
    
    def test_debug_log_when_disabled(self, capsys):
        """Test debug logging is suppressed when HOOK_DEBUG not set."""
        with patch.dict(os.environ, {}, clear=True):
            HookLogger.debug("Debug message")
        
        captured = capsys.readouterr()
        assert captured.err == ""
    
    def test_error_log(self, capsys):
        """Test error logging."""
        HookLogger.error("Error occurred")
        
        captured = capsys.readouterr()
        assert "[ERROR] Error occurred" in captured.err


class TestEventParser:
    """Test the EventParser class."""
    
    def test_parse_stdin_valid_json(self):
        """Test parsing valid JSON from stdin."""
        test_event = {'tool': 'Read', 'input': {'file_path': 'test.py'}}
        
        with patch('sys.stdin.read', return_value=json.dumps(test_event)):
            event, error = EventParser.parse_stdin()
        
        assert event == test_event
        assert error is None
    
    def test_parse_stdin_invalid_json(self):
        """Test parsing invalid JSON from stdin."""
        with patch('sys.stdin.read', return_value='{ invalid json'):
            event, error = EventParser.parse_stdin()
        
        assert event is None
        assert 'Invalid JSON' in error
    
    def test_parse_stdin_read_error(self):
        """Test handling stdin read errors."""
        with patch('sys.stdin.read', side_effect=IOError("Read failed")):
            event, error = EventParser.parse_stdin()
        
        assert event is None
        assert 'Error reading event' in error
    
    def test_get_tool_info(self):
        """Test extracting tool info from event."""
        event = {
            'tool': 'Write',
            'input': {'file_path': 'new.py', 'content': 'print()'}
        }
        
        tool, tool_input = EventParser.get_tool_info(event)
        assert tool == 'Write'
        assert tool_input == {'file_path': 'new.py', 'content': 'print()'}
    
    def test_get_tool_info_missing_fields(self):
        """Test extracting tool info with missing fields."""
        event = {}
        
        tool, tool_input = EventParser.get_tool_info(event)
        assert tool == ''
        assert tool_input == {}


class TestResponseBuilder:
    """Test the ResponseBuilder class."""
    
    def test_allow_response(self):
        """Test building an allow response."""
        response = ResponseBuilder.allow()
        data = json.loads(response)
        
        assert data['decision'] == 'allow'
        assert 'message' not in data
    
    def test_allow_response_with_message(self):
        """Test building an allow response with message."""
        response = ResponseBuilder.allow("Operation permitted")
        data = json.loads(response)
        
        assert data['decision'] == 'allow'
        assert data['message'] == 'Operation permitted'
    
    def test_deny_response(self):
        """Test building a deny response."""
        response = ResponseBuilder.deny("Not allowed in this step")
        data = json.loads(response)
        
        assert data['decision'] == 'block'
        assert data['reason'] == 'Not allowed in this step'
        assert 'suggestions' not in data
    
    def test_deny_response_with_suggestions(self):
        """Test building a deny response with suggestions."""
        suggestions = ["Try using Read instead", "Complete planning first"]
        response = ResponseBuilder.deny("Write not allowed", suggestions)
        data = json.loads(response)
        
        assert data['decision'] == 'block'
        assert data['reason'] == 'Write not allowed'
        assert data['suggestions'] == suggestions
    
    def test_error_response(self):
        """Test building an error response."""
        response = ResponseBuilder.error("Something went wrong")
        data = json.loads(response)
        
        assert data['decision'] == 'allow'  # Errors still allow operation
        assert data['message'] == 'Something went wrong'


class TestUtilityFunctions:
    """Test standalone utility functions."""
    
    def test_format_time_delta_seconds(self):
        """Test formatting seconds."""
        assert format_time_delta(45) == "45s"
        assert format_time_delta(59) == "59s"
    
    def test_format_time_delta_minutes(self):
        """Test formatting minutes."""
        assert format_time_delta(60) == "1m"
        assert format_time_delta(150) == "2m"
        assert format_time_delta(599) == "9m"
    
    def test_format_time_delta_hours(self):
        """Test formatting hours and minutes."""
        assert format_time_delta(3600) == "1h"
        assert format_time_delta(3660) == "1h 1m"
        assert format_time_delta(7320) == "2h 2m"
        assert format_time_delta(7200) == "2h"  # No minutes
    
    def test_safe_state_update_success(self):
        """Test successful state update."""
        mock_state_manager = MagicMock()
        updates = {'workflow_step': 'implementation'}
        
        result = safe_state_update(mock_state_manager, updates)
        
        assert result == True
        mock_state_manager.update.assert_called_once_with(updates)
    
    def test_safe_state_update_failure(self, capsys):
        """Test failed state update with error logging."""
        mock_state_manager = MagicMock()
        mock_state_manager.update.side_effect = Exception("Update failed")
        updates = {'workflow_step': 'implementation'}
        
        result = safe_state_update(mock_state_manager, updates)
        
        assert result == False
        captured = capsys.readouterr()
        assert "Failed to update state: Update failed" in captured.err


if __name__ == '__main__':
    pytest.main([__file__, '-v'])