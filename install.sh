#!/bin/bash

# Install Claude Code Project Management Commands
# This script installs the Python-based command system and creates wrapper scripts

echo "🚀 Installing Claude Code Project Management Commands..."

# Get the absolute path to the project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Create the commands directory if it doesn't exist
mkdir -p ~/.claude/commands/project

# Create Python library directory
mkdir -p ~/.claude/commands/project/lib

echo "📦 Installing Python command system..."

# Copy Python source code to lib directory
cp -r "$PROJECT_ROOT/src" ~/.claude/commands/project/lib/
cp -r "$PROJECT_ROOT/tests" ~/.claude/commands/project/lib/

echo "🔧 Installing command files..."

# Copy all command files from src/commands
echo "📋 Installing Claude Code commands..."
cp "$PROJECT_ROOT/src/commands/"*.md ~/.claude/commands/project/

# Copy hook scripts
echo "🪝 Installing hook scripts..."
mkdir -p ~/.claude/commands/project/hooks
cp "$PROJECT_ROOT/src/hooks/"*.py ~/.claude/commands/project/hooks/
cp "$PROJECT_ROOT/src/hooks/settings.json.template" ~/.claude/commands/project/hooks/

# Create hook configuration helper
echo "📝 Creating hook configuration template..."
cat > ~/.claude/commands/project/hooks/README.md << 'EOF'
# Claude Code Hooks Configuration

To enable automated workflow enforcement, add these hooks to your project's .claude/settings.json:

```json
{
  "hooks": {
    "PreToolUse": {
      "command": "python3 ${HOME}/.claude/commands/project/hooks/pre_tool_use.py",
      "timeout": 5000
    },
    "PostToolUse": {
      "command": "python3 ${HOME}/.claude/commands/project/hooks/post_tool_use.py",
      "timeout": 3000
    },
    "Stop": {
      "command": "python3 ${HOME}/.claude/commands/project/hooks/stop.py",
      "timeout": 3000
    }
  }
}
```

The hooks enforce the 6-step workflow automatically.
EOF

echo "✅ Installation complete!"
echo ""
echo "📦 Installed Components:"
echo "  • Commands: ~/.claude/commands/project/*.md"
echo "  • Hooks: ~/.claude/commands/project/hooks/*.py"
echo "  • Python modules: ~/.claude/commands/project/lib/src/"
echo ""
echo "🎯 Available Commands:"
echo "  /user:project:setup <name>     - Create new project worktree"
echo "  /user:project:start            - Begin automated development"
echo "  /user:project:status           - Show project progress"
echo "  /user:project:pause [reason]   - Pause automation"
echo "  /user:project:resume           - Resume from pause"
echo "  /user:project:stop [reason]    - End project with summary"
echo "  /user:project:doctor           - Validate project setup"
echo "  /user:project:advance [sprint]  - Force sprint advancement"
echo "  /user:project:sprint <action>   - Manage sprints"
echo "  /user:project:update <k> <v>   - Update project state"
echo ""
echo "🚀 Quick Start:"
echo "1. Navigate to a git repository"
echo "2. Run: /user:project:setup my-awesome-project"
echo "3. cd ../my-awesome-project"
echo "4. Customize sprint files in sprints/"
echo "5. Run: /user:project:doctor to validate"
echo "6. Run: /user:project:start to begin automation"
echo ""
echo "🪝 Hook Setup (Optional - for automation):"
echo "1. Copy hook configuration from:"
echo "   ~/.claude/commands/project/hooks/README.md"
echo "2. Add to your project's .claude/settings.json"
echo "3. Hooks will enforce 6-step workflow automatically"
echo ""
echo "💡 Key Features:"
echo "• Simple 10-20 line commands with YAML frontmatter"
echo "• Python hooks for workflow enforcement"
echo "• StateManager for reliable persistence"
echo "• Git worktree isolation for safety"
echo "• Automatic workflow progression"
echo ""
echo "⚠️  Note: Commands use --dangerously-skip-permissions mode"
