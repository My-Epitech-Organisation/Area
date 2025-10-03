#!/bin/bash

# lint-check.sh - Code quality verification script (read-only)
# This script checks code quality without making any modifications

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"
VENV_PATH="$BACKEND_DIR/venv"

# Exit codes
EXIT_SUCCESS=0
EXIT_FORMAT_ISSUES=1
EXIT_STYLE_ISSUES=2
EXIT_SECURITY_ISSUES=8

total_exit_code=0

echo -e "${BLUE}🔍 Django Backend Code Quality Check${NC}"
echo "========================================"

# Check if virtual environment exists
if [ ! -d "$VENV_PATH" ]; then
    echo -e "${RED}❌ Virtual environment not found at $VENV_PATH${NC}"
    echo "Please create a virtual environment first:"
    echo "  python -m venv $VENV_PATH"
    echo "  source $VENV_PATH/bin/activate"
    echo "  pip install -r requirements.txt -r requirements-dev.txt"
    exit 1
fi

# Activate virtual environment
echo -e "${BLUE}🐍 Activating virtual environment...${NC}"
source "$VENV_PATH/bin/activate"

# Check if dev dependencies are installed
if ! python -c "import ruff" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Development dependencies not found. Installing...${NC}"
    pip install -r "$BACKEND_DIR/requirements-dev.txt"
fi

# Change to backend directory
cd "$BACKEND_DIR"

# Determine target path
TARGET_PATH=${1:-.}

echo -e "${BLUE}📂 Checking: $TARGET_PATH${NC}"
echo

# 1. Ruff linting check (replaces flake8, black --check, isort --check)
echo -e "${BLUE}⚡ Checking code with Ruff (linting + formatting + imports)...${NC}"
if ruff check "$TARGET_PATH" 2>/dev/null; then
    echo -e "${GREEN}✅ Ruff linting: PASSED${NC}"
else
    echo -e "${RED}❌ Ruff linting: FAILED${NC}"
    echo "Run './scripts/lint-fix.sh' to auto-fix your code"
    total_exit_code=$((total_exit_code | EXIT_STYLE_ISSUES))
fi
echo

# 2. Ruff formatting check
echo -e "${BLUE}🎨 Checking code formatting with Ruff...${NC}"
if ruff format --check --diff "$TARGET_PATH" 2>/dev/null; then
    echo -e "${GREEN}✅ Ruff formatting: PASSED${NC}"
else
    echo -e "${RED}❌ Ruff formatting: FAILED${NC}"
    echo "Run './scripts/lint-fix.sh' to auto-format your code"
    total_exit_code=$((total_exit_code | EXIT_FORMAT_ISSUES))
fi
echo

# 4. Security check with bandit
echo -e "${BLUE}🔒 Checking security with bandit...${NC}"
if bandit -r "$TARGET_PATH" -f screen -x "*/tests/*,*/migrations/*,*/venv/*" --severity-level medium 2>/dev/null; then
    echo -e "${GREEN}✅ Security check: PASSED${NC}"
else
    echo -e "${RED}❌ Security check: FAILED${NC}"
    echo "Please review and fix the security issues reported above"
    total_exit_code=$((total_exit_code | EXIT_SECURITY_ISSUES))
fi
echo

# Final summary
echo "========================================"
if [ $total_exit_code -eq 0 ]; then
    echo -e "${GREEN}🎉 All checks passed! Your code is clean.${NC}"
else
    echo -e "${RED}❌ Some checks failed. Exit code: $total_exit_code${NC}"
    echo
    echo "Quick fixes available:"
    echo "  - Format issues: Run './scripts/lint-fix.sh'"
    echo "  - Style/Security: Review and fix manually"
fi

exit $total_exit_code