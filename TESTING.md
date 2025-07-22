# Testing Architecture

This project implements a 4-layer testing architecture designed specifically for AI-powered systems. Each layer provides different guarantees and serves distinct purposes in ensuring system reliability.

## Overview

The testing architecture progresses from deterministic unit tests to real AI integration tests:

```
Layer 1: Unit Tests (Deterministic) ✅
Layer 2: Integration Tests (Mock AI) ✅
Layer 3: Contract-Based Tests (Real AI, Validated) 🔄
Layer 4: Chaos Tests (Real AI, Edge Cases) 🔄
```

## Running Tests

### Run All Tests
```bash
python test_runner_v2.py
```

### Run Specific Layer
```bash
# Run only unit tests
python -m unittest discover -s tests/unit -p "test_*.py"

# Run only integration tests
python -m unittest discover -s tests/integration -p "test_*.py"
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

## Layer 4: Chaos and Real AI Validation Tests (Not Implemented)

**Purpose**: Test system resilience with unpredictable real AI responses.

**Planned Location**: `tests/chaos/`

**Characteristics**:
- Non-deterministic
- Tests edge cases
- Validates error recovery
- Ensures production readiness

**What to test here**:
- Timeout handling
- Retry mechanisms
- Malformed response handling
- Rate limit handling
- Graceful degradation

**Example (Planned)**:
```python
def test_ai_timeout_recovery(self):
    """Test system handles AI timeouts gracefully"""
    with simulate_timeout():
        result = system.execute_with_ai("Complex task")
        self.assertTrue(result.recovered)
        self.assertIn("timeout", result.recovery_reason)
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
- **Overall**: 83.3% (10/12 tests passing)
- **Layer 1 (Unit)**: 80% (4/5 tests passing)
- **Layer 2 (Integration)**: 100% (2/2 tests passing)
- **Shell Tests**: 100% (5/5 tests passing)

## Design Principles

1. **Fast Feedback**: Layers 1 & 2 run quickly without API calls
2. **Cost Efficiency**: Most tests don't require expensive AI API calls
3. **Deterministic First**: Lower layers are reproducible and reliable
4. **Progressive Confidence**: Each layer builds on the previous
5. **Fail Fast**: Catch most bugs in lower layers

## Future Improvements

- [x] Implement Layer 3: Contract-based testing
- [ ] Implement Layer 4: Chaos testing
- [ ] Add performance benchmarks
- [ ] Create test data generators
- [ ] Add mutation testing
- [ ] Implement test coverage reporting
- [ ] Add real Anthropic Claude API integration
- [ ] Implement cost tracking and optimization
- [ ] Add contract schema versioning

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