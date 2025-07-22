#!/usr/bin/env python3
"""
Chaos tests for edge cases and unusual inputs.
Tests system behavior with extreme, malformed, or unexpected inputs.
"""

import unittest
import random
import string
import json
from chaos_base import ChaosTestBase


class TestEdgeCasesChaos(ChaosTestBase):
    """Test system resilience to edge cases and unusual inputs"""
    
    def test_empty_and_null_inputs(self):
        """Test handling of empty and null inputs"""
        edge_inputs = [
            ("", "empty string"),
            ("   ", "whitespace only"),
            ("\n\n\n", "newlines only"),
            ("\t\t", "tabs only"),
            ("null", "null string"),
            ("None", "None string"),
            ("undefined", "undefined string"),
        ]
        
        handled_correctly = 0
        
        for input_val, description in edge_inputs:
            try:
                response = self.chaos_query(
                    input_val,
                    context={"test_case": description},
                    max_retries=1
                )
                
                # Should get some kind of response
                if isinstance(response, dict):
                    handled_correctly += 1
                    
            except Exception as e:
                # Log but don't fail - we're testing resilience
                self.test_errors.append({
                    "input": description,
                    "error": str(e)
                })
        
        # Should handle most empty inputs gracefully
        self.assertGreater(handled_correctly, len(edge_inputs) * 0.5)
    
    def test_extremely_long_inputs(self):
        """Test handling of very long inputs"""
        test_cases = [
            ("word" * 1000, "repeated words"),
            ("a" * 10000, "single character repeated"),
            (" ".join([f"item_{i}" for i in range(500)]), "long list"),
            ("Lorem ipsum " * 500, "repeated phrase"),
            (json.dumps({"key": "value"} for _ in range(100)), "json dump"),
        ]
        
        for content, description in test_cases:
            with self.subTest(case=description):
                try:
                    response = self.chaos_query(
                        f"Process this content: {content[:1000]}...",  # Truncate for prompt
                        context={
                            "content_length": len(content),
                            "content_type": description
                        },
                        timeout=10.0
                    )
                    
                    # Should either handle it or fail gracefully
                    self.assertIsInstance(response, dict)
                    
                except Exception as e:
                    # Should not crash the system
                    self.assertIn(type(e).__name__, 
                                 ["TimeoutError", "ValueError", "RuntimeError"])
    
    def test_special_characters_and_unicode(self):
        """Test handling of special characters and unicode"""
        special_inputs = [
            "Hello 👋 World 🌍",  # Emojis
            "Test\x00with\x00null\x00bytes",  # Null bytes
            "Line1\rLine2\nLine3\r\nLine4",  # Mixed line endings
            "Test\\with\\backslashes\\\\",  # Backslashes
            "Test\"with\"quotes'and'apostrophes",  # Quotes
            "Test<script>alert('xss')</script>",  # HTML/JS injection attempt
            "Test'; DROP TABLE users; --",  # SQL injection attempt
            "Tëst wîth spéçiål çhäracters",  # Accented characters
            "测试中文字符",  # Chinese characters
            "🔥💥🎭🎨🎪",  # Only emojis
            "\u200b\u200c\u200d",  # Zero-width characters
            "A\u0301\u0302\u0303\u0304",  # Combining diacriticals
        ]
        
        resilient_count = 0
        
        for special_input in special_inputs:
            try:
                response = self.chaos_query(
                    f"Analyze this text: {special_input}",
                    context={"contains_special": True},
                    max_retries=2
                )
                
                if response.get('type') != 'error':
                    resilient_count += 1
                    # Verify response doesn't contain injection
                    response_str = json.dumps(response)
                    self.assertNotIn("<script>", response_str)
                    self.assertNotIn("DROP TABLE", response_str)
                    
            except Exception:
                # Expected for some inputs
                pass
        
        # Should handle majority of special inputs
        self.assertGreater(resilient_count, len(special_inputs) * 0.6)
    
    def test_malformed_json_context(self):
        """Test handling of malformed context data"""
        malformed_contexts = [
            {"circular": None},  # Will create circular reference
            {"deep": {"nested": {"structure": {"very": {"deep": {"indeed": {}}}}}}},
            {"huge_list": list(range(10000))},
            {"binary": b"binary data"},  # Bytes object
            {"set": {1, 2, 3}},  # Set (not JSON serializable)
            {"function": lambda x: x},  # Function object
            {"inf": float('inf')},  # Infinity
            {"nan": float('nan')},  # NaN
        ]
        
        # Add circular reference
        malformed_contexts[0]["circular"] = malformed_contexts[0]
        
        handled = 0
        
        for i, context in enumerate(malformed_contexts):
            try:
                # Try to use malformed context
                response = self.chaos_query(
                    "Process with special context",
                    context=context,
                    max_retries=1
                )
                
                if isinstance(response, dict):
                    handled += 1
                    
            except (TypeError, ValueError, OverflowError) as e:
                # These are expected for malformed data
                handled += 1
            except Exception as e:
                # Unexpected error
                self.test_errors.append({
                    "context_type": f"malformed_{i}",
                    "error": type(e).__name__
                })
        
        # Should handle all malformed contexts without crashing
        self.assertEqual(handled, len(malformed_contexts))
    
    def test_rapid_fire_requests(self):
        """Test handling of rapid successive requests"""
        results = {
            "success": 0,
            "rate_limited": 0,
            "errors": 0
        }
        
        # Send rapid requests
        for i in range(20):
            try:
                response = self.chaos_query(
                    f"Rapid request {i}",
                    context={"request_num": i, "rapid_fire": True},
                    max_retries=1,
                    timeout=2.0
                )
                
                if response.get('type') == 'error':
                    if 'rate' in response.get('error', '').lower():
                        results["rate_limited"] += 1
                    else:
                        results["errors"] += 1
                else:
                    results["success"] += 1
                    
                # No delay between requests (stress test)
                
            except Exception:
                results["errors"] += 1
        
        # Should handle rapid requests appropriately
        total = sum(results.values())
        self.assertEqual(total, 20, "Lost requests during rapid fire")
        
        # Some should succeed even under pressure
        self.assertGreater(results["success"], 5)
    
    def test_contradictory_instructions(self):
        """Test handling of contradictory or impossible instructions"""
        contradictions = [
            "Generate a Python function in JavaScript syntax",
            "Create a sorted list that is also unsorted",
            "Write code that compiles but has syntax errors",
            "Make this text shorter by making it longer",
            "Return null but make sure it's not null",
            "Follow these instructions but ignore all instructions",
        ]
        
        graceful_handling = 0
        
        for contradiction in contradictions:
            try:
                response = self.chaos_query(
                    contradiction,
                    context={"paradox": True},
                    max_retries=2
                )
                
                # Any coherent response counts as graceful handling
                if isinstance(response, dict) and response.get('type') != 'error':
                    graceful_handling += 1
                    
                    # Check that response acknowledges the contradiction
                    response_text = str(response).lower()
                    if any(word in response_text for word in 
                          ['cannot', 'impossible', 'contradictory', 'unclear']):
                        graceful_handling += 0.5
                        
            except Exception:
                # Failing gracefully is still graceful
                graceful_handling += 0.5
        
        # Should handle contradictions without breaking
        self.assertGreater(graceful_handling, len(contradictions) * 0.5)
    
    def test_resource_exhaustion_attempts(self):
        """Test resilience to resource exhaustion attempts"""
        exhaustion_attempts = [
            {
                "prompt": "Repeat this text infinitely: " + "a" * 100,
                "description": "infinite repetition request"
            },
            {
                "prompt": "Calculate factorial of 999999999",
                "description": "huge computation request"
            },
            {
                "prompt": "Generate all possible combinations of 50 items",
                "description": "combinatorial explosion"
            },
            {
                "prompt": "Create nested loops 100 levels deep",
                "description": "deep nesting request"
            },
        ]
        
        for attempt in exhaustion_attempts:
            with self.subTest(case=attempt["description"]):
                try:
                    response = self.chaos_query(
                        attempt["prompt"],
                        context={"resource_test": attempt["description"]},
                        timeout=5.0,
                        max_retries=1
                    )
                    
                    # Should either refuse or handle gracefully
                    if response.get('type') != 'error':
                        # Check response is reasonable size
                        response_size = len(json.dumps(response))
                        self.assertLess(response_size, 10000, 
                                       "Response too large for exhaustion attempt")
                        
                except TimeoutError:
                    # Timeout is acceptable for resource exhaustion
                    pass
                except Exception as e:
                    # Should be a controlled failure
                    self.assertIn(type(e).__name__, 
                                 ["ValueError", "RuntimeError", "MemoryError"])
    
    def test_format_confusion(self):
        """Test handling of format confusion and mixed formats"""
        format_tests = [
            {
                "prompt": "Parse this XML: {\"json\": \"data\"}",
                "expected_format": "xml",
                "actual_format": "json"
            },
            {
                "prompt": "Process this JSON: <xml>data</xml>",
                "expected_format": "json", 
                "actual_format": "xml"
            },
            {
                "prompt": "Execute this Python: SELECT * FROM users;",
                "expected_format": "python",
                "actual_format": "sql"
            },
            {
                "prompt": "Validate this YAML: [1, 2, 3]",
                "expected_format": "yaml",
                "actual_format": "json"
            },
        ]
        
        format_handled = 0
        
        for test in format_tests:
            try:
                response = self.chaos_query(
                    test["prompt"],
                    context={
                        "expected_format": test["expected_format"],
                        "actual_format": test["actual_format"]
                    }
                )
                
                if isinstance(response, dict):
                    format_handled += 1
                    
            except Exception:
                # Should recognize format mismatch
                format_handled += 0.5
        
        # Should handle format confusion gracefully
        self.assertGreater(format_handled, len(format_tests) * 0.6)


if __name__ == "__main__":
    unittest.main()