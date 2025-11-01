#!/bin/bash

# Script to clean all generated files from the frontend
# Usage: ./scripts/clean-generated.sh

echo "🧹 Cleaning generated files..."
echo ""

# Remove coverage reports
if [ -d "coverage" ]; then
    echo "  🗑️  Removing coverage/"
    rm -rf coverage
fi

# Remove HTML build artifacts
if [ -d "html" ]; then
    echo "  🗑️  Removing html/"
    rm -rf html
fi

# Remove meta files
if ls *.meta.json.gz 1> /dev/null 2>&1; then
    echo "  🗑️  Removing *.meta.json.gz"
    rm -f *.meta.json.gz
fi

# Remove Vitest cache
if [ -d ".vitest" ]; then
    echo "  🗑️  Removing .vitest/"
    rm -rf .vitest
fi

# Remove build artifacts
if [ -d "dist" ]; then
    echo "  🗑️  Removing dist/"
    rm -rf dist
fi

if [ -d "build" ]; then
    echo "  🗑️  Removing build/"
    rm -rf build
fi

# Remove accidentally generated test files
for file in Basic Dashboard Rendering Services should vitest frontend@*; do
    if [ -e "$file" ]; then
        echo "  🗑️  Removing $file"
        rm -f "$file"
    fi
done

echo ""
echo "✅ Cleanup complete!"
echo "📝 Cleaned directories: coverage, html, .vitest, dist, build"
