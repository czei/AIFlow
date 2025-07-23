#!/usr/bin/env python3
"""
PostToolUse Hook - Updates state after tool execution.

This hook runs after successful tool execution and updates project state
based on what was done (e.g., marking quality gates as passed).
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
            # No state file = nothing to update
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
        
        if updates:
            # Apply updates
            state_manager.update(updates)
            
            # Log significant updates
            if 'quality_gates_passed' in updates:
                print(f"✅ Quality gate passed: {updates['quality_gates_passed'][-1]}")
                
    except Exception as e:
        # Log error but don't fail
        print(f"PostToolUse hook error: {str(e)}", file=sys.stderr)


def process_tool_execution(state: dict, tool: str, event: dict, workflow_step: str) -> dict:
    """
    Process tool execution and return state updates.
    """
    updates = {}
    
    # Track file modifications
    if tool in ['Write', 'Edit', 'MultiEdit']:
        file_path = event.get('input', {}).get('file_path', '')
        if file_path:
            files_modified = state.get('files_modified', [])
            if file_path not in files_modified:
                files_modified.append(file_path)
                updates['files_modified'] = files_modified
                
    # Track test execution
    elif tool == 'Bash':
        command = event.get('input', {}).get('command', '')
        exit_code = event.get('exit_code', 0)
        
        # Check for test commands
        if any(test_cmd in command for test_cmd in ['pytest', 'npm test', 'cargo test', 'go test']):
            if exit_code == 0:
                # Tests passed
                gates = state.get('quality_gates_passed', [])
                if 'existing_tests' not in gates:
                    gates.append('existing_tests')
                    updates['quality_gates_passed'] = gates
                    
        # Check for build commands
        elif any(build_cmd in command for build_cmd in ['make', 'npm run build', 'cargo build', 'go build']):
            if exit_code == 0:
                # Build succeeded
                gates = state.get('quality_gates_passed', [])
                if 'compilation' not in gates:
                    gates.append('compilation')
                    updates['quality_gates_passed'] = gates
                    
        # Check for lint commands
        elif any(lint_cmd in command for lint_cmd in ['eslint', 'pylint', 'flake8', 'cargo clippy']):
            if exit_code == 0:
                # Linting passed
                gates = state.get('quality_gates_passed', [])
                if 'lint' not in gates:
                    gates.append('lint')
                    updates['quality_gates_passed'] = gates
                    
    # Track code review usage
    elif tool == 'mcp__zen__codereview':
        gates = state.get('quality_gates_passed', [])
        if 'review' not in gates:
            gates.append('review')
            updates['quality_gates_passed'] = gates
            
    # Always update last_updated
    if updates:
        updates['last_updated'] = datetime.now(timezone.utc).isoformat()
        
    return updates


if __name__ == '__main__':
    main()