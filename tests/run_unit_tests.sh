#!/bin/bash
# Run unit tests for deterministic components

echo "Running unit tests for deterministic components..."
echo "================================================"

# Ensure we're in the project root
cd "$(dirname "$0")/.." || exit 1

# Run unit tests
python3 -m unittest discover -s tests/unit -p "test_*.py" -v

# Capture exit code
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "✅ All unit tests passed!"
else
    echo ""
    echo "❌ Unit tests failed with exit code: $EXIT_CODE"
fi

exit $EXIT_CODE