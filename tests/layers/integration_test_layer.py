#!/usr/bin/env python3
"""
Integration test layer for test runner v2.
Runs integration tests with MockClaudeProvider.
"""

import subprocess
import time
from pathlib import Path
from typing import List
import json
import sys

# Import from parent module
try:
    from tests.runners.test_runner_v2 import TestLayer, TestContext, TestResult
except ImportError:
    # If direct import fails, try adding parent to path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from tests.runners.test_runner_v2 import TestLayer, TestContext, TestResult


class IntegrationTestLayer(TestLayer):
    """Layer for running integration tests with mock AI provider"""
    
    def discover_tests(self, context: TestContext) -> List[str]:
        """Discover integration test files"""
        patterns = context.config.get('patterns', ['**/test_*integration*.py'])
        tests = []
        
        # Look in tests/integration directory
        integration_dir = context.project_root / "tests" / "integration"
        if integration_dir.exists():
            for pattern in patterns:
                # Handle both absolute and relative patterns
                if pattern.startswith("**/"):
                    # Recursive pattern
                    for test_file in integration_dir.rglob(pattern[3:]):
                        if test_file.is_file() and test_file.suffix == '.py':
                            rel_path = test_file.relative_to(context.project_root)
                            tests.append(str(rel_path))
                else:
                    # Direct pattern
                    for test_file in integration_dir.glob(pattern):
                        if test_file.is_file() and test_file.suffix == '.py':
                            rel_path = test_file.relative_to(context.project_root)
                            tests.append(str(rel_path))
        
        # Also check for integration tests in other locations
        for pattern in patterns:
            for test_file in context.project_root.glob(pattern):
                # Skip if already found in integration dir
                if str(test_file.relative_to(context.project_root)) in tests:
                    continue
                    
                # Skip unit tests
                if 'unit' in test_file.parts:
                    continue
                    
                # Must contain 'integration' in name
                if 'integration' in test_file.name.lower():
                    rel_path = test_file.relative_to(context.project_root)
                    tests.append(str(rel_path))
                    
        return sorted(set(tests))  # Remove duplicates
    
    def run_test(self, test_path: str, context: TestContext) -> TestResult:
        """Run an integration test file"""
        start_time = time.time()
        test_file = context.project_root / test_path
        
        # Convert path to module name
        module_path = test_file.relative_to(context.project_root)
        module_name = str(module_path).replace('/', '.').replace('\\', '.')[:-3]  # Remove .py
        
        try:
            # Set up environment for integration tests
            env = {
                **subprocess.os.environ,
                'INTEGRATION_TEST': '1',
                'MOCK_CLAUDE_PROVIDER': '1'
            }
            
            # Run integration test with unittest
            cmd = [
                sys.executable, '-m', 'unittest',
                module_name,
                '-v'
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=context.timeout,
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
                        
            metadata = {
                'exit_code': result.returncode,
                'test_file': str(test_file),
                'module_name': module_name,
                'layer': 'integration',
                'test_count': test_count,
                'failures': failures,
                'errors': errors,
                'uses_mock_provider': True
            }
            
            # Check if MockClaudeProvider was actually used
            if 'MockClaudeProvider' in output:
                metadata['mock_provider_active'] = True
                
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
                error=f"Integration test timed out after {context.timeout} seconds",
                metadata={'layer': 'integration', 'timeout': True}
            )
            
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                name=test_path,
                success=False,
                duration=f"{duration:.2f}s",
                error=f"Error running integration test: {str(e)}",
                metadata={'layer': 'integration', 'error': str(e)}
            )