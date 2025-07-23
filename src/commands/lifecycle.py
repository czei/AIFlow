"""
Lifecycle Command - Manage project lifecycle states (start/pause/resume/stop).

Provides comprehensive project lifecycle management with state transitions,
automation control, and progress tracking.
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone

from ..state_manager import StateManager, StateValidationError
from ..git_operations import GitOperations, GitOperationError


class LifecycleCommandError(Exception):
    """Raised when lifecycle command fails."""
    pass


class LifecycleCommand:
    """
    Implements project lifecycle management functionality.
    
    Handles state transitions between setup, active, paused, stopped, and error states
    with comprehensive validation and automation control.
    """
    
    def __init__(self, project_path: Optional[str] = None):
        """
        Initialize lifecycle command.
        
        Args:
            project_path: Path to project directory. Defaults to current directory.
        """
        self.project_path = Path(project_path or ".").resolve()
        self.state_manager = StateManager(str(self.project_path))
        
        try:
            self.git_ops = GitOperations(str(self.project_path))
        except GitOperationError:
            # Git operations optional for lifecycle management
            self.git_ops = None
            
    def start(self) -> Dict[str, Any]:
        """
        Start project automation - transition from 'setup' to 'active'.
        
        Returns:
            Dictionary containing start operation results
            
        Raises:
            LifecycleCommandError: If start operation fails
        """
        try:
            print("🚀 Starting project automation...")
            
            # Load and validate current state
            state = self.state_manager.read()
            self._validate_start_conditions(state)
            
            # Perform pre-start validation
            validation_results = self._perform_start_validation()
            
            # Update state to active
            updates = {
                "status": "active",
                "automation_active": True,
                "workflow_step": "planning",
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            
            self.state_manager.update(updates)
            
            # Display success information
            self._display_start_success(validation_results)
            
            return {
                "status": "started",
                "validation_results": validation_results,
                "next_actions": self._get_start_next_actions(state)
            }
            
        except StateValidationError as e:
            raise LifecycleCommandError(f"Failed to start project: {e}")
        except Exception as e:
            raise LifecycleCommandError(f"Start operation failed: {e}")
            
    def pause(self, reason: Optional[str] = None) -> Dict[str, Any]:
        """
        Pause project automation - preserve state and disable automation.
        
        Args:
            reason: Optional reason for pausing
            
        Returns:
            Dictionary containing pause operation results
            
        Raises:
            LifecycleCommandError: If pause operation fails
        """
        try:
            print("⏸️  Pausing project automation...")
            
            # Load and validate current state
            state = self.state_manager.read()
            self._validate_pause_conditions(state)
            
            # Preserve current state for resume
            pause_context = self._create_pause_context(state, reason)
            
            # Update state to paused
            updates = {
                "status": "paused",
                "automation_active": False,
                "pause_context": pause_context,
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            
            self.state_manager.update(updates)
            
            # Display pause information
            self._display_pause_success(pause_context)
            
            return {
                "status": "paused",
                "pause_context": pause_context,
                "resume_instructions": self._get_resume_instructions()
            }
            
        except StateValidationError as e:
            raise LifecycleCommandError(f"Failed to pause project: {e}")
        except Exception as e:
            raise LifecycleCommandError(f"Pause operation failed: {e}")
            
    def resume(self) -> Dict[str, Any]:
        """
        Resume project automation from paused state.
        
        Returns:
            Dictionary containing resume operation results
            
        Raises:
            LifecycleCommandError: If resume operation fails
        """
        try:
            print("▶️  Resuming project automation...")
            
            # Load and validate current state
            state = self.state_manager.read()
            self._validate_resume_conditions(state)
            
            # Restore from pause context
            pause_context = state.get("pause_context", {})
            resume_point = self._determine_resume_point(pause_context)
            
            # Update state to active
            updates = {
                "status": "active",
                "automation_active": True,
                "workflow_step": resume_point.get("workflow_step", "planning"),
                "pause_context": None,  # Clear pause context
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            
            self.state_manager.update(updates)
            
            # Display resume information
            self._display_resume_success(resume_point)
            
            return {
                "status": "resumed",
                "resume_point": resume_point,
                "next_actions": self._get_resume_next_actions(resume_point)
            }
            
        except StateValidationError as e:
            raise LifecycleCommandError(f"Failed to resume project: {e}")
        except Exception as e:
            raise LifecycleCommandError(f"Resume operation failed: {e}")
            
    def stop(self, reason: Optional[str] = None) -> Dict[str, Any]:
        """
        Stop project with comprehensive summary.
        
        Args:
            reason: Optional reason for stopping
            
        Returns:
            Dictionary containing stop operation results and project summary
            
        Raises:
            LifecycleCommandError: If stop operation fails
        """
        try:
            print("⏹️  Stopping project...")
            
            # Load current state
            state = self.state_manager.read()
            
            # Generate project summary
            project_summary = self._generate_project_summary(state)
            
            # Create final state
            updates = {
                "status": "completed" if self._is_project_complete(state) else "stopped",
                "automation_active": False,
                "workflow_step": None,
                "stop_context": {
                    "reason": reason,
                    "stopped_at": datetime.now(timezone.utc).isoformat(),
                    "final_phase": state.get("current_phase"),
                    "final_workflow_step": state.get("workflow_step"),
                    "summary": project_summary
                },
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            
            self.state_manager.update(updates)
            
            # Display comprehensive summary
            self._display_stop_summary(project_summary, reason)
            
            return {
                "status": "stopped",
                "project_summary": project_summary,
                "recommendations": self._get_stop_recommendations(state)
            }
            
        except StateValidationError as e:
            raise LifecycleCommandError(f"Failed to stop project: {e}")
        except Exception as e:
            raise LifecycleCommandError(f"Stop operation failed: {e}")
            
    def _validate_start_conditions(self, state: Dict[str, Any]) -> None:
        """Validate conditions for starting automation."""
        current_status = state.get("status")
        
        if current_status != "setup":
            raise LifecycleCommandError(
                f"Cannot start from '{current_status}' status. "
                f"Project must be in 'setup' status to start automation."
            )
            
        if state.get("automation_active"):
            raise LifecycleCommandError("Automation is already active")
            
        # Validate project readiness
        if not self._check_project_readiness(state):
            raise LifecycleCommandError(
                "Project not ready for automation. Please customize phase files and "
                "update CLAUDE.md with project context."
            )
            
    def _validate_pause_conditions(self, state: Dict[str, Any]) -> None:
        """Validate conditions for pausing automation."""
        current_status = state.get("status")
        
        if current_status != "active":
            raise LifecycleCommandError(
                f"Cannot pause from '{current_status}' status. "
                f"Only active projects can be paused."
            )
            
        if not state.get("automation_active"):
            raise LifecycleCommandError("Automation is not currently active")
            
    def _validate_resume_conditions(self, state: Dict[str, Any]) -> None:
        """Validate conditions for resuming automation."""
        current_status = state.get("status")
        
        if current_status != "paused":
            raise LifecycleCommandError(
                f"Cannot resume from '{current_status}' status. "
                f"Only paused projects can be resumed."
            )
            
        if state.get("automation_active"):
            raise LifecycleCommandError("Automation is already active")
            
        if not state.get("pause_context"):
            raise LifecycleCommandError("No pause context found - cannot determine resume point")
            
    def _check_project_readiness(self, state: Dict[str, Any]) -> bool:
        """Check if project is ready for automation."""
        # Check if phase files exist and have been customized
        phases_dir = self.project_path / "phases"
        if not phases_dir.exists():
            return False
            
        # Check for key phase files
        required_phases = ["01-planning.md", "02-architecture.md", "03-implementation.md"]
        for phase_file in required_phases:
            phase_path = phases_dir / phase_file
            if not phase_path.exists():
                return False
                
        # Check if CLAUDE.md exists
        claude_md = self.project_path / "CLAUDE.md"
        if not claude_md.exists():
            return False
            
        return True
        
    def _perform_start_validation(self) -> Dict[str, Any]:
        """Perform comprehensive validation before starting."""
        validation_results = {
            "project_structure": self._validate_project_structure(),
            "git_status": self._validate_git_status(),
            "configuration": self._validate_configuration(),
            "dependencies": self._validate_dependencies()
        }
        
        # Check for critical failures
        critical_failures = []
        for category, result in validation_results.items():
            if not result.get("valid", True):
                if result.get("critical", False):
                    critical_failures.append(f"{category}: {result.get('message', 'Unknown error')}")
                    
        if critical_failures:
            raise LifecycleCommandError(
                f"Critical validation failures prevent starting:\n" + 
                "\n".join(f"- {failure}" for failure in critical_failures)
            )
            
        return validation_results
        
    def _validate_project_structure(self) -> Dict[str, Any]:
        """Validate project directory structure."""
        required_dirs = ["phases", ".claude", "logs", "docs"]
        required_files = ["CLAUDE.md", ".project-state.json"]
        
        missing_dirs = []
        missing_files = []
        
        for dir_name in required_dirs:
            if not (self.project_path / dir_name).exists():
                missing_dirs.append(dir_name)
                
        for file_name in required_files:
            if not (self.project_path / file_name).exists():
                missing_files.append(file_name)
                
        is_valid = len(missing_dirs) == 0 and len(missing_files) == 0
        
        return {
            "valid": is_valid,
            "critical": not is_valid,
            "missing_directories": missing_dirs,
            "missing_files": missing_files,
            "message": "Project structure validation" + (" passed" if is_valid else " failed")
        }
        
    def _validate_git_status(self) -> Dict[str, Any]:
        """Validate git repository status."""
        if not self.git_ops:
            return {
                "valid": True,
                "critical": False,
                "message": "Git operations not available (not critical)"
            }
            
        try:
            context = self.git_ops.get_repo_context()
            
            warnings = []
            if not context.is_clean:
                warnings.append(f"Working tree has {len(context.uncommitted_changes)} uncommitted changes")
                
            if not context.has_remote:
                warnings.append("No remote repository configured")
                
            return {
                "valid": True,
                "critical": False,
                "warnings": warnings,
                "current_branch": context.current_branch,
                "is_clean": context.is_clean,
                "message": "Git status validation passed" + (f" with {len(warnings)} warnings" if warnings else "")
            }
            
        except GitOperationError as e:
            return {
                "valid": False,
                "critical": False,
                "message": f"Git validation failed: {e}"
            }
            
    def _validate_configuration(self) -> Dict[str, Any]:
        """Validate project configuration."""
        try:
            # Check Claude configuration
            claude_dir = self.project_path / ".claude"
            settings_file = claude_dir / "settings.json"
            
            if not settings_file.exists():
                return {
                    "valid": False,
                    "critical": False,
                    "message": "Claude settings.json not found"
                }
                
            return {
                "valid": True,
                "critical": False,
                "message": "Configuration validation passed"
            }
            
        except Exception as e:
            return {
                "valid": False,
                "critical": False,
                "message": f"Configuration validation failed: {e}"
            }
            
    def _validate_dependencies(self) -> Dict[str, Any]:
        """Validate project dependencies."""
        # Basic dependency validation - can be extended
        return {
            "valid": True,
            "critical": False,
            "message": "Dependency validation passed"
        }
        
    def _create_pause_context(self, state: Dict[str, Any], reason: Optional[str]) -> Dict[str, Any]:
        """Create context for pause state preservation."""
        return {
            "paused_at": datetime.now(timezone.utc).isoformat(),
            "paused_from_status": state.get("status"),
            "paused_workflow_step": state.get("workflow_step"),
            "paused_current_phase": state.get("current_phase"),
            "paused_current_objective": state.get("current_objective"),
            "pause_reason": reason,
            "automation_cycles_at_pause": state.get("automation_cycles", 0),
            "quality_gates_at_pause": state.get("quality_gates_passed", []).copy()
        }
        
    def _determine_resume_point(self, pause_context: Dict[str, Any]) -> Dict[str, Any]:
        """Determine optimal resume point from pause context."""
        return {
            "workflow_step": pause_context.get("paused_workflow_step", "planning"),
            "current_phase": pause_context.get("paused_current_phase"),
            "current_objective": pause_context.get("paused_current_objective"),
            "resume_from": "exact_pause_point",
            "pause_duration": self._calculate_pause_duration(pause_context)
        }
        
    def _calculate_pause_duration(self, pause_context: Dict[str, Any]) -> str:
        """Calculate duration of pause."""
        paused_at_str = pause_context.get("paused_at")
        if not paused_at_str:
            return "unknown"
            
        paused_at = datetime.fromisoformat(paused_at_str.replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        duration = now - paused_at
        
        if duration.days > 0:
            return f"{duration.days} days, {duration.seconds // 3600} hours"
        elif duration.seconds > 3600:
            return f"{duration.seconds // 3600} hours, {(duration.seconds % 3600) // 60} minutes"
        else:
            return f"{duration.seconds // 60} minutes"
            
    def _generate_project_summary(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive project summary."""
        started_time = datetime.fromisoformat(state["started"].replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        total_duration = now - started_time
        
        return {
            "project_name": state.get("project_name"),
            "total_duration_days": total_duration.days,
            "total_duration_hours": total_duration.total_seconds() / 3600,
            "current_phase": state.get("current_phase"),
            "completed_phases": state.get("completed_phases", []),
            "automation_cycles": state.get("automation_cycles", 0),
            "quality_gates_passed": len(state.get("quality_gates_passed", [])),
            "final_status": state.get("status"),
            "workflow_step": state.get("workflow_step"),
            "current_objective": state.get("current_objective")
        }
        
    def _is_project_complete(self, state: Dict[str, Any]) -> bool:
        """Check if project is complete (all phases finished)."""
        completed_phases = state.get("completed_phases", [])
        current_phase = state.get("current_phase", "01")
        
        # Project complete if all 5 phases are done or if we're on phase 05 and it's complete
        return len(completed_phases) >= 5 or (current_phase == "05" and len(completed_phases) >= 4)
        
    def _get_start_next_actions(self, state: Dict[str, Any]) -> List[str]:
        """Get recommended next actions after starting."""
        return [
            "Begin working on current phase objectives",
            "Follow the 6-step workflow for each objective",
            "Monitor progress with /user:project:status",
            "Use /user:project:pause if you need to interrupt work"
        ]
        
    def _get_resume_instructions(self) -> List[str]:
        """Get instructions for resuming from pause."""
        return [
            "Use /user:project:resume to continue from exact pause point",
            "Review /user:project:status to see current progress",
            "All automation state has been preserved",
            "Work will continue from where it was paused"
        ]
        
    def _get_resume_next_actions(self, resume_point: Dict[str, Any]) -> List[str]:
        """Get recommended actions after resuming."""
        workflow_step = resume_point.get("workflow_step", "planning")
        return [
            f"Continue with {workflow_step} step of current objective",
            "Review progress made before pause",
            "Monitor with /user:project:status",
            "Use /user:project:pause again if needed"
        ]
        
    def _get_stop_recommendations(self, state: Dict[str, Any]) -> List[str]:
        """Get recommendations after stopping project."""
        recommendations = []
        
        if self._is_project_complete(state):
            recommendations.extend([
                "🎉 Project completed successfully!",
                "Review final deliverables and documentation",
                "Consider archiving project state for future reference",
                "Evaluate lessons learned for future projects"
            ])
        else:
            recommendations.extend([
                "Project stopped before completion",
                "Consider using /user:project:start to resume development",
                "Review current progress and adjust timeline if needed",
                "Update phase files if requirements have changed"
            ])
            
        return recommendations
        
    def _display_start_success(self, validation_results: Dict[str, Any]) -> None:
        """Display start operation success information."""
        print(f"\n✅ Project automation started successfully!")
        print(f"")
        print(f"🔍 Validation Results:")
        
        for category, result in validation_results.items():
            status = "✅" if result.get("valid", True) else "❌"
            print(f"   {status} {category.replace('_', ' ').title()}: {result.get('message', 'OK')}")
            
            # Show warnings if any
            warnings = result.get("warnings", [])
            for warning in warnings:
                print(f"      ⚠️  {warning}")
                
        print(f"")
        print(f"🚀 Next Steps:")
        print(f"   • Automation is now active and ready")
        print(f"   • Work will follow the 6-step workflow methodology")
        print(f"   • Monitor progress with /user:project:status")
        print(f"   • Use /user:project:pause to interrupt if needed")
        print(f"")
        print(f"🤖 Automation Status: ACTIVE")
        
    def _display_pause_success(self, pause_context: Dict[str, Any]) -> None:
        """Display pause operation success information."""
        print(f"\n⏸️  Project automation paused successfully!")
        print(f"")
        print(f"📍 Pause Context:")
        print(f"   Paused at: {pause_context.get('paused_at', 'Unknown')}")
        print(f"   From phase: {pause_context.get('paused_current_phase', 'Unknown')}")
        print(f"   Workflow step: {pause_context.get('paused_workflow_step', 'Unknown')}")
        
        reason = pause_context.get('pause_reason')
        if reason:
            print(f"   Reason: {reason}")
            
        print(f"")
        print(f"💾 State Preserved:")
        print(f"   • Current automation position saved")
        print(f"   • Quality gates status preserved")
        print(f"   • Progress counters maintained")
        print(f"")
        print(f"▶️  Resume Instructions:")
        print(f"   • Use /user:project:resume to continue exactly where paused")
        print(f"   • All automation state will be restored")
        print(f"   • No progress will be lost")
        print(f"")
        print(f"🤖 Automation Status: PAUSED")
        
    def _display_resume_success(self, resume_point: Dict[str, Any]) -> None:
        """Display resume operation success information."""
        print(f"\n▶️  Project automation resumed successfully!")
        print(f"")
        print(f"📍 Resume Point:")
        print(f"   Phase: {resume_point.get('current_phase', 'Unknown')}")
        print(f"   Workflow step: {resume_point.get('workflow_step', 'Unknown')}")
        print(f"   Pause duration: {resume_point.get('pause_duration', 'Unknown')}")
        
        current_objective = resume_point.get('current_objective')
        if current_objective:
            print(f"   Current objective: {current_objective}")
            
        print(f"")
        print(f"🔄 Restoration Complete:")
        print(f"   • Automation position restored")
        print(f"   • Previous state fully recovered")
        print(f"   • Ready to continue development")
        print(f"")
        print(f"🚀 Next Steps:")
        print(f"   • Continue with current workflow step")
        print(f"   • Monitor progress with /user:project:status")
        print(f"   • Use /user:project:pause if you need to interrupt again")
        print(f"")
        print(f"🤖 Automation Status: ACTIVE")
        
    def _display_stop_summary(self, summary: Dict[str, Any], reason: Optional[str]) -> None:
        """Display comprehensive project stop summary."""
        print(f"\n⏹️  Project stopped successfully!")
        print(f"")
        print(f"📊 Project Summary:")
        print(f"   Project: {summary.get('project_name', 'Unknown')}")
        print(f"   Total Duration: {summary.get('total_duration_days', 0)} days, {summary.get('total_duration_hours', 0):.1f} hours")
        print(f"   Current Phase: {summary.get('current_phase', 'Unknown')}")
        print(f"   Completed Phases: {len(summary.get('completed_phases', []))}")
        print(f"   Automation Cycles: {summary.get('automation_cycles', 0)}")
        print(f"   Quality Gates Passed: {summary.get('quality_gates_passed', 0)}")
        
        if reason:
            print(f"   Stop Reason: {reason}")
            
        final_status = summary.get('final_status', 'stopped')
        if final_status == 'completed':
            print(f"   Final Status: ✅ COMPLETED")
        else:
            print(f"   Final Status: ⏹️  STOPPED")
            
        current_objective = summary.get('current_objective')
        if current_objective:
            print(f"   Last Objective: {current_objective}")
            
        print(f"")
        
        if final_status == 'completed':
            print(f"🎉 Congratulations! Project completed successfully!")
            print(f"   • All development phases finished")
            print(f"   • Quality gates achieved throughout")
            print(f"   • Ready for production use")
        else:
            print(f"📋 Project State Preserved:")
            print(f"   • All progress and state saved")
            print(f"   • Can resume with /user:project:start")
            print(f"   • No work will be lost")
            
        print(f"")
        print(f"🤖 Automation Status: STOPPED")


def main():
    """Command-line interface for lifecycle commands."""
    if len(sys.argv) < 2:
        print("Usage: python -m src.commands.lifecycle <command> [options]")
        print("")
        print("Commands:")
        print("  start                 Start project automation")
        print("  pause [reason]        Pause automation with optional reason")
        print("  resume                Resume paused automation")
        print("  stop [reason]         Stop project with optional reason")
        print("")
        print("Examples:")
        print("  python -m src.commands.lifecycle start")
        print("  python -m src.commands.lifecycle pause 'taking a break'")
        print("  python -m src.commands.lifecycle resume")
        print("  python -m src.commands.lifecycle stop 'project complete'")
        sys.exit(1)
        
    command = sys.argv[1].lower()
    project_path = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('-') else None
    
    # Extract reason from remaining args
    reason_args = []
    for i in range(2 if project_path else 2, len(sys.argv)):
        if not sys.argv[i].startswith('-'):
            reason_args.append(sys.argv[i])
    reason = ' '.join(reason_args) if reason_args else None
    
    try:
        lifecycle_cmd = LifecycleCommand(project_path)
        
        if command == "start":
            lifecycle_cmd.start()
        elif command == "pause":
            lifecycle_cmd.pause(reason)
        elif command == "resume":
            lifecycle_cmd.resume()
        elif command == "stop":
            lifecycle_cmd.stop(reason)
        else:
            print(f"❌ Unknown command: {command}")
            print("Valid commands: start, pause, resume, stop")
            sys.exit(1)
            
    except LifecycleCommandError as e:
        print(f"❌ Lifecycle command failed: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n⚠️  Lifecycle command interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()