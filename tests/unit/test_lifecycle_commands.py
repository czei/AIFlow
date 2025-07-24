"""
Unit tests for LifecycleCommand class.

Tests project lifecycle management including start, pause, resume, and stop
operations with comprehensive state validation and error handling.
"""

import unittest
import tempfile
import shutil
import json
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.commands.lifecycle import LifecycleCommand, LifecycleCommandError
from src.state_manager import StateValidationError


class TestLifecycleCommand(unittest.TestCase):
    """Test LifecycleCommand functionality."""
    
    def setUp(self):
        """Set up test environment with temporary directory."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.project_path = self.test_dir / "test-project"
        self.project_path.mkdir()
        
        # Create basic project structure
        (self.project_path / "sprints").mkdir()
        (self.project_path / ".claude").mkdir()
        (self.project_path / "logs").mkdir()
        (self.project_path / "docs").mkdir()
        
        # Create required files
        (self.project_path / "CLAUDE.md").write_text("# Test Project")
        (self.project_path / ".project-state.json").write_text('{"project_name": "test"}')
        
        # Create sprint files
        sprints_dir = self.project_path / "sprints"
        for sprint in ["01-planning.md", "02-architecture.md", "03-implementation.md"]:
            (sprints_dir / sprint).write_text(f"# {sprint}")
            
        # Create Claude settings
        settings = {
            "version": "1.0.0",
            "project_name": "test-project",
            "automation_enabled": False
        }
        (self.project_path / ".claude" / "settings.json").write_text(json.dumps(settings))
        
        # Mock StateManager and GitOperations
        self.state_manager_patcher = patch('src.commands.lifecycle.StateManager')
        self.git_ops_patcher = patch('src.commands.lifecycle.GitOperations')
        
        self.mock_state_manager_class = self.state_manager_patcher.start()
        self.mock_git_ops_class = self.git_ops_patcher.start()
        
        # Create mock instances
        self.mock_state_manager = Mock()
        self.mock_git_ops = Mock()
        self.mock_state_manager_class.return_value = self.mock_state_manager
        self.mock_git_ops_class.return_value = self.mock_git_ops
        
    def tearDown(self):
        """Clean up test environment."""
        self.state_manager_patcher.stop()
        self.git_ops_patcher.stop()
        shutil.rmtree(self.test_dir)
        
    def test_init_success(self):
        """Test successful LifecycleCommand initialization."""
        cmd = LifecycleCommand(str(self.project_path))
        self.assertEqual(cmd.project_path, self.project_path.resolve())
        
    def test_init_git_operations_fail(self):
        """Test initialization when git operations fail."""
        from src.git_operations import GitOperationError
        self.mock_git_ops_class.side_effect = GitOperationError("Not a git repo")
        
        cmd = LifecycleCommand(str(self.project_path))
        self.assertIsNone(cmd.git_ops)
        
    def test_start_success(self):
        """Test successful project start."""
        # Mock state for setup status
        setup_state = {
            "status": "setup",
            "automation_active": False,
            "current_sprint": "01",
            "workflow_step": "planning",
            "automation_cycles": 0,
            "acceptance_criteria_passed": []
        }
        self.mock_state_manager.read.return_value = setup_state
        
        # Mock git context
        git_context = Mock()
        git_context.is_clean = True
        git_context.has_remote = True
        git_context.current_branch = "main"
        git_context.uncommitted_changes = []
        self.mock_git_ops.get_repo_context.return_value = git_context
        
        cmd = LifecycleCommand(str(self.project_path))
        
        with patch('builtins.print'):  # Suppress print output
            result = cmd.start()
            
        # Verify state update was called
        self.mock_state_manager.update.assert_called_once()
        update_call = self.mock_state_manager.update.call_args[0][0]
        self.assertEqual(update_call["status"], "active")
        self.assertTrue(update_call["automation_active"])
        self.assertEqual(update_call["workflow_step"], "planning")
        
        # Verify result
        self.assertEqual(result["status"], "started")
        self.assertIn("validation_results", result)
        self.assertIn("next_actions", result)
        
    def test_start_invalid_status(self):
        """Test start fails when not in setup status."""
        active_state = {
            "status": "active",
            "automation_active": True
        }
        self.mock_state_manager.read.return_value = active_state
        
        cmd = LifecycleCommand(str(self.project_path))
        
        with self.assertRaises(LifecycleCommandError) as context:
            cmd.start()
            
        self.assertIn("Cannot start from 'active' status", str(context.exception))
        
    def test_start_automation_already_active(self):
        """Test start fails when automation already active."""
        setup_state = {
            "status": "setup",
            "automation_active": True
        }
        self.mock_state_manager.read.return_value = setup_state
        
        cmd = LifecycleCommand(str(self.project_path))
        
        with self.assertRaises(LifecycleCommandError) as context:
            cmd.start()
            
        self.assertIn("Automation is already active", str(context.exception))
        
    def test_start_project_not_ready(self):
        """Test start fails when project not ready."""
        setup_state = {
            "status": "setup",
            "automation_active": False
        }
        self.mock_state_manager.read.return_value = setup_state
        
        # Remove required files to make project not ready
        (self.project_path / "CLAUDE.md").unlink()
        
        cmd = LifecycleCommand(str(self.project_path))
        
        with self.assertRaises(LifecycleCommandError) as context:
            cmd.start()
            
        self.assertIn("Project not ready for automation", str(context.exception))
        
    def test_pause_success(self):
        """Test successful project pause."""
        active_state = {
            "status": "active",
            "automation_active": True,
            "current_sprint": "02",
            "workflow_step": "implementation", 
            "current_user story": "Build API endpoints",
            "automation_cycles": 5,
            "acceptance_criteria_passed": ["compilation", "tests"]
        }
        self.mock_state_manager.read.return_value = active_state
        
        cmd = LifecycleCommand(str(self.project_path))
        
        with patch('builtins.print'):  # Suppress print output
            result = cmd.pause("Taking a break")
            
        # Verify state update
        self.mock_state_manager.update.assert_called_once()
        update_call = self.mock_state_manager.update.call_args[0][0]
        self.assertEqual(update_call["status"], "paused")
        self.assertFalse(update_call["automation_active"])
        self.assertIn("pause_context", update_call)
        
        # Verify pause context
        pause_context = update_call["pause_context"]
        self.assertEqual(pause_context["paused_from_status"], "active")
        self.assertEqual(pause_context["paused_workflow_step"], "implementation")
        self.assertEqual(pause_context["pause_reason"], "Taking a break")
        
        # Verify result
        self.assertEqual(result["status"], "paused")
        self.assertIn("pause_context", result)
        self.assertIn("resume_instructions", result)
        
    def test_pause_invalid_status(self):
        """Test pause fails when not in active status."""
        setup_state = {
            "status": "setup",
            "automation_active": False
        }
        self.mock_state_manager.read.return_value = setup_state
        
        cmd = LifecycleCommand(str(self.project_path))
        
        with self.assertRaises(LifecycleCommandError) as context:
            cmd.pause()
            
        self.assertIn("Cannot pause from 'setup' status", str(context.exception))
        
    def test_pause_automation_not_active(self):
        """Test pause fails when automation not active."""
        active_state = {
            "status": "active", 
            "automation_active": False
        }
        self.mock_state_manager.read.return_value = active_state
        
        cmd = LifecycleCommand(str(self.project_path))
        
        with self.assertRaises(LifecycleCommandError) as context:
            cmd.pause()
            
        self.assertIn("Automation is not currently active", str(context.exception))
        
    def test_resume_success(self):
        """Test successful project resume."""
        paused_state = {
            "status": "paused",
            "automation_active": False,
            "pause_context": {
                "paused_at": "2023-12-01T10:00:00Z",
                "paused_workflow_step": "validation",
                "paused_current_sprint": "03",
                "paused_current_user story": "Write unit tests"
            }
        }
        self.mock_state_manager.read.return_value = paused_state
        
        cmd = LifecycleCommand(str(self.project_path))
        
        with patch('builtins.print'):  # Suppress print output
            with patch('src.commands.lifecycle.datetime') as mock_datetime:
                mock_datetime.now.return_value = datetime(2023, 12, 1, 12, 0, 0, tzinfo=timezone.utc)
                mock_datetime.fromisoformat.return_value = datetime(2023, 12, 1, 10, 0, 0, tzinfo=timezone.utc)
                result = cmd.resume()
                
        # Verify state update
        self.mock_state_manager.update.assert_called_once()
        update_call = self.mock_state_manager.update.call_args[0][0]
        self.assertEqual(update_call["status"], "active")
        self.assertTrue(update_call["automation_active"])
        self.assertEqual(update_call["workflow_step"], "validation")
        self.assertIsNone(update_call["pause_context"])
        
        # Verify result
        self.assertEqual(result["status"], "resumed")
        self.assertIn("resume_point", result)
        self.assertIn("next_actions", result)
        
    def test_resume_invalid_status(self):
        """Test resume fails when not in paused status."""
        active_state = {
            "status": "active",
            "automation_active": True
        }
        self.mock_state_manager.read.return_value = active_state
        
        cmd = LifecycleCommand(str(self.project_path))
        
        with self.assertRaises(LifecycleCommandError) as context:
            cmd.resume()
            
        self.assertIn("Cannot resume from 'active' status", str(context.exception))
        
    def test_resume_no_pause_context(self):
        """Test resume fails when no pause context available."""
        paused_state = {
            "status": "paused",
            "automation_active": False,
            "pause_context": None
        }
        self.mock_state_manager.read.return_value = paused_state
        
        cmd = LifecycleCommand(str(self.project_path))
        
        with self.assertRaises(LifecycleCommandError) as context:
            cmd.resume()
            
        self.assertIn("No pause context found", str(context.exception))
        
    def test_stop_success_incomplete(self):
        """Test successful project stop when incomplete."""
        active_state = {
            "status": "active",
            "project_name": "test-project",
            "started": "2023-12-01T08:00:00Z",
            "current_sprint": "02",
            "completed_sprints": ["01"],
            "automation_cycles": 3,
            "acceptance_criteria_passed": ["compilation", "tests"],
            "workflow_step": "review",
            "current_user story": "Complete architecture"
        }
        self.mock_state_manager.read.return_value = active_state
        
        cmd = LifecycleCommand(str(self.project_path))
        
        with patch('builtins.print'):  # Suppress print output
            with patch('src.commands.lifecycle.datetime') as mock_datetime:
                mock_datetime.now.return_value = datetime(2023, 12, 1, 16, 0, 0, tzinfo=timezone.utc)
                mock_datetime.fromisoformat.return_value = datetime(2023, 12, 1, 8, 0, 0, tzinfo=timezone.utc)
                result = cmd.stop("User requested stop")
                
        # Verify state update
        self.mock_state_manager.update.assert_called_once()
        update_call = self.mock_state_manager.update.call_args[0][0]
        self.assertEqual(update_call["status"], "stopped")
        self.assertFalse(update_call["automation_active"])
        self.assertIsNone(update_call["workflow_step"])
        self.assertIn("stop_context", update_call)
        
        # Verify stop context
        stop_context = update_call["stop_context"]
        self.assertEqual(stop_context["reason"], "User requested stop")
        self.assertEqual(stop_context["final_sprint"], "02")
        
        # Verify result
        self.assertEqual(result["status"], "stopped")
        self.assertIn("project_summary", result)
        self.assertIn("recommendations", result)
        
    def test_stop_success_complete(self):
        """Test successful project stop when complete."""
        completed_state = {
            "status": "active",
            "project_name": "test-project",
            "started": "2023-12-01T08:00:00Z",
            "current_sprint": "05",
            "completed_sprints": ["01", "02", "03", "04", "05"],
            "automation_cycles": 15,
            "acceptance_criteria_passed": ["compilation", "tests", "review", "integration"],
            "workflow_step": "integration"
        }
        self.mock_state_manager.read.return_value = completed_state
        
        cmd = LifecycleCommand(str(self.project_path))
        
        with patch('builtins.print'):  # Suppress print output
            with patch('src.commands.lifecycle.datetime') as mock_datetime:
                mock_datetime.now.return_value = datetime(2023, 12, 5, 16, 0, 0, tzinfo=timezone.utc)
                mock_datetime.fromisoformat.return_value = datetime(2023, 12, 1, 8, 0, 0, tzinfo=timezone.utc)
                result = cmd.stop()
                
        # Verify state shows completed
        update_call = self.mock_state_manager.update.call_args[0][0]
        self.assertEqual(update_call["status"], "completed")
        
        # Verify result
        self.assertEqual(result["status"], "stopped")
        
    def test_validate_project_structure_missing_dirs(self):
        """Test project structure validation with missing directories."""
        # Remove required directory
        shutil.rmtree(self.project_path / "sprints")
        
        cmd = LifecycleCommand(str(self.project_path))
        result = cmd._validate_project_structure()
        
        self.assertFalse(result["valid"])
        self.assertTrue(result["critical"])
        self.assertIn("sprints", result["missing_directories"])
        
    def test_validate_project_structure_missing_files(self):
        """Test project structure validation with missing files."""
        # Remove required file
        (self.project_path / "CLAUDE.md").unlink()
        
        cmd = LifecycleCommand(str(self.project_path))
        result = cmd._validate_project_structure()
        
        self.assertFalse(result["valid"])
        self.assertTrue(result["critical"])
        self.assertIn("CLAUDE.md", result["missing_files"])
        
    def test_validate_git_status_success(self):
        """Test git status validation success."""
        git_context = Mock()
        git_context.is_clean = True
        git_context.has_remote = True
        git_context.current_branch = "main"
        git_context.uncommitted_changes = []
        self.mock_git_ops.get_repo_context.return_value = git_context
        
        cmd = LifecycleCommand(str(self.project_path))
        result = cmd._validate_git_status()
        
        self.assertTrue(result["valid"])
        self.assertFalse(result["critical"])
        self.assertEqual(result["current_branch"], "main")
        self.assertTrue(result["is_clean"])
        
    def test_validate_git_status_with_warnings(self):
        """Test git status validation with warnings."""
        git_context = Mock()
        git_context.is_clean = False
        git_context.has_remote = False
        git_context.current_branch = "feature"
        git_context.uncommitted_changes = ["M file1.py", "?? file2.py"]
        self.mock_git_ops.get_repo_context.return_value = git_context
        
        cmd = LifecycleCommand(str(self.project_path))
        result = cmd._validate_git_status()
        
        self.assertTrue(result["valid"])
        self.assertFalse(result["critical"])
        self.assertEqual(len(result["warnings"]), 2)
        self.assertIn("uncommitted changes", result["warnings"][0])
        self.assertIn("No remote repository", result["warnings"][1])
        
    def test_validate_git_status_no_git(self):
        """Test git status validation when git ops unavailable."""
        cmd = LifecycleCommand(str(self.project_path))
        cmd.git_ops = None
        
        result = cmd._validate_git_status()
        
        self.assertTrue(result["valid"])
        self.assertFalse(result["critical"])
        self.assertIn("not available", result["message"])
        
    def test_validate_configuration_success(self):
        """Test configuration validation success."""
        cmd = LifecycleCommand(str(self.project_path))
        result = cmd._validate_configuration()
        
        self.assertTrue(result["valid"])
        self.assertFalse(result["critical"])
        
    def test_validate_configuration_missing_settings(self):
        """Test configuration validation with missing settings."""
        # Remove settings file
        (self.project_path / ".claude" / "settings.json").unlink()
        
        cmd = LifecycleCommand(str(self.project_path))
        result = cmd._validate_configuration()
        
        self.assertFalse(result["valid"])
        self.assertFalse(result["critical"])
        self.assertIn("settings.json not found", result["message"])
        
    def test_check_project_readiness_success(self):
        """Test project readiness check success."""
        cmd = LifecycleCommand(str(self.project_path))
        self.assertTrue(cmd._check_project_readiness({}))
        
    def test_check_project_readiness_missing_sprints(self):
        """Test project readiness check with missing sprints."""
        shutil.rmtree(self.project_path / "sprints")
        
        cmd = LifecycleCommand(str(self.project_path))
        self.assertFalse(cmd._check_project_readiness({}))
        
    def test_check_project_readiness_missing_claude_md(self):
        """Test project readiness check with missing CLAUDE.md."""
        (self.project_path / "CLAUDE.md").unlink()
        
        cmd = LifecycleCommand(str(self.project_path))
        self.assertFalse(cmd._check_project_readiness({}))
        
    def test_create_pause_context(self):
        """Test pause context creation."""
        state = {
            "status": "active",
            "workflow_step": "implementation",
            "current_sprint": "03",
            "current_user story": "Build features",
            "automation_cycles": 7,
            "acceptance_criteria_passed": ["compilation", "tests"]
        }
        
        cmd = LifecycleCommand(str(self.project_path))
        
        with patch('src.commands.lifecycle.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2023, 12, 1, 15, 30, 0, tzinfo=timezone.utc)
            context = cmd._create_pause_context(state, "Break time")
            
        self.assertEqual(context["paused_from_status"], "active")
        self.assertEqual(context["paused_workflow_step"], "implementation")
        self.assertEqual(context["paused_current_sprint"], "03")
        self.assertEqual(context["pause_reason"], "Break time")
        self.assertEqual(context["automation_cycles_at_pause"], 7)
        
    def test_determine_resume_point(self):
        """Test resume point determination."""
        pause_context = {
            "paused_at": "2023-12-01T10:00:00Z",
            "paused_workflow_step": "validation",
            "paused_current_sprint": "02",
            "paused_current_user story": "Design APIs"
        }
        
        cmd = LifecycleCommand(str(self.project_path))
        
        with patch('src.commands.lifecycle.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2023, 12, 1, 14, 0, 0, tzinfo=timezone.utc)
            mock_datetime.fromisoformat.return_value = datetime(2023, 12, 1, 10, 0, 0, tzinfo=timezone.utc)
            resume_point = cmd._determine_resume_point(pause_context)
            
        self.assertEqual(resume_point["workflow_step"], "validation")
        self.assertEqual(resume_point["current_sprint"], "02")
        self.assertEqual(resume_point["resume_from"], "exact_pause_point")
        self.assertEqual(resume_point["pause_duration"], "4 hours, 0 minutes")
        
    def test_generate_project_summary(self):
        """Test project summary generation."""
        state = {
            "project_name": "test-project",
            "started": "2023-12-01T08:00:00Z",
            "current_sprint": "03",
            "completed_sprints": ["01", "02"],
            "automation_cycles": 8,
            "acceptance_criteria_passed": ["compilation", "tests", "review"],
            "status": "active",
            "workflow_step": "implementation"
        }
        
        cmd = LifecycleCommand(str(self.project_path))
        
        with patch('src.commands.lifecycle.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2023, 12, 2, 16, 0, 0, tzinfo=timezone.utc)
            mock_datetime.fromisoformat.return_value = datetime(2023, 12, 1, 8, 0, 0, tzinfo=timezone.utc)
            summary = cmd._generate_project_summary(state)
            
        self.assertEqual(summary["project_name"], "test-project")
        self.assertEqual(summary["total_duration_days"], 1)
        self.assertEqual(summary["total_duration_hours"], 32.0)
        self.assertEqual(summary["current_sprint"], "03")
        self.assertEqual(summary["automation_cycles"], 8)
        self.assertEqual(summary["acceptance_criteria_passed"], 3)
        
    def test_is_project_complete_true(self):
        """Test project completion check when complete."""
        state = {
            "completed_sprints": ["01", "02", "03", "04", "05"],
            "current_sprint": "05"
        }
        
        cmd = LifecycleCommand(str(self.project_path))
        self.assertTrue(cmd._is_project_complete(state))
        
    def test_is_project_complete_false(self):
        """Test project completion check when incomplete."""
        state = {
            "completed_sprints": ["01", "02"],
            "current_sprint": "03"
        }
        
        cmd = LifecycleCommand(str(self.project_path))
        self.assertFalse(cmd._is_project_complete(state))
        
    def test_state_validation_error_handling(self):
        """Test handling of StateValidationError."""
        self.mock_state_manager.read.side_effect = StateValidationError("Invalid state")
        
        cmd = LifecycleCommand(str(self.project_path))
        
        with self.assertRaises(LifecycleCommandError) as context:
            cmd.start()
            
        self.assertIn("Failed to start project", str(context.exception))
        
    def test_general_exception_handling(self):
        """Test handling of general exceptions."""
        self.mock_state_manager.read.side_effect = Exception("Unexpected error")
        
        cmd = LifecycleCommand(str(self.project_path))
        
        with self.assertRaises(LifecycleCommandError) as context:
            cmd.start()
            
        self.assertIn("Start operation failed", str(context.exception))


if __name__ == '__main__':
    unittest.main()