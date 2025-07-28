# Hook Test Isolation Plan

## The State Isolation Challenge

The hook system is deeply integrated with StateManager, which:
1. Reads/writes to `.project-state.json` files
2. Maintains persistent state across hook invocations
3. Tracks metrics that accumulate over time
4. Updates workflow progress that affects future decisions

Without proper isolation, tests will:
- Leave state files on disk
- Contaminate subsequent tests with modified state
- Cause false positives/negatives based on test order
- Make debugging failures extremely difficult

## Isolation Strategy

### 1. Temporary Directory Isolation
```python
@pytest.fixture
def isolated_project_dir(tmp_path):
    """Create an isolated project directory for each test."""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()
    
    # Create initial state file if needed
    state_file = project_dir / ".project-state.json"
    initial_state = {
        "automation_active": True,
        "workflow_step": "planning",
        "metrics": {
            "tools_allowed": 0,
            "tools_blocked": 0,
            "emergency_overrides": 0,
            "workflow_violations": 0
        }
    }
    state_file.write_text(json.dumps(initial_state, indent=2))
    
    yield project_dir
    
    # Cleanup happens automatically with tmp_path
```

### 2. StateManager Mocking Options

#### Option A: Full Mock (Unit Tests)
```python
@pytest.fixture
def mock_state_manager(mocker):
    """Fully mock StateManager for unit tests."""
    mock = mocker.patch('src.hooks.pre_tool_use.StateManager')
    instance = mock.return_value
    
    # Default state
    instance.read.return_value = {...}
    instance.update.return_value = None
    
    return instance
```

#### Option B: Real StateManager with Isolation (Integration Tests)
```python
@pytest.fixture
def real_state_manager(isolated_project_dir):
    """Use real StateManager with isolated directory."""
    from src.state_manager import StateManager
    return StateManager(str(isolated_project_dir))
```

### 3. Hook Test Base Class with Isolation

```python
class IsolatedHookTestBase:
    """Base class ensuring complete test isolation."""
    
    @pytest.fixture(autouse=True)
    def isolate_test(self, tmp_path, monkeypatch):
        """Ensure complete test isolation."""
        # 1. Isolate file system
        test_dir = tmp_path / "hook_test"
        test_dir.mkdir()
        monkeypatch.chdir(test_dir)
        
        # 2. Isolate stdin/stdout
        self.stdin_data = None
        self.stdout_capture = []
        self.stderr_capture = []
        
        # 3. Isolate environment variables
        monkeypatch.delenv("HOOK_DEBUG", raising=False)
        
        # 4. Reset module-level state
        self._reset_module_state()
        
        yield
        
        # Cleanup handled by pytest
    
    def _reset_module_state(self):
        """Reset any module-level state in hooks."""
        # Reset HookConfig cached values
        from src.hooks.hook_utils import HookConfig
        HookConfig._config = None
        HookConfig._emergency_overrides = None
```

### 4. Test Organization Strategy

```
tests/unit/hooks/
├── test_pre_tool_use.py      # Unit tests with mocked StateManager
├── test_post_tool_use.py     # Unit tests with mocked StateManager
├── test_stop.py              # Unit tests with mocked StateManager
├── test_workflow_rules.py    # Pure logic tests (no state)
├── test_hook_utils.py        # Utility function tests
└── test_event_validator.py   # Validation logic tests

tests/integration/hooks/
├── test_hook_state_integration.py  # Real StateManager tests
├── test_workflow_flow.py           # Multi-hook workflow tests
└── test_emergency_overrides.py     # Emergency pattern tests
```

### 5. Specific Isolation Patterns

#### Pattern 1: State Mutation Tests
```python
def test_metrics_update_isolation(isolated_hook_test):
    """Test that metrics updates don't affect other tests."""
    # Arrange
    initial_state = isolated_hook_test.get_state()
    assert initial_state['metrics']['tools_blocked'] == 0
    
    # Act - Block a tool
    isolated_hook_test.run_hook('pre_tool_use', {
        'tool': 'Write',  # Blocked in planning
        'cwd': str(isolated_hook_test.project_dir)
    })
    
    # Assert - Metrics updated in this test only
    updated_state = isolated_hook_test.get_state()
    assert updated_state['metrics']['tools_blocked'] == 1
```

#### Pattern 2: Workflow Progress Tests
```python
def test_workflow_advancement_isolation(isolated_hook_test):
    """Test workflow advancement without affecting other tests."""
    # Start in planning
    assert isolated_hook_test.get_workflow_step() == 'planning'
    
    # Complete planning
    isolated_hook_test.complete_step('planning')
    
    # Verify advancement
    assert isolated_hook_test.get_workflow_step() == 'implementation'
    # Other tests still start in planning
```

### 6. Pytest Configuration

```python
# conftest.py
@pytest.fixture(autouse=True)
def reset_imports():
    """Reset imported modules between tests."""
    # Clear any cached imports of hooks
    modules_to_clear = [
        'src.hooks.pre_tool_use',
        'src.hooks.post_tool_use',
        'src.hooks.stop',
        'src.hooks.hook_utils'
    ]
    for module in modules_to_clear:
        if module in sys.modules:
            del sys.modules[module]
```

### 7. Test Execution Strategy

1. **Run tests in random order** to detect isolation issues:
   ```bash
   pytest --random-order tests/unit/hooks/
   ```

2. **Run tests in parallel** to ensure thread safety:
   ```bash
   pytest -n auto tests/unit/hooks/
   ```

3. **Use markers** for different test types:
   ```python
   @pytest.mark.unit
   @pytest.mark.no_state
   def test_pure_logic():
       pass
   
   @pytest.mark.integration
   @pytest.mark.uses_state
   def test_with_real_state():
       pass
   ```

## Implementation Priority

1. **Phase 1**: Implement base isolation fixtures
2. **Phase 2**: Write unit tests with full mocking
3. **Phase 3**: Add integration tests with real StateManager
4. **Phase 4**: Add stress tests to verify isolation

## Success Criteria

- Tests pass regardless of execution order
- No test leaves artifacts on disk
- State changes in one test don't affect others
- Parallel execution works without conflicts
- Each test starts with predictable initial state