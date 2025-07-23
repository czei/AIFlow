---
allowed-tools: Bash(python3:*)
description: Update project state manually
argument-hint: <key> <value>
---

# Project Update - Manual State Update

Update specific project state values.

!`[ -f ".project-state.json" ] || { echo "❌ No project found"; exit 1; }`
!`[ -n "$ARGUMENTS" ] || { echo "❌ Usage: /user:project:update <key> <value>"; exit 1; }`
!`python3 -c "import sys, json; sys.path.append('$(git rev-parse --show-toplevel)/src'); from state_manager import StateManager; args = '${ARGUMENTS}'.split(' ', 1); key, value = args if len(args) == 2 else (args[0], ''); sm = StateManager('.'); sm.update({key: json.loads(value) if value and value[0] in '[{\\"' else value}); print(f'✅ Updated {key}')"`