# Quick Start: Testing the Phase-Driven Development System

## Location
All tests are now located in:
```
/Users/czei/ai-software-project-management/tests/
```

## Running Tests

### Option 1: Run All Tests
```bash
cd /Users/czei/ai-software-project-management/tests
chmod +x run_all_tests.sh
./run_all_tests.sh
```

### Option 2: Run Individual Tests

#### Unit Tests
```bash
# Basic run
python3 test_phases.py

# Verbose output
python3 test_phases.py -v

# Run specific test class
python3 test_phases.py TestPhaseDrivenDevelopment

# Run specific test method
python3 test_phases.py TestPhaseDrivenDevelopment.test_phase_operations
```

#### Integration Test
```bash
chmod +x integration_test.sh
./integration_test.sh

# The test will create artifacts in:
# /Users/czei/ai-software-project-management/test-output/
```

#### Command Flow Test
```bash
python3 test_command_flow.py

# This simulates Claude Code commands and creates test artifacts
```

## Test Output Locations

All test outputs are created in:
```
/Users/czei/ai-software-project-management/test-output/
├── test-measurable-project/     # Integration test outputs
│   ├── phases/
│   ├── output/
│   └── .logs/
└── command-test/                # Command flow test outputs
    └── test-project/
```

## What the Tests Validate

1. **Unit Tests**: Core functionality in isolation
   - State management
   - Workflow progression
   - Quality gates
   - Error recovery

2. **Integration Test**: Full workflow with measurable outcomes
   - Git worktree operations
   - Phase execution creating specific files
   - State persistence
   - Logging infrastructure

3. **Command Flow Test**: Command sequencing
   - All project commands work correctly
   - State transitions properly
   - Files created as expected

## Cleanup

Test artifacts are created in the `test-output` directory. To clean up:
```bash
rm -rf /Users/czei/ai-software-project-management/test-output
```

## Success Criteria

All tests pass when you see:
```
✅ All tests passed!
```

Individual test success is indicated by measurable file creation and state transitions.
