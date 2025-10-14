#!/bin/bash

#  lint-check.sh - Code quality check script for React frontend
#  This script checks linting, CSS styling and formatting.
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

echo -e "${BLUE}🔍 React Frontend Code Quality Check${NC}"
echo "========================================"

# ESLint check
echo -e "${BLUE}🔎 Running ESLint...${NC}"
if npm run lint --silent; then
    echo -e "${GREEN}✅ ESLint: PASSED${NC}"
else
    echo -e "${RED}❌ ESLint: FAILED${NC}"
    echo "👉 Run './scripts/lint-fix.sh' to fix automatically."
    exit 1
fi
echo

# CSS Linting
echo -e "${BLUE}💅 Running Stylelint...${NC}"
if npm run lint:css --silent; then
    echo -e "${GREEN}✅ Stylelint: PASSED${NC}"
else
    echo -e "${RED}❌ Stylelint: FAILED${NC}"
    echo "👉 Run './scripts/lint-fix.sh' to fix automatically."
    exit 1
fi
echo

# Format check with Prettier
echo -e "${BLUE}✨ Checking formatting with Prettier...${NC}"
if npx prettier --check "**/*.{ts,tsx,css,md,json}" 2>/dev/null; then
    echo -e "${GREEN}✅ Prettier: PASSED${NC}"
else
    echo -e "${RED}❌ Prettier: FAILED${NC}"
    echo "👉 Run './scripts/lint-fix.sh' to fix automatically."
    exit 1
fi
echo

echo "========================================"
echo -e "${GREEN}🎉 All checks passed!${NC}"