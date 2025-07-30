#!/usr/bin/env python3
"""
PreToolUse Hook - Enforces workflow rules based on current state.

This hook runs before any tool execution and can block operations
that violate the current workflow step rules.
"""

import json
import sys
import os
from pathlib import Path

# Add parent directory to path for imports (use append for safety)
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from src.state_manager import StateManager
    from src.hooks.workflow_rules import WorkflowRules
    from src.hooks.hook_utils import EventParser, ResponseBuilder, HookLogger
    from src.hooks.event_validator import EventValidator
except ImportError as e:
    # If imports fail, allow all operations
    print(json.dumps({"decision": "allow", "message": f"Import error: {str(e)}"}))
    sys.exit(0)


def main():
    """Main hook entry point."""
    # Parse event from stdin
    event, error = EventParser.parse_stdin()
    if error:
        print(ResponseBuilder.error(error))
        return
    
    # Validate event data
    is_valid, validation_error = EventValidator.validate_pre_tool_use(event)
    if not is_valid:
        HookLogger.error(f"Invalid event data: {validation_error}")
        print(ResponseBuilder.error(f"Invalid event data: {validation_error}"))
        return
    
    try:
        # Get current working directory
        cwd = event.get('cwd', '.')
        
        # Initialize StateManager
        state_manager = StateManager(cwd)
        
        # Try to read state
        try:
            state = state_manager.read()
        except FileNotFoundError:
            # No state file = allow all operations
            print(ResponseBuilder.allow())
            return
        except Exception as e:
            # Other errors - log but allow
            HookLogger.error(f"State read error: {str(e)}")
            print(ResponseBuilder.allow(f"State read error: {str(e)}"))
            return
            
        # Check if automation is active
        if not state.get('automation_active', False):
            # Automation not active = allow all operations
            print(ResponseBuilder.allow())
            return
            
        # Get current workflow step and tool
        workflow_step = state.get('workflow_step', 'planning')
        tool = event.get('tool', '')
        
        # Use WorkflowRules engine
        allow, message, suggestions = WorkflowRules.evaluate_tool_use(
            workflow_step, tool, {'event': event}
        )
        
        # Update metrics
        metrics = state.get('metrics', {})
        if allow:
            metrics['tools_allowed'] = metrics.get('tools_allowed', 0) + 1
        else:
            metrics['tools_blocked'] = metrics.get('tools_blocked', 0) + 1
        
        # Check for emergency override
        if allow and WorkflowRules._check_emergency_override({'event': event}):
            metrics['emergency_overrides'] = metrics.get('emergency_overrides', 0) + 1
            # Notify about emergency override
            from src.hooks.hook_utils import notify_emergency_override
            notify_emergency_override()
        
        # Update state with metrics
        try:
            state_manager.update({'metrics': metrics})
        except Exception as e:
            # Log error but don't fail the hook
            HookLogger.error(f"Failed to update metrics: {str(e)}")
            # Include warning in response
            if allow:
                print(ResponseBuilder.allow(f"Warning: metrics update failed - {str(e)}"))
            else:
                print(ResponseBuilder.deny(message, suggestions))
            return
        
        # Build and send response
        if allow:
            print(ResponseBuilder.allow())
        else:
            print(ResponseBuilder.deny(message, suggestions))
                
    except Exception as e:
        # On error, allow operation but log
        HookLogger.error(f"Hook error: {str(e)}")
        print(ResponseBuilder.error(f"Hook error: {str(e)}"))


if __name__ == '__main__':
    main()