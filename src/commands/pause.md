---
allowed-tools: Bash(test:*), Bash(python3:*), Bash(jq:*), Bash(git:*)
description: Pause active project automation
argument-hint: [reason]
---

# Project Pause - Temporarily Stop Automation

Pause active automation while preserving state.

!`[ -f ".project-state.json" ] || { echo "❌ No project found"; exit 1; }`
!`jq -r '.status' .project-state.json | grep -q "active" || { echo "❌ Project not active"; exit 1; }`
!`python3 -c "import sys; sys.path.append('$(git rev-parse --show-toplevel)/src'); from state_manager import StateManager; StateManager('.').update({'status': 'paused', 'automation_active': False, 'pause_reason': '${ARGUMENTS:-Manual pause}', 'paused_at': __import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat()})"`
!`git add .project-state.json && git commit -m "Pause automation: ${ARGUMENTS:-Manual pause}" 2>/dev/null || true`

⏸️  Automation paused. State preserved.
Resume with `/user:project:resume`