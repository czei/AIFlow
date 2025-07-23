#!/usr/bin/env python3
"""
Chaos tests for timeout resilience.
Tests system behavior under various timeout conditions.
"""

import unittest
import time
import random
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from chaos_base import ChaosTestBase


class TestTimeoutResilienceChaos(ChaosTestBase):
    """Test system resilience to timeout conditions"""
    
    def test_basic_timeout_recovery(self):
        """Test basic recovery from timeout"""
        def timeout_operation():
            return self.chaos_query(
                "Generate a simple function that adds two numbers",
                context={"force_timeout": random.random() < 0.3},
                timeout=5.0
            )
        
        # Should recover from occasional timeouts
        self.assert_resilient(timeout_operation, min_success_rate=0.7)
    
    def test_cascading_timeouts(self):
        """Test recovery from cascading timeout failures"""
        consecutive_timeouts = 0
        max_consecutive = 0
        recoveries = 0
        
        for i in range(20):
            try:
                # Increase timeout probability after consecutive failures
                timeout_prob = min(0.8, 0.2 + (consecutive_timeouts * 0.2))
                
                response = self.chaos_query(
                    f"Process request {i} with potential timeout",
                    context={
                        "request_id": i,
                        "timeout_probability": timeout_prob
                    },
                    timeout=3.0,
                    max_retries=2
                )
                
                if response.get('type') != 'error':
                    if consecutive_timeouts > 0:
                        recoveries += 1
                    consecutive_timeouts = 0
                else:
                    consecutive_timeouts += 1
                    max_consecutive = max(max_consecutive, consecutive_timeouts)
                    
            except Exception:
                consecutive_timeouts += 1
                max_consecutive = max(max_consecutive, consecutive_timeouts)
        
        # System should recover from timeout cascades
        self.assertGreater(recoveries, 0, "No recovery from timeout cascades")
        self.assertLess(max_consecutive, 10, "Timeout cascade too long")
    
    def test_variable_timeout_thresholds(self):
        """Test different timeout thresholds for different operations"""
        operations = [
            {
                "name": "quick_operation",
                "prompt": "Return a simple greeting",
                "timeout": 1.0,
                "expected_success_rate": 0.9
            },
            {
                "name": "medium_operation", 
                "prompt": "Generate a 5-line Python function",
                "timeout": 5.0,
                "expected_success_rate": 0.8
            },
            {
                "name": "long_operation",
                "prompt": "Create a comprehensive project plan with 10 steps",
                "timeout": 10.0,
                "expected_success_rate": 0.7
            }
        ]
        
        for op in operations:
            successes = 0
            attempts = 10
            
            for _ in range(attempts):
                try:
                    response = self.chaos_query(
                        op["prompt"],
                        timeout=op["timeout"],
                        max_retries=1
                    )
                    if response.get('type') != 'error':
                        successes += 1
                except Exception:
                    pass
            
            success_rate = successes / attempts
            self.assertGreaterEqual(
                success_rate, op["expected_success_rate"] * 0.8,  # Allow some variance
                f"{op['name']} success rate too low: {success_rate}"
            )
    
    def test_timeout_with_partial_response(self):
        """Test handling of timeouts with partial responses"""
        partial_responses = []
        
        for i in range(10):
            try:
                # Simulate operations that might timeout mid-response
                response = self.chaos_query(
                    "Generate a long response that might be interrupted",
                    context={
                        "response_chunks": 10,
                        "chunk_delay": 0.5,
                        "interrupt_probability": 0.3
                    },
                    timeout=3.0
                )
                
                # Check if we got a partial response
                if response.get('partial', False):
                    partial_responses.append(response)
                    
            except TimeoutError:
                # Expected for some iterations
                pass
        
        # Should handle some partial responses gracefully
        self.assertGreater(len(partial_responses), 0, 
                          "No partial responses handled")
    
    def test_adaptive_timeout_adjustment(self):
        """Test adaptive timeout adjustment based on response patterns"""
        base_timeout = 2.0
        adaptive_timeout = base_timeout
        timeout_history = []
        adjustments = 0
        
        for i in range(15):
            start_time = time.time()
            
            try:
                response = self.chaos_query(
                    f"Operation {i} with adaptive timeout",
                    context={"complexity": random.choice(["low", "medium", "high"])},
                    timeout=adaptive_timeout
                )
                
                response_time = time.time() - start_time
                timeout_history.append({
                    "success": True,
                    "time": response_time,
                    "timeout": adaptive_timeout
                })
                
                # Adjust timeout based on response time
                if response_time > adaptive_timeout * 0.8:
                    # Close to timeout, increase
                    adaptive_timeout = min(30.0, adaptive_timeout * 1.5)
                    adjustments += 1
                elif response_time < adaptive_timeout * 0.3:
                    # Very fast, decrease
                    adaptive_timeout = max(1.0, adaptive_timeout * 0.8)
                    adjustments += 1
                    
            except TimeoutError:
                timeout_history.append({
                    "success": False,
                    "time": adaptive_timeout,
                    "timeout": adaptive_timeout
                })
                # Timeout occurred, increase threshold
                adaptive_timeout = min(30.0, adaptive_timeout * 2)
                adjustments += 1
        
        # Should make some adjustments
        self.assertGreater(adjustments, 2, "Not enough adaptive adjustments")
        
        # Final timeout should be different from initial
        self.assertNotAlmostEqual(adaptive_timeout, base_timeout, places=1,
                                 msg="Timeout not adapted")
    
    def test_concurrent_timeout_handling(self):
        """Test handling multiple concurrent operations with different timeouts"""
        import threading
        
        results = {
            "completed": 0,
            "timed_out": 0,
            "errors": 0
        }
        lock = threading.Lock()
        
        def concurrent_operation(op_id, timeout):
            try:
                response = self.chaos_query(
                    f"Concurrent operation {op_id}",
                    context={"operation_id": op_id},
                    timeout=timeout
                )
                
                with lock:
                    if response.get('type') != 'error':
                        results["completed"] += 1
                    else:
                        results["errors"] += 1
                        
            except TimeoutError:
                with lock:
                    results["timed_out"] += 1
            except Exception:
                with lock:
                    results["errors"] += 1
        
        # Launch concurrent operations
        threads = []
        for i in range(10):
            timeout = random.uniform(1.0, 5.0)
            thread = threading.Thread(
                target=concurrent_operation,
                args=(i, timeout)
            )
            threads.append(thread)
            thread.start()
        
        # Wait for all to complete
        for thread in threads:
            thread.join(timeout=10.0)
        
        # Should handle concurrent timeouts without system failure
        total = sum(results.values())
        self.assertEqual(total, 10, "Not all operations accounted for")
        self.assertGreater(results["completed"], 3, "Too few completions")
        self.assertLess(results["timed_out"], 7, "Too many timeouts")
    
    def test_timeout_during_retry(self):
        """Test timeout handling during retry attempts"""
        retry_patterns = []
        
        for i in range(5):
            pattern = {
                "attempt": i,
                "retries": [],
                "final_result": None
            }
            
            try:
                # Custom retry logic with timeout tracking
                for retry in range(3):
                    try:
                        response = self.chaos_query(
                            f"Operation with retry attempt {retry}",
                            context={
                                "fail_first_n": random.randint(0, 2),
                                "attempt": i,
                                "retry": retry
                            },
                            timeout=2.0,
                            max_retries=1  # Handle retries manually
                        )
                        
                        pattern["retries"].append({
                            "retry": retry,
                            "success": response.get('type') != 'error'
                        })
                        
                        if response.get('type') != 'error':
                            pattern["final_result"] = "success"
                            break
                            
                    except TimeoutError:
                        pattern["retries"].append({
                            "retry": retry,
                            "success": False,
                            "timeout": True
                        })
                        
                if pattern["final_result"] is None:
                    pattern["final_result"] = "failed"
                    
            except Exception as e:
                pattern["final_result"] = f"error: {type(e).__name__}"
                
            retry_patterns.append(pattern)
        
        # Analyze retry patterns
        successful_patterns = [p for p in retry_patterns if p["final_result"] == "success"]
        self.assertGreater(len(successful_patterns), 1, "Too few successful retry patterns")
        
        # Check that some succeeded after retries
        succeeded_after_retry = [
            p for p in successful_patterns 
            if len(p["retries"]) > 1
        ]
        self.assertGreater(len(succeeded_after_retry), 0, "No success after retry")


if __name__ == "__main__":
    unittest.main()