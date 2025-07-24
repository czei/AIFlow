---
allowed-tools: Bash(test:*), Bash(python3:*), Bash(jq:*), Bash(git:*)
description: Show comprehensive project status
---

# Project Status - Progress Analysis

Display detailed status and progress of the sprint-based project.

!`[ -f ".project-state.json" ] || { echo "❌ No project found in current directory"; exit 1; }`
!`echo "📊 PROJECT STATUS"`
!`echo "================"`
!`jq -r '"Project: " + .project_name' .project-state.json`
!`jq -r '"Status: " + .status' .project-state.json`
!`jq -r '"Sprint: " + .current_sprint' .project-state.json`
!`jq -r '"Workflow: " + (.workflow_step // "none")' .project-state.json`
!`jq -r '"Automation: " + if .automation_active then "✅ Active" else "❌ Inactive" end' .project-state.json`
!`jq -r '"Cycles: " + (.automation_cycles | tostring)' .project-state.json`
!`echo ""`
!`echo "Acceptance Criteria:"`
!`jq -r '.acceptance_criteria_passed | if length > 0 then "  ✅ " + join("\n  ✅ ") else "  None passed yet" end' .project-state.json`
!`echo ""`
!`git branch --show-current | xargs -I {} echo "Git Branch: {}"`
!`python3 -c "import sys; sys.path.insert(0, '$(git rev-parse --show-toplevel)'); from src.state_manager import StateManager; sm = StateManager('.'); state = sm.read(); print(f\"\\nNext: {state.get('current_user_story', 'No user story set')}\")"`