---
allowed-tools: Bash(test:*), Bash(python3:*), Bash(jq:*), Bash(git:*)
description: Show comprehensive project status
---

# Project Status - Progress Analysis

Display detailed status and progress of the sprint-based project.

!`PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"; if [[ -f "$PROJECT_ROOT/.claude/commands/project/lib/src/commands/utils/check_project.py" ]]; then python3 "$PROJECT_ROOT/.claude/commands/project/lib/src/commands/utils/check_project.py"; elif [[ -f "$PROJECT_ROOT/src/commands/utils/check_project.py" ]]; then python3 "$PROJECT_ROOT/src/commands/utils/check_project.py"; else echo "❌ Error: check_project.py not found"; exit 1; fi || exit`
!`[ -f ".project-state.json" ] || exit`
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
!`PYTHONPATH="$(git rev-parse --show-toplevel 2>/dev/null || pwd)" python3 -c "from src.state_manager import StateManager; sm = StateManager('.'); state = sm.read(); story = state.get('current_user_story', 'No user story set'); print(''); print('Next: ' + story)"`