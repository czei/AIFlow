#!/bin/bash
# Run all tests for AIFlow

echo "🧪 AIFlow - Full Test Suite"
echo "=========================================================="
echo

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Change to tests directory
cd "$(dirname "$0")" || exit 1

# Track test results
tests_passed=0
tests_failed=0

# Function to run a test script
run_test_script() {
    local test_name=$1
    local test_script=$2
    
    echo -e "\n${YELLOW}Running: $test_name${NC}"
    echo "----------------------------------------"
    
    if bash "$test_script"; then
        echo -e "${GREEN}✅ $test_name passed${NC}"
        ((tests_passed++))
        return 0
    else
        echo -e "${RED}❌ $test_name failed${NC}"
        ((tests_failed++))
        return 1
    fi
}

# Run unit tests
run_test_script "Unit Tests" "./run_unit_tests.sh"

# Run integration tests (includes Phase 3 tests)
run_test_script "Integration Tests" "./run_integration_tests.sh"

# Summary
echo
echo "=========================================================="
echo "Test Summary:"
echo -e "  ${GREEN}Test Suites Passed: $tests_passed${NC}"
echo -e "  ${RED}Test Suites Failed: $tests_failed${NC}"
echo

if [ $tests_failed -eq 0 ]; then
    echo -e "${GREEN}✅ All test suites passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some test suites failed${NC}"
    exit 1
fi