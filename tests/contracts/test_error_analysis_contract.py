#!/usr/bin/env python3
"""
Contract tests for error analysis AI responses.
Validates that AI responses for error analysis meet the defined contract.
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from contract_base import ContractTestBase


class TestErrorAnalysisContract(ContractTestBase):
    """Test contract compliance for error analysis responses"""
    
    def test_basic_error_analysis_contract(self):
        """Test that basic error analysis response meets contract"""
        error_message = """
Traceback (most recent call last):
  File "main.py", line 10, in <module>
    result = divide(10, 0)
  File "main.py", line 5, in divide
    return a / b
ZeroDivisionError: division by zero
"""
        
        response = self.query_ai(
            f"Analyze this Python error and provide a fix:\n{error_message}",
            context={"language": "python", "error_type": "runtime"}
        )
        
        # Validate against schema
        self.validate_schema(response, "error_analysis_schema")
        
        # Validate required fields
        self.assertIn("type", response)
        self.assertIn(response["type"], ["error_analysis", "debug", "troubleshooting"])
        self.assertIn("diagnosis", response)
        self.assertIn("fix", response)
        
        # Diagnosis and fix should be meaningful
        self.assertGreater(len(response["diagnosis"]), 10)
        self.assertGreater(len(response["fix"]), 5)
    
    def test_syntax_error_analysis_contract(self):
        """Test contract for syntax error analysis"""
        syntax_error = """
  File "script.py", line 3
    if x = 5:
         ^
SyntaxError: invalid syntax
"""
        
        response = self.query_ai(
            f"Analyze this syntax error:\n{syntax_error}",
            context={"language": "python", "error_type": "syntax"}
        )
        
        # Validate schema
        self.validate_schema(response, "error_analysis_schema")
        
        # Should identify error type correctly if present
        if "error_type" in response:
            self.assertEqual(response["error_type"], "syntax")
    
    def test_error_with_code_fix_contract(self):
        """Test contract when code fix is provided"""
        response = self.query_ai(
            "TypeError: unsupported operand type(s) for +: 'int' and 'str'",
            context={"include_code_fix": True}
        )
        
        # Validate schema
        self.validate_schema(response, "error_analysis_schema")
        
        # Code fix should be present if requested
        if "code_fix" in response:
            self.assertIsInstance(response["code_fix"], str)
            self.assertGreater(len(response["code_fix"]), 0)
    
    def test_error_with_prevention_advice_contract(self):
        """Test contract when prevention advice is included"""
        response = self.query_ai(
            "Analyze null pointer exception and how to prevent it",
            context={"language": "java", "include_prevention": True}
        )
        
        # Validate schema
        self.validate_schema(response, "error_analysis_schema")
        
        # Prevention advice should be meaningful if present
        if "prevention" in response:
            self.assertIsInstance(response["prevention"], str)
            self.assertGreater(len(response["prevention"]), 20)
    
    def test_runtime_error_analysis_contract(self):
        """Test contract for runtime error analysis"""
        runtime_error = """
IndexError: list index out of range
Context: Accessing items[10] when items has length 5
"""
        
        response = self.query_ai(
            f"Debug this runtime error:\n{runtime_error}",
            context={"error_type": "runtime", "include_debugging_steps": True}
        )
        
        # Validate schema
        self.validate_schema(response, "error_analysis_schema")
        
        # Debugging steps should be present if requested
        if "debugging_steps" in response:
            self.assertIsInstance(response["debugging_steps"], list)
            self.assertGreater(len(response["debugging_steps"]), 0)
            for step in response["debugging_steps"]:
                self.assertIsInstance(step, str)
    
    def test_error_analysis_with_confidence_contract(self):
        """Test contract when confidence level is included"""
        vague_error = "Something went wrong with the application"
        
        response = self.query_ai(
            f"Analyze this vague error message:\n{vague_error}",
            context={"include_confidence": True}
        )
        
        # Validate schema
        self.validate_schema(response, "error_analysis_schema")
        
        # Confidence should be valid if present
        if "confidence" in response:
            confidence = response["confidence"]
            self.assertIsInstance(confidence, (int, float))
            self.assertGreaterEqual(confidence, 0)
            self.assertLessEqual(confidence, 1)
    
    def test_error_with_related_issues_contract(self):
        """Test contract when related issues are documented"""
        response = self.query_ai(
            "Analyze memory leak error and list related issues",
            context={"error_type": "performance", "include_related": True}
        )
        
        # Validate schema
        self.validate_schema(response, "error_analysis_schema")
        
        # Related issues should be a list if present
        if "related_issues" in response:
            self.assertIsInstance(response["related_issues"], list)
            for issue in response["related_issues"]:
                self.assertIsInstance(issue, str)
    
    def test_error_type_validation_contract(self):
        """Test that error types are valid"""
        response = self.query_ai(
            "Analyze various types of errors",
            context={"error": "Generic error for testing"}
        )
        
        # Validate schema
        self.validate_schema(response, "error_analysis_schema")
        
        # Error type should be valid if present
        if "error_type" in response:
            valid_types = [
                "syntax", "runtime", "logic", "type", 
                "reference", "permission", "network", "configuration"
            ]
            self.assertIn(response["error_type"], valid_types)
    
    def test_minimal_error_analysis_contract(self):
        """Test contract with minimal valid response"""
        response = self.query_ai(
            "Error: failed",
            context={"minimal": True}
        )
        
        # Must meet base contract
        self.validate_schema(response, "error_analysis_schema")
        
        # Required fields
        required_fields = ["type", "diagnosis", "fix"]
        self.validate_required_fields(response, required_fields)
    
    def test_error_analysis_field_types(self):
        """Test that all fields have correct types"""
        response = self.query_ai(
            "Analyze comprehensive error with all details",
            context={"error": "Test error", "comprehensive": True}
        )
        
        # Validate schema
        self.validate_schema(response, "error_analysis_schema")
        
        # Validate field types
        field_types = {
            "type": str,
            "diagnosis": str,
            "fix": str
        }
        self.validate_field_types(response, field_types)
        
        # Optional fields
        if "code_fix" in response:
            self.assertIsInstance(response["code_fix"], str)
        if "explanation" in response:
            self.assertIsInstance(response["explanation"], str)
        if "root_cause" in response:
            self.assertIsInstance(response["root_cause"], str)


if __name__ == "__main__":
    unittest.main()