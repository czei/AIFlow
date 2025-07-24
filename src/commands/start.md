---
allowed-tools: Bash(test:*), Bash(python3:*), Bash(jq:*)
description: Start automated sprint-driven development
---

# Project Start - Begin Automated Development

Start automated sprint-driven development with 6-step workflow enforcement.

!`[ -f ".project-state.json" ] || { echo "❌ Error: No project found. Run setup first."; exit 1; }`
!`jq -r '.status' .project-state.json | grep -qE "setup|paused" || { echo "❌ Error: Project not in setup or paused state"; exit 1; }`
!`python3 -c "import sys; sys.path.insert(0, '$(git rev-parse --show-toplevel)'); from src.state_manager import StateManager; StateManager('.').update({'status': 'active', 'automation_active': True, 'workflow_step': 'planning'})"`

✅ Automation activated! I'll now follow the 6-step workflow:
1. Planning → 2. Implementation → 3. Validation → 4. Review → 5. Refinement → 6. Integration

Current sprint: Planning - I'll analyze requirements before writing any code.