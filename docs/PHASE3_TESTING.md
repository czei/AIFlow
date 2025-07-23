# Phase 3 End-to-End Testing Guide

## Overview

Phase 3 implements comprehensive end-to-end testing for the automated development system without requiring real Claude interaction. The tests validate the complete workflow from project setup through all 6 development steps.

## Architecture

The Phase 3 testing system uses:
- **Subprocess-based hook execution** - Simulates Claude Code's hook system
- **JSON event simulation** - Mimics Claude Code's event format
- **Isolated test environments** - Each test runs in its own git repository
- **Command markdown parsing** - Executes actual command files

### Key Components

1. **CommandExecutor** (`tests/integration/command_executor.py`)
   - Parses and executes /user:project:* commands
   - Simulates tool usage through hooks
   - Handles shell command execution

2. **TestUtilities** (`tests/integration/test_utilities.py`)
   - Creates isolated test environments
   - Manages state files
   - Provides assertion helpers

3. **Phase3TestRunner** (`tests/integration/test_phase3_runner.py`)
   - Orchestrates all test suites
   - Tracks results and metrics
   - Provides comprehensive reporting

## Running Tests

### Run All Phase 3 Tests
```bash
./run_phase3_tests.sh
```

### Run Specific Test Suite
```bash
# Command execution tests
python tests/integration/test_command_execution.py

# Workflow enforcement tests  
python tests/integration/test_workflow_enforcement.py

# Workflow progression tests
python tests/integration/test_workflow_progression.py

# Complete workflow tests
python tests/integration/test_complete_workflow.py

# Performance tests
python tests/integration/test_performance.py
```

### Run with Verbose Output
```bash
python tests/integration/test_phase3_runner.py -v
```

## Expected Output

A successful test run should show:
```
######################################################################
# PHASE 3 END-TO-END INTEGRATION TESTS
# Minimal test suite for proof-of-concept validation
######################################################################

======================================================================
Running Command Execution Tests
======================================================================
🧪 Testing setup command...
  ✓ Worktree created successfully
  ✓ Project structure created
  ✓ State file initialized
✅ Setup command test passed

[... more test output ...]

======================================================================
PHASE 3 TEST SUMMARY
======================================================================
✅ PASS Command Execution Tests           4.2s (8 passed, 0 failed)
✅ PASS Workflow Enforcement Tests        2.1s (8 passed, 0 failed)
✅ PASS Workflow Progression Tests        3.5s (9 passed, 0 failed)
✅ PASS Complete Workflow Tests           5.8s (2 passed, 0 failed)
✅ PASS Performance Tests                 1.2s (5 passed, 0 failed)
----------------------------------------------------------------------
Total: 32 tests
Passed: 32 (100.0%)
Failed: 0
Duration: 16.8s
======================================================================

🎉 ALL PHASE 3 TESTS PASSED! 🎉
```

## Test Structure

### 1. Command Execution Tests
- Tests all /user:project:* commands
- Validates state changes
- Ensures proper error handling

### 2. Workflow Enforcement Tests
- Validates tool blocking/allowing based on workflow step
- Tests emergency override functionality
- Ensures workflow rules are enforced

### 3. Workflow Progression Tests
- Tests advancement between workflow steps
- Validates phase completion
- Ensures proper state transitions

### 4. Complete Workflow Tests
- Tests full 6-step workflow execution
- Validates metrics tracking
- Ensures quality gates work

### 5. Performance Tests
- Validates hook execution time (<100ms requirement)
- Tests concurrent operations
- Measures system performance

## Event Structure

The test system simulates Claude Code events:

```json
{
  "cwd": "/path/to/project",
  "tool": "Write",
  "input": {
    "file_path": "src/example.py",
    "content": "# Python code here"
  }
}
```

### Required Fields
- `cwd`: Current working directory
- `tool`: Tool being used (Write, Read, Bash, etc.)
- `input`: Tool-specific parameters

## Troubleshooting

### Common Issues

#### ImportError in setup command
**Symptom**: `ImportError: attempted relative import with no known parent package`

**Fix**: Ensure PROJECT_ROOT is correctly set in test environment. The fix has been applied to use absolute paths.

#### KeyError 'input'
**Symptom**: `KeyError: 'input'` in complete workflow tests

**Fix**: The event structure must include the 'input' field. This has been fixed in the test files.

#### Shell escaping errors
**Symptom**: Quote handling issues in pause/resume commands

**Fix**: Commands now use separate Python scripts instead of inline shell commands.

#### Phase completion not tracked
**Symptom**: Phases not marked as completed in workflow progression

**Fix**: The stop hook now correctly reads current_phase from state instead of phase_info.

### Debug Mode

Enable debug output:
```bash
DEBUG=1 ./run_phase3_tests.sh
```

### Running Individual Tests

To debug a specific test:
```bash
# Run with pytest for better output
python -m pytest tests/integration/test_workflow_enforcement.py::WorkflowEnforcementTest::test_planning_phase_rules -xvs

# Run with Python directly
python tests/integration/test_workflow_enforcement.py
```

## Command Markdown Format

Commands use YAML frontmatter:
```markdown
---
allowed-tools: Bash(echo:*), Bash(test:*), Bash(python3:*)
description: Command description
argument-hint: <arguments>
---

# Command Title

Command description.

!`shell command 1`
!`shell command 2`

Success message.
```

## Adding New Tests

1. Create test class inheriting from appropriate base
2. Use TestEnvironment for setup/teardown
3. Use CommandExecutor for command execution
4. Assert on state changes and outputs
5. Clean up resources in teardown

Example:
```python
class MyNewTest:
    def setup(self):
        self.env = TestEnvironment()
        self.test_dir = self.env.setup("test-project")
        self.executor = CommandExecutor(self.test_dir)
        
    def teardown(self):
        self.env.teardown()
        
    def test_my_feature(self):
        # Test implementation
        exit_code, stdout, stderr = self.executor.run_user_command("mycommand")
        assert exit_code == 0
```

## Performance Requirements

- Hook execution: <100ms per hook
- Command execution: <500ms for simple commands
- State operations: <50ms for read/write
- Test suite: <30 seconds total

## Next Steps

1. Add more edge case tests
2. Implement stress testing
3. Add integration with real Claude Code
4. Create visual test reporter
5. Add test coverage metrics