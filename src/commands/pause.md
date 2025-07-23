---
allowed-tools: Bash(test:*), Bash(python3:*), Bash(jq:*), Bash(git:*)
description: Pause active project automation
argument-hint: [reason]
---

# Project Pause - Temporarily Stop Automation

Pause active automation while preserving state.

!`[ -f ".project-state.json" ] || { echo "❌ No project found"; exit 1; }`
!`jq -r '.status' .project-state.json | grep -q "active" || { echo "❌ Project not active"; exit 1; }`
!`PROJECT_ROOT="$(git rev-parse --show-toplevel)"`
!`python3 "$PROJECT_ROOT/src/scripts/pause_project.py" "${ARGUMENTS:-Manual pause}" || { echo "❌ Pause failed"; exit 1; }`
!`git add .project-state.json && git commit -m "Pause automation: ${ARGUMENTS:-Manual pause}" 2>/dev/null || true`

⏸️  Automation paused. State preserved.
Resume with `/user:project:resume`