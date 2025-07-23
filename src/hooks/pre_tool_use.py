#!/usr/bin/env python3
"""
PreToolUse Hook - Enforces workflow rules based on current state.

This hook runs before any tool execution and can block operations
that violate the current workflow step rules.
"""

import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from state_manager import StateManager
except ImportError:
    # If no StateManager, allow all operations
    print(json.dumps({"allow": True}))
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
        except:
            # No state file = allow all operations
            print(json.dumps({"allow": True}))
            return
            
        # Check if automation is active
        if not state.get('automation_active', False):
            # Automation not active = allow all operations
            print(json.dumps({"allow": True}))
            return
            
        # Get current workflow step and tool
        workflow_step = state.get('workflow_step', 'planning')
        tool = event.get('tool', '')
        
        # Apply workflow rules
        allow, message = apply_workflow_rules(workflow_step, tool, event)
        
        # Return decision
        result = {"allow": allow}
        if not allow and message:
            result["message"] = message
            
        print(json.dumps(result))
        
    except Exception as e:
        # On error, allow operation but log
        print(json.dumps({
            "allow": True,
            "warning": f"Hook error: {str(e)}"
        }), file=sys.stderr)


def apply_workflow_rules(workflow_step: str, tool: str, event: dict) -> tuple[bool, str]:
    """
    Apply workflow-specific rules to tool usage.
    
    Returns: (allow, message)
    """
    # Planning phase rules
    if workflow_step == 'planning':
        # Block code writing tools
        if tool in ['Write', 'Edit', 'MultiEdit']:
            return False, "🚫 Planning phase: Complete requirements analysis before writing code. Focus on understanding the problem and designing the approach."
            
        # Block compilation/build commands
        if tool == 'Bash':
            command = event.get('input', {}).get('command', '')
            if any(cmd in command for cmd in ['make', 'npm run build', 'cargo build', 'go build']):
                return False, "🚫 Planning phase: Focus on requirements, not building. Code implementation comes in the next phase."
                
    # Validation phase rules
    elif workflow_step == 'validation':
        # Require tests before commits
        if tool == 'Bash':
            command = event.get('input', {}).get('command', '')
            if 'git commit' in command:
                # This is a simplified check - in production, check state for test results
                return False, "🚫 Validation phase: Ensure all tests pass before committing. Run tests first."
                
    # Review phase rules
    elif workflow_step == 'review':
        # Discourage major changes during review
        if tool in ['Write', 'MultiEdit']:
            return True, "⚠️  Review phase: Major changes should wait for refinement phase."
            
    # All other cases: allow
    return True, ""


if __name__ == '__main__':
    main()