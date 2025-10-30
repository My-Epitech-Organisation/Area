#!/bin/bash

# Simple script to display frontend coverage summary
# Usage: ./scripts/coverage-summary.sh

echo "🧪 Running tests with coverage..."
echo ""

OUTPUT=$(npm run test:coverage 2>&1)

echo "📝 TEST FILES:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

counter=1
echo "$OUTPUT" | grep "src/" | grep -E "✓|✗" | awk -F'[()]' '{
    # Extract full path and test count
    path = $1
    tests = $2

    # Extract just the filename from the path
    gsub(/.*\//, "", path)
    gsub(/^ +| +$/, "", path)
    gsub(/ tests.*/, "", tests)

    printf "[%2d] ✅ %-60s %s\n", NR, path, tests
}'

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "📊 GLOBAL SUMMARY:"
echo "$OUTPUT" | grep -E "Test Files|Tests " | head -2
echo "$OUTPUT" | grep "All files"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Format: Statements | Branches | Functions | Lines"
echo "🎯 Target: 60% minimum for Statements and Lines"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
