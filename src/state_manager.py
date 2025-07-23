"""
StateManager - Core project state management for the automated development system.

Provides atomic operations for creating, reading, updating, and validating
project state files with comprehensive error handling and validation.
"""

import json
import os
import tempfile
import shutil
import fcntl
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from pathlib import Path

from config import state as state_config, messages, workflow as workflow_config


class StateValidationError(Exception):
    """Raised when state validation fails."""
    pass


class FileLock:
    """Simple file locking implementation for state file protection."""
    
    def __init__(self, file_path: Path, timeout: float = None):
        """
        Initialize file lock.
        
        Args:
            file_path: Path to the file to lock
            timeout: Maximum time to wait for lock (seconds)
        """
        self.lock_file = Path(str(file_path) + '.lock')
        self.timeout = timeout or state_config.LOCK_TIMEOUT_SECONDS
        self.lock_fd = None
        
    def __enter__(self):
        """Acquire lock with timeout."""
        start_time = time.time()
        
        while True:
            try:
                # Try to create lock file exclusively
                self.lock_fd = os.open(
                    str(self.lock_file), 
                    os.O_CREAT | os.O_EXCL | os.O_RDWR
                )
                # Lock acquired successfully
                break
            except FileExistsError:
                # Lock file exists, check timeout
                if time.time() - start_time > self.timeout:
                    # Check if lock file is stale (older than timeout)
                    try:
                        lock_age = time.time() - os.path.getmtime(self.lock_file)
                        if lock_age > self.timeout * 2:
                            # Stale lock, remove it
                            os.unlink(self.lock_file)
                            continue
                    except FileNotFoundError:
                        # Lock was released, try again
                        continue
                    raise TimeoutError(messages.ERROR_MESSAGES['lock_timeout'].format(timeout=self.timeout))
                # Wait a bit before retrying
                time.sleep(state_config.LOCK_RETRY_DELAY)
        
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Release lock."""
        if self.lock_fd is not None:
            try:
                os.close(self.lock_fd)
            except:
                pass
            try:
                os.unlink(self.lock_file)
            except:
                pass


class StateManager:
    """
    Manages project state with atomic operations and comprehensive validation.
    
    Handles .project-state.json files with schema validation, atomic updates,
    and state transition management for the phase-driven development system.
    """
    
    def __init__(self, project_path: str):
        """
        Initialize StateManager for a specific project directory.
        
        Args:
            project_path: Path to the project directory containing .project-state.json
        """
        self.project_path = Path(project_path).resolve()
        self.state_file = self.project_path / state_config.STATE_FILE_NAME
        
    def create(self, project_name: str, initial_phase: str = "01") -> Dict[str, Any]:
        """
        Create initial project state file with default values.
        
        Args:
            project_name: Name of the project
            initial_phase: Starting phase (default: "01")
            
        Returns:
            Created state dictionary
            
        Raises:
            StateValidationError: If state file already exists or creation fails
        """
        if self.state_file.exists():
            raise StateValidationError(messages.ERROR_MESSAGES['state_exists'].format(path=self.state_file))
            
        initial_state = {
            "project_name": project_name,
            "current_phase": initial_phase,
            "status": "setup",
            "automation_active": False,
            "workflow_step": "planning",
            "current_objective": None,
            "quality_gates_passed": [],
            "completed_phases": [],
            "automation_cycles": 0,
            "started": datetime.now(timezone.utc).isoformat(),
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "git_branch": self._get_current_branch(),
            "git_worktree": str(self.project_path),
            "version": state_config.STATE_FILE_VERSION
        }
        
        self._validate_state(initial_state)
        self._write_state_atomic(initial_state)
        
        return initial_state
        
    def read(self) -> Dict[str, Any]:
        """
        Load and validate existing project state.
        
        Returns:
            Current state dictionary
            
        Raises:
            StateValidationError: If state file doesn't exist or is invalid
        """
        if not self.state_file.exists():
            raise StateValidationError(f"State file not found: {self.state_file}")
            
        # Use file locking for concurrent access protection
        with FileLock(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                raise StateValidationError(f"Failed to read state file: {e}")
            
        self._validate_state(state)
        return state
        
    def update(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Atomically update project state with validation.
        
        Args:
            updates: Dictionary of fields to update
            
        Returns:
            Updated state dictionary
            
        Raises:
            StateValidationError: If updates are invalid or operation fails
        """
        # Use file locking for the entire update operation
        with FileLock(self.state_file):
            # Re-read state inside lock to ensure consistency
            if not self.state_file.exists():
                raise StateValidationError(f"State file not found: {self.state_file}")
                
            try:
                with open(self.state_file, 'r') as f:
                    current_state = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                raise StateValidationError(f"Failed to read state file: {e}")
            
            # Apply updates
            updated_state = current_state.copy()
            updated_state.update(updates)
            updated_state["last_updated"] = datetime.now(timezone.utc).isoformat()
            
            # Validate updated state
            self._validate_state(updated_state)
            
            # Write atomically (still within lock)
            self._write_state_atomic(updated_state)
        
        return updated_state
        
    def transition_phase(self, new_phase: str, force: bool = False) -> Dict[str, Any]:
        """
        Transition to a new phase with validation.
        
        Args:
            new_phase: Target phase identifier
            force: Skip validation checks if True
            
        Returns:
            Updated state dictionary
            
        Raises:
            StateValidationError: If transition is invalid
        """
        current_state = self.read()
        current_phase = current_state["current_phase"]
        
        if not force:
            # Validate phase transition logic
            if not self._is_valid_phase_transition(current_phase, new_phase):
                raise StateValidationError(
                    f"Invalid phase transition from {current_phase} to {new_phase}"
                )
                
            # Check if current phase is complete
            if not self._is_phase_complete(current_phase):
                raise StateValidationError(
                    f"Cannot advance from incomplete phase {current_phase}"
                )
        
        # Update completed phases if advancing
        completed_phases = current_state["completed_phases"].copy()
        if current_phase not in completed_phases and current_phase != new_phase:
            completed_phases.append(current_phase)
            
        updates = {
            "current_phase": new_phase,
            "completed_phases": completed_phases,
            "workflow_step": "planning",  # Reset to planning for new phase
            "current_objective": None,
            "quality_gates_passed": []  # Reset quality gates for new phase
        }
        
        return self.update(updates)
        
    def validate(self) -> bool:
        """
        Validate current state file.
        
        Returns:
            True if state is valid
            
        Raises:
            StateValidationError: If state is invalid
        """
        state = self.read()
        self._validate_state(state)
        return True
        
    def backup_state(self) -> str:
        """
        Create a backup of the current state file.
        
        Returns:
            Path to backup file
        """
        if not self.state_file.exists():
            raise StateValidationError("No state file to backup")
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.state_file.with_suffix(f".backup.{timestamp}.json")
        
        shutil.copy2(self.state_file, backup_path)
        return str(backup_path)
        
    def restore_state(self, backup_path: str) -> Dict[str, Any]:
        """
        Restore state from backup file.
        
        Args:
            backup_path: Path to backup file
            
        Returns:
            Restored state dictionary
        """
        backup_file = Path(backup_path)
        if not backup_file.exists():
            raise StateValidationError(f"Backup file not found: {backup_path}")
            
        # Validate backup before restoring
        try:
            with open(backup_file, 'r') as f:
                backup_state = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            raise StateValidationError(f"Failed to read backup file: {e}")
            
        self._validate_state(backup_state)
        
        # Create backup of current state before restoring
        if self.state_file.exists():
            self.backup_state()
            
        # Restore from backup
        self._write_state_atomic(backup_state)
        return backup_state
        
    def _validate_state(self, state: Dict[str, Any]) -> None:
        """Validate state dictionary against schema."""
        required_fields = [
            "project_name", "current_phase", "status", "automation_active",
            "workflow_step", "quality_gates_passed", "completed_phases",
            "automation_cycles", "started", "last_updated"
        ]
        
        # Check required fields
        for field in required_fields:
            if field not in state:
                raise StateValidationError(f"Missing required field: {field}")
                
        # Validate field types and values
        if not isinstance(state["project_name"], str) or not state["project_name"]:
            raise StateValidationError("project_name must be a non-empty string")
            
        if state["status"] not in state_config.VALID_STATES:
            raise StateValidationError(f"Invalid status: {state['status']}")
            
        if state["workflow_step"] not in workflow_config.WORKFLOW_STEPS:
            raise StateValidationError(f"Invalid workflow step: {state['workflow_step']}")
            
        if not isinstance(state["automation_active"], bool):
            raise StateValidationError("automation_active must be boolean")
            
        if not isinstance(state["quality_gates_passed"], list):
            raise StateValidationError("quality_gates_passed must be a list")
            
        if not isinstance(state["completed_phases"], list):
            raise StateValidationError("completed_phases must be a list")
            
        if not isinstance(state["automation_cycles"], int) or state["automation_cycles"] < 0:
            raise StateValidationError("automation_cycles must be a non-negative integer")
            
        # Validate timestamps
        for timestamp_field in ["started", "last_updated"]:
            try:
                datetime.fromisoformat(state[timestamp_field].replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                raise StateValidationError(f"Invalid timestamp format: {timestamp_field}")
                
    def _write_state_atomic(self, state: Dict[str, Any]) -> None:
        """Write state file atomically to prevent corruption."""
        # Write to temporary file first
        temp_file = None
        try:
            with tempfile.NamedTemporaryFile(
                mode='w',
                suffix='.json',
                dir=self.project_path,
                delete=False
            ) as f:
                json.dump(state, f, indent=2, sort_keys=True)
                temp_file = f.name
                
            # Atomic move to final location
            shutil.move(temp_file, self.state_file)
            
        except Exception as e:
            # Clean up temp file on error
            if temp_file and os.path.exists(temp_file):
                os.unlink(temp_file)
            raise StateValidationError(f"Failed to write state file: {e}")
            
    def _get_current_branch(self) -> Optional[str]:
        """Get current git branch name."""
        try:
            import subprocess
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip() or None
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None
            
    def _is_valid_phase_transition(self, current: str, target: str) -> bool:
        """Validate phase transition logic."""
        # Simple sequential validation - can be enhanced with complex rules
        try:
            current_num = int(current)
            target_num = int(target)
            
            # Allow advancing to next phase or jumping back
            return target_num <= current_num + 1
        except ValueError:
            # Non-numeric phases allowed for now
            return True
            
    def _is_phase_complete(self, phase: str) -> bool:
        """Check if phase objectives are complete."""
        # This would check phase files for completion status
        # For now, assume phases can be advanced
        return True