---
allowed-tools: Bash(echo:*), Bash(test:*), Bash(python3:*), Bash(git:*)
description: Create new phase-driven project worktree
argument-hint: <project-name>
---

# Project Setup - Create Phase-Driven Project

Create a new git worktree and branch for project: $ARGUMENTS

!`[ -n "$ARGUMENTS" ] || { echo "❌ Error: Project name required"; exit 1; }`
!`[[ "$ARGUMENTS" =~ ^[a-zA-Z0-9_-]+$ ]] || { echo "❌ Error: Project name must contain only letters, numbers, hyphens, and underscores"; exit 1; }`
!`[ -d ".git" ] || { echo "❌ Error: Must be run from git repository"; exit 1; }`
!`git worktree add "../$ARGUMENTS" -b "feature/$ARGUMENTS" 2>/dev/null || { echo "❌ Error: Worktree creation failed"; exit 1; }`
!`cd "../$ARGUMENTS" && python3 -c "import sys; sys.path.append('$(pwd)/../src'); from project_builder import ProjectBuilder; ProjectBuilder('$ARGUMENTS').create_structure()"`
!`cd "../$ARGUMENTS" && python3 -c "import sys; sys.path.append('$(pwd)/../src'); from state_manager import StateManager; StateManager('.').create('$ARGUMENTS')"`
!`cd "../$ARGUMENTS" && git add . && git commit -m "Initial setup: $ARGUMENTS project structure"`
!`mkdir -p "../$ARGUMENTS/.claude" && sed "s|__HOOKS_PATH__|$HOME/.claude/commands/project/hooks|g" "$HOME/.claude/commands/project/hooks/settings.json.template" > "../$ARGUMENTS/.claude/settings.json" && echo "✅ Created .claude/settings.json with hook configuration"`

✅ Project created at ../$ARGUMENTS
Next: Customize phase files and run `/user:project:doctor` to validate setup.