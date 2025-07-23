"""
Configuration module for AI Software Project Management System.

Central location for all configuration values to avoid hardcoded
strings and improve maintainability.
"""

from typing import List, Dict, Any


class WorkflowConfig:
    """Workflow-related configuration."""
    
    # Workflow steps in order
    WORKFLOW_STEPS: List[str] = [
        "planning",
        "implementation", 
        "validation",
        "review",
        "refinement",
        "integration"
    ]
    
    # Quality gates
    QUALITY_GATES: List[str] = [
        "compilation",
        "existing_tests",
        "new_tests",
        "review",
        "integration",
        "documentation",
        "performance"
    ]
    
    # Tool categories
    READ_TOOLS: List[str] = ['Read', 'LS', 'Glob', 'Grep', 'WebSearch', 'WebFetch', 'Task']
    WRITE_TOOLS: List[str] = ['Write', 'Edit', 'MultiEdit']
    EXEC_TOOLS: List[str] = ['Bash', 'Python', 'JavaScript']
    GIT_TOOLS: List[str] = ['GitStatus', 'GitDiff', 'GitCommit', 'GitPush']
    
    # Emergency override patterns
    EMERGENCY_PATTERNS: List[str] = [
        r'EMERGENCY:',
        r'HOTFIX:',
        r'CRITICAL:',
        r'OVERRIDE:',
        r'production.*down',
        r'security.*vulnerability',
        r'data.*loss'
    ]


class StateConfig:
    """State management configuration."""
    
    # Valid project states
    VALID_STATES: List[str] = [
        "setup",
        "active",
        "paused",
        "stopped",
        "completed",
        "error"
    ]
    
    # State file settings
    STATE_FILE_NAME: str = ".project-state.json"
    STATE_FILE_VERSION: str = "1.0.0"
    
    # File locking
    LOCK_TIMEOUT_SECONDS: float = 5.0
    LOCK_RETRY_DELAY: float = 0.1


class ProjectConfig:
    """Project structure configuration."""
    
    # Directory names
    PROJECT_DIRS: List[str] = ['phases', '.claude', 'logs', 'docs']
    
    # Phase file names
    PHASE_FILES: Dict[str, str] = {
        '01-planning.md': 'Planning',
        '02-architecture.md': 'Architecture',
        '03-implementation.md': 'Implementation',
        '04-testing.md': 'Testing',
        '05-deployment.md': 'Deployment'
    }
    
    # Claude settings
    CLAUDE_SETTINGS_FILE: str = ".claude/settings.json"
    CLAUDE_SETTINGS_VERSION: str = "1.0.0"


class HookConfig:
    """Hook configuration."""
    
    # Hook names
    PRE_TOOL_USE_HOOK: str = "pre_tool_use"
    POST_TOOL_USE_HOOK: str = "post_tool_use"
    STOP_HOOK: str = "stop"
    
    # Performance settings
    MAX_HOOK_EXECUTION_MS: int = 100
    PERFORMANCE_TEST_ITERATIONS: int = 10


class MessagesConfig:
    """User-facing messages configuration."""
    
    # Workflow messages
    WORKFLOW_MESSAGES: Dict[str, str] = {
        'planning': "🚫 Planning phase: Complete requirements analysis before writing code.",
        'implementation': "✅ Implementation phase: All tools available.",
        'validation': "🧪 Validation phase: Focus on testing and verification.",
        'review': "👀 Review phase: Analyze code quality and architecture.",
        'refinement': "🔧 Refinement phase: Apply review feedback.",
        'integration': "🔀 Integration phase: Prepare for merge."
    }
    
    # Step guidance
    STEP_GUIDANCE: Dict[str, str] = {
        'planning': "Analyze requirements and design your approach",
        'implementation': "Write production-quality code",
        'validation': "Run tests and verify functionality",
        'review': "Perform code review and analysis",
        'refinement': "Address feedback and improve quality",
        'integration': "Final testing, documentation, and commit"
    }
    
    # Success messages
    SUCCESS_MESSAGES: Dict[str, str] = {
        'project_created': "✅ Project created at {path}",
        'state_created': "✅ Project state initialized",
        'workflow_advanced': "✅ Advanced to {step} phase",
        'phase_completed': "🎉 Phase completed: {phase}",
        'all_phases_completed': "🏆 All {count} phases completed!"
    }
    
    # Error messages
    ERROR_MESSAGES: Dict[str, str] = {
        'state_exists': "State file already exists: {path}",
        'state_not_found': "State file not found: {path}",
        'invalid_transition': "Invalid phase transition from {current} to {target}",
        'incomplete_phase': "Cannot advance from incomplete phase {phase}",
        'corrupt_state': "Corrupt state file: {error}",
        'permission_denied': "Permission denied: {error}",
        'lock_timeout': "Could not acquire lock after {timeout}s"
    }


class TestConfig:
    """Test configuration."""
    
    # Test settings
    TEST_PROJECT_NAME: str = "test-integration"
    TEST_DIR_PREFIX: str = "claude_"
    
    # Performance benchmarks
    MAX_STATE_READ_MS: float = 10.0
    MAX_STATE_UPDATE_MS: float = 10.0
    MAX_HOOK_EXECUTION_MS: float = 100.0
    
    # Concurrent test settings
    CONCURRENT_PROCESSES: int = 5
    UPDATES_PER_PROCESS: int = 10
    READS_PER_PROCESS: int = 20


# Singleton instances
workflow = WorkflowConfig()
state = StateConfig()
project = ProjectConfig()
hooks = HookConfig()
messages = MessagesConfig()
tests = TestConfig()