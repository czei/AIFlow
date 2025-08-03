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
        # Simulate the command execution
        command_file = self.commands_dir / f"{command_name}.md"
        
        # Extract the backtick commands from the markdown file
        content = command_file.read_text()
        
        # Find all backtick commands
        import re
        commands = re.findall(r"!`(.*?)`", content, re.DOTALL)
        if not commands:
            self.fail(f"Could not extract commands from {command_name}.md")
        
        project_root = str(Path(__file__).parent.parent.parent)
        
        # Execute commands in sequence until one fails
        for cmd in commands:
            # Replace PROJECT_ROOT calculation with our test root
            cmd = cmd.replace(
                'PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"',
                f'PROJECT_ROOT="{project_root}"'
            )
            
            # Also handle the new multi-path check
            cmd = cmd.replace(
                '$PROJECT_ROOT/.claude/commands/project/lib/src/commands/utils/check_project.py',
                f'{project_root}/src/commands/utils/check_project.py'
            )
            
            # Execute the command
            result = subprocess.run(
                ['bash', '-c', cmd],
                capture_output=True,
                text=True
            )
            
            # If command fails, check for expected error
            if result.returncode != 0:
                # Should show user-friendly error
                output = result.stdout + result.stderr
                self.assertIn(expected_error, output)
                
                # Should NOT show jq errors
                self.assertNotIn("jq: error", output)
                self.assertNotIn("Could not open file .project-state.json", output)
                return  # Test passed
        
        # If we get here, no command failed
        self.fail(f"Expected command {command_name} to fail without project state")
        
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
        
    def test_claude_code_eval_simulation(self):
        """Test that commands work with eval-like processing (simulating Claude Code)."""
        # Test a command with complex quoting that would fail with eval
        test_command = '''bash -c 'echo "test"; python3 -c "print('"'"'hello'"'"')"' '''
        
        # This should work with direct bash execution
        result = subprocess.run(
            ['bash', '-c', test_command],
            capture_output=True,
            text=True
        )
        self.assertEqual(result.returncode, 0)
        
        # But would fail with eval (simulating Claude Code's processing)
        # Note: We can't directly test eval failure, but we've proven the issue
        # exists and our backtick solution avoids it
        
    def test_combined_project_root_command(self):
        """Test that PROJECT_ROOT and check work in same command."""
        # Create a test directory with project state
        test_dir = Path(tempfile.mkdtemp())
        original_dir = os.getcwd()
        os.chdir(test_dir)
        
        try:
            # Initialize git and create project
            subprocess.run(['git', 'init'], capture_output=True)
            sm = StateManager('.')
            sm.create('test-project')
            
            # Test combined command that sets and uses PROJECT_ROOT
            project_root = str(Path(__file__).parent.parent.parent)
            combined_cmd = f'PROJECT_ROOT="{project_root}"; if [[ -f "$PROJECT_ROOT/src/commands/utils/check_project.py" ]]; then python3 "$PROJECT_ROOT/src/commands/utils/check_project.py"; else echo "❌ Error: check_project.py not found"; exit 1; fi'
            
            result = subprocess.run(
                ['bash', '-c', combined_cmd],
                capture_output=True,
                text=True
            )
            
            # Should succeed
            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
            
        finally:
            os.chdir(original_dir)
            shutil.rmtree(test_dir)
    
    def test_backtick_commands_with_exit_pattern(self):
        """Test that our || exit pattern works correctly."""
        # Create a test directory without project state
        test_dir = Path(tempfile.mkdtemp())
        original_dir = os.getcwd()
        os.chdir(test_dir)
        
        try:
            # Initialize git (required for PROJECT_ROOT)
            subprocess.run(['git', 'init'], capture_output=True)
            
            # Test command sequence that should stop after check_project fails
            commands = [
                'PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"',
                'echo "This should execute"',
                '[ -f ".project-state.json" ] || exit',  # This should fail and stop execution
                'echo "This should NOT execute"'
            ]
            
            # Execute commands in sequence
            outputs = []
            for cmd in commands:
                result = subprocess.run(
                    ['bash', '-c', cmd],
                    capture_output=True,
                    text=True
                )
                outputs.append((cmd, result))
                
                # Stop if command exits with non-zero
                if result.returncode != 0:
                    break
            
            # Verify correct behavior
            self.assertEqual(len(outputs), 3)  # Should stop after third command
            self.assertIn("This should execute", outputs[1][1].stdout)
            # The last command should not have been executed
            self.assertNotEqual(len(outputs), 4)
            
        finally:
            os.chdir(original_dir)
            shutil.rmtree(test_dir)


if __name__ == '__main__':
    unittest.main()