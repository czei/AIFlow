#!/usr/bin/env python3
"""
Base class for chaos testing.
Provides utilities for testing system resilience with unpredictable AI responses.
"""

import unittest
import time
import random
import os
import sys
import json
import threading
from typing import Dict, Any, Optional, Callable, List
from contextlib import contextmanager
from pathlib import Path

# Add parent directories to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import AI providers
from src.ai_providers.claude_provider import ClaudeProvider
from mocks.mock_claude_provider import MockClaudeProvider


class ChaosTestBase(unittest.TestCase):
    """Base class for all chaos tests"""
    
    # Initialize class-level metrics to ensure they always exist
    total_attempts = 0
    successful_recoveries = 0
    failed_recoveries = 0
    timeouts = 0
    errors = {}
    
    @classmethod
    def setUpClass(cls):
        """Set up class-level resources"""
        # Initialize chaos parameters
        cls.chaos_seed = int(os.getenv('CHAOS_SEED', random.randint(1, 10000)))
        random.seed(cls.chaos_seed)
        
        # Configure failure simulation
        cls.simulate_failures = os.getenv('SIMULATE_FAILURES', '1') == '1'
        cls.network_latency = float(os.getenv('CHAOS_NETWORK_LATENCY', '0.5'))
        cls.failure_rate = float(os.getenv('CHAOS_FAILURE_RATE', '0.1'))
        cls.timeout_probability = float(os.getenv('CHAOS_TIMEOUT_PROB', '0.05'))
        
        # Initialize AI provider
        cls.ai_provider = cls._initialize_chaos_provider()
        
        # Track resilience metrics
        cls.total_attempts = 0
        cls.successful_recoveries = 0
        cls.failed_recoveries = 0
        cls.timeouts = 0
        cls.errors = {}
        
    @classmethod
    def _initialize_chaos_provider(cls):
        """Initialize AI provider with chaos wrapper"""
        use_real_ai = os.getenv('USE_REAL_AI', '1') == '1'
        
        if use_real_ai:
            api_key = os.getenv('CLAUDE_API_KEY')
            if api_key:
                base_provider = ClaudeProvider(api_key=api_key)
            else:
                print("Warning: No API key, using mock provider")
                base_provider = MockClaudeProvider()
        else:
            base_provider = MockClaudeProvider()
            
        # Wrap provider with chaos functionality
        return ChaosAIProvider(base_provider, cls)
    
    def setUp(self):
        """Set up test-specific resources"""
        self.start_time = time.time()
        self.test_errors = []
        self.recovery_attempts = []
        
    def chaos_query(self, prompt: str, context: Optional[Dict[str, Any]] = None,
                   max_retries: int = 3, timeout: float = 30.0) -> Dict[str, Any]:
        """
        Query AI with chaos injection and retry logic.
        
        Args:
            prompt: The prompt to send
            context: Optional context
            max_retries: Maximum retry attempts
            timeout: Timeout in seconds
            
        Returns:
            AI response or error response
        """
        ChaosTestBase.total_attempts += 1
        
        for attempt in range(max_retries):
            try:
                # Add chaos context
                chaos_context = {
                    **(context or {}),
                    '_chaos_attempt': attempt,
                    '_chaos_seed': self.chaos_seed
                }
                
                # Set timeout
                response = self._query_with_timeout(
                    prompt, chaos_context, timeout
                )
                
                # Validate response
                if self._is_valid_response(response):
                    if attempt > 0:
                        ChaosTestBase.successful_recoveries += 1
                        self.recovery_attempts.append({
                            'attempt': attempt,
                            'success': True,
                            'prompt': prompt[:50]
                        })
                    return response
                    
            except TimeoutError:
                ChaosTestBase.timeouts += 1
                self.test_errors.append({
                    'type': 'timeout',
                    'attempt': attempt,
                    'prompt': prompt[:50]
                })
                
            except Exception as e:
                error_type = type(e).__name__
                ChaosTestBase.errors[error_type] = ChaosTestBase.errors.get(error_type, 0) + 1
                self.test_errors.append({
                    'type': error_type,
                    'message': str(e),
                    'attempt': attempt
                })
                
            # Exponential backoff
            if attempt < max_retries - 1:
                backoff = (2 ** attempt) * random.uniform(0.5, 1.5)
                time.sleep(backoff)
                
        # All retries failed
        ChaosTestBase.failed_recoveries += 1
        return {
            'type': 'error',
            'error': 'All retry attempts failed',
            'attempts': max_retries,
            'errors': self.test_errors[-max_retries:]
        }
    
    def _query_with_timeout(self, prompt: str, context: Dict[str, Any], 
                           timeout: float) -> Dict[str, Any]:
        """Query with timeout enforcement"""
        result = {'response': None, 'error': None}
        
        def query_thread():
            try:
                result['response'] = self.ai_provider.query(prompt, context)
            except Exception as e:
                result['error'] = e
                
        thread = threading.Thread(target=query_thread)
        thread.daemon = True
        thread.start()
        thread.join(timeout)
        
        if thread.is_alive():
            raise TimeoutError(f"Query timed out after {timeout} seconds")
            
        if result['error']:
            raise result['error']
            
        return result['response']
    
    def _is_valid_response(self, response: Any) -> bool:
        """Check if response is valid"""
        if not isinstance(response, dict):
            return False
        if response.get('type') == 'error':
            return False
        if not response:
            return False
        return True
    
    @contextmanager
    def simulate_network_issues(self, latency_range=(0.1, 2.0), 
                               packet_loss=0.1):
        """Context manager to simulate network issues"""
        original_latency = self.network_latency
        self.network_latency = random.uniform(*latency_range)
        
        # Simulate packet loss
        if random.random() < packet_loss:
            raise ConnectionError("Simulated packet loss")
            
        try:
            yield
        finally:
            self.network_latency = original_latency
    
    def assert_resilient(self, operation: Callable, min_success_rate: float = 0.7):
        """
        Assert that an operation is resilient to failures.
        
        Args:
            operation: Function to test
            min_success_rate: Minimum required success rate
        """
        successes = 0
        attempts = 10
        
        for _ in range(attempts):
            try:
                result = operation()
                if result and not isinstance(result, dict) or result.get('type') != 'error':
                    successes += 1
            except Exception:
                pass
                
        success_rate = successes / attempts
        self.assertGreaterEqual(
            success_rate, min_success_rate,
            f"Operation not resilient enough: {success_rate:.2f} < {min_success_rate}"
        )
    
    def inject_malformed_response(self, probability: float = 0.2):
        """Inject malformed responses with given probability"""
        if random.random() < probability:
            malformed_types = [
                None,  # Null response
                "",    # Empty string
                [],    # List instead of dict
                {"incomplete": True},  # Missing required fields
                {"type": "💥🔥🎭"},   # Unicode chaos
                {"nested": {"too": {"deep": {"for": {"parsing": {}}}}}},
                "Just a string",  # String instead of dict
            ]
            return random.choice(malformed_types)
        return None
    
    @classmethod
    def get_resilience_score(cls) -> float:
        """Calculate overall resilience score"""
        if cls.total_attempts == 0:
            return 1.0
            
        recovery_rate = cls.successful_recoveries / max(1, cls.successful_recoveries + cls.failed_recoveries)
        timeout_rate = 1 - (cls.timeouts / cls.total_attempts)
        error_diversity = 1 - (len(cls.errors) / 10)  # Penalize many error types
        
        # Weighted score
        score = (
            recovery_rate * 0.5 +
            timeout_rate * 0.3 +
            error_diversity * 0.2
        )
        
        return max(0, min(1, score))
    
    def tearDown(self):
        """Clean up after test"""
        duration = time.time() - self.start_time
        
        # Log test metrics
        if self.test_errors:
            print(f"\nTest errors encountered: {len(self.test_errors)}")
            for error in self.test_errors[:5]:  # Show first 5
                print(f"  - {error.get('type', 'unknown_error')}: {error.get('message', 'No message')}")
                
        if self.recovery_attempts:
            successful = sum(1 for r in self.recovery_attempts if r['success'])
            print(f"Recovery attempts: {successful}/{len(self.recovery_attempts)} successful")
    
    @classmethod
    def tearDownClass(cls):
        """Clean up class resources and print summary"""
        score = cls.get_resilience_score()
        print(f"\n{'='*60}")
        print(f"CHAOS TEST SUMMARY")
        print(f"{'='*60}")
        print(f"Chaos seed: {cls.chaos_seed}")
        print(f"Total attempts: {cls.total_attempts}")
        print(f"Successful recoveries: {cls.successful_recoveries}")
        print(f"Failed recoveries: {cls.failed_recoveries}")
        print(f"Timeouts: {cls.timeouts}")
        print(f"Error types encountered: {len(cls.errors)}")
        for error_type, count in cls.errors.items():
            print(f"  - {error_type}: {count}")
        print(f"Resilience score: {score:.2%}")
        print(f"{'='*60}\n")


class ChaosAIProvider:
    """Wrapper that adds chaos to AI provider"""
    
    def __init__(self, base_provider, chaos_config):
        self.base_provider = base_provider
        self.chaos_config = chaos_config
        
    def query(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Query with chaos injection"""
        # Simulate network latency
        if self.chaos_config.network_latency > 0:
            time.sleep(random.uniform(0, self.chaos_config.network_latency))
            
        # Simulate failures
        if self.chaos_config.simulate_failures:
            if random.random() < self.chaos_config.failure_rate:
                failure_types = [
                    ConnectionError("Connection refused"),
                    TimeoutError("Request timeout"),
                    ValueError("Invalid response format"),
                    RuntimeError("Internal server error"),
                    json.JSONDecodeError("Invalid JSON", "", 0)
                ]
                raise random.choice(failure_types)
                
            # Simulate timeout
            if random.random() < self.chaos_config.timeout_probability:
                time.sleep(35)  # Exceed typical timeout
                
        # Get base response
        response = self.base_provider.query(prompt, context)
        
        # Inject response mutations
        if self.chaos_config.simulate_failures and random.random() < 0.1:
            mutations = [
                # Truncate response
                lambda r: {**r, 'response': r.get('response', '')[:10]},
                # Add unexpected fields
                lambda r: {**r, 'chaos_injected': True, 'warnings': ['Chaos test']},
                # Change response type
                lambda r: {**r, 'type': 'chaos_' + r.get('type', 'unknown')},
                # Duplicate fields
                lambda r: {**r, 'response': r.get('response', '') * 2},
                # Remove required fields (25% chance)
                lambda r: {k: v for k, v in r.items() if k != 'type'} if random.random() < 0.25 else r
            ]
            mutation = random.choice(mutations)
            response = mutation(response)
            
        return response