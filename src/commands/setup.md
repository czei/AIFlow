---
allowed-tools: Bash(echo:*), Bash(test:*), Bash(python3:*), Bash(git:*)
description: Create new sprint-driven project worktree
argument-hint: <project-name>
---

# Project Setup - Create Sprint-Driven Project

Create a new git worktree and branch for project: $ARGUMENTS

!`[ -n "$ARGUMENTS" ] || { echo "❌ Error: Project name required"; exit 1; }`
!`[ -d ".git" ] || { echo "❌ Error: Must be run from git repository"; exit 1; }`
!`PROJECT_ROOT="$(git rev-parse --show-toplevel)"`
!`VALIDATED_NAME=$(python3 -c "import sys; sys.path.insert(0, '$PROJECT_ROOT'); from src.project_builder import ProjectBuilder; print(ProjectBuilder.validate_project_name('$ARGUMENTS'))" 2>&1) || { echo "❌ Error: $VALIDATED_NAME"; exit 1; }`
!`git worktree add "../$VALIDATED_NAME" -b "feature/$VALIDATED_NAME" 2>/dev/null || { echo "❌ Error: Worktree creation failed"; exit 1; }`
!`cd "../$VALIDATED_NAME" && python3 -c "import sys; sys.path.insert(0, '$PROJECT_ROOT'); from src.project_builder import ProjectBuilder; ProjectBuilder('$VALIDATED_NAME').create_structure()"`
!`cd "../$VALIDATED_NAME" && python3 -c "import sys; sys.path.insert(0, '$PROJECT_ROOT'); from src.state_manager import StateManager; StateManager('.').create('$VALIDATED_NAME')"`
!`cd "../$VALIDATED_NAME" && git add . && git commit -m "Initial setup: $VALIDATED_NAME project structure"`
!`mkdir -p "../$VALIDATED_NAME/.claude" && [ -f "$HOME/.claude/commands/project/hooks/settings.json.template" ] && sed "s|__HOOKS_PATH__|$HOME/.claude/commands/project/hooks|g" "$HOME/.claude/commands/project/hooks/settings.json.template" > "../$VALIDATED_NAME/.claude/settings.json" && echo "✅ Created .claude/settings.json with hook configuration" || echo "⚠️  Warning: Could not create .claude/settings.json - template not found"`

!`echo "✅ Project created at ../$VALIDATED_NAME"`
!`echo "Next: Customize sprint files and run /user:project:doctor to validate setup."`