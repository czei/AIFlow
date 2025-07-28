# Testing Architecture

This project implements a 4-layer testing architecture designed specifically for AI-powered systems. Each layer provides different guarantees and serves distinct purposes in ensuring system reliability.

## Overview

The testing architecture progresses from deterministic unit tests to real AI integration tests:

```
Layer 1: Unit Tests (Deterministic) ✅
Layer 2: Integration Tests (Mock AI) ✅
Layer 3: Contract-Based Tests (Real AI, Validated) ✅
Layer 4: Chaos Tests (Real AI, Edge Cases) ✅
```

## Running Tests

### Run All Tests (Recommended Methods)

#### Method 1: Using Test Runner v2 (Most Comprehensive)
```bash
python tests/runners/test_runner_v2.py
```

#### Method 2: Using Shell Scripts
```bash
# Run all tests
tests/run_all_tests.sh

# Run only unit tests
tests/run_unit_tests.sh

# Run only integration tests (includes Phase 3 tests)
tests/run_integration_tests.sh
```

### Run Specific Test Files
```bash
# Run specific test file
python -m unittest tests.unit.test_state_manager

# Run with pattern matching
python -m unittest discover -s tests/unit -p "test_*.py"
```

### Run Individual Test Files
```bash
python -m unittest tests.unit.test_basic_logger
python -m unittest tests.integration.test_mock_claude_integration
```

## Layer 1: Unit Tests for Deterministic Components

**Purpose**: Test pure functions and deterministic code without any AI involvement.

**Location**: `tests/unit/`

**Characteristics**:
- Fast execution (milliseconds)
- 100% deterministic
- No external dependencies
- No API calls

**What to test here**:
- Data structures and models
- Utility functions
- File I/O operations
- Command validation logic
- Configuration parsing

**Example**:
```python
def test_logger_initialization(self):
    """Test logger initializes with correct attributes"""
    logger = BasicLogger("/test/project", correlation_id="test-123")
    self.assertEqual(logger.correlation_id, "test-123")
```

## Layer 2: Integration Tests with MockClaudeProvider

**Purpose**: Test system integration with AI using deterministic mock responses.

**Location**: `tests/integration/`

**Characteristics**:
- Predictable AI responses
- Tests integration points
- Validates workflow logic
- No real API calls

**What to test here**:
- AI-guided workflows
- Command generation flows
- Error recovery mechanisms
- State management with AI
- Multi-step processes

**MockClaudeProvider Features**:
- Deterministic responses based on prompt patterns
- State tracking across calls
- Failure mode simulation
- Custom response injection

**Example**:
```python
def test_ai_guided_workflow(self):
    """Test complete workflow with AI guidance"""
    provider = MockClaudeProvider()
    response = provider.query("Create a plan for building a calculator")
    self.assertEqual(response["type"], "project_setup")
```

## Phase 3: End-to-End Integration Tests

**Purpose**: Test the complete automated development system without requiring real Claude interaction.

**Location**: `tests/integration/`

**Characteristics**:
- Subprocess-based hook execution simulating Claude Code's system
- JSON event simulation mimicking Claude Code's format
- Isolated test environments with git repositories
- Command markdown parsing and execution
- Complete story lifecycle validation

**Test Suites**:

1. **Command Execution Tests** (`test_command_execution.py`)
   - Tests all /user:project:* commands
   - Validates state changes
   - Ensures proper error handling

2. **Workflow Enforcement Tests** (`test_workflow_enforcement.py`)
   - Validates tool blocking/allowing based on workflow step
   - Tests emergency override functionality
   - Ensures workflow rules are enforced

3. **Workflow Progression Tests** (`test_workflow_progression.py`)
   - Tests advancement between workflow steps
   - Validates sprint completion
   - Ensures proper state transitions

4. **Complete Workflow Tests** (`test_complete_workflow.py`)
   - Tests full story lifecycle execution
   - Validates metrics tracking
   - Ensures acceptance criteria work

5. **Performance Tests** (`test_performance.py`)
   - Validates hook execution time (<100ms requirement)
   - Tests concurrent operations
   - Measures system performance

**Running Phase 3 Tests**:
```bash
# Run all Phase 3 tests
python tests/integration/test_phase3_runner.py

# Run specific test suite
python tests/integration/test_command_execution.py
python tests/integration/test_workflow_enforcement.py
python tests/integration/test_workflow_progression.py
python tests/integration/test_complete_workflow.py
python tests/integration/test_performance.py

# Run with verbose output
python tests/integration/test_phase3_runner.py -v
```

**Expected Output**:
```
======================================================================
PHASE 3 TEST SUMMARY
======================================================================
✅ PASS Command Execution Tests           4.2s (8 passed, 0 failed)
✅ PASS Workflow Enforcement Tests        2.1s (8 passed, 0 failed)
✅ PASS Workflow Progression Tests        3.5s (9 passed, 0 failed)
✅ PASS Complete Workflow Tests           5.8s (2 passed, 0 failed)
✅ PASS Performance Tests                 1.2s (5 passed, 0 failed)
----------------------------------------------------------------------
Total: 28 tests
Passed: 28 (100.0%)
Failed: 0
Duration: 16.8s
======================================================================

🎉 ALL PHASE 3 TESTS PASSED! 🎉
```

## Layer 3: Contract-Based AI Testing ✅

**Purpose**: Validate that real AI responses meet expected contracts and schemas.

**Location**: `tests/contracts/`

**Characteristics**:
- Can use real AI API or mock provider
- Validates response structure against JSON schemas
- Ensures parseability and type correctness
- Tests API contracts without requiring deterministic output
- Supports response caching for cost efficiency

**What to test here**:
- Response schema validation
- Required field presence
- Data type correctness
- Format compliance (regex patterns)
- API error handling
- Response time constraints
- Token usage tracking

**Contract Test Base Features**:
- JSON Schema validation using jsonschema library
- Response caching with TTL support
- Field type validation helpers
- Enum field validation
- Usage statistics tracking

**Available Schemas**:
- `project_setup_schema.json` - Project initialization responses
- `code_generation_schema.json` - Code generation responses
- `code_review_schema.json` - Code review responses
- `error_analysis_schema.json` - Error debugging responses
- `general_response_schema.json` - Generic AI responses

**Example**:
```python
class TestCodeGenerationContract(ContractTestBase):
    def test_function_generation_contract(self):
        """Test that function generation meets contract"""
        response = self.query_ai(
            "Generate a Python function to calculate factorial",
            context={"language": "python"}
        )
        
        # Validate against JSON schema
        self.validate_schema(response, "code_generation_schema")
        
        # Additional validations
        self.assertIn("code", response)
        self.assertTrue("def" in response["code"])
```

**Configuration**:
```yaml
contract:
  enabled: true
  description: "Layer 3: Contract-based AI validation"
  timeout: 600
  patterns:
    - "**/test_*_contract.py"
  api_provider: "mock"  # or "claude" for real API
  cache_responses: true
```

## Layer 4: Chaos and Real AI Validation Tests ✅

**Purpose**: Test system resilience with unpredictable real AI responses.

**Location**: `tests/chaos/`

**Characteristics**:
- Non-deterministic testing
- Simulates failures and edge cases
- Tests error recovery mechanisms
- Validates graceful degradation
- Tracks resilience metrics
- Can use real AI or chaos-wrapped mock

**What to test here**:
- Timeout handling and recovery
- Network error resilience
- Malformed response handling
- Rate limiting and backoff
- Graceful degradation under load
- Recovery from extended failures
- Edge case and invalid input handling
- Resource exhaustion protection

**Chaos Test Base Features**:
- Automatic retry with exponential backoff
- Failure injection (network, timeout, errors)
- Resilience scoring and metrics
- Response mutation for edge cases
- Concurrent operation testing
- Extended failure recovery patterns

**Available Test Suites**:
- `test_timeout_resilience_chaos.py` - Timeout handling scenarios
- `test_edge_cases_chaos.py` - Unusual inputs and edge cases
- `test_error_recovery_chaos.py` - Error recovery patterns

**Example**:
```python
class TestTimeoutResilienceChaos(ChaosTestBase):
    def test_basic_timeout_recovery(self):
        """Test basic recovery from timeout"""
        def timeout_operation():
            return self.chaos_query(
                "Generate a simple function",
                timeout=5.0
            )
        
        # Should recover from occasional timeouts
        self.assert_resilient(timeout_operation, min_success_rate=0.7)
```

**Resilience Metrics**:
- Recovery rate from failures
- Timeout handling effectiveness
- Error type diversity
- Degradation characteristics
- Overall resilience score (0-1)

**Configuration**:
```yaml
chaos:
  enabled: true
  description: "Layer 4: Chaos and real AI tests"
  timeout: 1200  # 20 minutes
  patterns:
    - "**/test_*_chaos.py"
  use_real_ai: false  # Set to true for real AI
  simulate_failures: true
  resilience_threshold: 0.7
  chaos_config:
    network_latency: 0.5
    failure_rate: 0.1
    timeout_probability: 0.05
```

## Configuration

Test layers are configured in `test_config.yaml`:

```yaml
test_layers:
  unit:
    enabled: true
    description: "Layer 1: Unit tests for deterministic components"
    timeout: 300
    patterns:
      - "**/test_*.py"
      - "**/*_test.py"
  
  integration:
    enabled: true
    description: "Layer 2: Integration tests with MockClaudeProvider"
    timeout: 600
    patterns:
      - "**/test_*integration*.py"
  
  contract:
    enabled: false
    description: "Layer 3: Contract-based AI testing"
    
  chaos:
    enabled: false
    description: "Layer 4: Chaos and real AI validation tests"
```

## Writing Tests

### Adding Unit Tests (Layer 1)

1. Create test file in `tests/unit/test_<component>.py`
2. Import the component to test
3. Mock all external dependencies
4. Test pure functionality

### Adding Integration Tests (Layer 2)

1. Create test file in `tests/integration/test_<feature>_integration.py`
2. Use `MockClaudeProvider` for AI interactions
3. Test complete workflows
4. Verify state transitions

### Test Naming Conventions

- Unit tests: `test_<component>_<behavior>`
- Integration tests: `test_<workflow>_integration`
- Contract tests: `test_<api>_contract`
- Chaos tests: `test_<scenario>_chaos`

## Current Test Coverage

As of last run:
- **Overall**: 100% (All tests passing)
- **Layer 1 (Unit)**: 100% (8/8 tests passing)
- **Layer 2 (Integration)**: 100% (2/2 tests passing)
- **Phase 3 (End-to-End)**: 100% (28/28 tests passing)
  - Command Execution: 8/8 tests
  - Workflow Enforcement: 8/8 tests
  - Workflow Progression: 9/9 tests
  - Complete Workflow: 2/2 tests
  - Performance: 1/1 test
- **Shell Tests**: 100% (5/5 tests passing)

## Design Principles

1. **Fast Feedback**: Layers 1 & 2 run quickly without API calls
2. **Cost Efficiency**: Most tests don't require expensive AI API calls
3. **Deterministic First**: Lower layers are reproducible and reliable
4. **Progressive Confidence**: Each layer builds on the previous
5. **Fail Fast**: Catch most bugs in lower layers

## Future Improvements

- [x] Implement Layer 3: Contract-based testing
- [x] Implement Layer 4: Chaos testing
- [ ] Add performance benchmarks
- [ ] Create test data generators
- [ ] Add mutation testing
- [ ] Implement test coverage reporting
- [ ] Add real Anthropic Claude API integration
- [ ] Implement cost tracking and optimization
- [ ] Add contract schema versioning
- [ ] Add distributed chaos testing
- [ ] Implement load testing scenarios
- [ ] Add security chaos tests

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure test files add parent directory to sys.path
2. **Mock Failures**: Check that all external dependencies are mocked
3. **Timeout Errors**: Increase timeout in test_config.yaml
4. **Plugin Not Found**: Ensure test layer files end with `_test_layer.py`

### Debug Mode

Enable debug output:
```bash
DEBUG=1 python test_runner_v2.py
```

## Contributing

When adding new tests:
1. Determine the appropriate layer
2. Follow naming conventions
3. Mock external dependencies in Layers 1 & 2
4. Document any new test patterns
5. Update this documentation if needed