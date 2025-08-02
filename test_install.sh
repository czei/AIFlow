#!/bin/bash
set -euo pipefail

# AIFlow - Installation Test Script
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
TEST_DIR=$(secure_temp_dir "aiflow-test") || {
    echo "Error: Failed to create test directory" >&2
    exit 1
}
TEST_HOME="$TEST_DIR/home"
TEST_PROJECT="$TEST_DIR/test-project"
TEST_LOG="$TEST_DIR/test.log"

# Non-interactive mode for CI
export CI=true

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

echo "🧪 AIFlow - Installation Test Suite"
echo "========================================================"
echo "Testing new project-level and global installation modes"
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
    
    # Run test with timeout
    if timeout 30s $test_function; then
        ((TESTS_PASSED++))
        print_status "success" "$test_name"
    else
        local exit_code=$?
        if [[ $exit_code -eq 124 ]]; then
            print_status "error" "$test_name (TIMEOUT)"
        else
            print_status "error" "$test_name"
        fi
        ((TESTS_FAILED++))
    fi
}

# Setup test environment
setup_test_env() {
    print_status "info" "Setting up test environment at $TEST_DIR"
    
    # Create test directory structure
    mkdir -p "$TEST_HOME/.claude/commands" || return 1
    mkdir -p "$TEST_PROJECT" || return 1
    mkdir -p "$TEST_DIR/logs" || return 1
    
    # Initialize git repo for project tests
    cd "$TEST_PROJECT" && git init > /dev/null 2>&1
    cd "$PROJECT_ROOT"
    
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

# Test: Argument parsing - help
test_args_help() {
    local output
    output=$(bash "$PROJECT_ROOT/install.sh" --help 2>&1)
    
    if echo "$output" | grep -q "Usage:.*install.sh.*OPTIONS"; then
        return 0
    fi
    echo "Help output missing usage information" >> "$TEST_LOG"
    return 1
}

# Test: Default project installation (current directory)
test_project_install_default() {
    # Create a temp project directory
    local temp_project="$TEST_DIR/default-project"
    mkdir -p "$temp_project"
    cd "$temp_project"
    git init > /dev/null 2>&1
    
    # Run install in project mode (default)
    bash "$PROJECT_ROOT/install.sh" >> "$TEST_LOG" 2>&1
    
    # Check if project installation succeeded
    if [[ -d "$temp_project/.claude/commands/project" ]] && \
       [[ -f "$temp_project/.claude/settings.json" ]] && \
       [[ -d "$temp_project/.claude/hooks" ]]; then
        cd "$PROJECT_ROOT"
        return 0
    fi
    
    cd "$PROJECT_ROOT"
    echo "Project installation failed" >> "$TEST_LOG"
    return 1
}

# Test: Global installation with --global flag
test_global_install() {
    # Run install script with test home and global flag
    HOME="$TEST_HOME" bash "$PROJECT_ROOT/install.sh" --global >> "$TEST_LOG" 2>&1
    
    # Check if global installation succeeded
    if [[ -d "$TEST_HOME/.claude/commands/project" ]] && \
       [[ -d "$TEST_HOME/.claude/commands/project/hooks" ]]; then
        return 0
    fi
    echo "Global installation failed" >> "$TEST_LOG"
    return 1
}

# Test: Project installation with --project-dir
test_project_dir_install() {
    # Run install with specific project directory
    bash "$PROJECT_ROOT/install.sh" --project-dir "$TEST_PROJECT" >> "$TEST_LOG" 2>&1
    
    # Check if installation succeeded in specified directory
    if [[ -d "$TEST_PROJECT/.claude/commands/project" ]] && \
       [[ -f "$TEST_PROJECT/.claude/settings.json" ]] && \
       [[ -d "$TEST_PROJECT/.claude/hooks" ]]; then
        return 0
    fi
    echo "Project directory installation failed" >> "$TEST_LOG"
    return 1
}

# Test: Hook import mechanism for project install
test_hooks_import_project() {
    # First ensure we have a project installation
    if [[ ! -d "$TEST_PROJECT/.claude" ]]; then
        test_project_dir_install
    fi
    
    # Test that hooks can import modules correctly
    cd "$TEST_PROJECT"
    local test_output
    test_output=$(echo '{"tool": "Test", "cwd": ".", "input": {}}' | python3 .claude/hooks/pre_tool_use.py 2>&1)
    
    # Check if import was successful (no ImportError)
    if echo "$test_output" | grep -q "ImportError"; then
        echo "Hook import failed for project install: $test_output" >> "$TEST_LOG"
        cd "$PROJECT_ROOT"
        return 1
    fi
    
    cd "$PROJECT_ROOT"
    return 0
}

# Test: Hook import mechanism for global install
test_hooks_import_global() {
    # First ensure we have a global installation
    if [[ ! -d "$TEST_HOME/.claude/commands/project" ]]; then
        test_global_install
    fi
    
    # Test that hooks can import modules correctly
    local hook_path="$TEST_HOME/.claude/commands/project/hooks/pre_tool_use.py"
    local test_output
    HOME="$TEST_HOME" test_output=$(echo '{"tool": "Test", "cwd": ".", "input": {}}' | python3 "$hook_path" 2>&1)
    
    # Check if import was successful (no ImportError)
    if echo "$test_output" | grep -q "ImportError"; then
        echo "Hook import failed for global install: $test_output" >> "$TEST_LOG"
        return 1
    fi
    
    return 0
}

# Test: Settings.json created for project install
test_settings_json_creation() {
    # Check if settings.json was created with correct content
    local settings_file="$TEST_PROJECT/.claude/settings.json"
    
    if [[ ! -f "$settings_file" ]]; then
        echo "settings.json not created" >> "$TEST_LOG"
        return 1
    fi
    
    # Check if it contains correct hook paths
    if grep -q "python3 .claude/hooks/pre_tool_use.py" "$settings_file" && \
       grep -q "python3 .claude/hooks/post_tool_use.py" "$settings_file" && \
       grep -q "python3 .claude/hooks/stop.py" "$settings_file"; then
        return 0
    fi
    
    echo "settings.json has incorrect content" >> "$TEST_LOG"
    return 1
}

# Test: Uninstall project installation
test_uninstall_project() {
    # Ensure we have a project installation
    if [[ ! -d "$TEST_PROJECT/.claude" ]]; then
        test_project_dir_install
    fi
    
    # Run uninstall
    bash "$PROJECT_ROOT/install.sh" --project-dir "$TEST_PROJECT" --uninstall >> "$TEST_LOG" 2>&1
    
    # Check if .claude directory was removed
    if [[ ! -d "$TEST_PROJECT/.claude" ]]; then
        return 0
    fi
    
    echo "Project uninstall failed" >> "$TEST_LOG"
    return 1
}

# Test: Uninstall global installation  
test_uninstall_global() {
    # Ensure we have a global installation
    if [[ ! -d "$TEST_HOME/.claude/commands/project" ]]; then
        test_global_install
    fi
    
    # Run uninstall
    HOME="$TEST_HOME" bash "$PROJECT_ROOT/install.sh" --global --uninstall >> "$TEST_LOG" 2>&1
    
    # Check if directory was removed
    if [[ ! -d "$TEST_HOME/.claude/commands/project" ]]; then
        return 0
    fi
    
    echo "Global uninstall failed" >> "$TEST_LOG"
    return 1
}

# Test: Invalid arguments handling
test_args_invalid() {
    local output
    output=$(bash "$PROJECT_ROOT/install.sh" --invalid-option 2>&1)
    
    # Should show error and help
    if echo "$output" | grep -q "Error: Unknown option --invalid-option" && \
       echo "$output" | grep -q "Usage:"; then
        return 0
    fi
    
    echo "Invalid argument not handled properly" >> "$TEST_LOG"
    return 1
}

# Test: Missing argument value
test_args_missing_value() {
    local output
    output=$(bash "$PROJECT_ROOT/install.sh" --project-dir 2>&1 || true)
    
    # Should show error about missing directory
    if echo "$output" | grep -q "Error" || echo "$output" | grep -q "requires"; then
        return 0
    fi
    
    echo "Missing argument value not handled properly" >> "$TEST_LOG"
    return 1
}

# Test: Non-git directory warning
test_non_git_directory() {
    # Create a non-git directory
    local non_git_dir="$TEST_DIR/non-git-project"
    mkdir -p "$non_git_dir"
    
    # Try to install (should warn but continue in CI mode)
    local output
    output=$(CI=true bash "$PROJECT_ROOT/install.sh" --project-dir "$non_git_dir" 2>&1)
    
    # Check for warning
    if echo "$output" | grep -q "Warning.*not a git repository"; then
        # In CI mode, it should exit with error
        if [[ -d "$non_git_dir/.claude" ]]; then
            echo "Non-git directory should not install in CI mode" >> "$TEST_LOG"
            return 1
        fi
        return 0
    fi
    
    echo "No warning for non-git directory" >> "$TEST_LOG"
    return 1
}

# Test: Validate path bug fix
test_validate_path_fix() {
    # This tests the bug we found where validate_path was called with wrong number of arguments
    # The install should work with an absolute path
    local abs_path="$TEST_DIR/absolute-path-test"
    mkdir -p "$abs_path"
    cd "$abs_path"
    git init > /dev/null 2>&1
    
    # This used to fail with "unbound variable" error
    local output
    output=$(bash "$PROJECT_ROOT/install.sh" --project-dir "$abs_path" 2>&1)
    local exit_code=$?
    
    cd "$PROJECT_ROOT"
    
    if [[ $exit_code -eq 0 ]] && [[ -d "$abs_path/.claude" ]]; then
        return 0
    fi
    
    echo "Absolute path installation failed: $output" >> "$TEST_LOG"
    return 1
}

# Test: Directory structure for project install
test_project_directory_structure() {
    # Check project installation structure
    if [[ ! -d "$TEST_PROJECT/.claude/commands/project" ]] || \
       [[ ! -d "$TEST_PROJECT/.claude/hooks" ]] || \
       [[ ! -f "$TEST_PROJECT/.claude/settings.json" ]]; then
        echo "Project directory structure incorrect" >> "$TEST_LOG"
        return 1
    fi
    
    # Check hooks are in project location, not global
    if [[ ! -f "$TEST_PROJECT/.claude/hooks/pre_tool_use.py" ]]; then
        echo "Hooks not in project location" >> "$TEST_LOG"
        return 1
    fi
    
    return 0
}

# Test: Global directory structure
test_global_directory_structure() {
    # Ensure we have global install
    if [[ ! -d "$TEST_HOME/.claude/commands/project" ]]; then
        test_global_install
    fi
    
    # Check global installation structure
    if [[ ! -d "$TEST_HOME/.claude/commands/project/hooks" ]] || \
       [[ ! -d "$TEST_HOME/.claude/commands/project/lib" ]]; then
        echo "Global directory structure incorrect" >> "$TEST_LOG"
        return 1
    fi
    
    # Check hooks are in global location
    if [[ ! -f "$TEST_HOME/.claude/commands/project/hooks/pre_tool_use.py" ]]; then
        echo "Hooks not in global location" >> "$TEST_LOG"
        return 1
    fi
    
    return 0
}

# Test: Hook import helper exists
test_hook_import_helper() {
    # Check both installation types have the import helper
    local project_helper="$TEST_PROJECT/.claude/hooks/hook_import_helper.py"
    local global_helper="$TEST_HOME/.claude/commands/project/hooks/hook_import_helper.py"
    
    # Check project install
    if [[ -d "$TEST_PROJECT/.claude" ]] && [[ ! -f "$project_helper" ]]; then
        echo "Missing hook_import_helper.py in project install" >> "$TEST_LOG"
        return 1
    fi
    
    # Check global install
    if [[ -d "$TEST_HOME/.claude/commands/project" ]] && [[ ! -f "$global_helper" ]]; then
        echo "Missing hook_import_helper.py in global install" >> "$TEST_LOG"
        return 1
    fi
    
    return 0
}

# Test: Performance - installation completes quickly
test_performance() {
    local start_time=$(date +%s)
    
    # Run a project installation
    local temp_perf_dir="$TEST_DIR/perf-test"
    mkdir -p "$temp_perf_dir"
    cd "$temp_perf_dir"
    git init > /dev/null 2>&1
    
    bash "$PROJECT_ROOT/install.sh" > /dev/null 2>&1
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    cd "$PROJECT_ROOT"
    
    # Should complete in less than 10 seconds
    if [[ $duration -lt 10 ]]; then
        return 0
    fi
    
    echo "Installation took too long: ${duration}s" >> "$TEST_LOG"
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
    
    # Basic tests
    print_status "info" "=== Argument Parsing Tests ==="
    run_test "Help Option" test_args_help
    run_test "Invalid Arguments" test_args_invalid
    run_test "Missing Argument Value" test_args_missing_value
    
    echo ""
    print_status "info" "=== Installation Mode Tests ==="
    run_test "Prerequisites Check" test_prerequisites
    run_test "Project Install (Default)" test_project_install_default
    run_test "Project Install (--project-dir)" test_project_dir_install
    run_test "Global Install (--global)" test_global_install
    
    echo ""
    print_status "info" "=== Directory Structure Tests ==="
    run_test "Project Directory Structure" test_project_directory_structure
    run_test "Global Directory Structure" test_global_directory_structure
    
    echo ""
    print_status "info" "=== Hook System Tests ==="
    run_test "Hook Import Helper" test_hook_import_helper
    run_test "Hook Imports (Project)" test_hooks_import_project
    run_test "Hook Imports (Global)" test_hooks_import_global
    run_test "Settings.json Creation" test_settings_json_creation
    
    echo ""
    print_status "info" "=== Edge Case Tests ==="
    run_test "Non-Git Directory Warning" test_non_git_directory
    run_test "Validate Path Bug Fix" test_validate_path_fix
    
    echo ""
    print_status "info" "=== Cleanup Tests ==="
    run_test "Uninstall Project" test_uninstall_project
    run_test "Uninstall Global" test_uninstall_global
    
    echo ""
    print_status "info" "=== Performance Tests ==="
    run_test "Installation Speed" test_performance
    
    # Show results
    show_results
    
    # Cleanup (optional - comment out to inspect test directory)
    if [[ -t 0 ]] && [[ -z "${CI:-}" ]]; then
        # Interactive mode - ask user
        read -p "Clean up test directory? (Y/n): " cleanup_choice
        if [[ "$cleanup_choice" =~ ^[Nn]$ ]]; then
            print_status "info" "Test directory preserved at: $TEST_DIR"
        else
            cleanup_test_env
        fi
    else
        # Non-interactive mode - always cleanup
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