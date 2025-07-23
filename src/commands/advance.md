---
allowed-tools: Bash(test:*), Bash(python3:*), Bash(jq:*)
description: Force advance to next phase
argument-hint: [phase-number]
---

# Project Advance - Force Phase Transition

Force advancement to next phase or specific phase.

!`[ -f ".project-state.json" ] || { echo "❌ No project found"; exit 1; }`
!`jq -r '.status' .project-state.json | grep -qE "active|paused" || { echo "❌ Project must be active or paused"; exit 1; }`
!`python3 -c "import sys; sys.path.append('$(git rev-parse --show-toplevel)/src'); from state_manager import StateManager; sm = StateManager('.'); phase = '${ARGUMENTS}' if '${ARGUMENTS}' else str(int(sm.read()['current_phase']) + 1).zfill(2); sm.update({'current_phase': phase, 'workflow_step': 'planning', 'quality_gates_passed': []}); print(f'✅ Advanced to phase {phase}')"`

Phase advanced. Workflow reset to planning stage.