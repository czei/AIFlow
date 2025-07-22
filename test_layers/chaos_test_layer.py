#!/usr/bin/env python3
"""
Chaos test layer for test runner v2.
Runs chaos tests that validate system resilience with real AI and edge cases.
"""

import subprocess
import time
from pathlib import Path
from typing import List
import json
import sys
import os
import random

# Import from parent module
try:
    from test_runner_v2 import TestLayer, TestContext, TestResult
except ImportError:
    # If direct import fails, try adding parent to path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from test_runner_v2 import TestLayer, TestContext, TestResult


class ChaosTestLayer(TestLayer):
    """Layer for running chaos and resilience tests with real AI"""
    
    def discover_tests(self, context: TestContext) -> List[str]:
        """Discover chaos test files"""
        patterns = context.config.get('patterns', ['**/test_*_chaos.py'])
        tests = []
        
        # Look in tests/chaos directory
        chaos_dir = context.project_root / "tests" / "chaos"
        if chaos_dir.exists():
            for pattern in patterns:
                # Handle both absolute and relative patterns
                if pattern.startswith("**/"):
                    # Recursive pattern
                    for test_file in chaos_dir.rglob(pattern[3:]):
                        if test_file.is_file() and test_file.suffix == '.py':
                            rel_path = test_file.relative_to(context.project_root)
                            tests.append(str(rel_path))
                else:
                    # Direct pattern
                    for test_file in chaos_dir.glob(pattern):
                        if test_file.is_file() and test_file.suffix == '.py':
                            rel_path = test_file.relative_to(context.project_root)
                            tests.append(str(rel_path))
        
        # Also check for chaos tests in other locations
        for pattern in patterns:
            for test_file in context.project_root.glob(pattern):
                # Skip if already found in chaos dir
                if str(test_file.relative_to(context.project_root)) in tests:
                    continue
                    
                # Skip unit/integration/contract tests
                if any(layer in test_file.parts for layer in ['unit', 'integration', 'contracts']):
                    continue
                    
                # Must contain 'chaos' in name
                if 'chaos' in test_file.name.lower():
                    rel_path = test_file.relative_to(context.project_root)
                    tests.append(str(rel_path))
                    
        return sorted(set(tests))  # Remove duplicates
    
    def run_test(self, test_path: str, context: TestContext) -> TestResult:
        """Run a chaos test file"""
        start_time = time.time()
        test_file = context.project_root / test_path
        
        # Convert path to module name
        module_path = test_file.relative_to(context.project_root)
        module_name = str(module_path).replace('/', '.').replace('\\', '.')[:-3]  # Remove .py
        
        try:
            # Set up environment for chaos tests
            env = {
                **os.environ.copy(),
                'CHAOS_TEST': '1',
                'USE_REAL_AI': context.config.get('use_real_ai', True) and '1' or '0',
                'SIMULATE_FAILURES': context.config.get('simulate_failures', True) and '1' or '0',
                'CHAOS_SEED': str(context.config.get('chaos_seed', random.randint(1, 10000)))
            }
            
            # Add API keys if configured
            if context.config.get('api_key'):
                env['CLAUDE_API_KEY'] = context.config['api_key']
            
            # Configure chaos parameters
            chaos_config = context.config.get('chaos_config', {})
            if chaos_config.get('network_latency'):
                env['CHAOS_NETWORK_LATENCY'] = str(chaos_config['network_latency'])
            if chaos_config.get('failure_rate'):
                env['CHAOS_FAILURE_RATE'] = str(chaos_config['failure_rate'])
            if chaos_config.get('timeout_probability'):
                env['CHAOS_TIMEOUT_PROB'] = str(chaos_config['timeout_probability'])
            
            # Run chaos test with unittest
            cmd = [
                sys.executable, '-m', 'unittest',
                module_name,
                '-v'
            ]
            
            # Chaos tests may have longer timeouts
            timeout = context.config.get('chaos_timeout', context.timeout * 2)
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(context.project_root),
                env=env,
                input=""  # Prevent hanging on interactive prompts
            )
            
            duration = time.time() - start_time
            
            # Parse unittest output
            success = result.returncode == 0
            output = result.stdout + ("\n" + result.stderr if result.stderr else "")
            
            # Extract test statistics
            test_count = 0
            failures = 0
            errors = 0
            resilience_score = 0
            
            for line in output.splitlines():
                if line.startswith("Ran "):
                    # "Ran X tests in Y.YYYs"
                    parts = line.split()
                    if len(parts) >= 2:
                        test_count = int(parts[1])
                elif "FAILED" in line:
                    # "FAILED (failures=X, errors=Y)"
                    import re
                    failures_match = re.search(r'failures=(\d+)', line)
                    errors_match = re.search(r'errors=(\d+)', line)
                    if failures_match:
                        failures = int(failures_match.group(1))
                    if errors_match:
                        errors = int(errors_match.group(1))
                elif "Resilience score:" in line:
                    # Extract resilience metrics
                    score_match = re.search(r'Resilience score: (\d+(?:\.\d+)?)', line)
                    if score_match:
                        resilience_score = float(score_match.group(1))
                        
            metadata = {
                'exit_code': result.returncode,
                'test_file': str(test_file),
                'module_name': module_name,
                'layer': 'chaos',
                'test_count': test_count,
                'failures': failures,
                'errors': errors,
                'uses_real_ai': env.get('USE_REAL_AI') == '1',
                'chaos_seed': env.get('CHAOS_SEED'),
                'resilience_score': resilience_score,
                'duration_seconds': duration
            }
            
            # Mark as success if resilience score is acceptable
            if resilience_score > 0:
                threshold = context.config.get('resilience_threshold', 0.7)
                if resilience_score >= threshold:
                    success = True
                    metadata['passed_resilience_check'] = True
                
            return TestResult(
                name=test_path,
                success=success,
                duration=f"{duration:.2f}s",
                error=output,
                metadata=metadata
            )
            
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            return TestResult(
                name=test_path,
                success=False,
                duration=f"{duration:.2f}s",
                error=f"Chaos test timed out after {timeout} seconds",
                metadata={'layer': 'chaos', 'timeout': True}
            )
            
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                name=test_path,
                success=False,
                duration=f"{duration:.2f}s",
                error=f"Error running chaos test: {str(e)}",
                metadata={'layer': 'chaos', 'error': str(e)}
            )