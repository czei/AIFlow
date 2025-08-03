---
allowed-tools: Bash(echo:*), Bash(ls:*), Bash(python3:*)
description: Test PYTHONPATH with minimal complexity
---

# Test PYTHONPATH

Minimal test of PYTHONPATH functionality.

!`echo "Checking src directory:"`
!`ls -la src/ | head -5`
!`echo ""`
!`echo "Testing PYTHONPATH with simple import:"`
!`PYTHONPATH="." python3 -c "import src.state_manager" && echo "SUCCESS: Import worked" || echo "FAILED: Import failed"`