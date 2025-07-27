#!/usr/bin/env python3
"""
Unit test layer for test runner v2.
Discovers and runs Python unit tests using unittest framework.
"""

import subprocess
import time
from pathlib import Path
from typing import List
import json
import sys
import re

# Import from parent module
try:
    from tests.runners.test_runner_v2 import TestLayer, TestContext, TestResult
except ImportError:
    # If direct import fails, try adding parent to path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from tests.runners.test_runner_v2 import TestLayer, TestContext, TestResult


class UnitTestLayer(TestLayer):
    """Layer for running Python unit tests"""
    
    def discover_tests(self, context: TestContext) -> List[str]:
        """Discover Python unit test files"""
        patterns = context.config.get('patterns', ['**/test_*.py', '**/*_test.py'])
        tests = []
        
        for pattern in patterns:
            for test_file in context.project_root.glob(pattern):
                # Skip __pycache__ directories
                if '__pycache__' in test_file.parts:
                    continue
                
                # Skip non-test files that happen to match pattern
                if test_file.name in ['test_runner.py', 'test_runner_v2.py', 'test_runner_v2_old.py']:
                    continue
                    
                # Skip non-unit tests (integration, chaos, contracts)
                if any(layer in test_file.parts for layer in ['integration', 'chaos', 'contracts']):
                    continue
                    
                # Skip files with specific suffixes that indicate non-unit tests
                if any(test_file.name.endswith(suffix) for suffix in ['_chaos.py', '_contract.py', '_integration.py']):
                    continue
                    
                # Get relative path for cleaner names
                rel_path = test_file.relative_to(context.project_root)
                tests.append(str(rel_path))
                
        return sorted(tests)
    
    def run_test(self, test_path: str, context: TestContext) -> TestResult:
        """Run a Python unit test file"""
        start_time = time.time()
        test_file = context.project_root / test_path
        
        # Convert path to module name
        module_path = test_file.relative_to(context.project_root)
        module_name = str(module_path).replace('/', '.').replace('\\', '.')[:-3]  # Remove .py
        
        try:
            # Check if this is a pytest-based test (hook tests and some others use pytest)
            if any(keyword in test_path for keyword in ['hook', 'subprocess', 'focused', 'workflow_rules', 'event_validator']):
                # Run with pytest for hook tests
                cmd = [
                    sys.executable, '-m', 'pytest',
                    str(test_file),
                    '-v'  # Verbose output
                ]
            else:
                # Run unittest for standard tests
                cmd = [
                    sys.executable, '-m', 'unittest',
                    module_name,
                    '-v'  # Verbose output
                ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=context.timeout,
                cwd=str(context.project_root),
                input=""  # Prevent hanging on interactive prompts
            )
            
            duration = time.time() - start_time
            
            # Parse output based on test runner
            success = result.returncode == 0
            output = result.stdout + ("\n" + result.stderr if result.stderr else "")
            
            # Extract test counts from output
            test_count = 0
            failures = 0
            errors = 0
            
            if 'pytest' in cmd[2]:
                # Parse pytest output
                for line in output.splitlines():
                    # Look for pytest summary line like "====== 16 passed in 1.38s ======"
                    if 'passed' in line and '=' in line:
                        match = re.search(r'(\d+)\s+passed', line)
                        if match:
                            test_count = int(match.group(1))
                    elif 'failed' in line and '=' in line:
                        match = re.search(r'(\d+)\s+failed', line)
                        if match:
                            failures = int(match.group(1))
                    elif line.startswith('collected'):
                        # "collected 16 items"
                        match = re.search(r'collected\s+(\d+)', line)
                        if match:
                            test_count = int(match.group(1))
            else:
                # Parse unittest output
                for line in output.splitlines():
                    if line.startswith("Ran "):
                        # "Ran X tests in Y.YYYs"
                        parts = line.split()
                        if len(parts) >= 2:
                            test_count = int(parts[1])
                    elif "FAILED" in line:
                        # "FAILED (failures=X, errors=Y)"
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
                'layer': 'unit',
                'test_count': test_count,
                'failures': failures,
                'errors': errors
            }
            
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
                error=f"Test timed out after {context.timeout} seconds",
                metadata={'layer': 'unit', 'timeout': True}
            )
            
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                name=test_path,
                success=False,
                duration=f"{duration:.2f}s",
                error=f"Error running test: {str(e)}",
                metadata={'layer': 'unit', 'error': str(e)}
            )