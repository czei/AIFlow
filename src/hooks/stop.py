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
    from hooks.event_validator import EventValidator
except ImportError:
    # If imports fail, just exit
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
        
        # Validate event data
        is_valid, validation_error = EventValidator.validate_stop(event)
        if not is_valid:
            print(json.dumps({
                "status": "error",
                "message": f"Invalid event data: {validation_error}",
                "action": "Check event format"
            }))
            print(f"Stop hook error: Invalid event - {validation_error}", file=sys.stderr)
            return
        
        # Get current working directory
        cwd = event.get('cwd', '.')
        
        # Initialize StateManager
        state_manager = StateManager(cwd)
        
        # Try to read state
        try:
            state = state_manager.read()
        except FileNotFoundError:
            # No state file = nothing to do. This is expected for non-project directories
            # Silent exit for non-project directories
            return
        except json.JSONDecodeError as e:
            # State file is corrupt
            print(json.dumps({
                "status": "error",
                "message": f"Corrupt state file preventing workflow advancement: {e}",
                "action": "Manual intervention required to fix state file"
            }))
            print(f"Stop hook error: Corrupt state file - {e}", file=sys.stderr)
            return
        except PermissionError as e:
            # No permission to read state file
            print(json.dumps({
                "status": "error",
                "message": f"Permission denied accessing state: {e}",
                "action": "Check file permissions for .project-state.json"
            }))
            print(f"Stop hook error: Permission denied - {e}", file=sys.stderr)
            return
        except Exception as e:
            # Other unexpected errors
            print(json.dumps({
                "status": "error",
                "message": f"Unexpected error in workflow automation: {type(e).__name__}: {e}",
                "action": "Check logs and report issue if persistent"
            }))
            print(f"Stop hook error: Unexpected error reading state - {e}", file=sys.stderr)
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
            
            # Handle sprint transition (integration → planning means new sprint)
            if workflow_step == 'integration' and next_step == 'planning':
                # Complete current sprint
                complete_sprint(state_manager, state)
            else:
                # Regular step advancement
                updates = {
                    'workflow_step': next_step,
                    'last_updated': datetime.now(timezone.utc).isoformat(),
                    'automation_cycles': state.get('automation_cycles', 0) + 1
                }
                
                # Preserve acceptance criteria for validation → review transition
                # For other transitions, don't reset acceptance_criteria_passed
                # Each step should add to the existing list
                
                state_manager.update(updates)
                
                print(f"\n✅ Advanced to {next_step} sprint")
                print(f"📋 {get_step_guidance(next_step)}\n")
                
                # Show suggestions for the new step
                _, _, suggestions = WorkflowRules.evaluate_tool_use(next_step, '', {})
                if suggestions:
                    print("💡 Suggestions:")
                    for suggestion in suggestions:
                        print(f"   • {suggestion}")
                    print()
                
    except json.JSONDecodeError as e:
        # Invalid JSON input from Claude Code
        print(f"Stop hook error: Invalid JSON input - {e}", file=sys.stderr)
    except KeyError as e:
        # Missing expected fields in event data
        print(f"Stop hook error: Missing required field - {e}", file=sys.stderr)
    except Exception as e:
        # Log unexpected errors but don't fail
        print(f"Stop hook error: Unexpected error - {type(e).__name__}: {e}", file=sys.stderr)


def should_advance_workflow(state: dict, workflow_step: str, step_progress: dict) -> bool:
    """
    Determine if the current workflow step is complete and ready to advance.
    Uses workflow progress tracking for more accurate detection.
    """
    # First check if PostToolUse already marked it complete
    last_progress = state.get('workflow_progress', {})
    if isinstance(last_progress, dict) and last_progress.get('complete'):
        return True
    
    # Use consolidated logic from WorkflowRules
    is_complete, _ = WorkflowRules.is_step_complete(workflow_step, step_progress)
    return is_complete


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


def complete_sprint(state_manager, state: dict):
    """Complete the current sprint and prepare for next."""
    # Get current sprint from state (not sprint_info)
    current_sprint = state.get('current_sprint', 'unknown')
    
    # Extract sprint number if it's in format like "01", "02", etc.
    try:
        sprint_num = int(current_sprint) if current_sprint.isdigit() else 1
    except:
        sprint_num = 1
    
    # For now, assume 5 total sprints (can be made configurable later)
    total_sprints = 5
    
    # Mark sprint as complete
    completed_sprints = state.get('completed_sprints', [])
    if current_sprint not in completed_sprints:
        completed_sprints.append(current_sprint)
    
    # Calculate compliance score
    metrics = state.get('metrics', {})
    compliance_score = WorkflowRules.calculate_compliance_score(metrics)
    
    updates = {
        'workflow_step': 'planning',
        # Don't reset acceptance_criteria_passed and files_modified - preserve them
        'completed_sprints': completed_sprints,
        'last_updated': datetime.now(timezone.utc).isoformat(),
        'workflow_progress': {},  # Reset progress tracking
        'metrics': {  # Reset metrics for next sprint
            'tools_allowed': 0,
            'tools_blocked': 0,
            'emergency_overrides': 0,
            'workflow_violations': 0
        }
    }
    
    print(f"\n🎉 Sprint completed: {current_sprint}")
    print(f"📊 Workflow compliance score: {compliance_score:.1f}%")
    
    # Check if there are more sprints
    if sprint_num < total_sprints:
        # Advance to next sprint
        next_sprint_num = sprint_num + 1
        updates['sprint_info'] = {
            'current_number': next_sprint_num,
            'total': total_sprints
        }
        print(f"\n📋 Ready for Sprint {next_sprint_num}/{total_sprints}")
        print("Use /user:project:advance to move to the next sprint\n")
    else:
        # All sprints complete
        updates['status'] = 'completed'
        updates['automation_active'] = False
        print(f"\n🏆 All {total_sprints} sprints completed!")
        print("Project automation complete. Use /user:project:status for summary.\n")
    
    state_manager.update(updates)


if __name__ == '__main__':
    main()