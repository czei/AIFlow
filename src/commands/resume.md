---
allowed-tools: Bash(test:*), Bash(python3:*), Bash(jq:*)
description: Resume paused project automation
---

# Project Resume - Continue Automation

Resume automation from exact pause point.

!`PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"`
!`if [[ -f "$PROJECT_ROOT/.claude/commands/project/lib/src/commands/utils/check_project.py" ]]; then python3 "$PROJECT_ROOT/.claude/commands/project/lib/src/commands/utils/check_project.py"; elif [[ -f "$PROJECT_ROOT/src/commands/utils/check_project.py" ]]; then python3 "$PROJECT_ROOT/src/commands/utils/check_project.py"; else echo "❌ Error: check_project.py not found"; exit 1; fi || exit`
!`[ -f ".project-state.json" ] || exit`
!`jq -r '.status' .project-state.json | grep -q "paused" || { echo "❌ Error: Project not paused"; exit 1; }`
!`PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"`
!`python3 "$PROJECT_ROOT/src/scripts/resume_project.py" || { echo "❌ Resume failed"; exit 1; }`

▶️  Automation resumed! Continuing workflow.