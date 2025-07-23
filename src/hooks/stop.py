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

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from state_manager import StateManager
except ImportError:
    # If no StateManager, just exit
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
        except:
            # No state file = nothing to do
            return
            
        # Check if automation is active
        if not state.get('automation_active', False):
            # Automation not active = no advancement
            return
            
        # Check if current step is complete
        workflow_step = state.get('workflow_step', 'planning')
        
        if should_advance_workflow(state, workflow_step):
            # Get next step
            try:
                current_idx = WORKFLOW_SEQUENCE.index(workflow_step)
                if current_idx < len(WORKFLOW_SEQUENCE) - 1:
                    next_step = WORKFLOW_SEQUENCE[current_idx + 1]
                    
                    # Update state
                    state_manager.update({
                        'workflow_step': next_step,
                        'quality_gates_passed': [],  # Reset gates for new step
                        'last_updated': datetime.now(timezone.utc).isoformat(),
                        'automation_cycles': state.get('automation_cycles', 0) + 1
                    })
                    
                    print(f"\n✅ Advanced to {next_step} phase")
                    print(f"Continue with: {get_step_guidance(next_step)}\n")
                else:
                    # Completed all steps for this objective
                    complete_objective(state_manager, state)
                    
            except ValueError:
                # Unknown workflow step
                pass
                
    except Exception as e:
        # Log error but don't fail
        print(f"Stop hook error: {str(e)}", file=sys.stderr)


def should_advance_workflow(state: dict, workflow_step: str) -> bool:
    """
    Determine if the current workflow step is complete and ready to advance.
    """
    gates = state.get('quality_gates_passed', [])
    
    if workflow_step == 'planning':
        # Advance if objective is set and some analysis done
        return state.get('current_objective') is not None
        
    elif workflow_step == 'implementation':
        # Advance if files have been modified
        return len(state.get('files_modified', [])) > 0
        
    elif workflow_step == 'validation':
        # Advance if tests have passed
        return 'existing_tests' in gates or 'new_tests' in gates
        
    elif workflow_step == 'review':
        # Advance if review is complete
        return 'review' in gates
        
    elif workflow_step == 'refinement':
        # Advance if integration tests pass
        return 'integration' in gates or len(gates) > 0
        
    elif workflow_step == 'integration':
        # Complete if documentation and final tests done
        return 'documentation' in gates or 'performance' in gates
        
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


def complete_objective(state_manager, state: dict):
    """Complete the current objective and prepare for next."""
    completed = state.get('completed_objectives', [])
    current = state.get('current_objective', 'Unknown objective')
    
    if current not in completed:
        completed.append(current)
        
    state_manager.update({
        'current_objective': None,
        'workflow_step': 'planning',
        'quality_gates_passed': [],
        'files_modified': [],
        'completed_objectives': completed,
        'last_updated': datetime.now(timezone.utc).isoformat()
    })
    
    print(f"\n🎉 Objective completed: {current}")
    print("Ready for next objective. Update with /user:project:update current_objective \"Your next task\"\n")


if __name__ == '__main__':
    main()