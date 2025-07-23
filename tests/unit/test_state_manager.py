"""
Unit tests for StateManager class.

Tests core functionality including create, read, update, validate operations
with comprehensive error handling and edge case coverage.
"""

import unittest
import tempfile
import shutil
import json
import sys
import os
from pathlib import Path
from datetime import datetime, timezone

# Add src to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from state_manager import StateManager, StateValidationError


class TestStateManager(unittest.TestCase):
    """Test StateManager functionality."""
    
    def setUp(self):
        """Set up test environment with temporary directory."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.manager = StateManager(self.test_dir)
        
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
        
    def test_create_initial_state(self):
        """Test creating initial project state."""
        state = self.manager.create("test-project")
        
        # Verify required fields
        self.assertEqual(state["project_name"], "test-project")
        self.assertEqual(state["current_sprint"], "01")
        self.assertEqual(state["status"], "setup")
        self.assertEqual(state["automation_active"], False)
        self.assertEqual(state["workflow_step"], "planning")
        self.assertIsNone(state["current_user story"])
        self.assertEqual(state["acceptance_criteria_passed"], [])
        self.assertEqual(state["completed_sprints"], [])
        self.assertEqual(state["automation_cycles"], 0)
        
        # Verify timestamps are valid
        started = datetime.fromisoformat(state["started"].replace('Z', '+00:00'))
        last_updated = datetime.fromisoformat(state["last_updated"].replace('Z', '+00:00'))
        self.assertIsInstance(started, datetime)
        self.assertIsInstance(last_updated, datetime)
        
        # Verify file was created
        self.assertTrue(self.manager.state_file.exists())
        
    def test_create_duplicate_state_fails(self):
        """Test that creating state twice fails."""
        self.manager.create("test-project")
        
        with self.assertRaises(StateValidationError) as context:
            self.manager.create("another-project")
            
        self.assertIn("already exists", str(context.exception))
        
    def test_read_existing_state(self):
        """Test reading existing state file."""
        original = self.manager.create("test-project")
        loaded = self.manager.read()
        
        self.assertEqual(original, loaded)
        
    def test_read_nonexistent_state_fails(self):
        """Test reading non-existent state file fails."""
        with self.assertRaises(StateValidationError) as context:
            self.manager.read()
            
        self.assertIn("not found", str(context.exception))
        
    def test_update_state(self):
        """Test updating state with new values."""
        self.manager.create("test-project")
        
        updates = {
            "status": "active",
            "automation_active": True,
            "workflow_step": "implementation",
            "current_user story": "Test feature"
        }
        
        updated_state = self.manager.update(updates)
        
        # Verify updates applied
        self.assertEqual(updated_state["status"], "active")
        self.assertEqual(updated_state["automation_active"], True)
        self.assertEqual(updated_state["workflow_step"], "implementation")
        self.assertEqual(updated_state["current_user story"], "Test feature")
        
        # Verify last_updated timestamp updated
        original_timestamp = self.manager.read()["last_updated"]
        self.assertEqual(updated_state["last_updated"], original_timestamp)
        
    def test_update_with_invalid_status_fails(self):
        """Test updating with invalid status value fails."""
        self.manager.create("test-project")
        
        with self.assertRaises(StateValidationError) as context:
            self.manager.update({"status": "invalid-status"})
            
        self.assertIn("Invalid status", str(context.exception))
        
    def test_update_with_invalid_workflow_step_fails(self):
        """Test updating with invalid workflow step fails."""
        self.manager.create("test-project")
        
        with self.assertRaises(StateValidationError) as context:
            self.manager.update({"workflow_step": "invalid-step"})
            
        self.assertIn("Invalid workflow step", str(context.exception))
        
    def test_transition_sprint(self):
        """Test sprint transition."""
        self.manager.create("test-project")
        
        updated_state = self.manager.transition_sprint("02")
        
        self.assertEqual(updated_state["current_sprint"], "02")
        self.assertEqual(updated_state["completed_sprints"], ["01"])
        self.assertEqual(updated_state["workflow_step"], "planning")
        self.assertEqual(updated_state["acceptance_criteria_passed"], [])
        
    def test_validate_correct_state(self):
        """Test validation of correct state."""
        self.manager.create("test-project")
        
        # Should not raise exception
        result = self.manager.validate()
        self.assertTrue(result)
        
    def test_validate_corrupted_state(self):
        """Test validation of corrupted state file."""
        # Create valid state first
        self.manager.create("test-project")
        
        # Corrupt the state file
        with open(self.manager.state_file, 'w') as f:
            json.dump({"invalid": "state"}, f)
            
        with self.assertRaises(StateValidationError):
            self.manager.validate()
            
    def test_backup_and_restore(self):
        """Test backup and restore functionality."""
        original_state = self.manager.create("test-project")
        
        # Create backup
        backup_path = self.manager.backup_state()
        self.assertTrue(Path(backup_path).exists())
        
        # Modify state
        self.manager.update({"status": "active", "current_user story": "Modified"})
        
        # Restore from backup
        restored_state = self.manager.restore_state(backup_path)
        
        # Verify restoration
        self.assertEqual(restored_state["status"], original_state["status"])
        self.assertEqual(restored_state["current_user story"], original_state["current_user story"])
        
    def test_atomic_write_on_failure(self):
        """Test that failed writes don't corrupt existing state."""
        original_state = self.manager.create("test-project")
        
        # Try to update with invalid data that will fail validation
        try:
            self.manager.update({"status": "invalid-status"})
        except StateValidationError:
            pass
            
        # Verify original state still intact
        current_state = self.manager.read()
        self.assertEqual(current_state, original_state)
        
    def test_missing_required_field_validation(self):
        """Test validation fails for missing required fields."""
        # Create state file manually with missing field
        invalid_state = {
            "project_name": "test",
            "current_sprint": "01",
            # Missing status field
            "automation_active": False,
            "workflow_step": "planning",
            "acceptance_criteria_passed": [],
            "completed_sprints": [],
            "automation_cycles": 0,
            "started": datetime.now(timezone.utc).isoformat(),
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
        
        with open(self.manager.state_file, 'w') as f:
            json.dump(invalid_state, f)
            
        with self.assertRaises(StateValidationError) as context:
            self.manager.read()
            
        self.assertIn("Missing required field", str(context.exception))
        
    def test_invalid_timestamp_validation(self):
        """Test validation fails for invalid timestamps."""
        self.manager.create("test-project")
        
        with self.assertRaises(StateValidationError):
            self.manager.update({"started": "invalid-timestamp"})
            
    def test_acceptance_criteria_tracking(self):
        """Test quality gates functionality."""
        self.manager.create("test-project")
        
        # Add quality gates
        gates = ["compilation", "existing_tests", "review"]
        updated_state = self.manager.update({"acceptance_criteria_passed": gates})
        
        self.assertEqual(updated_state["acceptance_criteria_passed"], gates)
        
        # Verify gates reset on sprint transition
        transitioned = self.manager.transition_sprint("02")
        self.assertEqual(transitioned["acceptance_criteria_passed"], [])
        
    def test_automation_cycles_increment(self):
        """Test automation cycles tracking."""
        self.manager.create("test-project")
        
        # Increment cycles
        for i in range(1, 4):
            updated = self.manager.update({"automation_cycles": i})
            self.assertEqual(updated["automation_cycles"], i)
            
    def test_git_branch_tracking(self):
        """Test git branch information tracking."""
        state = self.manager.create("test-project")
        
        # Git branch may be None if not in git repo
        self.assertIn("git_branch", state)
        self.assertIsInstance(state["git_worktree"], str)


if __name__ == '__main__':
    unittest.main()