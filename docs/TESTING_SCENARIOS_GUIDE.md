# Testing Scenarios Guide

This guide provides test scenarios and validation procedures for the AI Software Project Management System. For setup instructions, see POC_SETUP_GUIDE.md.

## Test Scenarios

### Scenario 1: Basic Project Lifecycle

**Objective**: Test full project lifecycle from setup to completion

```bash
# 1. Start automation
/user:project:start

# 2. Check initial status
/user:project:status

# 3. Let automation run for planning phase
# Watch for read-only operations during planning

# 4. Pause automation to verify state
/user:project:pause

# 5. Check current state
/user:project:status

# 6. Resume automation
/user:project:resume

# 7. Monitor progress
# Automation should advance through workflow steps
```

**Expected Results**:
- Automation starts in planning phase
- Only read operations allowed during planning
- State persists through pause/resume
- Workflow advances automatically

### Scenario 2: Workflow Enforcement

**Objective**: Verify tool restrictions based on workflow step

```bash
# 1. Start fresh project
/user:project:setup test-workflow
cd ../test-workflow

# 2. Customize sprints with simple objectives
# Edit sprints/01-planning.md with a basic task

# 3. Start automation
/user:project:start

# 4. Observe tool blocking
# During planning: Write/Edit tools should be blocked
# During implementation: Write/Edit tools should be allowed

# 5. Check logs for enforcement
tail -f logs/workflow.log | jq .
```

**Expected Results**:
- Planning phase blocks Write/Edit tools
- Implementation phase allows all tools
- Logs show enforcement decisions
- Emergency overrides work when needed

### Scenario 3: State Persistence

**Objective**: Test state recovery after interruption

```bash
# 1. Start project and let it run
/user:project:start

# 2. After some progress, stop Claude Code
# Ctrl+C or close terminal

# 3. Restart Claude Code
claude-code --dangerously-skip-permissions

# 4. Check state was preserved
/user:project:status

# 5. Resume from where it left off
/user:project:resume
```

**Expected Results**:
- State file preserves progress
- Workflow step maintained
- Objectives completion tracked
- Automation resumes correctly

### Scenario 4: Manual Intervention

**Objective**: Test human override capabilities

```bash
# 1. Start automation
/user:project:start

# 2. Pause when in implementation phase
/user:project:pause

# 3. Make manual changes
# Edit some files manually

# 4. Update state to reflect changes
/user:project:update

# 5. Resume automation
/user:project:resume
```

**Expected Results**:
- Pause stops automation immediately
- Manual changes are preserved
- State update reflects changes
- Automation continues from new state

## Comprehensive Test Scenarios

### Scenario A: Complete Sprint Execution

**Objective**: Test full sprint lifecycle from planning to completion

**Setup**:
1. Create project with single sprint
2. Define 2-3 simple objectives
3. Clear acceptance criteria

**Test Steps**:
1. Start automation and monitor each phase:
   - Planning: Research and analysis only
   - Implementation: Code creation
   - Validation: Test execution
   - Review: Code review process
   - Refinement: Addressing feedback
   - Integration: Final commits

**Validation Points**:
- [ ] Each workflow step executes in order
- [ ] Quality gates enforced at each step
- [ ] Sprint completes with 100% objectives
- [ ] All acceptance criteria passed
- [ ] Progress logged accurately

### Scenario B: Multi-Sprint Project

**Objective**: Test sprint transitions and dependencies

**Setup**:
1. Create project with 3 interdependent sprints
2. Set clear prerequisites between sprints
3. Define success criteria for transitions

**Test Steps**:
1. Run first sprint to completion
2. Verify automatic transition to sprint 2
3. Check prerequisite validation
4. Monitor state transitions
5. Complete all sprints

**Validation Points**:
- [ ] Sprints execute in correct order
- [ ] Prerequisites block premature execution
- [ ] State transitions logged properly
- [ ] Sprint completion triggers next sprint
- [ ] Final project state shows completion

### Scenario C: Error Recovery

**Objective**: Test system resilience and error handling

**Setup**:
1. Create project with known failure point
2. Prepare fix for the failure

**Test Steps**:
1. Start automation
2. Wait for deliberate error
3. Observe error handling
4. Apply manual fix
5. Resume automation
6. Verify recovery

**Validation Points**:
- [ ] Error detected and logged
- [ ] Automation pauses appropriately
- [ ] Clear error message provided
- [ ] Recovery successful after fix
- [ ] No state corruption

### Scenario D: Compliance Validation

**Objective**: Test quality gate enforcement

**Test Steps**:
1. Start project with strict quality gates
2. Attempt to bypass validation phase
3. Verify enforcement mechanisms
4. Complete proper validation
5. Check compliance scoring

**Validation Points**:
- [ ] Cannot skip required validations
- [ ] Compliance score tracks violations
- [ ] Emergency overrides logged
- [ ] Quality gates prevent progression
- [ ] Final compliance report accurate

## Validation Checklists

### Pre-Test Validation
- [ ] Commands installed correctly
- [ ] Git repository initialized
- [ ] Project structure created
- [ ] Sprint files customized
- [ ] CLAUDE.md contains project context
- [ ] Doctor command shows all green

### During Test Validation
- [ ] Workflow steps execute in order
- [ ] Tool restrictions enforced
- [ ] State updates after each step
- [ ] Logs capture all activities
- [ ] Progress percentages accurate
- [ ] Quality gates block when needed

### Post-Test Validation
- [ ] Sprint marked complete
- [ ] All objectives checked off
- [ ] State file shows completion
- [ ] Logs show full history
- [ ] Git commits created
- [ ] Documentation updated

## Log Analysis

### Real-Time Monitoring
```bash
# Watch automation decisions
tail -f logs/automation.log | jq '.level == "INFO"'

# Monitor workflow enforcement
tail -f logs/workflow.log | jq .

# Track errors
tail -f logs/errors.log | jq .

# View performance metrics
tail -f logs/performance.log | jq .
```

### Post-Test Analysis
```bash
# Analyze complete session
~/.claude/commands/analyze_logs.sh

# Check specific correlation ID
jq 'select(.correlation_id == "session-123")' logs/*.log

# Review quality gate violations
jq 'select(.event == "quality_gate_failed")' logs/quality-gates.log
```

## Debug Mode Testing

Enable verbose output for detailed troubleshooting:

```bash
# Set debug environment
export DEBUG=1
export LOG_LEVEL=DEBUG

# Run with verbose output
/user:project:start

# Check debug logs
jq 'select(.level == "DEBUG")' logs/*.log
```

## Performance Testing

### Measure Hook Execution Time
```bash
# Check hook performance
jq '.duration_ms' logs/performance.log | stats

# Find slow operations
jq 'select(.duration_ms > 100)' logs/performance.log
```

### Resource Usage
```bash
# Monitor during test
top -pid $(pgrep -f claude-code)

# Check memory usage
ps aux | grep claude-code
```

## Best Practices

1. **Start Simple**: Begin with single-objective sprints
2. **Incremental Complexity**: Add features gradually
3. **Document Anomalies**: Note unexpected behaviors
4. **Save Test Artifacts**: Keep logs and state files
5. **Reproducible Tests**: Document exact steps
6. **Compare Runs**: Look for consistency
7. **Edge Case Focus**: Test boundary conditions

## Troubleshooting Test Failures

### Common Issues During Testing

**Workflow Not Advancing**:
- Check current workflow step in state
- Look for blocked quality gates
- Verify acceptance criteria defined
- Check for errors in logs

**State Corruption**:
- Backup state file before tests
- Use /user:project:update --reset if needed
- Check JSON validity
- Review state transition logs

**Hook Failures**:
- Test hooks individually
- Check Python environment
- Verify file permissions
- Review hook logs specifically

**Performance Issues**:
- Check for infinite loops in sprints
- Monitor resource usage
- Look for large file operations
- Review performance logs

## Automated Test Suite

For comprehensive automated testing:

```bash
# Run all tests
python tests/runners/test_runner_v2.py

# Run specific test categories
python tests/integration/test_complete_workflow.py
python tests/integration/test_workflow_enforcement.py
python tests/integration/test_workflow_progression.py

# Run with coverage
pytest --cov=src tests/
```

See TESTING.md for detailed automated test documentation.