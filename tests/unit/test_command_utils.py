#!/usr/bin/env python3
"""
Unit tests for command utilities.

Tests the check_project.py utility and related command helpers.
"""

import unittest
import tempfile
import shutil
import subprocess
import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.state_manager import StateManager, StateValidationError


class TestCheckProjectUtility(unittest.TestCase):
    """Test check_project.py utility functionality."""
    
    def setUp(self):
        """Set up test environment with temporary directory."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)
        
        # Path to check_project.py
        self.check_project_script = Path(__file__).parent.parent.parent / "src" / "commands" / "utils" / "check_project.py"
        
    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)
        
    def test_check_project_no_state_file(self):
        """Test check_project.py when no project state exists."""
        # Run check_project.py
        result = subprocess.run(
            [sys.executable, str(self.check_project_script)],
            capture_output=True,
            text=True
        )
        
        # Should exit with code 1
        self.assertEqual(result.returncode, 1)
        
        # Should show error message
        self.assertIn("❌ Error: No project found in current directory", result.stdout)
        self.assertIn("To start a project, use: /user:project:start", result.stdout)
        
    def test_check_project_with_valid_state(self):
        """Test check_project.py when valid project state exists."""
        # Create a valid project state
        sm = StateManager('.')
        sm.create('test-project')
        
        # Run check_project.py
        result = subprocess.run(
            [sys.executable, str(self.check_project_script)],
            capture_output=True,
            text=True
        )
        
        # Should exit with code 0
        self.assertEqual(result.returncode, 0)
        
        # Should not output anything
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "")
        
    def test_check_project_with_invalid_json(self):
        """Test check_project.py when project state has invalid JSON."""
        # Create invalid JSON file
        with open('.project-state.json', 'w') as f:
            f.write('{"invalid": json content')
        
        # Run check_project.py
        result = subprocess.run(
            [sys.executable, str(self.check_project_script)],
            capture_output=True,
            text=True
        )
        
        # Should exit with code 1
        self.assertEqual(result.returncode, 1)
        
        # Should show error message
        self.assertIn("❌ Error:", result.stdout)
        
    def test_check_project_import_error_handling(self):
        """Test check_project.py handles import errors gracefully."""
        # Create a modified version of check_project that will fail to import
        test_script = self.test_dir / "test_check_project.py"
        
        # Read the original script and modify it to simulate import failure
        original_content = self.check_project_script.read_text()
        
        # Replace the successful import with one that will fail
        modified_content = original_content.replace(
            "from state_manager import StateManager, StateValidationError",
            "from nonexistent_module import StateManager, StateValidationError"
        ).replace(
            "from src.state_manager import StateManager, StateValidationError",
            "from nonexistent_module import StateManager, StateValidationError"
        )
        
        test_script.write_text(modified_content)
        
        # Run the modified script
        result = subprocess.run(
            [sys.executable, str(test_script)],
            capture_output=True,
            text=True
        )
        
        # Should exit with code 1
        self.assertEqual(result.returncode, 1)
        
        # Should show import error message
        self.assertIn("❌ Error: Unable to import StateManager", result.stdout)


class TestCommandErrorHandling(unittest.TestCase):
    """Test error handling in commands when project state is missing."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)
        
        # Initialize git repo (required for PROJECT_ROOT detection)
        subprocess.run(['git', 'init'], capture_output=True)
        
        # Path to commands
        self.commands_dir = Path(__file__).parent.parent.parent / "src" / "commands"
        
    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)
        
    def _test_command_without_project(self, command_name, expected_error):
        """Helper to test a command without project state."""
        # Simulate the command execution using bash
        command_file = self.commands_dir / f"{command_name}.md"
        
        # Extract the bash command from the markdown file
        content = command_file.read_text()
        
        # Find the bash -c block (handle multi-line)
        import re
        match = re.search(r"!`bash -c '(.*?)'`", content, re.DOTALL)
        if not match:
            self.fail(f"Could not extract bash command from {command_name}.md")
            
        bash_command = match.group(1)
        
        # Replace PROJECT_ROOT calculation with our test root
        project_root = str(Path(__file__).parent.parent.parent)
        bash_command = bash_command.replace(
            'PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"',
            f'PROJECT_ROOT="{project_root}"'
        )
        
        # Execute the command
        result = subprocess.run(
            ['bash', '-c', bash_command],
            capture_output=True,
            text=True
        )
        
        # Should exit with non-zero code
        self.assertNotEqual(result.returncode, 0)
        
        # Should show user-friendly error
        self.assertIn(expected_error, result.stdout + result.stderr)
        
        # Should NOT show jq errors
        self.assertNotIn("jq: error", result.stdout + result.stderr)
        self.assertNotIn("Could not open file .project-state.json", result.stdout + result.stderr)
        
    def test_status_command_without_project(self):
        """Test status command without project state."""
        self._test_command_without_project("status", "No project found in current directory")
        
    def test_pause_command_without_project(self):
        """Test pause command without project state."""
        self._test_command_without_project("pause", "No project found in current directory")
        
    def test_resume_command_without_project(self):
        """Test resume command without project state."""
        self._test_command_without_project("resume", "No project found in current directory")
        
    def test_stop_command_without_project(self):
        """Test stop command without project state."""
        self._test_command_without_project("stop", "No project found in current directory")


if __name__ == '__main__':
    unittest.main()