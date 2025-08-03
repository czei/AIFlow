---
allowed-tools: Bash(test:*), Bash(python3:*), Bash(jq:*), Bash(git:*), Bash(pwd:*)
description: Debug version of status command to diagnose path issues
---

# Debug Status - Path Diagnostics

Debug version to understand path resolution issues.

!`echo "=== DEBUG: Path Resolution ==="`
!`echo "Current directory: $(pwd)"`
!`echo "Git root attempt: $(git rev-parse --show-toplevel 2>/dev/null || echo 'FAILED')"`
!`echo ""`
!`python3 -c "import sys, os; print('Python sys.path:'); [print(f'  {p}') for p in sys.path]; print(); root = os.popen('git rev-parse --show-toplevel 2>/dev/null || pwd').read().strip(); print(f'os.popen result: [{root}]'); print(f'os.popen type: {type(root)}'); print(f'os.popen len: {len(root)}')"`
!`echo ""`
!`echo "=== Testing PYTHONPATH approach ==="`
!`PYTHONPATH="$(git rev-parse --show-toplevel 2>/dev/null || pwd)" python3 -c "import sys; print('With PYTHONPATH:'); [print(f'  {p}') for p in sys.path]; print(); try: from src.state_manager import StateManager; print('SUCCESS: StateManager imported'); except ImportError as e: print(f'FAILED: {e}')"`