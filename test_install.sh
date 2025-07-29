#!/bin/bash
set -euo pipefail

# AI Software Project Management System - Installation Test Script
# This script validates the installation in a temporary environment

# Get the absolute path to the project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source security library
source "$PROJECT_ROOT/scripts/common_security.sh" || {
    echo "Error: Failed to load security library" >&2
    exit 1
}

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Test configuration
TEST_DIR=$(secure_temp_dir "claude-pm-test") || {
    echo "Error: Failed to create test directory" >&2
    exit 1
}
TEST_HOME="$TEST_DIR/home"
TEST_LOG="$TEST_DIR/test.log"

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Cleanup function
final_cleanup() {
    if [[ -n "${TEST_DIR:-}" ]] && [[ -d "$TEST_DIR" ]]; then
        echo ""
        echo "Cleaning up test directory..."
        rm -rf "$TEST_DIR"
    fi
}

# Signal handler
handle_signal() {
    local signal="$1"
    print_status "warning" "Test interrupted by signal: $signal"
    log_security_event "INTERRUPT" "Test interrupted" "Signal: $signal"
    exit 130
}

# Set up cleanup and signal traps
setup_cleanup_trap final_cleanup
trap 'handle_signal INT' INT
trap 'handle_signal TERM' TERM
trap 'handle_signal HUP' HUP

echo "🧪 AI Software Project Management System - Installation Test"
echo "=========================================================="
echo ""

# Function to print colored output
print_status() {
    local status=$1
    local message=$2
    case $status in
        "success")
            echo -e "${GREEN}✅ $message${NC}" | tee -a "$TEST_LOG"
            ;;
        "error")
            echo -e "${RED}❌ $message${NC}" | tee -a "$TEST_LOG"
            ;;
        "warning")
            echo -e "${YELLOW}⚠️  $message${NC}" | tee -a "$TEST_LOG"
            ;;
        "info")
            echo -e "${BLUE}ℹ️  $message${NC}" | tee -a "$TEST_LOG"
            ;;
        "test")
            echo -e "${CYAN}🧪 $message${NC}" | tee -a "$TEST_LOG"
            ;;
    esac
}

# Function to run a test
run_test() {
    local test_name=$1
    local test_function=$2
    
    ((TESTS_RUN++))
    print_status "test" "Running: $test_name"
    
    if $test_function; then
        ((TESTS_PASSED++))
        print_status "success" "$test_name"
    else
        ((TESTS_FAILED++))
        print_status "error" "$test_name"
    fi
}

# Setup test environment
setup_test_env() {
    print_status "info" "Setting up test environment at $TEST_DIR"
    
    # Create test directory structure
    mkdir -p "$TEST_HOME/.claude/commands" || return 1
    mkdir -p "$TEST_DIR/logs" || return 1
    
    # Initialize log
    echo "Test started at $(date)" > "$TEST_LOG"
    
    return 0
}

# Cleanup test environment
cleanup_test_env() {
    print_status "info" "Cleaning up test environment"
    if [[ -d "$TEST_DIR" ]]; then
        rm -rf "$TEST_DIR"
    fi
}

# Test: Prerequisites check
test_prerequisites() {
    # Test Python detection
    if command -v python3 >/dev/null 2>&1; then
        local version=$(get_python_version "python3")
        if [[ $? -eq 0 ]] && version_ge "$version" "3.7"; then
            return 0
        fi
    fi
    return 1
}

# Test: Fresh installation
test_fresh_install() {
    # Run install script with test home
    HOME="$TEST_HOME" bash "$PROJECT_ROOT/install.sh" >> "$TEST_LOG" 2>&1
    
    # Check if installation succeeded
    if [[ -d "$TEST_HOME/.claude/commands/project" ]]; then
        return 0
    fi
    return 1
}

# Test: Command files installed
test_command_files() {
    local expected_commands=(
        "setup.md"
        "start.md"
        "status.md"
        "pause.md"
        "resume.md"
        "stop.md"
        "doctor.md"
    )
    
    local missing=0
    for cmd in "${expected_commands[@]}"; do
        if [[ ! -f "$TEST_HOME/.claude/commands/project/$cmd" ]]; then
            echo "Missing command: $cmd" >> "$TEST_LOG"
            ((missing++))
        fi
    done
    
    return $missing
}

# Test: Python modules installed
test_python_modules() {
    local module_path="$TEST_HOME/.claude/commands/project/lib"
    
    # Check key Python files
    local key_modules=(
        "src/state_manager.py"
        "src/config.py"
        "src/git_operations.py"
        "src/project_builder.py"
    )
    
    local missing=0
    for module in "${key_modules[@]}"; do
        if [[ ! -f "$module_path/$module" ]]; then
            echo "Missing module: $module" >> "$TEST_LOG"
            ((missing++))
        fi
    done
    
    return $missing
}

# Test: Hooks installed
test_hooks_installed() {
    local hooks_path="$TEST_HOME/.claude/commands/project/hooks"
    
    # Check key hook files
    local key_hooks=(
        "pre_tool_use.py"
        "post_tool_use.py"
        "stop.py"
        "workflow_rules.py"
        "hook_utils.py"
    )
    
    local missing=0
    for hook in "${key_hooks[@]}"; do
        if [[ ! -f "$hooks_path/$hook" ]]; then
            echo "Missing hook: $hook" >> "$TEST_LOG"
            ((missing++))
        fi
    done
    
    # Check README exists
    if [[ ! -f "$hooks_path/README.md" ]]; then
        echo "Missing hooks README" >> "$TEST_LOG"
        ((missing++))
    fi
    
    return $missing
}

# Test: No test files included
test_no_test_files() {
    # Ensure tests directory was not copied
    if [[ -d "$TEST_HOME/.claude/commands/project/lib/tests" ]]; then
        echo "Test files found in installation" >> "$TEST_LOG"
        return 1
    fi
    
    # Check for test files in other locations
    local test_files=$(find "$TEST_HOME/.claude/commands/project" -name "*test*.py" -o -name "test_*" | wc -l)
    if [[ $test_files -gt 0 ]]; then
        echo "Found $test_files test files in installation" >> "$TEST_LOG"
        return 1
    fi
    
    return 0
}

# Test: Python import validation
test_python_imports() {
    local module_path="$TEST_HOME/.claude/commands/project/lib"
    
    # Test basic import
    local import_test='import sys; sys.path.insert(0, "'"$module_path"'"); from src.state_manager import StateManager'
    if safe_execute "python3" -c "$import_test" 2>/dev/null; then
        return 0
    fi
    
    echo "Python import test failed" >> "$TEST_LOG"
    return 1
}

# Test: Scripts are executable
test_scripts_executable() {
    local errors=0
    
    # Check if scripts were copied and made executable
    for script in logged_secure_shell.py analyze_logs.sh; do
        local script_path="$TEST_HOME/.claude/commands/$script"
        if [[ -f "$script_path" ]]; then
            if [[ ! -x "$script_path" ]]; then
                echo "$script not executable" >> "$TEST_LOG"
                ((errors++))
            fi
        else
            echo "$script not found" >> "$TEST_LOG"
            ((errors++))
        fi
    done
    
    return $errors
}

# Test: Upgrade over existing installation
test_upgrade_install() {
    # Create a fake old installation
    mkdir -p "$TEST_HOME/.claude/commands/project/old_file"
    echo "old version" > "$TEST_HOME/.claude/commands/project/version.txt"
    
    # Run install again
    HOME="$TEST_HOME" bash "$PROJECT_ROOT/install.sh" >> "$TEST_LOG" 2>&1
    
    # Check if new files exist
    if [[ -f "$TEST_HOME/.claude/commands/project/setup.md" ]]; then
        return 0
    fi
    
    return 1
}

# Test: Installation validation
test_installation_validation() {
    # The install script should validate itself
    # Check if validation passed by looking for key indicators
    if grep -q "Installation validation passed" "$TEST_LOG"; then
        return 0
    fi
    
    return 1
}

# Test: Uninstall functionality
test_uninstall() {
    # First ensure we have an installation
    if [[ ! -d "$TEST_HOME/.claude/commands/project" ]]; then
        test_fresh_install
    fi
    
    # Run uninstall with auto-confirm
    echo "n" | HOME="$TEST_HOME" bash "$PROJECT_ROOT/uninstall.sh" >> "$TEST_LOG" 2>&1
    echo "y" | HOME="$TEST_HOME" bash "$PROJECT_ROOT/uninstall.sh" >> "$TEST_LOG" 2>&1
    
    # Check if files were removed
    if [[ ! -d "$TEST_HOME/.claude/commands/project" ]]; then
        return 0
    fi
    
    return 1
}

# Show test results
show_results() {
    echo ""
    echo "============================================="
    echo "Test Results"
    echo "============================================="
    echo ""
    echo "Tests run:    $TESTS_RUN"
    echo "Tests passed: $TESTS_PASSED"
    echo "Tests failed: $TESTS_FAILED"
    echo ""
    
    if [[ $TESTS_FAILED -eq 0 ]]; then
        print_status "success" "All tests passed! 🎉"
        echo ""
        echo "The installation script is working correctly."
    else
        print_status "error" "Some tests failed!"
        echo ""
        echo "Please check the test log for details:"
        echo "  $TEST_LOG"
        echo ""
        echo "Common issues:"
        echo "  • Missing files in the project"
        echo "  • Permission issues"
        echo "  • Script errors"
    fi
    
    echo ""
    echo "Test directory: $TEST_DIR"
    echo "(will be cleaned up automatically)"
}

# Main test flow
main() {
    # Setup test environment
    if ! setup_test_env; then
        print_status "error" "Failed to setup test environment"
        exit 1
    fi
    
    # Run tests
    print_status "info" "Running installation tests..."
    echo ""
    
    run_test "Prerequisites Check" test_prerequisites
    run_test "Fresh Installation" test_fresh_install
    run_test "Command Files" test_command_files
    run_test "Python Modules" test_python_modules
    run_test "Hook Scripts" test_hooks_installed
    run_test "No Test Files" test_no_test_files
    run_test "Python Imports" test_python_imports
    run_test "Scripts Executable" test_scripts_executable
    run_test "Upgrade Installation" test_upgrade_install
    run_test "Installation Validation" test_installation_validation
    run_test "Uninstall Script" test_uninstall
    
    # Show results
    show_results
    
    # Cleanup (optional - comment out to inspect test directory)
    read -p "Clean up test directory? (Y/n): " cleanup_choice
    validate_yes_no "$cleanup_choice"
    local response=$?
    if [[ $response -eq 0 ]] || [[ $response -eq 2 ]]; then
        # Yes or invalid (default to yes)
        cleanup_test_env
    fi
    
    # Exit with appropriate code
    if [[ $TESTS_FAILED -eq 0 ]]; then
        exit 0
    else
        exit 1
    fi
}

# Run main test
main