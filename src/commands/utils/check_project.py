#!/usr/bin/env python3
"""Check if a project exists in the current directory."""

import sys
from pathlib import Path

# Add parent directories to path for imports
script_path = Path(__file__).resolve()
utils_dir = script_path.parent
commands_dir = utils_dir.parent
src_dir = commands_dir.parent
project_root = src_dir.parent

# Try multiple import paths
sys.path.insert(0, str(src_dir))
sys.path.insert(0, str(project_root))

try:
    from state_manager import StateManager, StateValidationError
except ImportError:
    try:
        from src.state_manager import StateManager, StateValidationError
    except ImportError:
        print("❌ Error: Unable to import StateManager. Check project structure.")
        sys.exit(1)


def main():
    """Check if project exists and exit with appropriate code."""
    try:
        sm = StateManager('.')
        sm.read()  # This will raise StateValidationError if file doesn't exist
        sys.exit(0)  # Project exists
    except StateValidationError:
        print("❌ Error: No project found in current directory")
        print("")
        print("To start a project, use: /user:project:start")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()