#!/bin/bash
# Run all integration tests including Phase 3 tests

echo "Running all integration tests..."
echo "================================"

# Ensure we're in the project root
cd "$(dirname "$0")/.." || exit 1

# Run all integration tests
echo "Running integration tests with unittest discover..."
python3 -m unittest discover -s tests/integration -p "test_*.py" -v

# Capture exit code
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "✅ All integration tests passed!"
else
    echo ""
    echo "❌ Integration tests failed with exit code: $EXIT_CODE"
fi

exit $EXIT_CODE