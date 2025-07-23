"""
Status Command - Display comprehensive project progress and status.

Provides detailed reporting of project state, phase progress, quality gates,
workflow status, and automation information.
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timezone

from ..state_manager import StateManager, StateValidationError
from ..git_operations import GitOperations, GitOperationError


class StatusCommandError(Exception):
    """Raised when status command fails."""
    pass


class StatusCommand:
    """
    Implements project status reporting functionality.
    
    Displays comprehensive project status including phase progress,
    quality gates, workflow state, and git information.
    """
    
    def __init__(self, project_path: Optional[str] = None):
        """
        Initialize status command.
        
        Args:
            project_path: Path to project directory. Defaults to current directory.
        """
        self.project_path = Path(project_path or ".").resolve()
        self.state_manager = StateManager(str(self.project_path))
        
        try:
            self.git_ops = GitOperations(str(self.project_path))
        except GitOperationError:
            # Git operations optional for status display
            self.git_ops = None
            
    def execute(self) -> Dict[str, Any]:
        """
        Execute status reporting.
        
        Returns:
            Dictionary containing status information
            
        Raises:
            StatusCommandError: If status reporting fails
        """
        try:
            # Load project state
            state = self.state_manager.read()
            
            # Get git context if available
            git_context = self._get_git_context()
            
            # Generate status report
            status_report = self._generate_status_report(state, git_context)
            
            # Display status
            self._display_status(status_report)
            
            return status_report
            
        except StateValidationError as e:
            raise StatusCommandError(f"Failed to read project state: {e}")
        except Exception as e:
            raise StatusCommandError(f"Status reporting failed: {e}")
            
    def _get_git_context(self) -> Optional[Dict[str, Any]]:
        """Get git context information if available."""
        if not self.git_ops:
            return None
            
        try:
            context = self.git_ops.get_repo_context()
            commit_hash = self.git_ops.get_current_commit(self.project_path)
            
            return {
                "current_branch": context.current_branch,
                "is_clean": context.is_clean,
                "has_remote": context.has_remote,
                "remote_url": context.remote_url,
                "uncommitted_changes": context.uncommitted_changes,
                "current_commit": commit_hash,
                "worktree_path": str(self.project_path)
            }
        except GitOperationError:
            return None
            
    def _generate_status_report(
        self, 
        state: Dict[str, Any], 
        git_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate comprehensive status report."""
        
        # Calculate time information
        started_time = datetime.fromisoformat(state["started"].replace('Z', '+00:00'))
        last_updated_time = datetime.fromisoformat(state["last_updated"].replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        
        duration = now - started_time
        time_since_update = now - last_updated_time
        
        # Generate phase progress
        phase_progress = self._analyze_phase_progress(state)
        
        # Generate quality metrics
        quality_metrics = self._calculate_quality_metrics(state)
        
        # Generate next actions
        next_actions = self._determine_next_actions(state)
        
        return {
            "project_info": {
                "name": state["project_name"],
                "current_phase": state["current_phase"],
                "status": state["status"],
                "automation_active": state["automation_active"],
                "workflow_step": state["workflow_step"],
                "current_objective": state["current_objective"],
                "started": started_time,
                "last_updated": last_updated_time,
                "duration": duration,
                "time_since_update": time_since_update
            },
            "git_context": git_context,
            "phase_progress": phase_progress,
            "quality_metrics": quality_metrics,
            "next_actions": next_actions,
            "raw_state": state
        }
        
    def _analyze_phase_progress(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze phase progress and completion."""
        current_phase = state["current_phase"]
        completed_phases = state["completed_phases"]
        quality_gates = state["quality_gates_passed"]
        
        # Define standard phases
        standard_phases = ["01", "02", "03", "04", "05"]
        phase_names = {
            "01": "Planning",
            "02": "Architecture", 
            "03": "Implementation",
            "04": "Testing",
            "05": "Deployment"
        }
        
        phases_status = []
        for phase in standard_phases:
            if phase in completed_phases:
                status = "completed"
                progress = 100
            elif phase == current_phase:
                status = "in_progress"
                progress = self._estimate_phase_progress(state)
            elif self._is_phase_before(phase, current_phase):
                status = "completed"
                progress = 100
            else:
                status = "pending"
                progress = 0
                
            phases_status.append({
                "phase": phase,
                "name": phase_names.get(phase, f"Phase {phase}"),
                "status": status,
                "progress": progress
            })
            
        return {
            "phases": phases_status,
            "current_phase_name": phase_names.get(current_phase, f"Phase {current_phase}"),
            "completed_count": len(completed_phases),
            "total_count": len(standard_phases),
            "overall_progress": self._calculate_overall_progress(phases_status)
        }
        
    def _estimate_phase_progress(self, state: Dict[str, Any]) -> int:
        """Estimate progress within current phase based on quality gates."""
        quality_gates = state["quality_gates_passed"]
        workflow_step = state["workflow_step"]
        
        # Basic progress estimation based on workflow step
        step_progress = {
            "planning": 10,
            "implementation": 40,
            "validation": 60,
            "review": 75,
            "refinement": 85,
            "integration": 95
        }
        
        base_progress = step_progress.get(workflow_step, 0)
        
        # Add bonus for quality gates passed
        gate_bonus = min(len(quality_gates) * 5, 20)
        
        return min(base_progress + gate_bonus, 95)  # Never show 100% until completed
        
    def _is_phase_before(self, phase1: str, phase2: str) -> bool:
        """Check if phase1 comes before phase2."""
        try:
            return int(phase1) < int(phase2)
        except ValueError:
            return False
            
    def _calculate_overall_progress(self, phases_status: list) -> int:
        """Calculate overall project progress percentage."""
        if not phases_status:
            return 0
            
        total_progress = sum(phase["progress"] for phase in phases_status)
        return int(total_progress / len(phases_status))
        
    def _calculate_quality_metrics(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate quality metrics and statistics."""
        automation_cycles = state["automation_cycles"]
        quality_gates = state["quality_gates_passed"]
        
        # Time calculations
        started = datetime.fromisoformat(state["started"].replace('Z', '+00:00'))
        last_updated = datetime.fromisoformat(state["last_updated"].replace('Z', '+00:00'))
        duration = last_updated - started
        
        return {
            "automation_cycles": automation_cycles,
            "quality_gates_passed": len(quality_gates),
            "quality_gates_list": quality_gates,
            "project_duration_days": duration.days,
            "project_duration_hours": duration.total_seconds() / 3600,
            "average_cycle_time": duration.total_seconds() / max(automation_cycles, 1) / 3600,
            "gates_per_cycle": len(quality_gates) / max(automation_cycles, 1)
        }
        
    def _determine_next_actions(self, state: Dict[str, Any]) -> list:
        """Determine recommended next actions based on current state."""
        actions = []
        status = state["status"]
        workflow_step = state["workflow_step"]
        current_objective = state["current_objective"]
        
        if status == "setup":
            actions.extend([
                "Customize phase files in phases/ directory with project-specific objectives",
                "Edit CLAUDE.md with project context and requirements", 
                "Run /user:project:doctor to validate project setup",
                "Run /user:project:start to begin automated development"
            ])
        elif status == "active":
            if workflow_step == "planning":
                actions.append(f"Continue planning for: {current_objective or 'current objective'}")
            elif workflow_step == "implementation":
                actions.append(f"Continue implementation of: {current_objective or 'current objective'}")
            elif workflow_step == "validation":
                actions.append("Run tests and validate implementation")
            elif workflow_step == "review":
                actions.append("Complete code review and address feedback")
            elif workflow_step == "refinement":
                actions.append("Address review feedback and optimize implementation")
            elif workflow_step == "integration":
                actions.append("Complete integration and finalize objective")
                
            actions.extend([
                "Monitor progress with /user:project:status",
                "Pause automation with /user:project:pause if needed"
            ])
        elif status == "paused":
            actions.extend([
                "Resume automation with /user:project:resume",
                "Review current progress and make manual adjustments if needed",
                "Use /user:project:update to modify project state if necessary"
            ])
        elif status == "completed":
            actions.extend([
                "Review project completion summary",
                "Consider next phase or project iteration",
                "Archive project state for future reference"
            ])
        elif status == "error":
            actions.extend([
                "Review error logs and project state",
                "Fix identified issues manually",
                "Use /user:project:update to correct project state",
                "Resume with /user:project:resume or restart with /user:project:start"
            ])
            
        return actions
        
    def _display_status(self, report: Dict[str, Any]) -> None:
        """Display formatted status report."""
        info = report["project_info"]
        git = report["git_context"]
        phases = report["phase_progress"]
        quality = report["quality_metrics"]
        actions = report["next_actions"]
        
        print("=" * 60)
        print(f"📊 PROJECT STATUS: {info['name'].upper()}")
        print("=" * 60)
        
        # Git Context
        if git:
            print(f"\n🔧 Git Context:")
            print(f"   Worktree: {git['worktree_path']}")
            print(f"   Branch: {git['current_branch']}")
            print(f"   Commit: {git['current_commit'][:8]}")
            if git['has_remote']:
                print(f"   Remote: {git['remote_url']}")
            
            if not git['is_clean']:
                print(f"   ⚠️  Uncommitted changes: {len(git['uncommitted_changes'])} files")
            else:
                print(f"   ✅ Working tree clean")
        
        # Project Progress
        print(f"\n📈 Project Progress:")
        print(f"   Current Phase: {phases['current_phase_name']}")
        
        status_emoji = {
            "setup": "🔧", "active": "🚀", "paused": "⏸️", 
            "stopped": "⏹️", "completed": "✅", "error": "❌"
        }
        print(f"   Status: {status_emoji.get(info['status'], '❓')} {info['status'].title()}")
        
        if info['automation_active']:
            print(f"   Automation: 🤖 ACTIVE")
        else:
            print(f"   Automation: 😴 DISABLED")
            
        if info['workflow_step']:
            step_emoji = {
                "planning": "📋", "implementation": "⚙️", "validation": "🧪",
                "review": "👀", "refinement": "✨", "integration": "🔗"
            }
            print(f"   Workflow Step: {step_emoji.get(info['workflow_step'], '❓')} {info['workflow_step'].title()}")
            
        if info['current_objective']:
            print(f"   Current Objective: {info['current_objective']}")
            
        print(f"   Overall Progress: {phases['overall_progress']}%")
        
        # Phase Status
        print(f"\n📊 Phase Status:")
        for phase_info in phases['phases']:
            status_icon = {
                "completed": "✅", "in_progress": "🔄", "pending": "⏳"
            }
            icon = status_icon.get(phase_info['status'], '❓')
            print(f"   {icon} Phase {phase_info['phase']}: {phase_info['name']} ({phase_info['progress']}%)")
            
        # Quality Metrics
        print(f"\n📋 Quality Metrics:")
        print(f"   Project Duration: {quality['project_duration_days']} days, {quality['project_duration_hours']:.1f} hours")
        print(f"   Automation Cycles: {quality['automation_cycles']}")
        if quality['automation_cycles'] > 0:
            print(f"   Average Cycle Time: {quality['average_cycle_time']:.1f} hours")
        print(f"   Quality Gates Passed: {quality['quality_gates_passed']}")
        if quality['quality_gates_list']:
            gates_str = ", ".join(quality['quality_gates_list'])
            print(f"   Gates: {gates_str}")
            
        # Time Information
        print(f"\n⏰ Timing:")
        print(f"   Started: {info['started'].strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print(f"   Last Updated: {info['last_updated'].strftime('%Y-%m-%d %H:%M:%S UTC')}")
        
        hours_since_update = info['time_since_update'].total_seconds() / 3600
        if hours_since_update < 1:
            print(f"   Last Activity: {int(info['time_since_update'].total_seconds() / 60)} minutes ago")
        elif hours_since_update < 24:
            print(f"   Last Activity: {hours_since_update:.1f} hours ago")
        else:
            print(f"   Last Activity: {info['time_since_update'].days} days ago")
            
        # Next Actions
        if actions:
            print(f"\n🎯 Recommended Next Actions:")
            for i, action in enumerate(actions, 1):
                print(f"   {i}. {action}")
                
        print(f"\n{'=' * 60}")


def main():
    """Command-line interface for status command."""
    project_path = sys.argv[1] if len(sys.argv) > 1 else None
    
    try:
        status_cmd = StatusCommand(project_path)
        status_cmd.execute()
        
    except StatusCommandError as e:
        print(f"❌ Status command failed: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n⚠️  Status command interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()