---
allowed-tools: Bash(test:*), Bash(python3:*), Bash(jq:*)
description: Resume paused project automation
---

# Project Resume - Continue Automation

Resume automation from exact pause point.

!`bash -c '
# Get project root
PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

# Check project exists
# For project-level installations, check multiple possible paths
if [[ -f "$PROJECT_ROOT/.claude/commands/project/lib/src/commands/utils/check_project.py" ]]; then
    python3 "$PROJECT_ROOT/.claude/commands/project/lib/src/commands/utils/check_project.py" || exit 1
elif [[ -f "$PROJECT_ROOT/src/commands/utils/check_project.py" ]]; then
    python3 "$PROJECT_ROOT/src/commands/utils/check_project.py" || exit 1
else
    echo "❌ Error: check_project.py not found in installation"
    exit 1
fi

# Check if project is paused
if ! jq -r ".status" .project-state.json | grep -q "paused"; then
    echo "❌ Error: Project not paused"
    exit 1
fi

# Resume the project
python3 "$PROJECT_ROOT/src/scripts/resume_project.py" || { echo "❌ Resume failed"; exit 1; }

echo "▶️  Automation resumed! Continuing workflow."
'`