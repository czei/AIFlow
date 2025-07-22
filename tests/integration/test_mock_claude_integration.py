#!/usr/bin/env python3
"""
Integration tests using MockClaudeProvider.
Tests the interaction between system components and (mock) AI.
"""

import unittest
import json
import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

# Add parent directories to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mocks.mock_claude_provider import MockClaudeProvider, MockClaudeProviderWithState
from logged_secure_shell import LoggedSecureShell, BasicLogger


class TestMockClaudeProviderBasic(unittest.TestCase):
    """Test basic MockClaudeProvider functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.provider = MockClaudeProvider()
        
    def test_deterministic_project_setup(self):
        """Test deterministic responses for project setup"""
        response = self.provider.query("Please setup a new project called myapp")
        
        self.assertEqual(response["type"], "project_setup")
        self.assertIn("commands", response)
        self.assertTrue(any("mkdir" in cmd for cmd in response["commands"]))
        self.assertIn("explanation", response)
        
    def test_deterministic_code_implementation(self):
        """Test deterministic responses for code implementation"""
        response = self.provider.query("Implement a function calculate_total")
        
        self.assertEqual(response["type"], "code_implementation")
        self.assertIn("code", response)
        self.assertIn("def calculate_total", response["code"])
        self.assertIn("test_code", response)
        self.assertIn("test_calculate_total", response["test_code"])
        
    def test_deterministic_code_review(self):
        """Test deterministic responses for code review"""
        response = self.provider.query("Please review this code for quality")
        
        self.assertEqual(response["type"], "code_review")
        self.assertIn("issues", response)
        self.assertEqual(len(response["issues"]), 3)
        self.assertIn("summary", response)
        self.assertIn("recommendation", response)
        
    def test_deterministic_error_analysis(self):
        """Test deterministic responses for error analysis"""
        response = self.provider.query("Debug this error: TypeError in line 42")
        
        self.assertEqual(response["type"], "error_analysis")
        self.assertIn("diagnosis", response)
        self.assertIn("fix", response)
        self.assertIn("code_fix", response)
        
    def test_call_history_tracking(self):
        """Test that call history is properly tracked"""
        self.provider.query("First query")
        self.provider.query("Second query", context={"key": "value"})
        
        history = self.provider.get_call_history()
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["prompt"], "First query")
        self.assertEqual(history[1]["context"], {"key": "value"})
        
    def test_failure_mode(self):
        """Test failure response mode"""
        self.provider.set_response_mode("failure")
        response = self.provider.query("Any query")
        
        self.assertEqual(response["type"], "error")
        self.assertIn("error", response)
        self.assertIn("retry_after", response)
        
    def test_random_mode(self):
        """Test random response mode"""
        self.provider.set_response_mode("random")
        response = self.provider.query("Random query")
        
        self.assertIn("type", response)
        self.assertIn(response["type"], ["code", "explanation", "command", "analysis"])
        
    def test_clear_history(self):
        """Test clearing call history"""
        self.provider.query("Test query")
        self.assertEqual(len(self.provider.get_call_history()), 1)
        
        self.provider.clear_history()
        self.assertEqual(len(self.provider.get_call_history()), 0)
        
    def test_inject_custom_response(self):
        """Test injecting custom responses"""
        custom_response = {
            "type": "custom",
            "data": "Custom test response"
        }
        self.provider.inject_response("custom_pattern", custom_response)
        
        # Note: This is a simplified test - full implementation would need
        # to check patterns in _generate_deterministic_response
        self.assertTrue(hasattr(self.provider, "custom_responses"))
        self.assertIn("custom_pattern", self.provider.custom_responses)


class TestMockClaudeProviderWithState(unittest.TestCase):
    """Test stateful MockClaudeProvider"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.provider = MockClaudeProviderWithState()
        
    def test_initial_state(self):
        """Test initial state values"""
        state = self.provider.get_state()
        
        self.assertEqual(state["project_phase"], "planning")
        self.assertEqual(state["completed_tasks"], [])
        self.assertEqual(state["current_context"], {})
        self.assertEqual(state["error_count"], 0)
        
    def test_phase_transition_tracking(self):
        """Test that phase transitions are tracked"""
        self.provider.query("Let's implement the user authentication")
        state = self.provider.get_state()
        self.assertEqual(state["project_phase"], "implementation")
        
        self.provider.query("Run the test suite")
        state = self.provider.get_state()
        self.assertEqual(state["project_phase"], "testing")
        
    def test_error_count_tracking(self):
        """Test error counting"""
        self.provider.query("Fix the error in line 10")
        self.provider.query("Debug the connection error")
        
        state = self.provider.get_state()
        self.assertEqual(state["error_count"], 2)
        
    def test_completed_tasks_tracking(self):
        """Test tracking of completed tasks"""
        self.provider.query("Task completed", context={"task": "setup"})
        self.provider.query("Implementation done", context={"task": "auth"})
        
        state = self.provider.get_state()
        self.assertIn("setup", state["completed_tasks"])
        self.assertIn("auth", state["completed_tasks"])
        
    def test_context_accumulation(self):
        """Test that context accumulates across calls"""
        self.provider.query("Query 1", context={"key1": "value1"})
        self.provider.query("Query 2", context={"key2": "value2"})
        
        state = self.provider.get_state()
        self.assertEqual(state["current_context"]["key1"], "value1")
        self.assertEqual(state["current_context"]["key2"], "value2")
        
    def test_reset_state(self):
        """Test state reset functionality"""
        self.provider.query("Implement feature", context={"feature": "login"})
        self.provider.query("Error occurred")
        
        self.provider.reset_state()
        state = self.provider.get_state()
        
        self.assertEqual(state["project_phase"], "planning")
        self.assertEqual(state["completed_tasks"], [])
        self.assertEqual(state["error_count"], 0)
        
    def test_state_included_in_response(self):
        """Test that state is included in responses"""
        self.provider.query("Implement the database layer")
        response = self.provider.query("Check current status")
        
        self.assertIn("state", response)
        self.assertEqual(response["state"]["project_phase"], "implementation")


class TestMockClaudeWithLoggedShell(unittest.TestCase):
    """Integration tests with LoggedSecureShell"""
    
    @patch('logged_secure_shell.Path.mkdir')
    @patch('builtins.open', new_callable=mock_open)
    def setUp(self, mock_file, mock_mkdir):
        """Set up test fixtures"""
        self.provider = MockClaudeProvider()
        self.shell = LoggedSecureShell("/test/project")
        # Access the logger created by LoggedSecureShell
        self.logger = self.shell.logger
        
    def test_ai_guided_command_validation(self):
        """Test command validation with AI guidance"""
        # Simulate AI suggesting a command
        ai_response = self.provider.query("What command should I run to list files?")
        
        # In a real integration, the AI response would influence command validation
        # For now, we test the flow
        self.shell.current_phase = "implementation"
        is_valid = self.shell.validate_command_phase("ls -la", "implementation")
        
        self.assertTrue(is_valid)
        # Verify AI was consulted
        self.assertEqual(len(self.provider.get_call_history()), 1)
        
    def test_ai_error_recovery_flow(self):
        """Test error recovery flow with AI assistance"""
        # Simulate an error scenario
        error_context = {
            "error_type": "FileNotFoundError",
            "error_message": "No such file: config.json",
            "phase": "implementation"
        }
        
        # Ask AI for help
        response = self.provider.query(
            "How to fix FileNotFoundError for config.json?",
            context=error_context
        )
        
        self.assertEqual(response["type"], "error_analysis")
        self.assertIn("fix", response)
        
        # Verify we can track this in shell's error handling
        # In real integration, shell would use AI response to recover
        
    @patch('logged_secure_shell.subprocess.run')
    def test_ai_guided_workflow(self, mock_run):
        """Test complete workflow with AI guidance"""
        # Phase 1: Planning
        self.shell.current_phase = "planning"
        plan_response = self.provider.query("Create a plan for building a calculator")
        
        # Phase 2: Implementation based on AI plan
        self.shell.current_phase = "implementation"
        impl_response = self.provider.query("Implement the calculator based on the plan")
        
        # Simulate executing AI-suggested commands
        if "commands" in impl_response:
            for cmd in impl_response.get("commands", []):
                # In real integration, these would be validated and executed
                is_valid = self.shell.validate_command_phase(cmd, "implementation")
                self.assertTrue(is_valid)
        
        # Verify AI interaction history
        history = self.provider.get_call_history()
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["prompt"], "Create a plan for building a calculator")


class TestMockProviderEdgeCases(unittest.TestCase):
    """Test edge cases and error scenarios"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.provider = MockClaudeProvider()
        
    def test_empty_prompt(self):
        """Test handling of empty prompt"""
        response = self.provider.query("")
        self.assertIn("type", response)
        self.assertEqual(response["type"], "general")
        
    def test_very_long_prompt(self):
        """Test handling of very long prompt"""
        long_prompt = "x" * 10000
        response = self.provider.query(long_prompt)
        self.assertIn("type", response)
        
    def test_special_characters_in_prompt(self):
        """Test handling of special characters"""
        response = self.provider.query("Implement function $%^&*()")
        self.assertIn("type", response)
        
    def test_unicode_in_prompt(self):
        """Test handling of unicode characters"""
        response = self.provider.query("Implement 函数 with émojis 🚀")
        self.assertIn("type", response)
        
    def test_invalid_response_mode(self):
        """Test setting invalid response mode"""
        with self.assertRaises(ValueError):
            self.provider.set_response_mode("invalid_mode")
            
    def test_concurrent_queries(self):
        """Test handling of multiple queries"""
        # In a real scenario, this would test thread safety
        responses = []
        for i in range(10):
            response = self.provider.query(f"Query {i}")
            responses.append(response)
            
        self.assertEqual(len(responses), 10)
        self.assertEqual(len(self.provider.get_call_history()), 10)


if __name__ == '__main__':
    unittest.main()