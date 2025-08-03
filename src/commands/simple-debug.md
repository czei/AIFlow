---
allowed-tools: Bash(echo:*), Bash(pwd:*), Bash(git:*), Bash(python3:*)
description: Simple debug to test path resolution
---

# Simple Debug

Test basic path resolution.

!`echo "Current dir:"`
!`pwd`
!`echo ""`
!`echo "Git root:"`
!`git rev-parse --show-toplevel 2>/dev/null || echo "No git root found"`
!`echo ""`
!`echo "Testing PYTHONPATH:"`
!`PYTHONPATH="$(pwd)" python3 -c "import sys; print(sys.path[0])"`
!`echo ""`
!`echo "Testing import from current dir:"`
!`PYTHONPATH="$(pwd)" python3 -c "try: from src.state_manager import StateManager; print('Import successful'); except: print('Import failed')"`