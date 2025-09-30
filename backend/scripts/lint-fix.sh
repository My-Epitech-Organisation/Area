#!/bin/bash

# lint-fix.sh - Automatic code formatting and fixing script

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

echo -e "${BLUE}🔧 Django Backend Code Auto-Fixer${NC}"
echo "=================================="

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
if ! python -c "import black" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Development dependencies not found. Installing...${NC}"
    pip install -r "$BACKEND_DIR/requirements-dev.txt"
fi

# Change to backend directory
cd "$BACKEND_DIR"

# Determine target path
TARGET_PATH=${1:-.}

echo -e "${BLUE}📂 Fixing: $TARGET_PATH${NC}"
echo

# 1. Sort imports with isort
echo -e "${BLUE}📚 Sorting imports with isort...${NC}"
if isort "$TARGET_PATH"; then
    echo -e "${GREEN}✅ Import sorting: COMPLETED${NC}"
else
    echo -e "${YELLOW}⚠️  No import changes needed${NC}"
fi
echo

# 2. Format code with Black
echo -e "${BLUE}🎨 Formatting code with Black...${NC}"
if black "$TARGET_PATH"; then
    echo -e "${GREEN}✅ Code formatting: COMPLETED${NC}"
else
    echo -e "${YELLOW}⚠️  No formatting changes needed${NC}"
fi
echo

# 3. Check remaining issues that can't be auto-fixed
echo -e "${BLUE}🔍 Checking for remaining issues...${NC}"

# Run flake8 to show remaining style issues
echo -e "${YELLOW}📏 Checking remaining style issues (flake8):${NC}"
if flake8 "$TARGET_PATH" --max-line-length=88 --extend-ignore=E203,W503 \
    --exclude=migrations,venv,__pycache__,.mypy_cache,reports \
    --extend-select=B,C,S,F401 2>/dev/null; then
    echo -e "${GREEN}✅ No remaining style issues${NC}"
else
    echo -e "${YELLOW}⚠️  Some style issues require manual fixing${NC}"
fi

echo

# Run bandit to show security issues
echo -e "${YELLOW}🔒 Checking security issues (bandit):${NC}"
if bandit -r "$TARGET_PATH" -f screen -x "*/tests/*,*/migrations/*,*/venv/*" --severity-level medium 2>/dev/null; then
    echo -e "${GREEN}✅ No security issues${NC}"
else
    echo -e "${YELLOW}⚠️  Some security issues require manual review${NC}"
fi

echo
echo "=================================="
echo -e "${GREEN}🎉 Auto-fixing completed!${NC}"
echo
echo "What was fixed automatically:"
echo "  ✅ Import sorting (isort)"
echo "  ✅ Code formatting (black)"
echo
echo "If you saw warnings above, you may need to:"
echo "  📏 Fix remaining style issues manually"
echo "  🔒 Review and fix security issues"
echo
echo "Run './scripts/lint-check.sh' to verify all issues are resolved."