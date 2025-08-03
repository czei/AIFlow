---
allowed-tools: Bash(test:*), Bash(python3:*), Bash(jq:*), Bash(git:*)
description: Show comprehensive project status
---

# Project Status - Progress Analysis

Display detailed status and progress of the sprint-based project.

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

# Display status
echo "📊 PROJECT STATUS"
echo "================"
jq -r '"Project: " + .project_name' .project-state.json
jq -r '"Status: " + .status' .project-state.json
jq -r '"Sprint: " + .current_sprint' .project-state.json
jq -r '"Workflow: " + (.workflow_step // "none")' .project-state.json
jq -r '"Automation: " + if .automation_active then "✅ Active" else "❌ Inactive" end' .project-state.json
jq -r '"Cycles: " + (.automation_cycles | tostring)' .project-state.json
echo ""
echo "Acceptance Criteria:"
jq -r '.acceptance_criteria_passed | if length > 0 then "  ✅ " + join("\n  ✅ ") else "  None passed yet" end' .project-state.json
echo ""
git branch --show-current | xargs -I {} echo "Git Branch: {}"
python3 -c "import sys; sys.path.insert(0, '\''$PROJECT_ROOT'\''); from src.state_manager import StateManager; sm = StateManager('"'"'.'"'"'); state = sm.read(); print(f\"\\nNext: {state.get('"'"'current_user_story'"'"', '"'"'No user story set'"'"')}\");"
'`