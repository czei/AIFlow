#!/usr/bin/env python3
"""
PostToolUse Hook - Updates state after tool execution.

This hook runs after successful tool execution and updates project state
based on what was done (e.g., marking acceptance criteria as passed).
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone

# Add parent directory to path for imports (use append for safety)
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from src.state_manager import StateManager
    from src.hooks.workflow_rules import WorkflowRules
    from src.hooks.event_validator import EventValidator
except ImportError:
    # If imports fail, just exit
    sys.exit(0)


def main():
    """Main hook entry point."""
    try:
        # Read event data from stdin
        event_data = sys.stdin.read()
        event = json.loads(event_data)
        
        # Validate event data
        is_valid, validation_error = EventValidator.validate_post_tool_use(event)
        if not is_valid:
            print(json.dumps({
                "status": "error",
                "message": f"Invalid event data: {validation_error}",
                "action": "Check event format"
            }))
            print(f"PostToolUse hook error: Invalid event - {validation_error}", file=sys.stderr)
            return
        
        # Get current working directory
        cwd = event.get('cwd', '.')
        
        # Initialize StateManager
        state_manager = StateManager(cwd)
        
        # Try to read state
        try:
            state = state_manager.read()
        except FileNotFoundError:
            # No state file = nothing to update
            print(json.dumps({
                "status": "warning",
                "message": "No state file found - skipping post-tool processing"
            }))
            return
        except json.JSONDecodeError as e:
            # State file is corrupt
            print(json.dumps({
                "status": "error",
                "message": f"Corrupt state file: {e}",
                "action": "State updates skipped - manual intervention may be required"
            }))
            print(f"PostToolUse hook error: Corrupt state file - {e}", file=sys.stderr)
            return
        except PermissionError as e:
            # No permission to read state file
            print(json.dumps({
                "status": "error", 
                "message": f"Permission denied reading state: {e}",
                "action": "Check file permissions"
            }))
            print(f"PostToolUse hook error: Permission denied - {e}", file=sys.stderr)
            return
        except Exception as e:
            # Other unexpected errors
            print(json.dumps({
                "status": "error",
                "message": f"Unexpected error: {type(e).__name__}: {e}",
                "action": "Check logs for details"
            }))
            print(f"PostToolUse hook error: Unexpected error reading state - {e}", file=sys.stderr)
            return
            
        # Check if automation is active
        if not state.get('automation_active', False):
            # Automation not active = no updates needed
            return
            
        # Process tool execution
        tool = event.get('tool', '')
        workflow_step = state.get('workflow_step', '')
        
        # Update state based on tool usage
        updates = process_tool_execution(state, tool, event, workflow_step)
        
        # Check if workflow step might be complete
        if updates and workflow_step:
            completion_check = check_step_completion(state, workflow_step, updates)
            if completion_check:
                updates.update(completion_check)
        
        if updates:
            # Apply updates
            state_manager.update(updates)
            
            # Log significant updates
            if 'acceptance_criteria_passed' in updates:
                print(f"✅ Quality gate passed: {updates['acceptance_criteria_passed'][-1]}")
            if 'workflow_progress' in updates:
                progress = updates['workflow_progress']
                print(f"📊 Workflow progress: {progress.get('message', 'Step advancing')}")
                
    except json.JSONDecodeError as e:
        # Invalid JSON input from Claude Code
        print(f"PostToolUse hook error: Invalid JSON input - {e}", file=sys.stderr)
    except KeyError as e:
        # Missing expected fields in event data
        print(f"PostToolUse hook error: Missing required field - {e}", file=sys.stderr)
    except Exception as e:
        # Log unexpected errors but don't fail
        print(f"PostToolUse hook error: Unexpected error - {type(e).__name__}: {e}", file=sys.stderr)


def process_tool_execution(state: dict, tool: str, event: dict, workflow_step: str) -> dict:
    """
    Process tool execution and return state updates.
    """
    updates = {}
    
    # Initialize workflow progress tracking
    progress = state.get('workflow_progress', {})
    if workflow_step not in progress:
        progress[workflow_step] = {
            'started': datetime.now(timezone.utc).isoformat(),
            'tools_used': [],
            'files_modified': [],
            'tests_run': False,
            'build_success': False,
            'review_complete': False
        }
    
    step_progress = progress[workflow_step]
    
    # Track tool usage
    if tool not in step_progress['tools_used']:
        step_progress['tools_used'].append(tool)
    
    # Track file modifications
    if tool in ['Write', 'Edit', 'MultiEdit']:
        file_path = event.get('input', {}).get('file_path', '')
        if file_path:
            files_modified = state.get('files_modified', [])
            if file_path not in files_modified:
                files_modified.append(file_path)
                updates['files_modified'] = files_modified
            
            # Track in workflow progress
            if file_path not in step_progress['files_modified']:
                step_progress['files_modified'].append(file_path)
                
    # Track test execution
    elif tool == 'Bash':
        command = event.get('input', {}).get('command', '')
        exit_code = event.get('exit_code', 0)
        
        # Check for test commands
        if any(test_cmd in command for test_cmd in ['pytest', 'npm test', 'cargo test', 'go test', 'rspec']):
            step_progress['tests_run'] = True
            if exit_code == 0:
                # Tests passed
                gates = state.get('acceptance_criteria_passed', [])
                if 'existing_tests' not in gates:
                    gates.append('existing_tests')
                    updates['acceptance_criteria_passed'] = gates
                    
        # Check for build commands
        elif any(build_cmd in command for build_cmd in ['make', 'npm run build', 'cargo build', 'go build']):
            if exit_code == 0:
                step_progress['build_success'] = True
                # Build succeeded
                gates = state.get('acceptance_criteria_passed', [])
                if 'compilation' not in gates:
                    gates.append('compilation')
                    updates['acceptance_criteria_passed'] = gates
                    
        # Check for lint commands
        elif any(lint_cmd in command for lint_cmd in ['eslint', 'pylint', 'flake8', 'cargo clippy', 'rubocop']):
            if exit_code == 0:
                # Linting passed
                gates = state.get('acceptance_criteria_passed', [])
                if 'lint' not in gates:
                    gates.append('lint')
                    updates['acceptance_criteria_passed'] = gates
                    
    # Track code review usage
    elif tool == 'mcp__zen__codereview':
        step_progress['review_complete'] = True
        gates = state.get('acceptance_criteria_passed', [])
        if 'review' not in gates:
            gates.append('review')
            updates['acceptance_criteria_passed'] = gates
    
    # Track TodoWrite for planning completion
    elif tool == 'TodoWrite' and workflow_step == 'planning':
        # Check if implementation tasks were created
        if event.get('input', {}).get('todos'):
            step_progress['planning_complete'] = True
    
    # Update workflow progress
    updates['workflow_progress'] = progress
            
    # Always update last_updated
    if updates:
        updates['last_updated'] = datetime.now(timezone.utc).isoformat()
        
    return updates


def check_step_completion(state: dict, workflow_step: str, updates: dict) -> dict:
    """
    Check if the current workflow step is complete based on progress indicators.
    
    Returns dict with potential workflow advancement.
    """
    completion_updates = {}
    
    # Get completion indicators from WorkflowRules
    indicators = WorkflowRules.get_step_completion_indicators(workflow_step)
    if not indicators:
        return completion_updates
    
    # Get current progress
    progress = updates.get('workflow_progress', state.get('workflow_progress', {}))
    step_progress = progress.get(workflow_step, {})
    
    # Use consolidated logic from WorkflowRules
    is_complete, completion_message = WorkflowRules.is_step_complete(workflow_step, step_progress)
    
    if is_complete:
        completion_updates['workflow_progress'] = {
            'step': workflow_step,
            'complete': True,
            'message': completion_message,
            'ready_for_next': indicators.get('next_step', 'planning')
        }
    
    return completion_updates


if __name__ == '__main__':
    main()