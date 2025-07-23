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
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
import importlib.util
import inspect

# Add src to path for config import
sys.path.insert(0, str(Path(__file__).parent / "src"))
try:
    from config import (
        DEFAULT_TEST_TIMEOUT, DEFAULT_TEST_PATTERNS, DEFAULT_TEST_RESULTS_DIR,
        DEFAULT_PLUGIN_DIR, DEFAULT_CONFIG_FILE, UNIT_TEST_TIMEOUT, 
        INTEGRATION_TEST_TIMEOUT, CONTRACT_TEST_TIMEOUT, CHAOS_TEST_TIMEOUT
    )
except ImportError:
    # Fallback to hardcoded values if config not available
    DEFAULT_TEST_TIMEOUT = 300
    DEFAULT_TEST_PATTERNS = {"shell": ["**/*.sh"]}
    DEFAULT_TEST_RESULTS_DIR = "test_results"
    DEFAULT_PLUGIN_DIR = "test_layers"
    DEFAULT_CONFIG_FILE = "test_config.yaml"


@dataclass
class TestResult:
    """Represents the result of a single test execution"""
    name: str
    success: bool
    duration: str  # String format like "1.23s"
    error: str = ""
    metadata: Dict[str, Any] = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc).isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'name': self.name,
            'success': self.success,
            'duration': self.duration,
            'timestamp': self.timestamp,
            'metadata': self.metadata,
            'error': self.error
        }


@dataclass
class TestContext:
    """Shared context passed between test layers"""
    project_root: Path
    timeout: int = 300
    config: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.config is None:
            self.config = {}


class TestLayer(ABC):
    """Base class for all test layers in the 4-layer architecture"""
    
    @abstractmethod
    def discover_tests(self, context: TestContext) -> List[str]:
        """Discover tests for this layer"""
        pass
    
    @abstractmethod
    def run_test(self, test_path: str, context: TestContext) -> TestResult:
        """Run a single test and return result"""
        pass


class ShellTestLayer(TestLayer):
    """Layer for running shell script tests with all code review fixes applied"""
    
    def discover_tests(self, context: TestContext) -> List[str]:
        """Auto-discover shell scripts instead of hardcoding (fixes LOW priority issue)"""
        patterns = context.config.get('patterns', ['**/*.sh'])
        
        discovered_tests = []
        for pattern in patterns:
            for test_file in context.project_root.glob(pattern):
                # Skip non-test scripts
                name = test_file.name.lower()
                if any(skip in name for skip in ['install', 'setup', 'build', 'deploy', 'config']):
                    continue
                    
                # Only include scripts that look like tests
                if not any(test_pattern in name for test_pattern in ['test', 'check', 'verify']):
                    continue
                
                # Get relative path for cleaner output
                rel_path = test_file.relative_to(context.project_root)
                discovered_tests.append(str(rel_path))
        
        return sorted(discovered_tests)
    
    def _validate_path(self, path: Path, base_path: Path) -> Path:
        """Validate that path is within base_path to prevent traversal attacks"""
        try:
            # Resolve to absolute paths
            resolved_path = path.resolve()
            resolved_base = base_path.resolve()
            
            # Check if the resolved path is within the base path
            resolved_path.relative_to(resolved_base)
            return resolved_path
        except (ValueError, RuntimeError):
            raise ValueError(f"Path '{path}' is outside project root")
    
    def run_test(self, test_path: str, context: TestContext) -> TestResult:
        """Run shell test with all fixes from code review"""
        script_path = Path(test_path)
        
        if not script_path.is_absolute():
            script_path = context.project_root / script_path
        
        # Validate path to prevent traversal attacks
        try:
            script_path = self._validate_path(script_path, context.project_root)
        except ValueError as e:
            return TestResult(
                name=test_path,
                success=False,
                duration="0.00s",
                error=str(e)
            )
            
        if not script_path.exists():
            return TestResult(
                name=test_path,
                success=False,
                duration="0.00s",
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
                name=test_path,
                success=(result.returncode == 0),
                duration=f"{duration:.2f}s",
                error=result.stdout + ("\n" + result.stderr if result.stderr else ""),
                metadata={
                    "exit_code": result.returncode,
                    "script_path": str(script_path),
                    "layer": "shell"
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
                name=test_path,
                success=False,
                duration=f"{duration:.2f}s",
                error=f"Test timed out after {context.timeout} seconds",
                metadata={"layer": "shell"}
            )
            print(f"\n⏱️  TIMEOUT - {script_path.name} ({context.timeout}s)")
            
        except PermissionError:
            # FIX: Handle permission errors with helpful message (MEDIUM priority fix)
            duration = time.time() - start_time
            test_result = TestResult(
                name=test_path,
                success=False,
                duration=f"{duration:.2f}s",
                error=f"Script not executable. Please run: chmod +x {script_path}",
                metadata={"layer": "shell"}
            )
            print(f"\n🚨 PERMISSION ERROR - {script_path.name}")
            print(f"Fix with: chmod +x {script_path}")
            
        except Exception as e:
            duration = time.time() - start_time
            test_result = TestResult(
                name=test_path,
                success=False,
                duration=f"{duration:.2f}s",
                error=f"Unexpected error: {str(e)}",
                metadata={"layer": "shell"}
            )
            print(f"\n🚨 ERROR - {script_path.name}: {str(e)}")
        
        return test_result


class TestLayerRegistry:
    """Manages test layer plugins"""
    
    def __init__(self):
        self._layers: Dict[str, TestLayer] = {}
    
    def register(self, name: str, layer: TestLayer):
        """Register a test layer"""
        self._layers[name] = layer
    
    def get(self, name: str) -> Optional[TestLayer]:
        """Get a specific layer by name"""
        return self._layers.get(name)
    
    def list(self) -> List[str]:
        """List all registered layers"""
        return list(self._layers.keys())
    
    def load_plugins(self, plugin_dir: Path):
        """Dynamically load test layer plugins from directory"""
        if not plugin_dir.exists():
            print(f"Plugin directory does not exist: {plugin_dir}")
            return
            
        print(f"Loading plugins from: {plugin_dir}")
        sys.path.insert(0, str(plugin_dir.parent))
        
        for plugin_file in plugin_dir.glob("*_layer.py"):
            print(f"Found plugin file: {plugin_file}")
            try:
                # Load the module
                spec = importlib.util.spec_from_file_location(
                    plugin_file.stem, plugin_file
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Find TestLayer subclasses
                print(f"Module members: {[name for name, obj in inspect.getmembers(module) if inspect.isclass(obj)]}")
                print(f"Module name: {module.__name__}")
                for name, obj in inspect.getmembers(module):
                    # Look for classes ending with TestLayer that are defined in this module
                    if (inspect.isclass(obj) and 
                        name.endswith('TestLayer') and
                        hasattr(obj, '__module__') and
                        obj.__module__ == module.__name__):
                        print(f"Found TestLayer class: {name}")
                        # Create instance and register
                        try:
                            instance = obj()
                            # Derive layer name from class name
                            layer_name = name.lower().replace("testlayer", "")
                            if layer_name == "shell":  # Skip built-in shell layer
                                continue
                            self.register(layer_name, instance)
                            print(f"Loaded plugin: {layer_name} from {plugin_file.name}")
                        except Exception as e:
                            print(f"Failed to instantiate {name}: {e}")
                        
            except Exception as e:
                print(f"Failed to load plugin {plugin_file}: {e}")
                import traceback
                traceback.print_exc()


class TestRunner:
    """Main test orchestrator using plugin architecture"""
    
    def __init__(self, project_root: str = ".", config_path: Optional[str] = None):
        self.project_root = Path(project_root).resolve()
        self.results_dir = self.project_root / DEFAULT_TEST_RESULTS_DIR
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.registry = TestLayerRegistry()
        self.config = self._load_config(config_path)
        self._register_layers()
        
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""
        if config_path:
            config_file = Path(config_path).resolve()
            # Validate config path is accessible
            if not config_file.exists():
                print(f"Warning: Config file not found: {config_file}")
                return self._get_default_config()
        else:
            config_file = self.project_root / DEFAULT_CONFIG_FILE
            
        if config_file.exists():
            with open(config_file, 'r') as f:
                return yaml.safe_load(f) or {}
        
        # Default configuration
        return {
            "test_layers": {
                "shell": {
                    "enabled": True,
                    "timeout": DEFAULT_TEST_TIMEOUT,
                    "patterns": DEFAULT_TEST_PATTERNS.get("shell", ["**/*.sh"])
                },
                "unit": {
                    "enabled": True,
                    "timeout": UNIT_TEST_TIMEOUT,
                    "patterns": DEFAULT_TEST_PATTERNS.get("unit", ["**/test_*.py", "**/*_test.py"])
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
        # Register built-in shell layer
        self.registry.register("shell", ShellTestLayer())
        
        # Load plugins from test_layers directory
        plugin_dir = self.project_root / DEFAULT_PLUGIN_DIR
        if plugin_dir.exists() and plugin_dir.is_dir():
            self.registry.load_plugins(plugin_dir)
        else:
            print(f"Warning: Plugin directory not found: {plugin_dir}")
    
    def _run_layer(self, layer_name: str, layer: TestLayer) -> List[TestResult]:
        """Run all tests for a specific layer"""
        layer_config = self.config.get("test_layers", {}).get(layer_name, {})
        
        if not layer_config.get("enabled", False):
            print(f"\nSkipping disabled layer: {layer_name}")
            return []
        
        print(f"\n\n{'='*60}")
        print(f"Running {layer_name} tests")
        print(f"{'='*60}")
        
        # Create context with layer-specific config
        context = TestContext(
            project_root=self.project_root,
            timeout=layer_config.get("timeout", 300),
            config=layer_config
        )
        
        # Discover tests
        tests = layer.discover_tests(context)
        if not tests:
            print(f"No {layer_name} tests found")
            return []
        
        print(f"Found {len(tests)} {layer_name} test(s)")
        
        # Log test ownership for debugging
        if os.getenv('DEBUG_TEST_OWNERSHIP', '0') == '1':
            print(f"  Tests discovered by {layer_name} layer:")
            for test in tests[:5]:  # Show first 5
                print(f"    - {test}")
            if len(tests) > 5:
                print(f"    ... and {len(tests) - 5} more")
        
        # Run tests
        results = []
        for test_path in tests:
            result = layer.run_test(test_path, context)
            results.append(result)
            
        return results
    
    def run(self):
        """Run all enabled test layers"""
        print("🧪 AI Software Project Management - Test Runner v2")
        print("Extensible test framework with plugin architecture")
        print(f"Starting test execution at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        print(f"\nAvailable layers: {self.registry.list()}")
        
        all_results = []
        
        # Run each layer
        for layer_name in self.registry.list():
            layer = self.registry.get(layer_name)
            if layer:
                results = self._run_layer(layer_name, layer)
                all_results.extend(results)
        
        # Save results
        if all_results:
            self._save_results(all_results)
        
        # Return exit code
        failed = sum(1 for r in all_results if not r.success)
        return 0 if failed == 0 else 1
    
    def _save_results(self, results: List[TestResult]):
        """Save test results to JSON report"""
        # Calculate summary
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.success)
        failed_tests = total_tests - passed_tests
        
        # Parse durations and sum
        total_duration = 0.0
        for r in results:
            try:
                # Extract numeric part from duration string like "1.23s"
                duration_str = r.duration.rstrip('s')
                total_duration += float(duration_str)
            except:
                pass
        
        # Group by layer
        by_layer = {}
        for result in results:
            layer = result.metadata.get('layer', 'unknown')
            if layer not in by_layer:
                by_layer[layer] = {"total": 0, "passed": 0, "failed": 0}
            by_layer[layer]["total"] += 1
            if result.success:
                by_layer[layer]["passed"] += 1
            else:
                by_layer[layer]["failed"] += 1
        
        # Create report
        report = {
            "summary": {
                "total": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "success_rate": f"{(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%",
                "total_duration": f"{total_duration:.2f}s",
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            "by_layer": by_layer,
            "results": [r.to_dict() for r in results]
        }
        
        # Save to file
        report_path = self.results_dir / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print(f"\n\n{'='*60}")
        print("TEST SUMMARY")
        print(f"{'='*60}")
        print(f"Total Tests: {total_tests}")
        print(f"Passed:      {passed_tests} ✅")
        print(f"Failed:      {failed_tests} ❌")
        print(f"Success Rate: {report['summary']['success_rate']}")
        print(f"Total Time:   {total_duration:.2f}s")
        
        if by_layer:
            print(f"\nBy Layer:")
            for layer, stats in by_layer.items():
                print(f"  {layer}: {stats['passed']}/{stats['total']} passed")
        
        if failed_tests > 0:
            print("\nFailed Tests:")
            for result in results:
                if not result.success:
                    print(f"  ❌ {result.name}")
                    if result.error:
                        # Print first line of error
                        error_lines = result.error.strip().split('\n')
                        if error_lines:
                            print(f"     {error_lines[0]}")
        
        print(f"\nDetailed report saved to: {report_path}")
        print(f"{'='*60}")


def main():
    """Main entry point"""
    runner = TestRunner()
    exit_code = runner.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()