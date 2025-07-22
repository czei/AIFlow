#!/usr/bin/env python3
"""
Chaos tests for error recovery scenarios.
Tests system's ability to recover from various error conditions.
"""

import unittest
import random
import time
from chaos_base import ChaosTestBase


class TestErrorRecoveryChaos(ChaosTestBase):
    """Test system's ability to recover from errors"""
    
    def test_network_error_recovery(self):
        """Test recovery from simulated network errors"""
        network_errors = [
            ConnectionError("Connection refused"),
            ConnectionError("Connection reset by peer"),
            ConnectionError("Network is unreachable"),
            TimeoutError("Connection timed out"),
            OSError("No route to host"),
        ]
        
        recovery_success = 0
        total_attempts = len(network_errors) * 3
        
        for error_type in network_errors:
            for attempt in range(3):
                try:
                    # Simulate network issues
                    with self.simulate_network_issues(
                        latency_range=(0.5, 3.0),
                        packet_loss=0.3
                    ):
                        response = self.chaos_query(
                            f"Test recovery from {type(error_type).__name__}",
                            context={
                                "simulate_error": random.random() < 0.4,
                                "error_type": type(error_type).__name__
                            },
                            max_retries=3
                        )
                        
                    if response.get('type') != 'error':
                        recovery_success += 1
                        
                except Exception as e:
                    # Track but don't fail immediately
                    self.test_errors.append({
                        "original_error": type(error_type).__name__,
                        "actual_error": type(e).__name__,
                        "attempt": attempt
                    })
        
        # Should recover from at least half the network errors
        recovery_rate = recovery_success / total_attempts
        self.assertGreater(recovery_rate, 0.5, 
                          f"Poor network error recovery: {recovery_rate:.2%}")
    
    def test_partial_failure_recovery(self):
        """Test recovery from partial failures in multi-step operations"""
        multi_step_operations = [
            {
                "name": "data_processing",
                "steps": ["fetch", "validate", "transform", "store"],
                "failure_points": [1, 2]  # Fail at these steps sometimes
            },
            {
                "name": "report_generation",
                "steps": ["query", "aggregate", "format", "deliver"],
                "failure_points": [0, 3]
            },
            {
                "name": "deployment",
                "steps": ["build", "test", "package", "deploy", "verify"],
                "failure_points": [2, 4]
            }
        ]
        
        for operation in multi_step_operations:
            completed_steps = []
            failed_steps = []
            recovered = False
            
            for i, step in enumerate(operation["steps"]):
                try:
                    # Possibly fail at designated points
                    should_fail = (i in operation["failure_points"] and 
                                 random.random() < 0.5)
                    
                    response = self.chaos_query(
                        f"Execute {step} for {operation['name']}",
                        context={
                            "operation": operation["name"],
                            "step": step,
                            "step_number": i,
                            "force_failure": should_fail,
                            "previous_steps": completed_steps
                        },
                        max_retries=2
                    )
                    
                    if response.get('type') != 'error':
                        completed_steps.append(step)
                        if step in failed_steps:
                            recovered = True
                    else:
                        failed_steps.append(step)
                        
                except Exception:
                    failed_steps.append(step)
            
            # Should complete most steps even with failures
            completion_rate = len(completed_steps) / len(operation["steps"])
            self.assertGreater(completion_rate, 0.5,
                             f"{operation['name']} completion too low")
            
            # Check if recovery occurred
            if failed_steps and recovered:
                self.recovery_attempts.append({
                    "operation": operation["name"],
                    "recovered": True
                })
    
    def test_cascading_failure_isolation(self):
        """Test that failures don't cascade to unrelated operations"""
        operations = []
        
        # Run series of operations where some fail
        for i in range(10):
            operation_result = {
                "id": i,
                "type": random.choice(["safe", "risky", "failing"]),
                "result": None,
                "affected_by_previous": False
            }
            
            try:
                # Risky operations have higher failure chance
                failure_chance = {
                    "safe": 0.1,
                    "risky": 0.5,
                    "failing": 0.9
                }[operation_result["type"]]
                
                response = self.chaos_query(
                    f"Operation {i} of type {operation_result['type']}",
                    context={
                        "operation_id": i,
                        "failure_probability": failure_chance,
                        "previous_failed": any(
                            op["result"] == "failed" 
                            for op in operations[-3:]
                        ) if operations else False
                    },
                    max_retries=1
                )
                
                if response.get('type') != 'error':
                    operation_result["result"] = "success"
                else:
                    operation_result["result"] = "failed"
                    
            except Exception:
                operation_result["result"] = "failed"
            
            # Check if affected by previous failures
            if operations and operations[-1]["result"] == "failed":
                if operation_result["type"] == "safe" and operation_result["result"] == "failed":
                    operation_result["affected_by_previous"] = True
                    
            operations.append(operation_result)
        
        # Analyze cascade effects
        cascaded_failures = sum(1 for op in operations if op["affected_by_previous"])
        safe_operations = [op for op in operations if op["type"] == "safe"]
        safe_success_rate = sum(1 for op in safe_operations if op["result"] == "success") / len(safe_operations)
        
        # Safe operations should mostly succeed despite other failures
        self.assertGreater(safe_success_rate, 0.7, "Too many safe operations failed")
        self.assertLess(cascaded_failures, 3, "Too many cascading failures")
    
    def test_graceful_degradation(self):
        """Test system degrades gracefully under stress"""
        stress_levels = [
            {"name": "normal", "load": 1, "expected_quality": 0.9},
            {"name": "moderate", "load": 5, "expected_quality": 0.7},
            {"name": "high", "load": 10, "expected_quality": 0.5},
            {"name": "extreme", "load": 20, "expected_quality": 0.3},
        ]
        
        degradation_profile = []
        
        for level in stress_levels:
            successes = 0
            quality_scores = []
            response_times = []
            
            for i in range(level["load"]):
                start_time = time.time()
                
                try:
                    response = self.chaos_query(
                        f"Request under {level['name']} stress",
                        context={
                            "stress_level": level["name"],
                            "concurrent_load": level["load"],
                            "request_id": i
                        },
                        timeout=5.0,
                        max_retries=1
                    )
                    
                    response_time = time.time() - start_time
                    response_times.append(response_time)
                    
                    if response.get('type') != 'error':
                        successes += 1
                        
                        # Estimate response quality (simplified)
                        quality = 1.0
                        if response.get('degraded'):
                            quality *= 0.7
                        if response.get('partial'):
                            quality *= 0.8
                        if response_time > 3.0:
                            quality *= 0.9
                            
                        quality_scores.append(quality)
                        
                except Exception:
                    response_times.append(5.0)  # Timeout
                    quality_scores.append(0.0)
            
            # Calculate metrics
            success_rate = successes / level["load"]
            avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
            avg_response_time = sum(response_times) / len(response_times)
            
            degradation_profile.append({
                "level": level["name"],
                "success_rate": success_rate,
                "quality": avg_quality,
                "response_time": avg_response_time
            })
            
            # Verify graceful degradation
            self.assertGreater(success_rate, level["expected_quality"] * 0.5,
                             f"Success rate too low for {level['name']} stress")
        
        # Verify degradation is gradual, not sudden
        for i in range(1, len(degradation_profile)):
            prev = degradation_profile[i-1]
            curr = degradation_profile[i]
            
            # Quality shouldn't drop too sharply
            quality_drop = prev["quality"] - curr["quality"]
            self.assertLess(quality_drop, 0.5, 
                           f"Quality dropped too sharply from {prev['level']} to {curr['level']}")
    
    def test_recovery_after_extended_failure(self):
        """Test recovery after extended period of failures"""
        phases = [
            {"name": "healthy", "duration": 5, "failure_rate": 0.1},
            {"name": "degraded", "duration": 5, "failure_rate": 0.5},
            {"name": "failing", "duration": 5, "failure_rate": 0.9},
            {"name": "recovery", "duration": 5, "failure_rate": 0.3},
            {"name": "restored", "duration": 5, "failure_rate": 0.1},
        ]
        
        phase_results = []
        
        for phase in phases:
            phase_data = {
                "name": phase["name"],
                "requests": [],
                "success_count": 0,
                "avg_recovery_time": 0
            }
            
            recovery_times = []
            
            for i in range(phase["duration"]):
                request_start = time.time()
                
                try:
                    response = self.chaos_query(
                        f"Request during {phase['name']} phase",
                        context={
                            "phase": phase["name"],
                            "failure_rate": phase["failure_rate"],
                            "request_num": i
                        },
                        max_retries=2
                    )
                    
                    request_time = time.time() - request_start
                    
                    success = response.get('type') != 'error'
                    phase_data["requests"].append({
                        "success": success,
                        "time": request_time
                    })
                    
                    if success:
                        phase_data["success_count"] += 1
                        if phase["name"] in ["recovery", "restored"]:
                            recovery_times.append(request_time)
                            
                except Exception:
                    phase_data["requests"].append({
                        "success": False,
                        "time": time.time() - request_start
                    })
            
            # Calculate recovery metrics
            if recovery_times:
                phase_data["avg_recovery_time"] = sum(recovery_times) / len(recovery_times)
                
            phase_results.append(phase_data)
        
        # Verify recovery pattern
        failing_success_rate = phase_results[2]["success_count"] / phase_results[2]["duration"]
        recovery_success_rate = phase_results[3]["success_count"] / phase_results[3]["duration"]
        restored_success_rate = phase_results[4]["success_count"] / phase_results[4]["duration"]
        
        # Should show improvement during recovery
        self.assertGreater(recovery_success_rate, failing_success_rate,
                          "No improvement during recovery phase")
        
        # Should be mostly restored by the end
        self.assertGreater(restored_success_rate, 0.7,
                          "System not adequately restored after recovery")
        
        # Recovery time should improve
        recovery_avg_time = phase_results[3]["avg_recovery_time"]
        restored_avg_time = phase_results[4]["avg_recovery_time"]
        
        if recovery_avg_time > 0 and restored_avg_time > 0:
            self.assertLess(restored_avg_time, recovery_avg_time * 1.5,
                           "Response time not improving during recovery")


if __name__ == "__main__":
    unittest.main()