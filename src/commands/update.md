---
allowed-tools: Bash(python3:*)
description: Update project state manually
argument-hint: <key> <value>
---

# Project Update - Manual State Update

Update specific project state values.

!`[ -f ".project-state.json" ] || { echo "❌ No project found"; exit 1; }`
!`[ -n "$ARGUMENTS" ] || { echo "❌ Usage: /user:project:update <key> <value>"; exit 1; }`
!`python3 -c "
import sys
import json
import shlex
sys.path.append('$(git rev-parse --show-toplevel)/src')
from state_manager import StateManager

# Safely parse arguments
try:
    args = shlex.split('$ARGUMENTS')
    if len(args) < 1:
        print('❌ Usage: /user:project:update <key> <value>')
        sys.exit(1)
    
    key = args[0]
    value = ' '.join(args[1:]) if len(args) > 1 else ''
    
    # Validate key (alphanumeric + underscore only)
    if not key.replace('_', '').isalnum():
        print(f'❌ Invalid key: {key}. Use only letters, numbers, and underscores.')
        sys.exit(1)
    
    # Parse value
    if value:
        if value[0] in '[{\"':
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                pass  # Use as string if not valid JSON
    
    # Update state
    sm = StateManager('.')
    sm.update({key: value})
    print(f'✅ Updated {key}')
    
except Exception as e:
    print(f'❌ Error: {e}')
    sys.exit(1)
"`