#!/usr/bin/env python3
"""
Integration test for AI-driven workflow.
Tests complete workflow with MockClaudeProvider.
"""

import unittest
import json
import tempfile
import shutil
from pathlib import Path
import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mocks.mock_claude_provider import MockClaudeProviderWithState


class TestAIWorkflowIntegration(unittest.TestCase):
    """Test complete AI-driven development workflow"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.provider = MockClaudeProviderWithState()
        self.temp_dir = tempfile.mkdtemp()
        self.project_dir = Path(self.temp_dir) / "test_project"
        
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)
        
    def test_complete_development_workflow(self):
        """Test complete workflow from setup to implementation"""
        # Phase 1: Project Setup
        setup_response = self.provider.query(
            "Setup a new project called calculator",
            context={"project_name": "calculator"}
        )
        
        self.assertEqual(setup_response["type"], "project_setup")
        self.assertIn("commands", setup_response)
        
        # Verify state tracking
        state = self.provider.get_state()
        self.assertEqual(state["project_phase"], "planning")
        
        # Phase 2: Implementation
        impl_response = self.provider.query(
            "Implement a function add_numbers that adds two numbers"
        )
        
        self.assertEqual(impl_response["type"], "code_implementation")
        self.assertIn("code", impl_response)
        self.assertIn("def add_numbers", impl_response["code"])
        
        # Verify phase transition
        state = self.provider.get_state()
        self.assertEqual(state["project_phase"], "implementation")
        
        # Phase 3: Testing
        test_response = self.provider.query(
            "Create tests for the add_numbers function"
        )
        
        # Phase 4: Code Review
        review_response = self.provider.query(
            "Review the add_numbers implementation for quality"
        )
        
        self.assertEqual(review_response["type"], "code_review")
        self.assertIn("issues", review_response)
        
        # Phase 5: Error Handling
        error_response = self.provider.query(
            "Debug error: TypeError when adding string and number"
        )
        
        self.assertEqual(error_response["type"], "error_analysis")
        self.assertIn("fix", error_response)
        
        # Verify complete workflow tracking
        history = self.provider.get_call_history()
        self.assertEqual(len(history), 5)
        
        final_state = self.provider.get_state()
        self.assertEqual(final_state["error_count"], 1)
        
    def test_iterative_development_with_feedback(self):
        """Test iterative development with AI feedback loop"""
        # Initial implementation
        response1 = self.provider.query(
            "Implement a basic calculator class"
        )
        
        # Feedback and improvement
        response2 = self.provider.query(
            "The calculator needs error handling, please add it",
            context={"previous_code": response1.get("code", "")}
        )
        
        # Verify context accumulation
        state = self.provider.get_state()
        self.assertIn("previous_code", state["current_context"])
        
        # Another iteration
        response3 = self.provider.query(
            "Add support for division by zero handling"
        )
        
        # Verify we're tracking iterations
        history = self.provider.get_call_history()
        self.assertEqual(len(history), 3)
        
    def test_multi_phase_state_persistence(self):
        """Test that state persists across multiple phases"""
        # Planning phase
        self.provider.query("Plan the architecture for a web API")
        initial_state = self.provider.get_state()
        
        # Implementation phase
        self.provider.query("Implement the user authentication endpoint")
        self.provider.query("Task completed", context={"task": "auth_endpoint"})
        
        # Testing phase  
        self.provider.query("Write tests for the authentication")
        self.provider.query("Task completed", context={"task": "auth_tests"})
        
        # Deployment phase
        self.provider.query("Deploy the API to production")
        
        # Verify accumulated state
        final_state = self.provider.get_state()
        self.assertEqual(final_state["project_phase"], "deployment")
        self.assertIn("auth_endpoint", final_state["completed_tasks"])
        self.assertIn("auth_tests", final_state["completed_tasks"])
        
    def test_error_recovery_workflow(self):
        """Test AI-assisted error recovery workflow"""
        # Simulate multiple errors
        errors = [
            "FileNotFoundError: config.json not found",
            "ImportError: cannot import module 'requests'",
            "SyntaxError: invalid syntax on line 42"
        ]
        
        for error in errors:
            response = self.provider.query(f"Help fix this error: {error}")
            self.assertEqual(response["type"], "error_analysis")
            self.assertIn("fix", response)
            
        # Verify error tracking
        state = self.provider.get_state()
        self.assertEqual(state["error_count"], 3)
        
    def test_ai_guided_refactoring(self):
        """Test AI-guided code refactoring workflow"""
        # Initial messy code
        response1 = self.provider.query(
            "Here's my code, can you help refactor it?",
            context={"code": "def calc(x,y): return x+y"}
        )
        
        # Request specific improvements
        response2 = self.provider.query(
            "Add type hints and docstring to the refactored code"
        )
        
        # Verify context is maintained
        state = self.provider.get_state()
        self.assertIn("code", state["current_context"])
        
    def test_workflow_with_failures(self):
        """Test workflow behavior with simulated failures"""
        # Set failure mode
        self.provider.set_response_mode("failure")
        
        response = self.provider.query("Setup new project")
        self.assertEqual(response["type"], "error")
        self.assertIn("retry_after", response)
        
        # Switch back to normal mode
        self.provider.set_response_mode("deterministic")
        
        # Retry the operation
        retry_response = self.provider.query("Setup new project")
        self.assertEqual(retry_response["type"], "project_setup")
        
        # Verify we can continue after failure
        history = self.provider.get_call_history()
        self.assertEqual(len(history), 2)
        
    def test_complex_multi_step_workflow(self):
        """Test complex workflow with multiple interdependent steps"""
        workflow_steps = [
            ("Setup project structure", "project_setup"),
            ("Create database schema", "code_implementation"),
            ("Implement API endpoints", "code_implementation"),
            ("Write unit tests", "code_implementation"),
            ("Perform code review", "code_review"),
            ("Fix review issues", "code_implementation"),
            ("Run integration tests", "general"),
            ("Deploy to staging", "general")
        ]
        
        for step_description, expected_type in workflow_steps:
            response = self.provider.query(step_description)
            # Some steps might return different types based on keywords
            self.assertIn("type", response)
            
            # Mark step as completed
            if "implement" in step_description.lower():
                self.provider.query(
                    "Step completed",
                    context={"task": step_description}
                )
        
        # Verify workflow completion
        final_state = self.provider.get_state()
        self.assertTrue(len(final_state["completed_tasks"]) > 0)
        
        # Verify full history
        history = self.provider.get_call_history()
        self.assertEqual(len(history), len(workflow_steps) + 
                        len([s for s in workflow_steps if "implement" in s[0].lower()]))


if __name__ == '__main__':
    unittest.main()