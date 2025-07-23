#!/bin/bash

# Install Claude Code Project Management Commands
# This script copies the commands to ~/.claude/commands/project/

echo "🚀 Installing Claude Code Project Management Commands..."

# Create the commands directory if it doesn't exist
mkdir -p ~/.claude/commands/project

# Copy all command files
cp -r ./project/* ~/.claude/commands/project/

echo "✅ Commands installed successfully!"
echo ""
echo "Available commands:"
echo "  /user:project:setup <project-name>    - Create new project worktree and structure"
echo "  /user:project:doctor                  - Validate project setup"
echo "  /user:project:start                   - Begin automated development"
echo "  /user:project:status                  - Show project progress"
echo "  /user:project:pause                   - Pause automation"
echo "  /user:project:resume                  - Resume automation"
echo "  /user:project:stop                    - End project cleanly"
echo "  /user:project:advance [phase]         - Force phase advancement"
echo "  /user:project:phase <action>          - Manage phases"
echo ""
echo "Next steps:"
echo "1. Navigate to a git repository"
echo "2. Run: /user:project:setup my-project-name"
echo "3. Customize the phase files created"
echo "4. Run: /user:project:doctor"
echo "5. Run: /user:project:start"
echo ""
echo "Note: These commands are designed for use with --dangerously-skip-permissions"
echo "Ensure you understand the risks and operate in isolated git worktrees."
