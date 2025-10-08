#!/bin/bash

#  lint-fix.sh - Code quality fix script for Flutter frontend
#  This script auto-formats code and re-runs analysis.

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

echo -e "${BLUE}🔧 Flutter Frontend Auto-Fix${NC}"
echo "=================================="

# 1. Auto-format
echo -e "${BLUE}📏 Formatting code (dart format)...${NC}"
dart format .

# 2. Re-run analysis
echo -e "${BLUE}🔎 Running Flutter analyze...${NC}"
if flutter analyze; then
    echo -e "${GREEN}✅ Analyze: PASSED${NC}"
else
    echo -e "${YELLOW}⚠️ Issues remain, manual fixes required${NC}"
fi

echo "=================================="
echo -e "${GREEN}🎉 Auto-fix completed!${NC}"
echo "👉 Run './scripts/lint-check.sh' again to verify."
