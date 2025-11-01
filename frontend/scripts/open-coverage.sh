#!/bin/bash

# Usage: ./scripts/open-coverage.sh

COVERAGE_DIR="coverage"
COVERAGE_FILE="$COVERAGE_DIR/index.html"

if [ ! -f "$COVERAGE_FILE" ]; then
    echo "❌ Coverage report not found!"
    echo "📝 Please run 'npm run test:coverage' first to generate the report."
    exit 1
fi

echo "🌐 Opening coverage report in browser..."
echo "📊 Report location: $COVERAGE_FILE"
echo ""

if command -v xdg-open &> /dev/null; then
    xdg-open "$COVERAGE_FILE"
    echo "✅ Coverage report opened with default browser"
elif command -v firefox &> /dev/null; then
    firefox "$COVERAGE_FILE" &
    echo "✅ Coverage report opened in Firefox"
elif command -v google-chrome &> /dev/null; then
    google-chrome "$COVERAGE_FILE" &
    echo "✅ Coverage report opened in Chrome"
elif command -v chromium &> /dev/null; then
    chromium "$COVERAGE_FILE" &
    echo "✅ Coverage report opened in Chromium"
elif command -v open &> /dev/null; then
    open "$COVERAGE_FILE"
    echo "✅ Coverage report opened with default browser"
else
    echo "❌ No browser found!"
    echo "📝 Please open manually: file://$(pwd)/$COVERAGE_FILE"
    exit 1
fi
