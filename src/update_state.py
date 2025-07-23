#!/usr/bin/env python3
"""
Secure state update script for /user:project:update command.

This script safely handles argument parsing and state updates without
the risk of command injection.
"""

import sys
import json
import shlex
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

try:
    from src.state_manager import StateManager
except ImportError:
    print("❌ Error: Unable to import StateManager. Check project structure.")
    sys.exit(1)


def main():
    """Main entry point for state updates."""
    if len(sys.argv) < 2:
        print('❌ Usage: python3 update_state.py "<key> <value>"')
        sys.exit(1)

    try:
        # Safely parse arguments using shlex
        args_str = sys.argv[1]
        args = shlex.split(args_str)
        
        if len(args) < 1:
            print('❌ Usage: /user:project:update <key> <value>')
            sys.exit(1)

        key = args[0]
        value_str = ' '.join(args[1:]) if len(args) > 1 else ''

        # Validate key (alphanumeric + underscore only)
        if not key.replace('_', '').replace('-', '').isalnum():
            print(f'❌ Invalid key: {key}. Use only letters, numbers, underscores, and hyphens.')
            sys.exit(1)

        # Parse value
        value = value_str
        if value_str:
            # Try to parse as JSON if it looks like JSON
            if value_str.strip().startswith(('[', '{', '"')):
                try:
                    value = json.loads(value_str)
                except json.JSONDecodeError:
                    # Not valid JSON, use as string
                    pass

        # Update state
        sm = StateManager('.')
        sm.update({key: value})
        
        # Format output message
        if isinstance(value, str) and len(value) > 50:
            display_value = f"{value[:47]}..."
        else:
            display_value = str(value)
            
        print(f'✅ Updated {key} = {display_value}')

    except FileNotFoundError:
        print('❌ Error: No project state found. Run setup first.')
        sys.exit(1)
    except Exception as e:
        print(f'❌ Error: {e}')
        sys.exit(1)


if __name__ == "__main__":
    main()