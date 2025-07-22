# Phase-Driven Development Test Suite

This test suite validates the phase-driven development system without requiring Claude Code integration. It focuses on measurable outcomes that can be verified programmatically.

## Test Structure

### 1. Unit Tests (`test_phases.py`)
Python unittest-based tests that validate:
- Phase file structure and required sections
- State management and JSON operations
- Workflow progression (6-step cycle)
- Quality gate tracking
- Phase operations (file creation/modification)
- Automation control (pause/resume)
- Error recovery
- Logging infrastructure

### 2. Integration Test (`integration_test.sh`)
Bash script that simulates the full workflow:
- Git worktree creation
- Project structure setup
- Phase execution with measurable file operations
- State transitions
- Logging and metrics
- Validation of all outputs

## Measurable Test Project

The test project uses simple file operations as measurable outcomes:

### Phase 01: Setup
- Creates `output/setup.txt` with timestamp
- Creates `output/config.json` with initial settings
- Creates `output/metrics.json` to track progress

### Phase 02: Process  
- Appends lines to `output/setup.txt`
- Updates `output/config.json` with new keys
- Creates `output/processed_data.csv` with sample data

### Phase 03: Validate
- Creates `output/validation_report.txt` with all checks
- Updates `output/metrics.json` with validation results
- Verifies all files exist and are valid

### Phase 04: Completion
- Creates `output/test_summary.json` with project metrics
- Archives all outputs
- Records completion timestamp

## Running the Tests

### Unit Tests
```bash
cd /Users/czei/ai-software-project-management/tests
python3 test_phases.py

# Or for verbose output:
python3 test_phases.py -v
```

### Integration Test
```bash
cd /Users/czei/ai-software-project-management/tests
chmod +x integration_test.sh
./integration_test.sh
```

The integration test will:
1. Create a test git repository
2. Set up a git worktree with project structure
3. Execute all phases with measurable outcomes
4. Verify state management and logging
5. Generate a comprehensive test summary

## Measurable Outcomes

Each test verifies concrete, measurable results:

1. **File Creation**: Specific files must exist after each phase
2. **File Modification**: Files must contain expected content/structure
3. **JSON Validity**: All JSON files must parse correctly
4. **Line Counts**: Text files must have expected number of lines
5. **State Consistency**: State files must reflect current progress
6. **Log Entries**: Structured logs must contain required fields
7. **Quality Gates**: All gates must be tracked and passed

## Test Validation Points

### State Management
- `.project-state.json` tracks current phase and workflow step
- `.workflow-state.json` tracks position in 6-step cycle
- State transitions are atomic and consistent

### Workflow Enforcement
- Each objective must complete all 6 steps
- Quality gates must pass before advancement
- Workflow position is preserved across pause/resume

### Logging
- Every operation generates structured JSON logs
- Correlation IDs link related events
- Performance metrics are captured
- Errors include recovery recommendations

### File Operations
- Each phase creates/modifies specific files
- Files contain verifiable content
- Operations are idempotent when appropriate
- No destructive operations without backups

## Edge Cases Tested

1. **Corrupted State Recovery**: Invalid JSON in state files
2. **Mid-Phase Interruption**: Pause during workflow execution
3. **Quality Gate Failures**: Blocking advancement
4. **Missing Prerequisites**: Phase dependency validation
5. **Concurrent Modifications**: State file locking

## Success Criteria

The test suite validates that:
1. ✅ All phases execute measurable operations
2. ✅ State persists correctly across sessions
3. ✅ Workflow steps are enforced sequentially
4. ✅ Quality gates prevent poor-quality advancement
5. ✅ Logging provides complete audit trail
6. ✅ Recovery from errors is graceful
7. ✅ File operations are safe and reversible

## Limitations

These tests cannot validate:
- Claude Code hook integration
- Actual AI decision-making
- Command execution through secure_shell
- Real git operations beyond worktree setup
- Performance under production load

However, they thoroughly test the core mechanics that enable the phase-driven development system to function reliably.
