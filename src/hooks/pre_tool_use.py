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
sys.path.append(str(Path(__file__).parent.parent))

try:
    from state_manager import StateManager
    from hooks.workflow_rules import WorkflowRules
except ImportError as e:
    # If no StateManager or WorkflowRules, allow all operations
    print(json.dumps({"allow": True, "warning": f"Import error: {str(e)}"}))
    sys.exit(0)


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
            # No state file = allow all operations
            print(json.dumps({"allow": True}))
            return
        except Exception as e:
            # Other errors - log but allow
            print(json.dumps({"allow": True, "warning": f"State read error: {str(e)}"}))
            return
            
        # Check if automation is active
        if not state.get('automation_active', False):
            # Automation not active = allow all operations
            print(json.dumps({"allow": True}))
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
        
        # Update state with metrics (async, don't block on this)
        try:
            state_manager.update({'metrics': metrics})
        except Exception:
            pass  # Don't fail the hook on metrics update
        
        # Build response
        result = {"allow": allow}
        if not allow:
            if message:
                result["message"] = message
            if suggestions:
                result["suggestions"] = suggestions
                
        print(json.dumps(result))
        
    except json.JSONDecodeError:
        # Invalid JSON input
        print(json.dumps({
            "allow": True,
            "warning": "Invalid JSON input to hook"
        }))
    except Exception as e:
        # On error, allow operation but log
        print(json.dumps({
            "allow": True,
            "warning": f"Hook error: {str(e)}"
        }))


if __name__ == '__main__':
    main()