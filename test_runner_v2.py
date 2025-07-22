#!/usr/bin/env python3
"""
Test Runner v2 - Extensible test framework with plugin architecture.
Implements all code review fixes and provides foundation for 4-layer testing.
"""

import subprocess
import json
import sys
import time
import yaml
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple


class TestResult:
    """Represents the result of a single test execution"""
    def __init__(self, name: str, success: bool, duration: float, 
                 output: str = "", error: str = "", metadata: Dict = None):
        self.name = name
        self.success = success
        self.duration = duration
        self.output = output
        self.error = error
        self.metadata = metadata or {}
        self.timestamp = datetime.now(timezone.utc).isoformat()


@dataclass
class TestContext:
    """Shared context passed between test layers"""
    project_root: Path
    config: Dict[str, Any]
    results_dir: Path
    timeout: int = 300
    previous_results: List[TestResult] = None
    
    def __post_init__(self):
        if self.previous_results is None:
            self.previous_results = []


class TestLayer(ABC):
    """Base class for all test layers in the 4-layer architecture"""
    
    @abstractmethod
    def name(self) -> str:
        """Return the name of this test layer"""
        pass
    
    @abstractmethod
    def discover_tests(self, context: TestContext) -> List[str]:
        """Discover tests for this layer"""
        pass
    
    @abstractmethod
    def run_test(self, test_path: str, context: TestContext) -> TestResult:
        """Run a single test and return result"""
        pass
    
    def is_enabled(self, context: TestContext) -> bool:
        """Check if this layer is enabled in configuration"""
        layer_config = context.config.get('test_layers', {}).get(self.name(), {})
        return layer_config.get('enabled', True)


class ShellTestLayer(TestLayer):
    """Layer for running shell script tests with all code review fixes applied"""
    
    def name(self) -> str:
        return "shell"
    
    def discover_tests(self, context: TestContext) -> List[str]:
        """Auto-discover shell scripts instead of hardcoding (fixes LOW priority issue)"""
        test_dir = context.project_root / "tests"
        patterns = context.config.get('test_layers', {}).get('shell', {}).get('patterns', ['**/*.sh'])
        
        discovered_tests = []
        for pattern in patterns:
            discovered_tests.extend(str(p) for p in sorted(test_dir.glob(pattern)))
        
        return discovered_tests
    
    def run_test(self, test_path: str, context: TestContext) -> TestResult:
        """Run shell test with all fixes from code review"""
        script_path = Path(test_path)
        
        if not script_path.exists():
            return TestResult(
                name=str(script_path),
                success=False,
                duration=0.0,
                error=f"Script not found: {script_path}"
            )
        
        print(f"\n{'='*60}")
        print(f"Running: {script_path.name}")
        print(f"{'='*60}")
        
        start_time = time.time()
        try:
            # FIX: Add input="" to handle interactive tests (HIGH priority fix)
            # FIX: Remove chmod - let it fail properly (MEDIUM priority fix)
            result = subprocess.run(
                [str(script_path.absolute())],
                capture_output=True,
                text=True,
                timeout=context.timeout,
                cwd=str(context.project_root),
                input=""  # Prevents hanging on interactive prompts
            )
            
            duration = time.time() - start_time
            
            test_result = TestResult(
                name=script_path.name,
                success=(result.returncode == 0),
                duration=duration,
                output=result.stdout,
                error=result.stderr,
                metadata={
                    "exit_code": result.returncode,
                    "script_path": str(script_path),
                    "layer": self.name()
                }
            )
            
            # Print summary
            status = "✅ PASSED" if test_result.success else "❌ FAILED"
            print(f"\n{status} - {script_path.name} ({duration:.2f}s)")
            
            if result.stderr and not test_result.success:
                print(f"\nErrors:\n{result.stderr}")
                
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            test_result = TestResult(
                name=script_path.name,
                success=False,
                duration=duration,
                error=f"Test timed out after {context.timeout} seconds"
            )
            print(f"\n⏱️  TIMEOUT - {script_path.name} ({context.timeout}s)")
            
        except PermissionError:
            # FIX: Handle permission errors with helpful message (MEDIUM priority fix)
            duration = time.time() - start_time
            test_result = TestResult(
                name=script_path.name,
                success=False,
                duration=duration,
                error=f"Script not executable. Please run: chmod +x {script_path}"
            )
            print(f"\n🚨 PERMISSION ERROR - {script_path.name}")
            print(f"Fix with: chmod +x {script_path}")
            
        except Exception as e:
            duration = time.time() - start_time
            test_result = TestResult(
                name=script_path.name,
                success=False,
                duration=duration,
                error=f"Unexpected error: {str(e)}"
            )
            print(f"\n🚨 ERROR - {script_path.name}: {str(e)}")
        
        return test_result


class UnitTestLayer(TestLayer):
    """Layer 1: Unit tests for deterministic components (placeholder)"""
    
    def name(self) -> str:
        return "unit"
    
    def discover_tests(self, context: TestContext) -> List[str]:
        """Discover Python unit tests"""
        # TODO: Implement pytest discovery
        return []
    
    def run_test(self, test_path: str, context: TestContext) -> TestResult:
        """Run Python unit test"""
        # TODO: Implement pytest runner
        return TestResult(
            name=test_path,
            success=True,
            duration=0.0,
            output="Unit test layer not yet implemented"
        )


class MockAITestLayer(TestLayer):
    """Layer 2: Integration tests with MockClaudeProvider (placeholder)"""
    
    def name(self) -> str:
        return "integration"
    
    def discover_tests(self, context: TestContext) -> List[str]:
        return []
    
    def run_test(self, test_path: str, context: TestContext) -> TestResult:
        return TestResult(
            name=test_path,
            success=True,
            duration=0.0,
            output="Mock AI test layer not yet implemented"
        )


class ContractTestLayer(TestLayer):
    """Layer 3: Contract-based AI testing (placeholder)"""
    
    def name(self) -> str:
        return "contract"
    
    def discover_tests(self, context: TestContext) -> List[str]:
        return []
    
    def run_test(self, test_path: str, context: TestContext) -> TestResult:
        return TestResult(
            name=test_path,
            success=True,
            duration=0.0,
            output="Contract test layer not yet implemented"
        )


class ChaosTestLayer(TestLayer):
    """Layer 4: Chaos and real AI validation tests (placeholder)"""
    
    def name(self) -> str:
        return "chaos"
    
    def discover_tests(self, context: TestContext) -> List[str]:
        return []
    
    def run_test(self, test_path: str, context: TestContext) -> TestResult:
        return TestResult(
            name=test_path,
            success=True,
            duration=0.0,
            output="Chaos test layer not yet implemented"
        )


class TestLayerRegistry:
    """Manages test layer plugins"""
    
    def __init__(self):
        self._layers: Dict[str, TestLayer] = {}
    
    def register(self, layer: TestLayer):
        """Register a test layer"""
        self._layers[layer.name()] = layer
    
    def get_layer(self, name: str) -> Optional[TestLayer]:
        """Get a specific layer by name"""
        return self._layers.get(name)
    
    def get_enabled_layers(self, context: TestContext) -> List[TestLayer]:
        """Get all enabled layers"""
        return [layer for layer in self._layers.values() if layer.is_enabled(context)]
    
    def discover_all_tests(self, context: TestContext) -> List[Tuple[TestLayer, str]]:
        """Discover tests from all enabled layers"""
        all_tests = []
        for layer in self.get_enabled_layers(context):
            for test_path in layer.discover_tests(context):
                all_tests.append((layer, test_path))
        return all_tests


class TestRunner:
    """Main test orchestrator using plugin architecture (MEDIUM priority fix)"""
    
    def __init__(self, config_path: Optional[str] = None, results_dir: str = "test_results"):
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True)
        self.results: List[TestResult] = []
        self.registry = TestLayerRegistry()
        self.config = self._load_config(config_path)
        self._register_layers()
        
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        
        # Default configuration
        return {
            "test_layers": {
                "shell": {
                    "enabled": True,
                    "timeout": 300,
                    "patterns": ["**/*.sh"]
                },
                "unit": {
                    "enabled": False  # Not implemented yet
                },
                "integration": {
                    "enabled": False  # Layer 2
                },
                "contract": {
                    "enabled": False  # Layer 3
                },
                "chaos": {
                    "enabled": False  # Layer 4
                }
            }
        }
    
    def _register_layers(self):
        """Register all available test layers"""
        self.registry.register(ShellTestLayer())
        self.registry.register(UnitTestLayer())
        self.registry.register(MockAITestLayer())
        self.registry.register(ContractTestLayer())
        self.registry.register(ChaosTestLayer())
    
    def run_all_tests(self):
        """Run all discovered tests from all enabled layers"""
        context = TestContext(
            project_root=Path.cwd(),
            config=self.config,
            results_dir=self.results_dir,
            timeout=self.config.get('timeout', 300)
        )
        
        # Discover all tests
        all_tests = self.registry.discover_all_tests(context)
        
        if not all_tests:
            print("No tests found!")
            return
        
        print(f"\nDiscovered {len(all_tests)} tests across {len(self.registry.get_enabled_layers(context))} layers")
        
        # Run all tests
        for layer, test_path in all_tests:
            result = layer.run_test(test_path, context)
            self.results.append(result)
            context.previous_results.append(result)
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate a comprehensive test report"""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.success)
        failed_tests = total_tests - passed_tests
        total_duration = sum(r.duration for r in self.results)
        
        # Group results by layer
        by_layer = {}
        for result in self.results:
            layer = result.metadata.get('layer', 'unknown')
            if layer not in by_layer:
                by_layer[layer] = []
            by_layer[layer].append(result)
        
        report = {
            "summary": {
                "total": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "success_rate": f"{(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%",
                "total_duration": f"{total_duration:.2f}s",
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            "by_layer": {
                layer: {
                    "total": len(results),
                    "passed": sum(1 for r in results if r.success),
                    "failed": sum(1 for r in results if not r.success)
                }
                for layer, results in by_layer.items()
            },
            "results": [
                {
                    "name": r.name,
                    "success": r.success,
                    "duration": f"{r.duration:.2f}s",
                    "timestamp": r.timestamp,
                    "metadata": r.metadata,
                    "error": r.error if r.error else None
                }
                for r in self.results
            ]
        }
        
        # Save report to file
        report_path = self.results_dir / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def print_summary(self):
        """Print a summary of test results"""
        report = self.generate_report()
        summary = report["summary"]
        
        print(f"\n{'='*60}")
        print("TEST SUMMARY")
        print(f"{'='*60}")
        print(f"Total Tests: {summary['total']}")
        print(f"Passed:      {summary['passed']} ✅")
        print(f"Failed:      {summary['failed']} ❌")
        print(f"Success Rate: {summary['success_rate']}")
        print(f"Total Time:   {summary['total_duration']}")
        
        # Show results by layer
        if report["by_layer"]:
            print(f"\nBy Layer:")
            for layer, stats in report["by_layer"].items():
                print(f"  {layer}: {stats['passed']}/{stats['total']} passed")
        
        print(f"{'='*60}")
        
        if summary['failed'] > 0:
            print("\nFailed Tests:")
            for result in self.results:
                if not result.success:
                    print(f"  ❌ {result.name}: {result.error}")
        
        print(f"\nDetailed report saved to: {self.results_dir}/")


def main():
    """Main entry point for test runner v2"""
    print("🧪 AI Software Project Management - Test Runner v2")
    print("Extensible test framework with plugin architecture")
    print(f"Starting test execution at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Look for config file
    config_path = "test_config.yaml" if Path("test_config.yaml").exists() else None
    
    # Create and run test runner
    runner = TestRunner(config_path=config_path)
    runner.run_all_tests()
    runner.print_summary()
    
    # Exit with appropriate code
    report = runner.generate_report()
    sys.exit(0 if report["summary"]["failed"] == 0 else 1)


if __name__ == "__main__":
    main()