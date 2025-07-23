#!/usr/bin/env python3
"""
Test Utilities - Helper functions for integration testing.

Provides setup, teardown, and verification utilities for testing
the automated development system.
"""

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import sys

# Add src to path
sys.path.append(str(Path(__file__).parent.parent.parent / 'src'))

from state_manager import StateManager


class TestEnvironment:
    """Manages test environment setup and teardown."""
    
    def __init__(self):
        """Initialize test environment."""
        self.test_dir = None
        self.original_cwd = os.getcwd()
        
    def setup(self, project_name: str = "test-project") -> Path:
        """
        Create test environment with git repo.
        
        Args:
            project_name: Name for test project
            
        Returns:
            Path to test directory
        """
        # Create temporary directory
        self.test_dir = tempfile.mkdtemp(prefix=f"claude_test_{project_name}_")
        
        # Initialize git repo
        subprocess.run(['git', 'init'], cwd=self.test_dir, 
                      capture_output=True, check=True)
        subprocess.run(['git', 'config', 'user.email', 'test@example.com'], 
                      cwd=self.test_dir, capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'Test User'], 
                      cwd=self.test_dir, capture_output=True)
        
        # Create initial commit
        readme_path = Path(self.test_dir) / 'README.md'
        readme_path.write_text(f'# {project_name}\n\nTest project for automation.')
        subprocess.run(['git', 'add', '.'], cwd=self.test_dir, capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'Initial commit'], 
                      cwd=self.test_dir, capture_output=True)
        
        return Path(self.test_dir)
        
    def teardown(self):
        """Clean up test environment."""
        if self.test_dir and os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
            
        # Return to original directory
        os.chdir(self.original_cwd)


def setup_test_environment(project_name: str = "test-project") -> Path:
    """
    Quick setup for test environment.
    
    Args:
        project_name: Name for test project
        
    Returns:
        Path to test directory
    """
    env = TestEnvironment()
    return env.setup(project_name)


def cleanup_test_environment(test_dir: Path):
    """
    Clean up test directory.
    
    Args:
        test_dir: Directory to remove
    """
    if test_dir.exists():
        shutil.rmtree(test_dir)


def verify_workflow_state(test_dir: Path, expected_step: str, 
                         expected_status: str) -> bool:
    """
    Verify current workflow state.
    
    Args:
        test_dir: Test directory
        expected_step: Expected workflow step
        expected_status: Expected project status
        
    Returns:
        True if state matches expectations
    """
    state_manager = StateManager(test_dir)
    
    try:
        state = state_manager.read()
        return (state.get('workflow_step') == expected_step and 
                state.get('status') == expected_status)
    except:
        return False


def verify_project_structure(test_dir: Path) -> Dict[str, bool]:
    """
    Verify project directory structure.
    
    Args:
        test_dir: Test directory
        
    Returns:
        Dict of directory_name -> exists
    """
    expected_dirs = ['sprints', '.claude', 'logs', 'docs']
    results = {}
    
    for dir_name in expected_dirs:
        dir_path = test_dir / dir_name
        results[dir_name] = dir_path.exists() and dir_path.is_dir()
        
    # Check for sprint files
    sprints_dir = test_dir / 'sprints'
    if sprints_dir.exists():
        sprint_files = list(sprints_dir.glob('*.md'))
        results['sprint_files'] = len(sprint_files) > 0
    else:
        results['sprint_files'] = False
        
    return results


def read_project_state(test_dir: Path) -> Optional[Dict[str, Any]]:
    """
    Read project state safely.
    
    Args:
        test_dir: Test directory
        
    Returns:
        State dict or None if not found
    """
    state_file = test_dir / '.project-state.json'
    if not state_file.exists():
        return None
        
    try:
        with open(state_file, 'r') as f:
            return json.load(f)
    except:
        return None


def update_project_state(test_dir: Path, updates: Dict[str, Any]) -> bool:
    """
    Update project state for testing.
    
    Args:
        test_dir: Test directory
        updates: Fields to update
        
    Returns:
        True if successful
    """
    try:
        state_manager = StateManager(test_dir)
        state_manager.update(updates)
        return True
    except:
        return False


def simulate_claude_action(test_dir: Path, action_type: str, 
                          **kwargs) -> Dict[str, Any]:
    """
    Simulate various Claude Code actions.
    
    Args:
        test_dir: Test directory
        action_type: Type of action ('write', 'read', 'bash', etc.)
        **kwargs: Action-specific parameters
        
    Returns:
        Simulated response
    """
    from command_executor import CommandExecutor
    executor = CommandExecutor(test_dir)
    
    if action_type == 'write':
        return executor.simulate_tool_use('Write', {
            'file_path': kwargs.get('file_path', 'test.py'),
            'content': kwargs.get('content', '# test code')
        })
    elif action_type == 'read':
        return executor.simulate_tool_use('Read', {
            'file_path': kwargs.get('file_path', 'README.md')
        })
    elif action_type == 'bash':
        return executor.simulate_tool_use('Bash', {
            'command': kwargs.get('command', 'echo "test"')
        })
    elif action_type == 'todo':
        return executor.simulate_tool_use('TodoWrite', {
            'todos': kwargs.get('todos', [
                {'id': '1', 'content': 'Test task', 'status': 'pending'}
            ])
        })
    else:
        return {"error": f"Unknown action type: {action_type}"}


def create_test_files(test_dir: Path, files: Dict[str, str]):
    """
    Create files for testing.
    
    Args:
        test_dir: Test directory
        files: Dict of filepath -> content
    """
    for filepath, content in files.items():
        full_path = test_dir / filepath
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content)


def run_command_and_capture(command: List[str], cwd: Path) -> Tuple[int, str, str]:
    """
    Run command and capture output.
    
    Args:
        command: Command to run
        cwd: Working directory
        
    Returns:
        Tuple of (exit_code, stdout, stderr)
    """
    result = subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        text=True
    )
    return result.returncode, result.stdout, result.stderr


def assert_hook_response(response: Dict[str, Any], expected_decision: str,
                        check_message: bool = True):
    """
    Assert hook response matches expectations.
    
    Args:
        response: Hook response dict
        expected_decision: Expected decision ('allow', 'block', etc.)
        check_message: Whether to check for message
        
    Raises:
        AssertionError if response doesn't match
    """
    assert response.get('decision') == expected_decision, \
        f"Expected decision '{expected_decision}' but got '{response.get('decision')}'"
        
    if check_message:
        # Check for either 'message' or 'reason' field
        has_message = 'message' in response or 'reason' in response
        assert has_message, "Expected message or reason in response"
        
        message = response.get('message') or response.get('reason', '')
        assert len(message) > 0, "Expected non-empty message"


def wait_for_state_change(test_dir: Path, field: str, expected_value: Any,
                         timeout: float = 5.0, interval: float = 0.1) -> bool:
    """
    Wait for state field to change to expected value.
    
    Args:
        test_dir: Test directory
        field: State field to check
        expected_value: Expected value
        timeout: Maximum wait time
        interval: Check interval
        
    Returns:
        True if value changed within timeout
    """
    import time
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        state = read_project_state(test_dir)
        if state and state.get(field) == expected_value:
            return True
        time.sleep(interval)
        
    return False