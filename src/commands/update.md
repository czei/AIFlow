---
allowed-tools: Bash(python3:*)
description: Update project state manually
argument-hint: <key> <value>
---

# Project Update - Manual State Update

Update specific project state values.

!`[ -f ".project-state.json" ] || { echo "❌ No project found"; exit 1; }`
!`[ -n "$ARGUMENTS" ] || { echo "❌ Usage: /user:project:update <key> <value>"; exit 1; }`
!`python3 "$(git rev-parse --show-toplevel)/src/update_state.py" "$ARGUMENTS"`