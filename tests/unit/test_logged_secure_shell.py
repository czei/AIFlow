#!/usr/bin/env python3
"""
Unit tests for LoggedSecureShell class.
Tests deterministic command validation and sprint management without I/O.
"""

import unittest
from unittest.mock import patch, MagicMock, mock_open
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from scripts.logged_secure_shell import LoggedSecureShell


class TestLoggedSecureShell(unittest.TestCase):
    """Test deterministic functionality of LoggedSecureShell"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_workdir = "/test/project"
        
    @patch('scripts.logged_secure_shell.BasicLogger')
    @patch('scripts.logged_secure_shell.os.getpid')
    @patch('scripts.logged_secure_shell.sys.argv', ['script.py', 'test', 'command'])
    def test_shell_initialization(self, mock_getpid, mock_logger):
        """Test shell initializes with correct attributes"""
        mock_getpid.return_value = 12345
        
        shell = LoggedSecureShell(self.test_workdir)
        
        # Verify attributes
        self.assertEqual(shell.workdir, self.test_workdir)
        self.assertEqual(str(shell.state_file), "/test/project/.project-state.json")
        
        # Verify logger was initialized
        mock_logger.assert_called_once_with(self.test_workdir)
        
        # Verify initialization was logged
        shell.logger.log_event.assert_called_once_with(
            'automation', 'INFO', 'secure_shell_initialized',
            {
                'workdir': self.test_workdir,
                'pid': 12345,
                'command_args': ['script.py', 'test', 'command']
            }
        )
        
    @patch('scripts.logged_secure_shell.BasicLogger')
    def test_validate_command_sprint_planning(self, mock_logger):
        """Test command validation for planning sprint"""
        shell = LoggedSecureShell(self.test_workdir)
        
        # Test allowed commands
        allowed_commands = ["cat", "ls", "find", "grep", "git", "head", "tail", "wc", "sort"]
        for cmd in allowed_commands:
            result = shell.validate_command_sprint(cmd, [], "planning")
            self.assertTrue(result, f"{cmd} should be allowed in planning sprint")
            
        # Test disallowed commands
        disallowed_commands = ["python", "npm", "make", "rm", "touch"]
        for cmd in disallowed_commands:
            result = shell.validate_command_sprint(cmd, [], "planning")
            self.assertFalse(result, f"{cmd} should not be allowed in planning sprint")
            
    @patch('scripts.logged_secure_shell.BasicLogger')
    def test_validate_command_sprint_implementation(self, mock_logger):
        """Test command validation for implementation sprint"""
        shell = LoggedSecureShell(self.test_workdir)
        
        # Test allowed commands
        allowed_commands = ["python", "python3", "npm", "node", "pip", "make", "touch", "mkdir"]
        for cmd in allowed_commands:
            result = shell.validate_command_sprint(cmd, [], "implementation")
            self.assertTrue(result, f"{cmd} should be allowed in implementation sprint")
            
        # Test that planning commands are also allowed
        result = shell.validate_command_sprint("cat", [], "implementation")
        self.assertTrue(result, "cat should be allowed in implementation sprint")
        
    @patch('scripts.logged_secure_shell.BasicLogger')
    def test_validate_command_sprint_validation(self, mock_logger):
        """Test command validation for validation sprint"""
        shell = LoggedSecureShell(self.test_workdir)
        
        # Test allowed commands
        allowed_commands = ["pytest", "npm", "jest", "test", "coverage"]
        for cmd in allowed_commands:
            result = shell.validate_command_sprint(cmd, [], "validation")
            self.assertTrue(result, f"{cmd} should be allowed in validation sprint")
            
    @patch('scripts.logged_secure_shell.BasicLogger')
    def test_validate_command_sprint_review(self, mock_logger):
        """Test command validation for review sprint"""
        shell = LoggedSecureShell(self.test_workdir)
        
        # Test allowed commands
        allowed_commands = ["git", "diff", "grep", "cat", "ls"]
        for cmd in allowed_commands:
            result = shell.validate_command_sprint(cmd, [], "review")
            self.assertTrue(result, f"{cmd} should be allowed in review sprint")
            
        # Test disallowed commands
        result = shell.validate_command_sprint("npm", [], "review")
        self.assertFalse(result, "npm should not be allowed in review sprint")
        
    @patch('scripts.logged_secure_shell.BasicLogger')
    def test_validate_command_sprint_unknown(self, mock_logger):
        """Test command validation for unknown sprint"""
        shell = LoggedSecureShell(self.test_workdir)
        
        # Unknown sprint should not allow any commands
        result = shell.validate_command_sprint("ls", [], "unknown_sprint")
        self.assertFalse(result, "Commands should not be allowed in unknown sprint")
        
    @patch('scripts.logged_secure_shell.BasicLogger')
    @patch('builtins.open', new_callable=mock_open)
    def test_load_project_state_success(self, mock_file, mock_logger):
        """Test successful project state loading"""
        mock_state = {
            "current_sprint": "implementation",
            "workflow_step": "coding",
            "automation_active": True
        }
        mock_file.return_value.read.return_value = json.dumps(mock_state)
        
        shell = LoggedSecureShell(self.test_workdir)
        state = shell.load_project_state()
        
        self.assertEqual(state, mock_state)
        shell.logger.log_event.assert_any_call(
            'automation', 'DEBUG', 'project_state_loaded',
            {
                'state_file': str(shell.state_file),
                'current_sprint': 'implementation',
                'workflow_step': 'coding',
                'automation_active': True
            }
        )
        
    @patch('scripts.logged_secure_shell.BasicLogger')
    @patch('builtins.open', side_effect=FileNotFoundError)
    def test_load_project_state_file_not_found(self, mock_file, mock_logger):
        """Test project state loading when file not found"""
        shell = LoggedSecureShell(self.test_workdir)
        state = shell.load_project_state()
        
        # Should return default state
        self.assertEqual(state, {"workflow_step": "planning"})
        
        # Should log warning
        shell.logger.log_event.assert_any_call(
            'errors', 'WARNING', 'state_file_not_found',
            {
                'state_file': str(shell.state_file),
                'recovery_action': 'defaulting_to_planning'
            }
        )
        
    @patch('scripts.logged_secure_shell.BasicLogger')
    @patch('builtins.open', new_callable=mock_open)
    def test_load_project_state_invalid_json(self, mock_file, mock_logger):
        """Test project state loading with invalid JSON"""
        mock_file.return_value.read.return_value = "invalid json {"
        
        shell = LoggedSecureShell(self.test_workdir)
        state = shell.load_project_state()
        
        # Should return default state
        self.assertEqual(state, {"workflow_step": "planning"})
        
        # Should log error
        log_calls = shell.logger.log_event.call_args_list
        error_call = [call for call in log_calls if call[0][1] == 'ERROR'][0]
        self.assertEqual(error_call[0][0], 'errors')
        self.assertEqual(error_call[0][2], 'invalid_state_file')
        
    @patch('scripts.logged_secure_shell.BasicLogger')
    @patch('scripts.logged_secure_shell.time.time')
    def test_validate_command_sprint_performance_tracking(self, mock_time, mock_logger):
        """Test that command validation tracks performance"""
        mock_time.side_effect = [0.0, 0.1]  # 100ms duration
        
        shell = LoggedSecureShell(self.test_workdir)
        shell.validate_command_sprint("ls", ["file1", "file2"], "planning")
        
        # Find the validation log call
        log_calls = shell.logger.log_event.call_args_list
        validation_call = [call for call in log_calls if call[0][2] == 'command_sprint_validation'][0]
        
        # Verify performance metrics
        details = validation_call[0][3]
        self.assertEqual(details['duration_ms'], 100.0)
        self.assertEqual(details['args_count'], 2)
        self.assertIn('args_preview', details)
        
    @patch('scripts.logged_secure_shell.BasicLogger')
    def test_validate_command_sprint_args_preview(self, mock_logger):
        """Test args preview in validation logging"""
        shell = LoggedSecureShell(self.test_workdir)
        
        # Test with many args
        many_args = ['arg1', 'arg2', 'arg3', 'arg4', 'arg5']
        shell.validate_command_sprint("ls", many_args, "planning")
        
        # Get validation log call
        log_calls = shell.logger.log_event.call_args_list
        validation_call = [call for call in log_calls if call[0][2] == 'command_sprint_validation'][0]
        
        # Verify args preview is truncated
        details = validation_call[0][3]
        self.assertEqual(details['args_preview'], ['arg1', 'arg2', 'arg3', '...'])
        self.assertEqual(details['args_count'], 5)
        
    @patch('scripts.logged_secure_shell.BasicLogger')
    def test_validate_command_sprint_validation_result(self, mock_logger):
        """Test validation result logging"""
        shell = LoggedSecureShell(self.test_workdir)
        
        # Test allowed command
        shell.validate_command_sprint("ls", [], "planning")
        log_calls = shell.logger.log_event.call_args_list
        validation_call = [call for call in log_calls if call[0][2] == 'command_sprint_validation'][-1]
        self.assertEqual(validation_call[0][3]['validation_result'], 'ALLOWED')
        
        # Test denied command
        shell.validate_command_sprint("rm", [], "planning")
        log_calls = shell.logger.log_event.call_args_list
        validation_call = [call for call in log_calls if call[0][2] == 'command_sprint_validation'][-1]
        self.assertEqual(validation_call[0][3]['validation_result'], 'DENIED')


class TestLoggedSecureShellCommandParsing(unittest.TestCase):
    """Test command parsing and validation logic"""
    
    @patch('scripts.logged_secure_shell.BasicLogger')
    @patch('scripts.logged_secure_shell.sys.argv', ['script.py'])
    def test_main_no_command(self, mock_logger):
        """Test main with no command provided"""
        shell = LoggedSecureShell("/test")
        exit_code = shell.main()
        
        self.assertEqual(exit_code, 1)
        shell.logger.log_event.assert_any_call(
            'errors', 'ERROR', 'invalid_usage',
            {
                'message': 'No command provided',
                'usage': 'logged_secure_shell <command>',
                'args_received': ['script.py']
            }
        )
        
    @patch('scripts.logged_secure_shell.BasicLogger')
    @patch('scripts.logged_secure_shell.sys.argv', ['script.py', 'echo "unbalanced quote'])
    def test_main_invalid_command_string(self, mock_logger):
        """Test main with invalid command string"""
        shell = LoggedSecureShell("/test")
        exit_code = shell.main()
        
        self.assertEqual(exit_code, 1)
        # Verify error was logged
        error_calls = [call for call in shell.logger.log_event.call_args_list 
                      if call[0][2] == 'command_parse_error']
        self.assertEqual(len(error_calls), 1)
        
    @patch('scripts.logged_secure_shell.BasicLogger')
    @patch('scripts.logged_secure_shell.sys.argv', ['script.py', ''])
    def test_main_empty_command(self, mock_logger):
        """Test main with empty command string"""
        shell = LoggedSecureShell("/test")
        exit_code = shell.main()
        
        self.assertEqual(exit_code, 1)
        shell.logger.log_event.assert_any_call(
            'errors', 'ERROR', 'empty_command',
            {'command_string': ''}
        )


if __name__ == '__main__':
    unittest.main()