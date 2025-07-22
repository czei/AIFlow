#!/usr/bin/env python3
"""
Contract tests for project setup AI responses.
Validates that AI responses for project setup meet the defined contract.
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from contract_base import ContractTestBase


class TestProjectSetupContract(ContractTestBase):
    """Test contract compliance for project setup responses"""
    
    def test_basic_project_setup_contract(self):
        """Test that basic project setup response meets contract"""
        # Query AI for project setup
        response = self.query_ai(
            "Create a new Python project called 'calculator' with proper structure",
            context={"project_type": "python", "project_name": "calculator"}
        )
        
        # Validate against schema
        self.validate_schema(response, "project_setup_schema")
        
        # Additional contract validations
        self.assertIn("type", response)
        self.assertEqual(response["type"], "project_setup")
        
        # Validate commands are present and valid
        self.assertIn("commands", response)
        self.assertIsInstance(response["commands"], list)
        self.assertGreater(len(response["commands"]), 0)
        
        # Each command should be a non-empty string
        for cmd in response["commands"]:
            self.assertIsInstance(cmd, str)
            self.assertTrue(len(cmd.strip()) > 0)
            
        # Explanation should be meaningful
        self.assertIn("explanation", response)
        self.assertGreater(len(response["explanation"]), 20)
    
    def test_web_project_setup_contract(self):
        """Test contract for web project setup"""
        response = self.query_ai(
            "Set up a new React web application with TypeScript",
            context={"project_type": "web", "framework": "react", "language": "typescript"}
        )
        
        # Validate schema compliance
        self.validate_schema(response, "project_setup_schema")
        
        # Validate response type
        self.validate_enum_field(response, "type", ["project_setup"])
        
        # Commands should include npm/yarn commands for web projects
        commands_text = " ".join(response["commands"])
        self.assertTrue(
            "npm" in commands_text or "yarn" in commands_text or "npx" in commands_text,
            "Web project setup should include package manager commands"
        )
    
    def test_project_setup_with_dependencies_contract(self):
        """Test contract when project includes dependencies"""
        response = self.query_ai(
            "Create a data science project with pandas, numpy, and jupyter",
            context={
                "project_type": "python",
                "project_name": "data_analysis",
                "dependencies": ["pandas", "numpy", "jupyter"]
            }
        )
        
        # Validate schema
        self.validate_schema(response, "project_setup_schema")
        
        # Should have commands for installing dependencies
        commands_text = " ".join(response["commands"]).lower()
        self.assertTrue(
            "pip install" in commands_text or "requirements.txt" in commands_text,
            "Should include dependency installation"
        )
    
    def test_project_setup_field_types(self):
        """Test that all fields have correct types"""
        response = self.query_ai(
            "Initialize a new Go module for a microservice",
            context={"project_type": "go", "project_name": "user-service"}
        )
        
        # Validate schema first
        self.validate_schema(response, "project_setup_schema")
        
        # Validate specific field types
        field_types = {
            "type": str,
            "commands": list,
            "explanation": str
        }
        self.validate_field_types(response, field_types)
        
        # Optional fields if present
        if "files_to_create" in response:
            self.assertIsInstance(response["files_to_create"], list)
            for file in response["files_to_create"]:
                self.assertIsInstance(file, str)
                
        if "directories" in response:
            self.assertIsInstance(response["directories"], list)
            
        if "next_steps" in response:
            self.assertIsInstance(response["next_steps"], list)
    
    def test_minimal_project_setup_contract(self):
        """Test contract with minimal valid response"""
        response = self.query_ai(
            "mkdir testproject",
            context={"minimal": True}
        )
        
        # Even minimal responses must meet base contract
        self.validate_schema(response, "project_setup_schema")
        
        # Verify required fields
        required_fields = ["type", "commands", "explanation"]
        self.validate_required_fields(response, required_fields)
    
    def test_complex_project_setup_contract(self):
        """Test contract with complex project including multiple components"""
        response = self.query_ai(
            "Set up a full-stack application with React frontend, Node.js backend, "
            "PostgreSQL database, and Docker configuration",
            context={
                "project_type": "fullstack",
                "components": ["frontend", "backend", "database", "docker"]
            }
        )
        
        # Validate against schema
        self.validate_schema(response, "project_setup_schema")
        
        # Complex projects should have more commands
        self.assertGreater(len(response["commands"]), 3)
        
        # Should mention key components in explanation
        explanation_lower = response["explanation"].lower()
        self.assertTrue(
            any(term in explanation_lower for term in ["frontend", "backend", "full-stack", "fullstack"]),
            "Explanation should describe the full-stack nature"
        )
    
    def test_project_setup_with_warnings_contract(self):
        """Test contract when response includes warnings"""
        response = self.query_ai(
            "Create a project using deprecated Python 2.7",
            context={"project_type": "python", "version": "2.7"}
        )
        
        # Validate schema
        self.validate_schema(response, "project_setup_schema")
        
        # If warnings are present, they should be a list of strings
        if "warnings" in response:
            self.assertIsInstance(response["warnings"], list)
            for warning in response["warnings"]:
                self.assertIsInstance(warning, str)
                self.assertGreater(len(warning), 10)  # Meaningful warning


if __name__ == "__main__":
    unittest.main()