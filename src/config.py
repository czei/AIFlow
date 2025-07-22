#!/usr/bin/env python3
"""
Central configuration module for constants and settings.
This prevents magic numbers scattered throughout the codebase.
"""

# Timeout constants (in seconds)
DEFAULT_TEST_TIMEOUT = 300  # 5 minutes
UNIT_TEST_TIMEOUT = 300  # 5 minutes
INTEGRATION_TEST_TIMEOUT = 600  # 10 minutes
CONTRACT_TEST_TIMEOUT = 600  # 10 minutes
CHAOS_TEST_TIMEOUT = 1200  # 20 minutes
COMMAND_EXECUTION_TIMEOUT = 300  # 5 minutes

# AI Provider constants
MAX_PROMPT_LENGTH = 10000  # Maximum characters in a prompt
CACHE_TTL_HOURS = 24  # Cache time-to-live
MAX_RETRIES = 3  # Maximum retry attempts for AI queries
DEFAULT_AI_MODEL = "claude-3-opus-20240229"
DEFAULT_MAX_TOKENS = 4096
DEFAULT_TEMPERATURE = 0.7

# Test layer constants
DEFAULT_TEST_PATTERNS = {
    "shell": ["**/*.sh"],
    "unit": ["**/test_*.py", "**/*_test.py"],
    "integration": ["**/test_*integration*.py"],
    "contract": ["**/test_*_contract.py"],
    "chaos": ["**/test_*_chaos.py"]
}

# Chaos testing constants
DEFAULT_NETWORK_LATENCY = 0.5  # seconds
DEFAULT_FAILURE_RATE = 0.1  # 10% failure rate
DEFAULT_TIMEOUT_PROBABILITY = 0.05  # 5% timeout chance
CHAOS_SEED_RANGE = (1, 10000)
MIN_RESILIENCE_THRESHOLD = 0.7  # 70% minimum resilience score

# Logging constants
LOG_CATEGORIES = [
    "automation",
    "workflow", 
    "commands",
    "quality-gates",
    "phase-transitions",
    "errors",
    "performance"
]

# File path constants
DEFAULT_TEST_RESULTS_DIR = "test_results"
DEFAULT_PLUGIN_DIR = "test_layers"
DEFAULT_CACHE_DIR = ".cache/ai_project_mgmt"
DEFAULT_CONFIG_FILE = "test_config.yaml"

# Rate limiting constants
MAX_API_CALLS_PER_MINUTE = 60
MAX_API_CALLS_PER_HOUR = 1000

# Performance constants
DEFAULT_THREAD_POOL_SIZE = 4  # For parallel execution
MAX_CONCURRENT_TESTS = 10