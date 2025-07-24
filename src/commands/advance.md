---
allowed-tools: Bash(test:*), Bash(python3:*), Bash(jq:*)
description: Force advance to next sprint
argument-hint: [sprint-number]
---

# Project Advance - Force Sprint Transition

Force advancement to next sprint or specific sprint.

!`[ -f ".project-state.json" ] || { echo "❌ No project found"; exit 1; }`
!`jq -r '.status' .project-state.json | grep -qE "active|paused" || { echo "❌ Project must be active or paused"; exit 1; }`
!`python3 -c "import sys; sys.path.insert(0, '$(git rev-parse --show-toplevel)'); from src.state_manager import StateManager; sm = StateManager('.'); sprint = '${ARGUMENTS}' if '${ARGUMENTS}' else str(int(sm.read()['current_sprint']) + 1).zfill(2); sm.update({'current_sprint': sprint, 'workflow_step': 'planning', 'acceptance_criteria_passed': []}); print(f'✅ Advanced to sprint {sprint}')"`

Sprint advanced. Workflow reset to planning stage.