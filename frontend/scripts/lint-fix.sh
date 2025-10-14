#!/bin/bash

#  lint-fix.sh - Code quality fix script for React frontend
#  This script auto-fixes ESLint, Stylelint and Prettier issues.

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

echo -e "${BLUE}🔧 React Frontend Auto-Fix${NC}"
echo "=================================="

# 1. ESLint auto-fix
echo -e "${BLUE}🔎 Fixing ESLint issues...${NC}"
npm run lint:fix --silent
echo -e "${GREEN}✅ ESLint fixes applied${NC}"
echo

# 2. Stylelint auto-fix
echo -e "${BLUE}💅 Fixing Stylelint issues...${NC}"
npm run lint:css:fix --silent
echo -e "${GREEN}✅ Stylelint fixes applied${NC}"
echo

# 3. Prettier formatting
echo -e "${BLUE}✨ Fixing formatting with Prettier...${NC}"
npm run format --silent
echo -e "${GREEN}✅ Prettier formatting applied${NC}"
echo

echo "=================================="
echo -e "${GREEN}🎉 Auto-fix completed!${NC}"
echo "👉 Run './scripts/lint-check.sh' again to verify."