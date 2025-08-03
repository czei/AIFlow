---
allowed-tools: Bash(test:*), Bash(python3:*), Bash(jq:*), Bash(git:*)
description: Stop project and generate summary
---

# Project Stop - Complete Project

Stop project with comprehensive summary.

!`bash -c '
# Get project root
PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

# Check project exists
python3 "$PROJECT_ROOT/src/commands/utils/check_project.py" || exit 1

# Display summary
echo "📊 PROJECT SUMMARY"
echo "================"
jq -r '"Project: " + .project_name' .project-state.json
jq -r '"Started: " + .started' .project-state.json
jq -r '"Cycles: " + (.automation_cycles | tostring)' .project-state.json
jq -r '"Sprints Completed: " + (.completed_sprints | length | tostring)' .project-state.json
echo ""
echo "Acceptance Criteria Passed:"
jq -r '.acceptance_criteria_passed | unique | "  ✅ " + join("\n  ✅ ")' .project-state.json

# Stop the project
python3 -c "import sys; sys.path.insert(0, '\''$PROJECT_ROOT'\''); from src.state_manager import StateManager; StateManager('"'"'.'"'"').update({'"'"'status'"'"': '"'"'stopped'"'"', '"'"'automation_active'"'"': False, '"'"'stopped_at'"'"': __import__('"'"'datetime'"'"').datetime.now(__import__('"'"'datetime'"'"').timezone.utc).isoformat()})"

# Commit final state
git add .project-state.json && git commit -m "Project stopped: Final state" 2>/dev/null || true

echo ""
echo "🏁 Project stopped. Thank you for using sprint-based development!"
'`