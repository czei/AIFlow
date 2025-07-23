#!/bin/bash
# Run Sprint 3 End-to-End Integration Tests

echo "🚀 Running Sprint 3 Integration Tests..."
echo "====================================="
echo ""

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Run the Phase 3 test runner
python3 "$SCRIPT_DIR/tests/integration/test_phase3_runner.py"

# Capture exit code
EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Sprint 3 tests completed successfully!"
else
    echo "❌ Sprint 3 tests failed with exit code: $EXIT_CODE"
fi

exit $EXIT_CODE