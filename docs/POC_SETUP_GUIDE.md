# Proof of Concept Setup Guide

This guide helps you get the basic sprint-driven development system working quickly, without the complexity of the full security architecture.

## Current Implementation: Basic Git Worktree Safety + Comprehensive Logging

The proof-of-concept uses git worktree isolation as the primary safety mechanism, combined with `--dangerously-skip-permissions` for automation. **Critically, it includes comprehensive logging infrastructure** to enable effective debugging and monitoring of the automation process.

### Safety Model (Proof of Concept)

**Primary Protection: Git Worktree Isolation**
- All automation runs in isolated git worktrees (`../project-name/`)
- Cannot affect your main repository or other projects
- Easy rollback through git history
- Natural containment boundaries

**Secondary Protection: State Validation + Logging**
- Commands include built-in state checking
- Automation validates current sprint and project boundaries
- Human override always available through pause/stop commands
- **Comprehensive logging**: Every command, decision, and state change logged
- **Debug capabilities**: Full audit trail for troubleshooting automation issues

**Logging Infrastructure:**
- **7 specialized log files**: automation, workflow, commands, quality-gates, sprint-transitions, errors, performance
- **Structured JSON logging**: Machine-readable logs with full context
- **Correlation IDs**: Track all related events across an automation session
- **Real-time monitoring**: Live log tailing and analysis tools
- **Performance metrics**: Command execution times and resource usage
- **Error classification**: Detailed error logging with recommended actions

**Known Limitations:**
- Requires `--dangerously-skip-permissions` flag
- Commands could theoretically access other parts of your filesystem
- No fine-grained command validation
- Relies on git worktree boundaries and careful automation design

## Prerequisites

Before starting:
1. **Git Repository**: Must be in a git repository directory
2. **Claude Code**: Install Claude Code CLI tool
3. **Python 3.7+**: Required for scripts and hooks
4. **Directory Permissions**: Write access to parent directory for git worktrees
5. **Project Source**: Clone or have access to AIFlow repository

## Installation Guide

### Quick Installation (Recommended)

Use the automated installation script for the easiest setup:

```bash
# Clone the project
git clone https://github.com/your-org/AIFlow.git
cd AIFlow

# Run the installer
./install.sh
```

The installer will:
- Check prerequisites (Python 3.7+, Git, Claude Code CLI)
- Install commands and scripts to `~/.claude/commands/project/`
- Set up hook configurations
- Validate the installation
- Provide helpful next steps

### Manual Installation (Alternative)

If the automated installer fails or you prefer manual control:

```bash
# Clone the project (if not already available)
git clone https://github.com/your-org/AIFlow.git
cd AIFlow

# Install commands to Claude Code directory
mkdir -p ~/.claude/commands/project
cp -r src/commands/* ~/.claude/commands/project/

# Install Python modules (excluding tests)
mkdir -p ~/.claude/commands/project/lib
cp -r src ~/.claude/commands/project/lib/

# Install hook scripts
mkdir -p ~/.claude/commands/project/hooks
cp src/hooks/*.py ~/.claude/commands/project/hooks/

# Install supporting scripts
cp scripts/logged_secure_shell.py ~/.claude/commands/
cp scripts/analyze_logs.sh ~/.claude/commands/

# Make scripts executable
chmod +x ~/.claude/commands/logged_secure_shell.py
chmod +x ~/.claude/commands/analyze_logs.sh

# Install Python dependencies (if any)
pip install -r requirements.txt
```

### Uninstallation

To remove the installation:

```bash
# Run the uninstaller
./uninstall.sh
```

The uninstaller will:
- Check for active projects
- Optionally create a backup
- Remove all installed files
- Preserve your project worktrees

### Testing the Installation

To validate the installation works correctly:

```bash
# Run the test script
./test_install.sh
```

This will test the installation in a temporary environment without affecting your system.

### 2. Verify Installation
```bash
# Start Claude Code with permissions
cd your-existing-git-repo
claude-code --dangerously-skip-permissions

# Test command availability
/user:project:setup --help
# Should show command help

# List available commands
ls ~/.claude/commands/project/
# Should show: setup.md, start.md, status.md, etc.
```

## Creating Your First Project

There are two ways to get started:

### Option 1: Create a New Project (Recommended for New Development)

```bash
# Create a new project (replace "my-webapp" with your project name)
/user:project:setup my-webapp

# This creates:
# - Git worktree at ../my-webapp/
# - Sprint templates in sprints/
# - CLAUDE.md for project context
# - State management files
# - Hook configuration in .claude/settings.json
```

### Option 2: Learn with the Sample Project

See the [Sample Project Guide](SAMPLE_PROJECT_GUIDE.md) for:
- How to add the framework to existing projects
- A complete working example with the Disney Wait Times app
- Step-by-step integration tutorial

### 2. Navigate to Project
```bash
cd ../my-webapp

# Verify structure
ls -la
# Should show: sprints/, .claude/, docs/, logs/, CLAUDE.md, etc.
```

### 3. Customize Project Specifications

#### Edit Sprint Files
Navigate to `sprints/` and customize each file:

```bash
# Example: Edit planning sprint
vim sprints/01-planning.md

# Replace template objectives with your specific tasks
# See SPRINT_CREATION_INSTRUCTIONS.md for detailed guidance
```

#### Update CLAUDE.md
Add your project context:

```bash
vim CLAUDE.md

# Add:
# - Project description and goals
# - Technology stack
# - Development standards
# - Special instructions
```

### 4. Validate Setup
```bash
# Run doctor command
/user:project:doctor

# All items should show green checkmarks
# Fix any issues before proceeding
```

### 5. Start Automation
```bash
# Begin automated development
/user:project:start

# Monitor progress
/user:project:status

# Monitor logs in real-time (separate terminal)
tail -f logs/automation.log | jq .
tail -f logs/workflow.log | jq .

# Control automation
/user:project:pause  # Stop for manual work
/user:project:resume # Continue automation
```

## Safety Practices for Proof of Concept

### Recommended Usage Patterns
1. **Start with Non-Critical Projects**: Use for experimental or learning projects first
2. **Regular State Checks**: Monitor with `/user:project:status` frequently
3. **Git History Awareness**: Regular commits provide rollback points
4. **Worktree Boundaries**: Never run automation in your main repository directory
5. **Manual Oversight**: Be prepared to pause/stop automation if needed

### Risk Mitigation
- **Backup Important Work**: Ensure main repository has recent backups
- **Limited Scope**: Start with small, contained projects
- **Regular Monitoring**: Don't leave automation running unattended initially
- **Quick Recovery**: Keep the pause and stop commands readily available

## Transitioning to Production Security

Once the proof-of-concept is working and you're comfortable with the workflow:

### Sprint 2: Enhanced Security
The next major version will implement enterprise-grade security:

1. **Docker Containerization**
   - Complete filesystem isolation
   - Network access controls
   - Process boundary enforcement

2. **OPA Policy Engine** 
   - Contextual command validation
   - Eliminates `--dangerously-skip-permissions`
   - Audit trail for all operations

3. **Production Hardening**
   - Security monitoring and alerting
   - Comprehensive audit logging
   - Enterprise compliance features

See `SECURITY_ARCHITECTURE.md` for the complete future security design.

## Current Limitations and Workarounds

### Limitation: Permission System
**Issue**: Requires `--dangerously-skip-permissions` 
**Workaround**: Git worktree isolation + careful automation design
**Future**: OPA-based contextual validation

### Limitation: Command Validation
**Issue**: No fine-grained command filtering
**Workaround**: Automation designed with safety boundaries
**Future**: Policy-based command validation

### Limitation: Audit Trail
**Issue**: Limited security logging
**Workaround**: Git history provides implementation audit trail
**Future**: Comprehensive security decision logging

## Success Criteria for Proof of Concept

You'll know the PoC is successful when:

✅ **Setup Works**: `/user:project:setup` creates proper project structure
✅ **Doctor Validates**: `/user:project:doctor` shows green validation
✅ **Logging Active**: `.logs/` directory created with structured JSON logs
✅ **Automation Runs**: `/user:project:start` begins autonomous development
✅ **Acceptance Criteria Work**: System enforces story lifecycle with validation
✅ **State Persistence**: Can pause/resume automation maintaining context
✅ **Human Control**: Override and manual intervention work as expected
✅ **Debug Capability**: Can trace automation decisions through comprehensive logs
✅ **Performance Monitoring**: Log analysis shows command execution metrics
✅ **Error Handling**: Errors are properly logged with actionable information

## Getting Help

### Troubleshooting
- **Commands Not Found**: Verify installation in `~/.claude/commands/project/`
- **Setup Fails**: Ensure you're in a git repository directory
- **Doctor Fails**: Check sprint file customization and git worktree setup
- **Automation Stuck**: Use `/user:project:pause` then `/user:project:status`

### Common Issues
- **Git Worktree Errors**: Ensure clean git state before setup
- **Permission Errors**: Must use `--dangerously-skip-permissions` flag
- **State File Issues**: Check `.project-state.json` exists and is valid JSON
- **Sprint Validation**: Ensure sprint files are fully customized (no templates)
- **Missing Logs**: Check that `.logs/` directory exists and has proper permissions
- **Command Failures**: Use log analysis: `~/.claude/commands/analyze_logs.sh`
- **Automation Stuck**: Check error logs and recent correlation IDs for debugging
- **Performance Issues**: Monitor `performance.log` for slow operations

This proof-of-concept gives you a working system to evaluate the approach before investing in the full security architecture. The git worktree isolation provides reasonable safety boundaries for testing and initial development use.
