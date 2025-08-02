# Installation Guide

This comprehensive guide covers installing, testing, and troubleshooting the AIFlow system.

## Table of Contents

- [System Requirements](#system-requirements)
- [Quick Start](#quick-start)
- [Detailed Installation](#detailed-installation)
- [Testing Installation](#testing-installation)
- [Uninstallation](#uninstallation)
- [Troubleshooting](#troubleshooting)
- [Platform-Specific Notes](#platform-specific-notes)
- [Advanced Configuration](#advanced-configuration)

## System Requirements

### Required Software

- **Python 3.7 or higher**: Required for all scripts and hooks
  - Check version: `python3 --version`
  - Download: https://python.org

- **Git**: For version control and worktree management
  - Check version: `git --version`
  - Download: https://git-scm.com

- **Claude Code CLI**: The AI assistant interface
  - Check installation: `claude --version`
  - Install: `npm install -g @anthropic-ai/claude-code`

### Supported Platforms

- ✅ **macOS**: Fully supported (10.15+)
- ✅ **Linux**: Fully supported (Ubuntu 18.04+, RHEL 7+, etc.)
- ⚠️ **Windows**: Requires WSL (Windows Subsystem for Linux)
- ⚠️ **Docker**: Can run in containers with proper mounts

### Directory Permissions

- Write access to `~/.claude/` directory
- Write access to parent directory of git repositories (for worktrees)
- Approximately 50MB free disk space

## Quick Start

### 1. Clone and Install

```bash
# Clone the repository
git clone https://github.com/your-org/ai-software-project-management.git
cd ai-software-project-management

# Run the installer
./install.sh
```

### 2. Start Using

```bash
# Start Claude Code with permissions
claude --dangerously-skip-permissions

# Create your first project
cd your-git-repository
/user:project:setup my-project
```

## Detailed Installation

### Automated Installation (Recommended)

The `install.sh` script provides a complete installation with validation:

```bash
# Make installer executable if needed
chmod +x install.sh

# Run installer
./install.sh
```

#### What the Installer Does

1. **Prerequisite Checking**
   - Verifies Python 3.7+ is installed
   - Checks Git availability
   - Detects Claude Code CLI
   - Validates write permissions

2. **File Installation**
   - Copies commands to `~/.claude/commands/project/`
   - Installs Python modules (excludes test files)
   - Sets up hook scripts
   - Installs helper utilities

3. **Configuration**
   - Creates hook configuration templates
   - Sets executable permissions
   - Generates installation documentation

4. **Validation**
   - Verifies all files copied correctly
   - Tests Python imports
   - Validates directory structure

### Manual Installation

If you prefer manual control or the installer fails:

#### Step 1: Create Directory Structure

```bash
# Create base directories
mkdir -p ~/.claude/commands/project
mkdir -p ~/.claude/commands/project/lib
mkdir -p ~/.claude/commands/project/hooks
```

#### Step 2: Copy Command Files

```bash
# Copy markdown command files
cp src/commands/*.md ~/.claude/commands/project/
```

#### Step 3: Install Python Modules

```bash
# Copy source code (excluding tests)
cp -r src ~/.claude/commands/project/lib/

# Install helper scripts
cp scripts/logged_secure_shell.py ~/.claude/commands/
cp scripts/analyze_logs.sh ~/.claude/commands/

# Make executable
chmod +x ~/.claude/commands/*.py
chmod +x ~/.claude/commands/*.sh
```

#### Step 4: Install Hooks

```bash
# Copy hook scripts
cp src/hooks/*.py ~/.claude/commands/project/hooks/
cp src/hooks/*.json ~/.claude/commands/project/hooks/
cp src/hooks/*.template ~/.claude/commands/project/hooks/
```

#### Step 5: Verify Installation

```bash
# Test Python imports
python3 -c "import sys; sys.path.insert(0, '$HOME/.claude/commands/project/lib'); from src.state_manager import StateManager; print('✓ Installation successful')"
```

## Testing Installation

### Run Test Suite

```bash
# Run comprehensive installation tests
./test_install.sh
```

The test script validates:
- Prerequisites are met
- All files installed correctly
- No test files included in production
- Python imports work
- Scripts are executable
- Upgrade scenarios work
- Uninstall functions properly

### Manual Verification

```bash
# Check installed files
ls -la ~/.claude/commands/project/

# Verify commands available
claude --dangerously-skip-permissions
/user:project:doctor
```

## Uninstallation

### Complete Removal

```bash
# Run uninstaller
./uninstall.sh
```

The uninstaller will:
1. Check for active projects
2. Offer to create a backup
3. Remove all installed files
4. Preserve your project worktrees

### Manual Removal

```bash
# Remove installation directory
rm -rf ~/.claude/commands/project

# Remove helper scripts
rm -f ~/.claude/commands/logged_secure_shell.py
rm -f ~/.claude/commands/analyze_logs.sh
```

## Troubleshooting

### Common Issues

#### Python Not Found

**Symptom**: `Python 3.7 or higher is required but not found`

**Solution**:
```bash
# Check Python installation
python3 --version
python --version

# Install Python if needed
# macOS: brew install python3
# Ubuntu: sudo apt-get install python3
# RHEL: sudo yum install python3
```

#### Permission Denied

**Symptom**: `No write permissions for ~/.claude/`

**Solution**:
```bash
# Create directory with proper permissions
mkdir -p ~/.claude
chmod 755 ~/.claude
```

#### Claude Code Not Found

**Symptom**: `Claude Code CLI not found`

**Solution**:
```bash
# Install Claude Code
npm install -g @anthropic-ai/claude-code

# Verify installation
claude --version
```

#### Import Errors

**Symptom**: `Python module import test failed`

**Solution**:
```bash
# Check Python path
echo $PYTHONPATH

# Verify file structure
ls -la ~/.claude/commands/project/lib/src/

# Test import manually
python3 -c "import sys; print(sys.path)"
```

### Installation Log

Check the installation log for detailed error information:
```bash
# Installation logs are saved to /tmp/
ls -la /tmp/claude-pm-install-*.log
```

## Platform-Specific Notes

### macOS

- Requires macOS 10.15 (Catalina) or later
- May need to allow Terminal full disk access
- Use Homebrew for dependency management

### Linux

- Works on all major distributions
- May need to install `bc` for version comparison
- SELinux users may need to adjust contexts

### Windows

#### Using WSL (Recommended)

```bash
# Install WSL
wsl --install

# Inside WSL, follow Linux instructions
cd /mnt/c/your/project
./install.sh
```

#### Using Git Bash

Limited functionality, but basic commands work:
```bash
# Adjust paths for Windows
export HOME=/c/Users/YourName
./install.sh
```

### Docker

```dockerfile
FROM python:3.9-slim
RUN apt-get update && apt-get install -y git
COPY . /app
WORKDIR /app
RUN ./install.sh
```

## Advanced Configuration

### Custom Installation Path

```bash
# Set custom home for testing
export HOME=/custom/path
./install.sh
```

### Hook Configuration

After installation, configure hooks in your project:

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

### Environment Variables

```bash
# Optional: Set Python command
export PYTHON_CMD=python3.9

# Optional: Set installation directory
export CLAUDE_PM_HOME=$HOME/.claude/commands/project
```

## Next Steps

After successful installation:

1. Read the [POC Setup Guide](POC_SETUP_GUIDE.md)
2. Learn about [Sprint Creation](SPRINT_CREATION_INSTRUCTIONS.md)
3. Understand the [Workflow Specifications](WORKFLOW_SPECIFICATIONS.md)
4. Review [Testing Scenarios](TESTING_SCENARIOS_GUIDE.md)

## Support

If you encounter issues not covered here:

1. Check the [project issues](https://github.com/your-org/ai-software-project-management/issues)
2. Review the installation log
3. Run the test script for diagnostics
4. Submit a bug report with:
   - OS and version
   - Python version
   - Error messages
   - Installation log

## Future Improvements

The project is moving towards npm-based distribution:
- See [NPM Packaging Plan](NPM_PACKAGING_PLAN.md)
- This will simplify installation to: `npm install -g @anthropic-ai/claude-pm`
- Cross-platform compatibility will be improved
- Dependency management will be automated