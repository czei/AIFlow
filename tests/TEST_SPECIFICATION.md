# Phase-Driven Development System Test Specification

## Testing Philosophy

Given the tight integration with Claude Code, the test suite focuses on validating the **observable behaviors** and **measurable outcomes** of the system rather than trying to mock Claude's AI capabilities.

## Test Strategy

### 1. Unit Testing (test_phases.py)
Tests individual components in isolation:
- **State Management**: JSON read/write, state transitions
- **File Operations**: Creation, modification, validation
- **Workflow Logic**: 6-step progression, quality gates
- **Error Handling**: Recovery from corrupted states

### 2. Integration Testing (integration_test.sh)
Tests the full workflow with measurable outcomes:
- **Git Operations**: Worktree creation, branch management
- **Phase Execution**: File creation/modification per phase
- **State Persistence**: Tracking progress across phases
- **Logging**: Structured JSON logs with correlation

### 3. Command Flow Testing (test_command_flow.py)
Simulates Claude Code command execution:
- **Command Sequence**: setup → doctor → start → status → stop
- **State Transitions**: Active → paused → resumed → completed
- **Output Verification**: Each command produces expected files

## Measurable Test Project Design

Each phase performs specific, verifiable file operations:

```
Phase 01: Setup
├── Creates: output/setup.txt (with timestamp)
├── Creates: output/config.json (initial settings)
└── Creates: output/metrics.json (progress tracking)

Phase 02: Process  
├── Appends: output/setup.txt (processing logs)
├── Updates: output/config.json (new parameters)
└── Creates: output/processed_data.csv (sample data)

Phase 03: Validate
├── Creates: output/validation_report.txt (all checks)
├── Updates: output/metrics.json (validation results)
└── Verifies: All files exist and are valid

Phase 04: Complete
├── Creates: output/test_summary.json (final metrics)
├── Archives: All outputs
└── Records: Completion timestamp
```

## Key Test Scenarios

### 1. Happy Path
- Project setup with valid git repo
- All phases execute successfully
- Files created with correct content
- State transitions properly
- Clean project completion

### 2. Workflow Enforcement
- 6-step cycle for each objective
- Quality gates block advancement
- State persists across pause/resume
- Workflow position tracked accurately

### 3. Error Recovery
- Corrupted JSON state files
- Missing prerequisites
- Failed quality gates
- Interrupted phase execution

### 4. State Management
- Pause during active automation
- Resume from exact position
- Phase advancement validation
- Completion tracking

### 5. Logging and Metrics
- Structured JSON logs created
- Correlation IDs link events
- Performance metrics captured
- Error details logged

## Validation Criteria

### File-Based Validation
```python
# Each phase creates specific files
assert os.path.exists("output/setup.txt")
assert os.path.exists("output/config.json")
assert os.path.exists("output/processed_data.csv")

# Files contain expected content
with open("output/config.json") as f:
    config = json.load(f)
    assert config["version"] == "1.0"
    assert "processing" in config

# Files modified correctly
line_count_before = len(open("output/setup.txt").readlines())
# ... execute phase ...
line_count_after = len(open("output/setup.txt").readlines())
assert line_count_after > line_count_before
```

### State-Based Validation
```python
# Project state tracks progress
state = json.load(open(".project-state.json"))
assert state["current_phase"] == "02"
assert "01" in state["completed_phases"]
assert state["workflow_step"] in ["planning", "implementation", "validation", "review", "refinement", "integration"]

# Workflow state tracks position
workflow = json.load(open(".workflow-state.json"))
assert workflow["current_step"] between 1 and 6
assert len(workflow["quality_gates_passed"]) >= 0
```

### Log-Based Validation
```python
# Logs are structured JSON
log_entry = json.loads(log_line)
assert "timestamp" in log_entry
assert "level" in log_entry
assert "event" in log_entry
assert "correlation_id" in log_entry

# Performance tracked
assert log_entry["details"]["duration_ms"] > 0
assert log_entry["details"]["success"] in [True, False]
```

## Test Execution

### Automated Test Suite
```bash
# Run all unit tests
python3 test_phases.py -v

# Run integration test
./integration_test.sh

# Test command flow
python3 test_command_flow.py
```

### Manual Verification
1. Check that all expected files exist
2. Verify JSON files are valid
3. Confirm log entries are structured
4. Validate state transitions occurred
5. Review final test summary

## Limitations and Assumptions

### What We Can Test
- ✅ File creation and modification
- ✅ State management and persistence
- ✅ Workflow step progression
- ✅ Quality gate enforcement
- ✅ Error recovery mechanisms
- ✅ Logging infrastructure

### What We Cannot Test
- ❌ Claude's actual decision-making
- ❌ AI-generated code quality
- ❌ Claude Code hook integration
- ❌ Real secure_shell execution
- ❌ Production command validation

## Success Metrics

The test suite is successful when:

1. **All unit tests pass** (100% success rate)
2. **Integration test completes** all phases
3. **Expected files created** (minimum 8 files)
4. **State transitions tracked** (4 phases)
5. **Logs generated** (minimum 20 entries)
6. **No data corruption** occurs
7. **Recovery mechanisms work** as designed

## Future Testing Enhancements

1. **Performance Testing**: Measure phase execution times
2. **Stress Testing**: Multiple rapid state changes
3. **Security Testing**: Validate command injection prevention
4. **Integration Testing**: With actual git operations
5. **End-to-End Testing**: With Claude Code simulator

This comprehensive test suite ensures the phase-driven development system's core mechanics work reliably, even without the ability to test the full AI integration.
