#!/usr/bin/env python3
"""
Contract tests for code generation AI responses.
Validates that AI responses for code generation meet the defined contract.
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from contract_base import ContractTestBase


class TestCodeGenerationContract(ContractTestBase):
    """Test contract compliance for code generation responses"""
    
    def test_function_generation_contract(self):
        """Test that function generation meets contract"""
        response = self.query_ai(
            "Generate a Python function to calculate the factorial of a number",
            context={"language": "python", "function_name": "factorial"}
        )
        
        # Validate against schema
        self.validate_schema(response, "code_generation_schema")
        
        # Validate response type
        self.assertIn("type", response)
        self.assertIn(response["type"], ["code_generation", "code_implementation", "function"])
        
        # Validate code is present and looks like a function
        self.assertIn("code", response)
        code = response["code"]
        self.assertIsInstance(code, str)
        self.assertTrue("def" in code or "function" in code or "func" in code)
        
        # Explanation should be present
        self.assertIn("explanation", response)
        self.assertGreater(len(response["explanation"]), 20)
    
    def test_class_generation_contract(self):
        """Test contract for class generation"""
        response = self.query_ai(
            "Create a Python class for a BankAccount with deposit and withdraw methods",
            context={"language": "python", "class_name": "BankAccount"}
        )
        
        # Validate schema
        self.validate_schema(response, "code_generation_schema")
        
        # Validate code contains class definition
        self.assertIn("code", response)
        self.assertIn("class", response["code"])
        
        # Should have methods mentioned
        code_lower = response["code"].lower()
        self.assertIn("deposit", code_lower)
        self.assertIn("withdraw", code_lower)
    
    def test_code_with_tests_contract(self):
        """Test contract when test code is included"""
        response = self.query_ai(
            "Write a function to check if a string is a palindrome, include unit tests",
            context={"language": "python", "include_tests": True}
        )
        
        # Validate schema
        self.validate_schema(response, "code_generation_schema")
        
        # Main code should be present
        self.assertIn("code", response)
        self.assertGreater(len(response["code"]), 10)
        
        # Test code should be present when requested
        if "test_code" in response:
            self.assertIsInstance(response["test_code"], str)
            test_lower = response["test_code"].lower()
            self.assertTrue(
                "test" in test_lower or "assert" in test_lower or "expect" in test_lower,
                "Test code should contain testing keywords"
            )
    
    def test_code_with_complexity_contract(self):
        """Test contract when complexity analysis is included"""
        response = self.query_ai(
            "Implement binary search algorithm with complexity analysis",
            context={"language": "python", "include_complexity": True}
        )
        
        # Validate schema
        self.validate_schema(response, "code_generation_schema")
        
        # If complexity is present, validate format
        if "complexity" in response:
            complexity = response["complexity"]
            self.assertIsInstance(complexity, dict)
            
            if "time" in complexity:
                self.assertRegex(complexity["time"], r"^O\(.+\)$")
            if "space" in complexity:
                self.assertRegex(complexity["space"], r"^O\(.+\)$")
    
    def test_multi_language_generation_contract(self):
        """Test contract for different programming languages"""
        languages = ["javascript", "python", "java", "go"]
        
        for lang in languages:
            with self.subTest(language=lang):
                response = self.query_ai(
                    f"Write a hello world function in {lang}",
                    context={"language": lang}
                )
                
                # Validate schema
                self.validate_schema(response, "code_generation_schema")
                
                # Language field should match if present
                if "language" in response:
                    self.assertEqual(response["language"].lower(), lang.lower())
    
    def test_code_with_dependencies_contract(self):
        """Test contract when code has dependencies"""
        response = self.query_ai(
            "Create a Python function to fetch data from an API using requests library",
            context={"language": "python", "dependencies": ["requests"]}
        )
        
        # Validate schema
        self.validate_schema(response, "code_generation_schema")
        
        # Dependencies should be listed if present
        if "dependencies" in response:
            self.assertIsInstance(response["dependencies"], list)
            self.assertGreater(len(response["dependencies"]), 0)
            
            # Should mention the required library
            deps_str = " ".join(response["dependencies"]).lower()
            self.assertIn("requests", deps_str)
    
    def test_code_with_edge_cases_contract(self):
        """Test contract when edge cases are documented"""
        response = self.query_ai(
            "Write a division function that handles edge cases properly",
            context={"language": "python", "document_edge_cases": True}
        )
        
        # Validate schema
        self.validate_schema(response, "code_generation_schema")
        
        # Edge cases should be documented if present
        if "edge_cases" in response:
            self.assertIsInstance(response["edge_cases"], list)
            for edge_case in response["edge_cases"]:
                self.assertIsInstance(edge_case, str)
                self.assertGreater(len(edge_case), 5)
    
    def test_minimal_code_generation_contract(self):
        """Test contract with minimal valid response"""
        response = self.query_ai(
            "x = 1",
            context={"minimal": True}
        )
        
        # Even minimal responses must meet base contract
        self.validate_schema(response, "code_generation_schema")
        
        # Required fields
        required_fields = ["type", "code", "explanation"]
        self.validate_required_fields(response, required_fields)
    
    def test_code_generation_field_types(self):
        """Test that all fields have correct types"""
        response = self.query_ai(
            "Generate a sorting algorithm",
            context={"language": "python"}
        )
        
        # Validate schema
        self.validate_schema(response, "code_generation_schema")
        
        # Validate field types
        field_types = {
            "type": str,
            "code": str,
            "explanation": str
        }
        self.validate_field_types(response, field_types)
        
        # Optional fields
        if "language" in response:
            self.assertIsInstance(response["language"], str)
        if "test_code" in response:
            self.assertIsInstance(response["test_code"], str)
        if "dependencies" in response:
            self.assertIsInstance(response["dependencies"], list)
        if "usage_example" in response:
            self.assertIsInstance(response["usage_example"], str)


if __name__ == "__main__":
    unittest.main()