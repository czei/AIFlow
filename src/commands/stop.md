---
allowed-tools: Bash(test:*), Bash(python3:*), Bash(jq:*), Bash(git:*)
description: Stop project and generate summary
---

# Project Stop - Complete Project

Stop project with comprehensive summary.

!`PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"`
!`if [[ -f "$PROJECT_ROOT/.claude/commands/project/lib/src/commands/utils/check_project.py" ]]; then python3 "$PROJECT_ROOT/.claude/commands/project/lib/src/commands/utils/check_project.py"; elif [[ -f "$PROJECT_ROOT/src/commands/utils/check_project.py" ]]; then python3 "$PROJECT_ROOT/src/commands/utils/check_project.py"; else echo "❌ Error: check_project.py not found"; exit 1; fi || exit`
!`[ -f ".project-state.json" ] || exit`
!`echo "📊 PROJECT SUMMARY"`
!`echo "================"`
!`jq -r '"Project: " + .project_name' .project-state.json`
!`jq -r '"Started: " + .started' .project-state.json`
!`jq -r '"Cycles: " + (.automation_cycles | tostring)' .project-state.json`
!`jq -r '"Sprints Completed: " + (.completed_sprints | length | tostring)' .project-state.json`
!`echo ""`
!`echo "Acceptance Criteria Passed:"`
!`jq -r '.acceptance_criteria_passed | unique | "  ✅ " + join("\n  ✅ ")' .project-state.json`
!`PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)" && python3 -c "import sys; sys.path.insert(0, '$PROJECT_ROOT'); from src.state_manager import StateManager; StateManager('.').update({'status': 'stopped', 'automation_active': False, 'stopped_at': __import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat()})"`
!`git add .project-state.json && git commit -m "Project stopped: Final state" 2>/dev/null || true`
!`echo ""`
!`echo "🏁 Project stopped. Thank you for using sprint-based development!"`