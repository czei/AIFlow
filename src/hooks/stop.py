#!/usr/bin/env python3
"""
Stop Hook - Advances workflow steps when conditions are met.

This hook runs after Claude finishes responding and can automatically
advance to the next workflow step if the current step is complete.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone

# Add parent directory to path for imports (use append for safety)
sys.path.append(str(Path(__file__).parent.parent))

try:
    from state_manager import StateManager
    from hooks.workflow_rules import WorkflowRules
except ImportError:
    # If no StateManager or WorkflowRules, just exit
    sys.exit(0)


# Define workflow sequence
WORKFLOW_SEQUENCE = [
    "planning",
    "implementation", 
    "validation",
    "review",
    "refinement",
    "integration"
]


def main():
    """Main hook entry point."""
    try:
        # Read event data from stdin
        event_data = sys.stdin.read()
        event = json.loads(event_data)
        
        # Get current working directory
        cwd = event.get('cwd', '.')
        
        # Initialize StateManager
        state_manager = StateManager(cwd)
        
        # Try to read state
        try:
            state = state_manager.read()
        except FileNotFoundError:
            # No state file = nothing to do
            return
        except Exception:
            # Other errors - just log and continue
            return
            
        # Check if automation is active
        if not state.get('automation_active', False):
            # Automation not active = no advancement
            return
            
        # Check if current step is complete
        workflow_step = state.get('workflow_step', 'planning')
        
        # Check workflow progress for completion signals
        workflow_progress = state.get('workflow_progress', {})
        step_progress = workflow_progress.get(workflow_step, {})
        
        # Use enhanced completion detection
        if should_advance_workflow(state, workflow_step, step_progress):
            # Get next step from WorkflowRules
            indicators = WorkflowRules.get_step_completion_indicators(workflow_step)
            next_step = indicators.get('next_step', 'planning')
            
            # Handle phase transition (integration → planning means new phase)
            if workflow_step == 'integration' and next_step == 'planning':
                # Complete current phase
                complete_phase(state_manager, state)
            else:
                # Regular step advancement
                updates = {
                    'workflow_step': next_step,
                    'last_updated': datetime.now(timezone.utc).isoformat(),
                    'automation_cycles': state.get('automation_cycles', 0) + 1
                }
                
                # Preserve quality gates for validation → review transition
                if not (workflow_step == 'validation' and next_step == 'review'):
                    updates['quality_gates_passed'] = []
                
                state_manager.update(updates)
                
                print(f"\n✅ Advanced to {next_step} phase")
                print(f"📋 {get_step_guidance(next_step)}\n")
                
                # Show suggestions for the new step
                _, _, suggestions = WorkflowRules.evaluate_tool_use(next_step, '', {})
                if suggestions:
                    print("💡 Suggestions:")
                    for suggestion in suggestions:
                        print(f"   • {suggestion}")
                    print()
                
    except json.JSONDecodeError:
        # Invalid JSON input
        pass
    except Exception as e:
        # Log error but don't fail
        print(f"Stop hook error: {str(e)}", file=sys.stderr)


def should_advance_workflow(state: dict, workflow_step: str, step_progress: dict) -> bool:
    """
    Determine if the current workflow step is complete and ready to advance.
    Uses workflow progress tracking for more accurate detection.
    """
    # First check if PostToolUse already marked it complete
    last_progress = state.get('workflow_progress', {})
    if isinstance(last_progress, dict) and last_progress.get('complete'):
        return True
    
    # Otherwise use step-specific logic
    if workflow_step == 'planning':
        # Advance if planning is marked complete (todo list created)
        return step_progress.get('planning_complete', False)
        
    elif workflow_step == 'implementation':
        # Advance if files have been modified
        return len(step_progress.get('files_modified', [])) > 0
        
    elif workflow_step == 'validation':
        # Advance if tests have been run
        return step_progress.get('tests_run', False)
        
    elif workflow_step == 'review':
        # Advance if review is complete
        return step_progress.get('review_complete', False)
        
    elif workflow_step == 'refinement':
        # Advance if edits were made after review
        return 'Edit' in step_progress.get('tools_used', [])
        
    elif workflow_step == 'integration':
        # Complete if git operations were performed
        git_tools = [t for t in step_progress.get('tools_used', []) if 'Git' in t or 'git' in t]
        bash_git = False
        
        # Also check for git commands in Bash
        if 'Bash' in step_progress.get('tools_used', []):
            # This is a simple heuristic - in production would analyze actual commands
            bash_git = True
            
        return len(git_tools) > 0 or bash_git
        
    return False


def get_step_guidance(step: str) -> str:
    """Get guidance message for the next workflow step."""
    guidance = {
        'planning': "Analyze requirements and design your approach",
        'implementation': "Write production-quality code",
        'validation': "Run tests and verify functionality",
        'review': "Perform code review and analysis",
        'refinement': "Address feedback and improve quality",
        'integration': "Final testing, documentation, and commit"
    }
    return guidance.get(step, "Continue with next step")


def complete_phase(state_manager, state: dict):
    """Complete the current phase and prepare for next."""
    phase_info = state.get('phase_info', {})
    current_phase = phase_info.get('current', 'unknown')
    phase_num = phase_info.get('current_number', 1)
    total_phases = phase_info.get('total', 1)
    
    # Mark phase as complete
    completed_phases = state.get('completed_phases', [])
    if current_phase not in completed_phases:
        completed_phases.append(current_phase)
    
    # Calculate compliance score
    metrics = state.get('metrics', {})
    compliance_score = WorkflowRules.calculate_compliance_score(metrics)
    
    updates = {
        'workflow_step': 'planning',
        'quality_gates_passed': [],
        'files_modified': [],
        'completed_phases': completed_phases,
        'last_updated': datetime.now(timezone.utc).isoformat(),
        'workflow_progress': {},  # Reset progress tracking
        'metrics': {  # Reset metrics for next phase
            'tools_allowed': 0,
            'tools_blocked': 0,
            'emergency_overrides': 0,
            'workflow_violations': 0
        }
    }
    
    print(f"\n🎉 Phase completed: {current_phase}")
    print(f"📊 Workflow compliance score: {compliance_score:.1f}%")
    
    # Check if there are more phases
    if phase_num < total_phases:
        # Advance to next phase
        next_phase_num = phase_num + 1
        updates['phase_info'] = {
            'current_number': next_phase_num,
            'total': total_phases
        }
        print(f"\n📋 Ready for Phase {next_phase_num}/{total_phases}")
        print("Use /user:project:advance to move to the next phase\n")
    else:
        # All phases complete
        updates['status'] = 'completed'
        updates['automation_active'] = False
        print(f"\n🏆 All {total_phases} phases completed!")
        print("Project automation complete. Use /user:project:status for summary.\n")
    
    state_manager.update(updates)


if __name__ == '__main__':
    main()