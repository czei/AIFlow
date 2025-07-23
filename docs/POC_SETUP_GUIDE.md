# Proof of Concept Setup Guide

This guide helps you get the basic phase-driven development system working quickly, without the complexity of the full security architecture.

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
- Automation validates current phase and project boundaries
- Human override always available through pause/stop commands
- **Comprehensive logging**: Every command, decision, and state change logged
- **Debug capabilities**: Full audit trail for troubleshooting automation issues

**Logging Infrastructure:**
- **7 specialized log files**: automation, workflow, commands, quality-gates, phase-transitions, errors, performance
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

## Quick Start (Proof of Concept)

### 1. Install the Commands
```bash
# Install to Claude Code commands directory
mkdir -p ~/.claude/commands/project
cp -r /Users/czei/claude-project-commands/project/* ~/.claude/commands/project/
```

### 2. Test Basic Setup
```bash
# Start Claude Code with permissions
cd your-existing-git-repo
claude-code --dangerously-skip-permissions

# Test command availability
/user:project:setup test-project
```

### 3. Validate Installation
```bash
# Check that setup created proper structure
ls ../test-project/
# Should show: phases/, .project-state.json, CLAUDE.md, etc.

# Validate with doctor command
cd ../test-project
/user:project:doctor
```

### 4. Set Up Logging Infrastructure (Essential for Debugging)
```bash
# Copy the logging infrastructure
cp /Users/czei/claude-project-commands/logged_secure_shell.py ~/.claude/commands/
cp /Users/czei/claude-project-commands/analyze_logs.sh ~/.claude/commands/

# Make scripts executable
chmod +x ~/.claude/commands/logged_secure_shell.py
chmod +x ~/.claude/commands/analyze_logs.sh
```

### 5. Run First Automation Test
```bash
# After customizing phase files per doctor recommendations:
/user:project:start

# Monitor progress:
/user:project:status

# Monitor logs in real-time (open in separate terminal):
tail -f .logs/automation.log | jq .
tail -f .logs/errors.log | jq .

# Analyze logs:
~/.claude/commands/analyze_logs.sh

# Control automation:
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

### Phase 2: Enhanced Security
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
✅ **Quality Gates Work**: System enforces 6-step workflow with validation
✅ **State Persistence**: Can pause/resume automation maintaining context
✅ **Human Control**: Override and manual intervention work as expected
✅ **Debug Capability**: Can trace automation decisions through comprehensive logs
✅ **Performance Monitoring**: Log analysis shows command execution metrics
✅ **Error Handling**: Errors are properly logged with actionable information

## Getting Help

### Troubleshooting
- **Commands Not Found**: Verify installation in `~/.claude/commands/project/`
- **Setup Fails**: Ensure you're in a git repository directory
- **Doctor Fails**: Check phase file customization and git worktree setup
- **Automation Stuck**: Use `/user:project:pause` then `/user:project:status`

### Common Issues
- **Git Worktree Errors**: Ensure clean git state before setup
- **Permission Errors**: Must use `--dangerously-skip-permissions` flag
- **State File Issues**: Check `.project-state.json` exists and is valid JSON
- **Phase Validation**: Ensure phase files are fully customized (no templates)
- **Missing Logs**: Check that `.logs/` directory exists and has proper permissions
- **Command Failures**: Use log analysis: `~/.claude/commands/analyze_logs.sh`
- **Automation Stuck**: Check error logs and recent correlation IDs for debugging
- **Performance Issues**: Monitor `performance.log` for slow operations

This proof-of-concept gives you a working system to evaluate the approach before investing in the full security architecture. The git worktree isolation provides reasonable safety boundaries for testing and initial development use.
