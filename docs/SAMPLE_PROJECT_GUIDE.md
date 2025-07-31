# Sample Project Guide

This guide explains how to use the Disney Wait Times sample project to learn the AI Software Project Management framework.

## Overview

The sample project is maintained in a separate repository to provide a clean learning environment. It demonstrates both:
1. How to create a new project with the framework
2. How to add the framework to an existing project

## Sample Repository Location

The sample project is available at: `/Users/czei/ai-software-project-management-sample`
(In production, this would be a GitHub URL)

## Two Learning Paths

### Path 1: Creating a New Project

If you're starting a brand new project, you don't need the sample repository. Instead:

```bash
# 1. Navigate to your workspace
cd ~/my-projects

# 2. Create a new project using the framework
/user:project:setup my-awesome-app

# 3. Navigate to your new project
cd ../my-awesome-app

# 4. Start development
/user:project:start
```

The framework handles everything automatically:
- Creates git worktree
- Sets up project structure
- Configures hooks
- Creates sprint templates

### Path 2: Adding to an Existing Project

If you have an existing project and want to add the AI-driven development framework:

```bash
# 1. Clone the sample repository
git clone <sample-repo-url> disney-sample
cd disney-sample

# 2. Switch to the tutorial branch
git checkout tutorial/start

# 3. Ensure the framework is installed
cd /path/to/ai-software-project-management
./install.sh

# 4. Return to the sample and follow the integration steps
cd ~/disney-sample
```

Now follow these steps to integrate the framework:

#### Step 1: Create Hook Configuration

```bash
# Create .claude directory
mkdir -p .claude

# Create settings.json with hook configuration
cat > .claude/settings.json << 'EOF'
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
EOF
```

#### Step 2: Create Project Context

```bash
# Create CLAUDE.md with project context
cat > CLAUDE.md << 'EOF'
# Project Context for AI Development

[Add your project description and guidelines here]
EOF
```

#### Step 3: Initialize Project State (Optional)

If you want to use the state management features:

```bash
# Start Claude in your project directory
claude

# Run the doctor command to validate setup
/user:project:doctor
```

## Comparing Your Work

After integrating the framework, you can compare with the fully integrated version:

```bash
# See all changes needed for integration
git diff tutorial/start..main

# Or view specific files
git diff tutorial/start..main -- .claude/settings.json
```

## Key Files in the Sample

### On `main` branch (fully integrated):
- `.claude/settings.json` - Hook configuration
- `CLAUDE.md` - Project context for AI
- `sprints/` - Sprint definitions
- `README.md` - Full documentation

### On `tutorial/start` branch (starting point):
- `sprints/` - Sprint definitions (already included)
- `README.md` - Basic project description
- No `.claude` directory yet

## Best Practices

1. **Start Simple**: If creating a new project, use `/user:project:setup`
2. **Learn by Doing**: Use the tutorial branch to practice integration
3. **Reference the Diff**: `git diff tutorial/start..main` shows exactly what's needed
4. **Test Your Setup**: Use `/user:project:doctor` to validate

## Troubleshooting

### "Command not found"
- Ensure you've run the install script: `./install.sh`
- Restart Claude Code after installation

### "Hooks not working"
- Check that `.claude/settings.json` exists and has correct paths
- Verify hooks are installed: `ls ~/.claude/commands/project/hooks/`

### "State management issues"
- Run `/user:project:doctor` to diagnose
- Ensure you're in a git repository
- Check that you have write permissions

## Next Steps

After setting up your project:
1. Review and customize the sprint files in `sprints/`
2. Update `CLAUDE.md` with your project specifics
3. Run `/user:project:start` to begin AI-driven development
4. Use `/user:project:status` to track progress

The framework will guide you through each sprint automatically!