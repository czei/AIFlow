#!/usr/bin/env python3
"""
Contract tests for code review AI responses.
Validates that AI responses for code review meet the defined contract.
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from contract_base import ContractTestBase


class TestCodeReviewContract(ContractTestBase):
    """Test contract compliance for code review responses"""
    
    def test_basic_code_review_contract(self):
        """Test that basic code review response meets contract"""
        code_to_review = """
def calculate_average(numbers):
    total = 0
    for n in numbers:
        total = total + n
    avg = total / len(numbers)
    return avg
"""
        
        response = self.query_ai(
            f"Review this Python code for quality and potential issues:\n{code_to_review}",
            context={"language": "python", "review_type": "comprehensive"}
        )
        
        # Validate against schema
        self.validate_schema(response, "code_review_schema")
        
        # Validate required fields
        self.assertEqual(response["type"], "code_review")
        self.assertIn("issues", response)
        self.assertIn("summary", response)
        
        # Issues should be a list
        self.assertIsInstance(response["issues"], list)
        
        # Each issue should have required fields
        for issue in response["issues"]:
            self.assertIn("severity", issue)
            self.assertIn("message", issue)
            self.assertIn(issue["severity"], ["critical", "high", "medium", "low", "info"])
            self.assertGreater(len(issue["message"]), 5)
    
    def test_security_focused_review_contract(self):
        """Test contract for security-focused code review"""
        vulnerable_code = """
def get_user_data(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return db.execute(query)
"""
        
        response = self.query_ai(
            f"Review this code for security vulnerabilities:\n{vulnerable_code}",
            context={"language": "python", "review_type": "security"}
        )
        
        # Validate schema
        self.validate_schema(response, "code_review_schema")
        
        # Should identify security issues
        has_security_issue = any(
            issue.get("category") == "security" or 
            "security" in issue.get("message", "").lower() or
            "sql" in issue.get("message", "").lower()
            for issue in response["issues"]
        )
        self.assertTrue(has_security_issue, "Should identify security vulnerabilities")
    
    def test_code_review_with_recommendations(self):
        """Test contract when review includes recommendations"""
        response = self.query_ai(
            "Review this code and provide improvement recommendations: def f(x): return x*2",
            context={"include_recommendations": True}
        )
        
        # Validate schema
        self.validate_schema(response, "code_review_schema")
        
        # Recommendation field should be valid if present
        if "recommendation" in response:
            valid_recommendations = [
                "approve", 
                "approve_with_suggestions", 
                "request_changes", 
                "needs_major_refactor"
            ]
            self.assertIn(response["recommendation"], valid_recommendations)
    
    def test_code_review_with_positive_aspects(self):
        """Test contract when review includes positive feedback"""
        good_code = """
def calculate_fibonacci(n: int) -> int:
    \"\"\"Calculate the nth Fibonacci number using dynamic programming.\"\"\"
    if n <= 0:
        raise ValueError("n must be positive")
    if n <= 2:
        return 1
    
    fib = [0] * (n + 1)
    fib[1] = fib[2] = 1
    
    for i in range(3, n + 1):
        fib[i] = fib[i-1] + fib[i-2]
    
    return fib[n]
"""
        
        response = self.query_ai(
            f"Review this well-written Python code:\n{good_code}",
            context={"language": "python", "balanced_review": True}
        )
        
        # Validate schema
        self.validate_schema(response, "code_review_schema")
        
        # Should have positive aspects if present
        if "positive_aspects" in response:
            self.assertIsInstance(response["positive_aspects"], list)
            self.assertGreater(len(response["positive_aspects"]), 0)
    
    def test_code_review_with_line_numbers(self):
        """Test contract when issues include line numbers"""
        response = self.query_ai(
            "Review code and indicate specific line numbers for issues:\ndef f():\n  x=1\n  return x",
            context={"include_line_numbers": True}
        )
        
        # Validate schema
        self.validate_schema(response, "code_review_schema")
        
        # Line numbers should be valid if present
        for issue in response["issues"]:
            if "line" in issue:
                self.assertIsInstance(issue["line"], int)
                self.assertGreater(issue["line"], 0)
    
    def test_code_review_categories(self):
        """Test that issue categories are valid"""
        response = self.query_ai(
            "Perform comprehensive code review covering all aspects",
            context={"code": "def slow_func(): return [i for i in range(1000000)]"}
        )
        
        # Validate schema
        self.validate_schema(response, "code_review_schema")
        
        # Check categories if present
        valid_categories = ["security", "performance", "maintainability", "style", "bug", "design"]
        for issue in response["issues"]:
            if "category" in issue:
                self.assertIn(issue["category"], valid_categories)
    
    def test_code_review_with_metrics(self):
        """Test contract when review includes code metrics"""
        response = self.query_ai(
            "Review code and provide quality metrics",
            context={"include_metrics": True, "code": "def complex_function(): pass"}
        )
        
        # Validate schema
        self.validate_schema(response, "code_review_schema")
        
        # Metrics should be valid if present
        if "metrics" in response:
            metrics = response["metrics"]
            self.assertIsInstance(metrics, dict)
            
            if "complexity" in metrics:
                self.assertIsInstance(metrics["complexity"], (int, float))
                self.assertGreaterEqual(metrics["complexity"], 0)
                
            if "maintainability" in metrics:
                self.assertIsInstance(metrics["maintainability"], (int, float))
                self.assertGreaterEqual(metrics["maintainability"], 0)
                self.assertLessEqual(metrics["maintainability"], 100)
    
    def test_minimal_code_review_contract(self):
        """Test contract with minimal valid response"""
        response = self.query_ai(
            "Quick review: x=1",
            context={"minimal": True}
        )
        
        # Must meet base contract
        self.validate_schema(response, "code_review_schema")
        
        # Required fields
        required_fields = ["type", "issues", "summary"]
        self.validate_required_fields(response, required_fields)
    
    def test_code_review_field_types(self):
        """Test that all fields have correct types"""
        response = self.query_ai(
            "Review this code comprehensively",
            context={"code": "def main(): print('hello')"}
        )
        
        # Validate schema
        self.validate_schema(response, "code_review_schema")
        
        # Validate field types
        field_types = {
            "type": str,
            "issues": list,
            "summary": str
        }
        self.validate_field_types(response, field_types)


if __name__ == "__main__":
    unittest.main()