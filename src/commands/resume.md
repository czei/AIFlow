---
allowed-tools: Bash(test:*), Bash(python3:*), Bash(jq:*)
description: Resume paused project automation
---

# Project Resume - Continue Automation

Resume automation from exact pause point.

!`[ -f ".project-state.json" ] || { echo "❌ No project found"; exit 1; }`
!`jq -r '.status' .project-state.json | grep -q "paused" || { echo "❌ Project not paused"; exit 1; }`
!`PROJECT_ROOT="$(git rev-parse --show-toplevel)"`
!`python3 "$PROJECT_ROOT/src/scripts/resume_project.py" || { echo "❌ Resume failed"; exit 1; }`

▶️  Automation resumed! Continuing workflow.