#!/usr/bin/env python3
"""
Pause active project automation.

This script safely pauses an active project by updating the state
without shell escaping issues.
"""

import sys
from pathlib import Path
from datetime import datetime, timezone

# Add parent directory to path for imports
script_dir = Path(__file__).parent.parent
sys.path.insert(0, str(script_dir))

# Also try to add the src directory if we're in a different structure
src_dir = script_dir / 'src'
if src_dir.exists():
    sys.path.insert(0, str(src_dir))

try:
    from state_manager import StateManager
except ImportError:
    # Try alternative import path
    try:
        from src.state_manager import StateManager
    except ImportError:
        print("❌ Error: Unable to import StateManager. Check project structure.")
        sys.exit(1)


def main():
    """Pause active project."""
    # Get pause reason from command line
    pause_reason = sys.argv[1] if len(sys.argv) > 1 else "Manual pause"
    
    try:
        # Initialize StateManager
        sm = StateManager('.')
        
        # Read current state
        state = sm.read()
        
        # Check if project is active
        if state.get('status') != 'active':
            print(f"❌ Error: Project is not active (status: {state.get('status')})")
            sys.exit(1)
        
        # Update state to pause
        sm.update({
            'status': 'paused',
            'automation_active': False,
            'pause_reason': pause_reason,
            'paused_at': datetime.now(timezone.utc).isoformat()
        })
        
        print(f"✅ Project paused: {pause_reason}")
        
    except FileNotFoundError:
        print("❌ Error: No project state found. Not in a project directory.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()