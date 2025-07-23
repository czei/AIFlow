---
allowed-tools: Bash(test:*), Bash(python3:*), Bash(jq:*)
description: Resume paused project automation
---

# Project Resume - Continue Automation

Resume automation from exact pause point.

!`[ -f ".project-state.json" ] || { echo "❌ No project found"; exit 1; }`
!`jq -r '.status' .project-state.json | grep -q "paused" || { echo "❌ Project not paused"; exit 1; }`
!`python3 -c "import sys; sys.path.append('$(git rev-parse --show-toplevel)/src'); from state_manager import StateManager; sm = StateManager('.'); state = sm.read(); print(f'Resuming from: {state.get(\"workflow_step\", \"unknown\")} phase')`
!`python3 -c "import sys; sys.path.append('$(git rev-parse --show-toplevel)/src'); from state_manager import StateManager; StateManager('.').update({'status': 'active', 'automation_active': True, 'pause_reason': None, 'paused_at': None})"`

▶️  Automation resumed! Continuing workflow.