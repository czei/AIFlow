---
allowed-tools: Bash(python3:*), Bash(echo:*), Bash(git:*)
description: Test different import approaches
---

# Test Import Approaches

Test different ways to import StateManager.

!`echo "=== Method 1: Original approach (failing) ==="`
!`python3 -c "import sys, os; root = os.popen('git rev-parse --show-toplevel 2>/dev/null || pwd').read().strip(); sys.path.insert(0, root); from src.state_manager import StateManager; print('SUCCESS: Method 1 worked!')" 2>&1 || echo "FAILED: Method 1"`
!`echo ""`
!`echo "=== Method 2: PYTHONPATH approach ==="`
!`PYTHONPATH="$(git rev-parse --show-toplevel 2>/dev/null || pwd)" python3 -c "from src.state_manager import StateManager; print('SUCCESS: Method 2 worked!')" 2>&1 || echo "FAILED: Method 2"`
!`echo ""`
!`echo "=== Method 3: Direct path calculation ==="`
!`PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)" && PYTHONPATH="$PROJECT_ROOT" python3 -c "from src.state_manager import StateManager; print('SUCCESS: Method 3 worked!')" 2>&1 || echo "FAILED: Method 3"`