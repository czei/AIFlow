#!/bin/bash
# Run all tests for the Sprint-Driven Development System

echo "🧪 Sprint-Driven Development System - Full Test Suite"
echo "==================================================="
echo

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Change to tests directory
cd "$(dirname "$0")" || exit 1

# Function to run a test
run_test() {
    local test_name=$1
    local test_command=$2
    
    echo -e "\n${YELLOW}Running: $test_name${NC}"
    echo "----------------------------------------"
    
    if eval "$test_command"; then
        echo -e "${GREEN}✅ $test_name passed${NC}"
        return 0
    else
        echo -e "${RED}❌ $test_name failed${NC}"
        return 1
    fi
}

# Track test results
tests_passed=0
tests_failed=0

# Run unit tests
if run_test "Unit Tests" "python3 test_sprints.py"; then
    ((tests_passed++))
else
    ((tests_failed++))
fi

# Run command flow test
if run_test "Command Flow Test" "python3 ../scripts/command_flow_simulation.py < /dev/null"; then
    ((tests_passed++))
else
    ((tests_failed++))
fi

# Run integration test (non-interactive mode)
if run_test "Integration Test" "bash integration_test.sh < /dev/null"; then
    ((tests_passed++))
else
    ((tests_failed++))
fi

# Summary
echo
echo "==================================================="
echo "Test Summary:"
echo -e "  ${GREEN}Passed: $tests_passed${NC}"
echo -e "  ${RED}Failed: $tests_failed${NC}"
echo

if [ $tests_failed -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some tests failed${NC}"
    exit 1
fi
