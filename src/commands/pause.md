---
allowed-tools: Bash(test:*), Bash(python3:*), Bash(jq:*), Bash(git:*)
description: Pause active project automation
argument-hint: [reason]
---

# Project Pause - Temporarily Stop Automation

Pause active automation while preserving state.

!`PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"`
!`if [[ -f "$PROJECT_ROOT/.claude/commands/project/lib/src/commands/utils/check_project.py" ]]; then python3 "$PROJECT_ROOT/.claude/commands/project/lib/src/commands/utils/check_project.py"; elif [[ -f "$PROJECT_ROOT/src/commands/utils/check_project.py" ]]; then python3 "$PROJECT_ROOT/src/commands/utils/check_project.py"; else echo "❌ Error: check_project.py not found"; exit 1; fi || exit`
!`[ -f ".project-state.json" ] || exit`
!`jq -r '.status' .project-state.json | grep -q "active" || { echo "❌ Error: Project not active"; exit 1; }`
!`PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"`
!`python3 "$PROJECT_ROOT/src/scripts/pause_project.py" "${ARGUMENTS:-Manual pause}" || { echo "❌ Pause failed"; exit 1; }`
!`git add .project-state.json && git commit -m "Pause automation: ${ARGUMENTS:-Manual pause}" 2>/dev/null || true`

⏸️  Automation paused. State preserved.
Resume with `/user:project:resume`