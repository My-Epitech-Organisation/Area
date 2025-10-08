#!/bin/bash

#  lint-check.sh - Code quality check script for Flutter frontend
#  This script checks formatting and linting using Flutter & Dart tools.
#  Exits with non-zero if any issue is found.

set -euo pipefail

# Colors
RED="\033[0;31m"
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
BLUE="\033[0;34m"
NC="\033[0m" # No Color

# Paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="$(dirname "$SCRIPT_DIR")"

cd "$FRONTEND_DIR"

echo -e "${BLUE}🔍 Flutter Frontend Code Quality Check${NC}"
echo "========================================"

# Format check
echo -e "${BLUE}📏 Checking code formatting (dart format)...${NC}"
if dart format --output=none --set-exit-if-changed .; then
    echo -e "${GREEN}✅ Format: PASSED${NC}"
else
    echo -e "${RED}❌ Format: FAILED${NC}"
    echo "👉 Run './scripts/lint-fix.sh' to fix automatically."
    exit 1
fi
echo

# Static analysis
echo -e "${BLUE}🔎 Running Flutter analyze...${NC}"
if flutter analyze; then
    echo -e "${GREEN}✅ Analyze: PASSED${NC}"
else
    echo -e "${RED}❌ Analyze: FAILED${NC}"
    exit 1
fi
echo

echo "========================================"
echo -e "${GREEN}🎉 All checks passed!${NC}"
