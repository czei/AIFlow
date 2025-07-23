# Claude Code Hook Documentation

## Overview

The AI Software Project Management System uses Claude Code hooks to enforce a disciplined 6-step workflow for phase-driven development. These hooks integrate with Claude Code to guide development through planning, implementation, validation, review, refinement, and integration phases.

## Hook Architecture

### Three Hooks, One Workflow

1. **PreToolUse Hook** - Enforces workflow rules before tool execution
2. **PostToolUse Hook** - Tracks progress and updates state after tool execution  
3. **Stop Hook** - Advances workflow steps when conditions are met

### State Management

All hooks interact with the project state stored in `.project-state.json`:
- Current workflow step
- Automation active/inactive status
- Progress tracking per step
- Quality gates passed
- Metrics and compliance scoring

## PreToolUse Hook

**Purpose**: Enforces tool restrictions based on the current workflow step.

**Location**: `src/hooks/pre_tool_use.py`

### Workflow Rules by Phase

#### Planning Phase
- **Allowed**: Read, LS, Glob, Grep, WebSearch, WebFetch, Task, TodoWrite
- **Blocked**: Write, Edit, MultiEdit, Bash, Python, JavaScript
- **Purpose**: Force requirements analysis before coding

#### Implementation Phase  
- **Allowed**: All tools
- **Blocked**: None
- **Purpose**: Full development freedom

#### Validation Phase
- **Allowed**: Read tools, execution tools, Edit (for minor fixes)
- **Blocked**: Write (no new files)
- **Purpose**: Focus on testing and verification

#### Review Phase
- **Allowed**: Read tools, TodoWrite
- **Blocked**: Write tools, execution tools
- **Purpose**: Code analysis without modifications

#### Refinement Phase
- **Allowed**: Read tools, Edit, MultiEdit, execution tools
- **Blocked**: Write (no new files)
- **Purpose**: Apply review feedback

#### Integration Phase
- **Allowed**: Read tools, Git tools, execution tools
- **Blocked**: Write tools
- **Purpose**: Final testing and commit

### Emergency Override

The hook recognizes emergency patterns for production issues:
- `EMERGENCY:`
- `HOTFIX:`
- `CRITICAL:`
- `OVERRIDE:`
- Production down scenarios
- Security vulnerabilities
- Data loss situations

### Response Format

```json
{
  "decision": "allow" | "block",
  "reason": "Explanation message",
  "suggestions": ["Helpful", "suggestions", "for user"]
}
```

## PostToolUse Hook

**Purpose**: Updates project state based on tool execution results.

**Location**: `src/hooks/post_tool_use.py`

### Progress Tracking

The hook tracks:
- Files modified (Write, Edit, MultiEdit tools)
- Tools used per workflow step
- Test execution (detects pytest, npm test, etc.)
- Build success (make, npm run build, etc.)
- Lint results (eslint, pylint, flake8, etc.)
- Code review completion (mcp__zen__codereview)

### Quality Gates

Automatically marks quality gates as passed:
- `existing_tests` - When tests run successfully
- `compilation` - When build commands succeed
- `lint` - When linting passes
- `review` - When code review is performed

### Step Completion Detection

Uses indicators to determine when a step is complete:
- Planning: TodoWrite with implementation tasks
- Implementation: Files modified
- Validation: Tests executed
- Review: Code review performed
- Refinement: Edit/MultiEdit tools used
- Integration: Git operations performed

## Stop Hook

**Purpose**: Automatically advances workflow steps when current step is complete.

**Location**: `src/hooks/stop.py`

### Workflow Advancement

The hook:
1. Checks if current step is complete
2. Advances to next step in sequence
3. Resets quality gates for new step
4. Provides guidance for the new phase
5. Handles phase completion (integration → planning)

### Phase Completion

When integration completes:
- Calculates workflow compliance score
- Marks phase as complete
- Prepares for next phase or marks project complete

## Troubleshooting Guide

### Common Issues

#### 1. Hooks Not Triggering

**Symptom**: Tools execute without workflow enforcement

**Solutions**:
- Check `.claude/settings.json` exists with hook paths
- Verify automation is active: `/user:project:status`
- Ensure you're in a project directory with `.project-state.json`

#### 2. Tool Blocked Unexpectedly

**Symptom**: "Tool not allowed in current phase" errors

**Solutions**:
- Check current phase: `/user:project:status`
- Use emergency override for critical fixes
- Advance workflow if step is complete
- Use `/user:project:pause` to disable automation temporarily

#### 3. Workflow Not Advancing

**Symptom**: Stuck in same phase despite completing work

**Solutions**:
- Check step completion requirements
- Ensure quality gates are passed
- Look for required actions in status output
- Manually advance with `/user:project:advance`

#### 4. State File Corruption

**Symptom**: Hook errors about corrupt state file

**Solutions**:
- Run `/user:project:doctor` to diagnose
- Check file permissions
- Restore from backup if available
- Reset project with caution

### Debug Commands

```bash
# Check hook configuration
cat .claude/settings.json

# View current state
cat .project-state.json | jq .

# Test hook directly
echo '{"cwd":".", "tool":"Write", "input":{}}' | python src/hooks/pre_tool_use.py

# Check hook logs (if errors occur)
# Hooks output errors to stderr
```

### Hook Response Codes

- Exit 0: Success
- Exit 1: Hook error (check stderr)
- No response: Hook not found or import error

### Manual Override

To temporarily disable workflow enforcement:
```bash
/user:project:pause
```

To re-enable:
```bash
/user:project:resume
```

### Testing Hooks

Run the comprehensive test suite:
```bash
python tests/unit/test_hooks.py
```

Tests verify:
- Workflow rule enforcement
- Progress tracking
- Emergency overrides
- Step advancement
- State management

## Best Practices

1. **Follow the Workflow**: Let the system guide you through phases
2. **Use Emergency Overrides Sparingly**: Only for production issues
3. **Complete Quality Gates**: Run tests, linting, and reviews
4. **Trust the Automation**: The system prevents common mistakes
5. **Monitor Progress**: Use `/user:project:status` frequently

## Integration with Claude Code

The hooks integrate via `.claude/settings.json`:
```json
{
  "hooks": {
    "preToolUse": "path/to/pre_tool_use.py",
    "postToolUse": "path/to/post_tool_use.py", 
    "stop": "path/to/stop.py"
  }
}
```

This file is automatically created during project setup.

## Metrics and Compliance

The system tracks:
- Tools allowed vs blocked
- Emergency override usage
- Workflow violations
- Compliance score (0-100%)

High compliance indicates disciplined development following the intended workflow.

## Extending the System

To modify workflow rules:
1. Edit `src/hooks/workflow_rules.py`
2. Update `WORKFLOW_RULES` dictionary
3. Add new tool categories as needed
4. Update completion indicators
5. Run tests to verify changes

Remember: The goal is disciplined, high-quality development through systematic phases.