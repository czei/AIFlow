---
allowed-tools: Bash(test:*), Bash(python3:*), Bash(jq:*), Bash(git:*)
description: Pause active project automation
argument-hint: [reason]
---

# Project Pause - Temporarily Stop Automation

Pause active automation while preserving state.

!`bash -c '
# Get project root
PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

# Check project exists
python3 "$PROJECT_ROOT/src/commands/utils/check_project.py" || exit 1

# Check if project is active
if ! jq -r ".status" .project-state.json | grep -q "active"; then
    echo "❌ Error: Project not active"
    exit 1
fi

# Pause the project
python3 "$PROJECT_ROOT/src/scripts/pause_project.py" "${ARGUMENTS:-Manual pause}" || { echo "❌ Pause failed"; exit 1; }

# Commit the state change
git add .project-state.json && git commit -m "Pause automation: ${ARGUMENTS:-Manual pause}" 2>/dev/null || true

echo "⏸️  Automation paused. State preserved."
echo "Resume with /user:project:resume"
'`