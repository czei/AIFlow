#!/usr/bin/env python3
"""
Unit tests for test runner v2 components.
Tests plugin architecture, test discovery, and result aggregation.
"""

import unittest
from unittest.mock import patch, MagicMock, mock_open
import json
import yaml
from pathlib import Path
from datetime import datetime
import sys
import os
import subprocess

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from test_runner_v2 import (
    TestContext, TestResult, TestLayer, ShellTestLayer,
    TestLayerRegistry, TestRunner
)


class TestTestContext(unittest.TestCase):
    """Test TestContext dataclass"""
    
    def test_context_initialization(self):
        """Test TestContext initializes correctly"""
        context = TestContext(
            project_root=Path("/test/project"),
            timeout=300,
            config={'key': 'value'}
        )
        
        self.assertEqual(context.project_root, Path("/test/project"))
        self.assertEqual(context.timeout, 300)
        self.assertEqual(context.config, {'key': 'value'})
        
    def test_context_defaults(self):
        """Test TestContext default values"""
        context = TestContext(project_root=Path("/test"))
        
        self.assertEqual(context.timeout, 300)
        self.assertEqual(context.config, {})


class TestTestResult(unittest.TestCase):
    """Test TestResult dataclass"""
    
    def test_result_initialization(self):
        """Test TestResult initializes correctly"""
        result = TestResult(
            name="test.sh",
            success=True,
            duration="1.23s",
            error="",
            metadata={'exit_code': 0}
        )
        
        self.assertEqual(result.name, "test.sh")
        self.assertTrue(result.success)
        self.assertEqual(result.duration, "1.23s")
        self.assertEqual(result.error, "")
        self.assertEqual(result.metadata, {'exit_code': 0})
        
    def test_result_to_dict(self):
        """Test TestResult.to_dict method"""
        result = TestResult(
            name="test.sh",
            success=False,
            duration="2.5s",
            error="Test failed",
            metadata={'exit_code': 1}
        )
        
        result_dict = result.to_dict()
        
        self.assertEqual(result_dict['name'], "test.sh")
        self.assertFalse(result_dict['success'])
        self.assertEqual(result_dict['duration'], "2.5s")
        self.assertEqual(result_dict['error'], "Test failed")
        self.assertEqual(result_dict['metadata'], {'exit_code': 1})
        self.assertIn('timestamp', result_dict)


class TestShellTestLayer(unittest.TestCase):
    """Test ShellTestLayer implementation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.layer = ShellTestLayer()
        self.context = TestContext(
            project_root=Path("/test/project"),
            config={'patterns': ['**/*.sh']}
        )
        
    @patch('test_runner_v2.Path.glob')
    def test_discover_tests(self, mock_glob):
        """Test test discovery"""
        # Mock glob results
        mock_glob.return_value = [
            Path("/test/project/test1.sh"),
            Path("/test/project/tests/test2.sh")
        ]
        
        tests = self.layer.discover_tests(self.context)
        
        self.assertEqual(len(tests), 2)
        self.assertIn("test1.sh", tests)
        self.assertIn("tests/test2.sh", tests)
        
    @patch('test_runner_v2.Path.glob')
    def test_discover_tests_multiple_patterns(self, mock_glob):
        """Test discovery with multiple patterns"""
        context = TestContext(
            project_root=Path("/test/project"),
            config={'patterns': ['*.sh', 'tests/*.py']}
        )
        
        # Mock different results for each pattern
        mock_glob.side_effect = [
            [Path("/test/project/test.sh")],
            [Path("/test/project/tests/test.py")]
        ]
        
        tests = self.layer.discover_tests(context)
        
        self.assertEqual(len(tests), 2)
        self.assertIn("test.sh", tests)
        self.assertIn("tests/test.py", tests)
        
    @patch('test_runner_v2.Path.exists')
    @patch('test_runner_v2.subprocess.run')
    def test_run_test_success(self, mock_run, mock_exists):
        """Test successful test execution"""
        # Mock file exists
        mock_exists.return_value = True
        
        # Mock successful subprocess result
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Test passed"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        result = self.layer.run_test("test.sh", self.context)
        
        self.assertTrue(result.success)
        self.assertEqual(result.name, "test.sh")
        self.assertEqual(result.metadata['exit_code'], 0)
        self.assertIn("Test passed", result.error)  # stdout/stderr go to error field
        
        # Verify subprocess call
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        self.assertTrue(call_args[0].endswith("test.sh"))
        
    @patch('test_runner_v2.Path.exists')
    @patch('test_runner_v2.subprocess.run')
    def test_run_test_failure(self, mock_run, mock_exists):
        """Test failed test execution"""
        # Mock file exists
        mock_exists.return_value = True
        
        # Mock failed subprocess result
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Test failed"
        mock_run.return_value = mock_result
        
        result = self.layer.run_test("test.sh", self.context)
        
        self.assertFalse(result.success)
        self.assertEqual(result.metadata['exit_code'], 1)
        self.assertIn("Test failed", result.error)
        
    @patch('test_runner_v2.Path.exists')
    @patch('test_runner_v2.subprocess.run')
    def test_run_test_timeout(self, mock_run, mock_exists):
        """Test test execution timeout"""
        # Mock file exists
        mock_exists.return_value = True
        
        mock_run.side_effect = subprocess.TimeoutExpired('cmd', 300)
        
        result = self.layer.run_test("test.sh", self.context)
        
        self.assertFalse(result.success)
        self.assertIn("Test timed out", result.error)
        
    @patch('test_runner_v2.Path.exists')
    @patch('test_runner_v2.subprocess.run')
    def test_run_test_permission_error(self, mock_run, mock_exists):
        """Test permission error handling"""
        # Mock file exists
        mock_exists.return_value = True
        
        mock_run.side_effect = PermissionError("Permission denied")
        
        result = self.layer.run_test("test.sh", self.context)
        
        self.assertFalse(result.success)
        self.assertIn("Script not executable", result.error)
        self.assertIn("chmod +x", result.error)
        
    @patch('test_runner_v2.Path.exists')
    @patch('test_runner_v2.subprocess.run')
    def test_run_test_with_input(self, mock_run, mock_exists):
        """Test that input="" is passed to prevent hangs"""
        # Mock file exists
        mock_exists.return_value = True
        
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        self.layer.run_test("test.sh", self.context)
        
        # Verify input parameter
        mock_run.assert_called_once()
        call_kwargs = mock_run.call_args[1]
        self.assertEqual(call_kwargs['input'], "")


class TestTestLayerRegistry(unittest.TestCase):
    """Test TestLayerRegistry functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.registry = TestLayerRegistry()
        
    def test_register_layer(self):
        """Test layer registration"""
        layer = ShellTestLayer()
        self.registry.register("test", layer)
        
        self.assertIn("test", self.registry._layers)
        self.assertEqual(self.registry._layers["test"], layer)
        
    def test_get_layer(self):
        """Test getting registered layer"""
        layer = ShellTestLayer()
        self.registry.register("test", layer)
        
        retrieved = self.registry.get("test")
        self.assertEqual(retrieved, layer)
        
    def test_get_nonexistent_layer(self):
        """Test getting non-existent layer returns None"""
        result = self.registry.get("nonexistent")
        self.assertIsNone(result)
        
    def test_list_layers(self):
        """Test listing all layers"""
        layer1 = ShellTestLayer()
        layer2 = ShellTestLayer()
        
        self.registry.register("layer1", layer1)
        self.registry.register("layer2", layer2)
        
        layers = self.registry.list()
        self.assertEqual(set(layers), {"layer1", "layer2"})


class TestTestRunner(unittest.TestCase):
    """Test TestRunner main class"""
    
    @patch('test_runner_v2.Path.mkdir')
    def setUp(self, mock_mkdir):
        """Set up test fixtures"""
        self.runner = TestRunner(project_root="/test/project")
        
    @patch('test_runner_v2.Path.mkdir')
    def test_initialization(self, mock_mkdir):
        """Test runner initialization"""
        runner = TestRunner(project_root="/test/project")
        
        self.assertEqual(runner.project_root, Path("/test/project"))
        self.assertEqual(runner.results_dir, Path("/test/project/test_results"))
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        
        # Verify shell layer is registered
        shell_layer = runner.registry.get("shell")
        self.assertIsInstance(shell_layer, ShellTestLayer)
        
    @patch('test_runner_v2.yaml.safe_load')
    @patch('builtins.open', new_callable=mock_open)
    @patch('test_runner_v2.Path.exists')
    @patch('test_runner_v2.Path.mkdir')
    def test_load_config_success(self, mock_mkdir, mock_exists, mock_file, mock_yaml_load):
        """Test successful config loading"""
        mock_exists.return_value = True
        mock_config = {
            'test_layers': {
                'shell': {'enabled': True, 'timeout': 600}
            }
        }
        mock_yaml_load.return_value = mock_config
        
        # Create a new runner instance with mocked exists
        runner = TestRunner(project_root="/test/project")
        config = runner._load_config(None)
        
        self.assertEqual(config, mock_config)
        
    @patch('builtins.open', side_effect=FileNotFoundError)
    def test_load_config_missing(self, mock_file):
        """Test config loading with missing file"""
        config = self.runner._load_config(None)
        
        # Should return default config
        self.assertIn('test_layers', config)
        self.assertIn('shell', config['test_layers'])
        self.assertTrue(config['test_layers']['shell']['enabled'])
        
    def test_run_layer_disabled(self):
        """Test running disabled layer"""
        layer = ShellTestLayer()
        self.runner.registry.register("test", layer)
        
        # Mock config with disabled layer
        self.runner.config = {
            'test_layers': {
                'test': {'enabled': False}
            }
        }
        
        results = self.runner._run_layer("test", layer)
        
        self.assertEqual(results, [])
        
    @patch('test_runner_v2.ShellTestLayer.discover_tests')
    @patch('test_runner_v2.ShellTestLayer.run_test')
    def test_run_layer_success(self, mock_run_test, mock_discover):
        """Test running enabled layer"""
        # Set up mocks
        mock_discover.return_value = ["test1.sh", "test2.sh"]
        mock_run_test.side_effect = [
            TestResult("test1.sh", True, "1s", "", {}),
            TestResult("test2.sh", False, "2s", "Failed", {})
        ]
        
        layer = self.runner.registry.get("shell")
        results = self.runner._run_layer("shell", layer)
        
        self.assertEqual(len(results), 2)
        self.assertTrue(results[0].success)
        self.assertFalse(results[1].success)
        
    @patch('builtins.open', new_callable=mock_open)
    @patch('test_runner_v2.datetime')
    def test_save_results(self, mock_datetime, mock_file):
        """Test saving results to JSON"""
        # Mock datetime.now instead of utcnow
        mock_now = MagicMock()
        mock_now.isoformat.return_value = "2025-01-01T00:00:00"
        mock_now.strftime.return_value = "20250101_000000"
        mock_datetime.now.return_value = mock_now
        
        results = [
            TestResult("test1.sh", True, "1s", "", {"layer": "shell"}),
            TestResult("test2.sh", False, "2s", "Failed", {"layer": "shell"})
        ]
        
        self.runner._save_results(results)
        
        # Verify file was written
        mock_file.assert_called()
        # Get all write calls
        write_calls = [call[0][0] for call in mock_file.return_value.write.call_args_list if call[0]]
        # Find the JSON write
        # Instead of parsing write calls, mock json.dump
        with patch('test_runner_v2.json.dump') as mock_json_dump:
            # Call again to capture json.dump
            self.runner._save_results(results)
            self.assertTrue(mock_json_dump.called)
            report = mock_json_dump.call_args[0][0]
        
        # Verify report structure
        self.assertEqual(report['summary']['total'], 2)
        self.assertEqual(report['summary']['passed'], 1)
        self.assertEqual(report['summary']['failed'], 1)
        self.assertEqual(report['summary']['success_rate'], "50.0%")
        self.assertEqual(len(report['results']), 2)
        
    def test_calculate_summary(self):
        """Test summary calculation from results"""
        results = [
            TestResult("test1.sh", True, "1.5s", "", {"layer": "shell"}),
            TestResult("test2.sh", False, "2.3s", "Failed", {"layer": "shell"}),
            TestResult("test3.py", True, "0.5s", "", {"layer": "python"})
        ]
        
        # Access private method for testing
        summary = self.runner._save_results.__code__.co_consts
        
        # Test by calling save_results and checking output
        with patch('builtins.open', mock_open()) as mock_file:
            with patch('test_runner_v2.json.dump') as mock_json_dump:
                self.runner._save_results(results)
                # Get the report from json.dump call
                self.assertTrue(mock_json_dump.called)
                report = mock_json_dump.call_args[0][0]
            
            # Verify summary calculations
            self.assertEqual(report['summary']['total'], 3)
            self.assertEqual(report['summary']['passed'], 2)
            self.assertEqual(report['summary']['failed'], 1)
            self.assertEqual(report['summary']['success_rate'], "66.7%")
            self.assertEqual(report['summary']['total_duration'], "4.30s")
            
            # Verify by_layer summary
            self.assertEqual(report['by_layer']['shell']['total'], 2)
            self.assertEqual(report['by_layer']['shell']['passed'], 1)
            self.assertEqual(report['by_layer']['python']['total'], 1)
            self.assertEqual(report['by_layer']['python']['passed'], 1)


if __name__ == '__main__':
    unittest.main()