---
allowed-tools: Bash(echo:*), Bash(pwd:*), Bash(git:*), Bash(python3:*), Bash(cat:*)
description: Debug using temporary Python file to avoid escaping issues
---

# Debug with File

Debug by writing Python code to a file first.

!`echo "=== Path Information ==="`
!`echo "Current directory: $(pwd)"`
!`echo "Git root: $(git rev-parse --show-toplevel 2>/dev/null || echo 'Not in git repo')"`
!`echo ""`
!`cat > /tmp/debug_import.py << 'EOF'
import sys
import os

print("Python executable:", sys.executable)
print("Python version:", sys.version.split()[0])
print()
print("sys.path:")
for p in sys.path:
    print(f"  {p}")

print()
print("Attempting to import StateManager...")
try:
    from src.state_manager import StateManager
    print("SUCCESS: StateManager imported successfully")
    print(f"StateManager location: {StateManager.__module__}")
except ImportError as e:
    print(f"FAILED: {e}")

print()
print("Checking if src directory exists:")
if os.path.exists("src"):
    print("  src/ directory found")
    if os.path.exists("src/state_manager.py"):
        print("  src/state_manager.py found")
    else:
        print("  src/state_manager.py NOT found")
else:
    print("  src/ directory NOT found")
EOF`
!`echo "=== Running debug script ==="`
!`PYTHONPATH="$(git rev-parse --show-toplevel 2>/dev/null || pwd)" python3 /tmp/debug_import.py`