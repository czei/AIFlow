#!/usr/bin/env python3
"""
Unit tests for BasicLogger class.
Tests deterministic logging functionality without I/O operations.
"""

import unittest
from unittest.mock import patch, mock_open, MagicMock
import json
from pathlib import Path
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from scripts.logged_secure_shell import BasicLogger


class TestBasicLogger(unittest.TestCase):
    """Test deterministic functionality of BasicLogger"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_correlation_id = "test-uuid-1234"
        self.test_project_dir = "/test/project"
        
    @patch('scripts.logged_secure_shell.Path.mkdir')
    @patch('scripts.logged_secure_shell.uuid.uuid4')
    @patch('builtins.open', new_callable=mock_open)
    def test_logger_initialization(self, mock_file, mock_uuid, mock_mkdir):
        """Test logger initializes with correct attributes"""
        mock_uuid.return_value = self.test_correlation_id
        
        logger = BasicLogger(self.test_project_dir, correlation_id="custom-id")
        
        # Verify attributes
        self.assertEqual(str(logger.project_dir), self.test_project_dir)
        self.assertEqual(str(logger.logs_dir), "/test/project/.logs")
        self.assertEqual(logger.correlation_id, "custom-id")
        
        # Verify log files dictionary
        expected_files = [
            'automation', 'workflow', 'commands', 'quality-gates',
            'phase-transitions', 'errors', 'performance'
        ]
        self.assertEqual(set(logger.log_files.keys()), set(expected_files))
        
        # Verify mkdir was called
        mock_mkdir.assert_called_once_with(exist_ok=True)
        
    @patch('scripts.logged_secure_shell.uuid.uuid4')
    @patch('builtins.open', new_callable=mock_open)
    @patch('scripts.logged_secure_shell.Path.mkdir')
    def test_logger_auto_correlation_id(self, mock_mkdir, mock_file, mock_uuid):
        """Test logger generates correlation ID when not provided"""
        mock_uuid.return_value = self.test_correlation_id
        
        logger = BasicLogger(self.test_project_dir)
        
        self.assertEqual(logger.correlation_id, str(self.test_correlation_id))
        mock_uuid.assert_called_once()
        
    @patch('builtins.open', new_callable=mock_open)
    @patch('scripts.logged_secure_shell.datetime')
    @patch('scripts.logged_secure_shell.Path.mkdir')
    def test_log_event_structure(self, mock_mkdir, mock_datetime, mock_file):
        """Test log event creates proper JSON structure"""
        # Mock datetime to return consistent value
        mock_datetime.now.return_value.isoformat.return_value = "2025-01-01T00:00:00Z"
        
        # Mock project state file
        mock_file.return_value.read.return_value = json.dumps({
            "current_phase": "implementation",
            "workflow_step": "coding",
            "current_objective": "test-objective"
        })
        
        logger = BasicLogger(self.test_project_dir, self.test_correlation_id)
        
        # Clear initialization writes
        mock_file.reset_mock()
        
        # Log an event
        logger.log_event(
            'automation', 
            'INFO', 
            'test_event',
            {'key': 'value'},
            custom_field='custom_value'
        )
        
        # Get the written content
        write_calls = mock_file.return_value.write.call_args_list
        self.assertEqual(len(write_calls), 1)
        
        written_data = write_calls[0][0][0]
        log_entry = json.loads(written_data.strip())
        
        # Verify log structure
        expected_fields = {
            'timestamp': '2025-01-01T00:00:00Z',
            'level': 'INFO',
            'category': 'automation',
            'correlation_id': self.test_correlation_id,
            'phase': 'implementation',
            'workflow_step': 'coding',
            'objective': 'test-objective',
            'event': 'test_event',
            'details': {'key': 'value'},
            'custom_field': 'custom_value'
        }
        
        self.assertEqual(log_entry, expected_fields)
        
    @patch('builtins.open', new_callable=mock_open)
    @patch('scripts.logged_secure_shell.Path.mkdir')
    @patch('builtins.print')
    def test_log_event_console_output(self, mock_print, mock_mkdir, mock_file):
        """Test log event prints to console"""
        # Mock missing state file
        mock_file.side_effect = [
            FileNotFoundError(),  # State file not found
            mock_open()()  # Log file write
        ]
        
        logger = BasicLogger(self.test_project_dir, self.test_correlation_id)
        
        # Reset mocks after initialization
        mock_print.reset_mock()
        mock_file.side_effect = [
            FileNotFoundError(),  # State file not found
            mock_open()()  # Log file write
        ]
        
        logger.log_event('errors', 'ERROR', 'test_error', {'msg': 'error details'})
        
        # Verify console output
        mock_print.assert_called_once()
        console_msg = mock_print.call_args[0][0]
        self.assertIn('[ERROR] errors: test_error', console_msg)
        self.assertIn('"msg":"error details"', console_msg)
        
    @patch('builtins.open', new_callable=mock_open)
    @patch('scripts.logged_secure_shell.Path.mkdir')
    def test_log_event_missing_state_file(self, mock_mkdir, mock_file):
        """Test log event handles missing state file gracefully"""
        # Create a mock file handle for writing
        mock_write_handle = mock_open()()
        
        # Configure mock to raise FileNotFoundError for state file, then return write handle
        def side_effect(filename, *args, **kwargs):
            if '.project-state.json' in str(filename):
                raise FileNotFoundError()
            return mock_write_handle
        
        mock_file.side_effect = side_effect
        
        logger = BasicLogger(self.test_project_dir, self.test_correlation_id)
        
        # Log an event
        logger.log_event('automation', 'INFO', 'test_event')
        
        # Get written log entries (skip the initialization log)
        write_calls = mock_write_handle.write.call_args_list
        # Find the test_event log (not the initialization log)
        test_event_data = None
        for call in write_calls:
            data = call[0][0]
            if 'test_event' in data:
                test_event_data = data
                break
        
        self.assertIsNotNone(test_event_data)
        log_entry = json.loads(test_event_data.strip())
        
        # Verify defaults are used
        self.assertEqual(log_entry['phase'], 'unknown')
        self.assertEqual(log_entry['workflow_step'], 'unknown')
        self.assertEqual(log_entry['objective'], 'unknown')
        
    @patch('builtins.open', new_callable=mock_open)
    @patch('scripts.logged_secure_shell.Path.mkdir')
    def test_log_event_invalid_json_state(self, mock_mkdir, mock_file):
        """Test log event handles invalid JSON in state file"""
        # Configure mock to return invalid JSON
        mock_file.return_value.read.return_value = "invalid json {"
        
        logger = BasicLogger(self.test_project_dir, self.test_correlation_id)
        
        # Reset mock for log_event
        mock_file.reset_mock()
        mock_file.return_value.read.return_value = "invalid json {"
        
        logger.log_event('automation', 'INFO', 'test_event')
        
        # Verify it still logs with defaults
        write_calls = mock_file.return_value.write.call_args_list
        written_data = write_calls[0][0][0]
        log_entry = json.loads(written_data.strip())
        
        self.assertEqual(log_entry['phase'], 'unknown')
        self.assertEqual(log_entry['workflow_step'], 'unknown')
        
    @patch('builtins.open', new_callable=mock_open)
    @patch('scripts.logged_secure_shell.Path.mkdir')
    def test_log_file_selection(self, mock_mkdir, mock_file):
        """Test correct log file is selected based on category"""
        logger = BasicLogger(self.test_project_dir, self.test_correlation_id)
        
        # Test different categories
        categories = ['automation', 'workflow', 'commands', 'errors', 'performance']
        
        for category in categories:
            mock_file.reset_mock()
            mock_file.side_effect = [FileNotFoundError(), mock_open()()]
            
            logger.log_event(category, 'INFO', 'test_event')
            
            # Verify correct file path was used
            expected_path = Path(self.test_project_dir) / '.logs' / f'{category}.log'
            mock_file.assert_any_call(expected_path, 'a', encoding='utf-8')
            
    @patch('builtins.open', new_callable=mock_open)
    @patch('scripts.logged_secure_shell.Path.mkdir')
    def test_log_event_unknown_category(self, mock_mkdir, mock_file):
        """Test unknown category defaults to automation log"""
        logger = BasicLogger(self.test_project_dir, self.test_correlation_id)
        
        mock_file.reset_mock()
        mock_file.side_effect = [FileNotFoundError(), mock_open()()]
        
        logger.log_event('unknown_category', 'INFO', 'test_event')
        
        # Verify it uses automation.log
        expected_path = Path(self.test_project_dir) / '.logs' / 'automation.log'
        mock_file.assert_any_call(expected_path, 'a', encoding='utf-8')


if __name__ == '__main__':
    unittest.main()