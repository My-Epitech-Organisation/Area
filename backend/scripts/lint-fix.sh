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
if ! python -c "import ruff" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Development dependencies not found. Installing...${NC}"
    pip install -r "$BACKEND_DIR/requirements-dev.txt"
fi

# Change to backend directory
cd "$BACKEND_DIR"

# Determine target path
TARGET_PATH=${1:-.}

echo -e "${BLUE}📂 Fixing: $TARGET_PATH${NC}"
echo

# 1. Fix all auto-fixable issues with Ruff
echo -e "${BLUE}⚡ Auto-fixing with Ruff (imports + style + formatting)...${NC}"
if ruff check --fix "$TARGET_PATH"; then
    echo -e "${GREEN}✅ Ruff linting fixes: COMPLETED${NC}"
else
    echo -e "${YELLOW}⚠️  No linting changes needed${NC}"
fi
echo

# 2. Format code with Ruff
echo -e "${BLUE}🎨 Formatting code with Ruff...${NC}"
if ruff format "$TARGET_PATH"; then
    echo -e "${GREEN}✅ Ruff formatting: COMPLETED${NC}"
else
    echo -e "${YELLOW}⚠️  No formatting changes needed${NC}"
fi
echo

# 3. Check remaining issues that can't be auto-fixed
echo -e "${BLUE}🔍 Checking for remaining issues...${NC}"

# Run ruff check to show remaining unfixable issues
echo -e "${YELLOW}📏 Checking remaining issues (Ruff):${NC}"
if ruff check "$TARGET_PATH" 2>/dev/null; then
    echo -e "${GREEN}✅ No remaining issues${NC}"
else
    echo -e "${YELLOW}⚠️  Some issues require manual fixing${NC}"
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
echo "  ✅ Import sorting (Ruff I rules)"
echo "  ✅ Code formatting (Ruff formatter)"
echo "  ✅ Style issues (Ruff auto-fixes)"
echo
echo "If you saw warnings above, you may need to:"
echo "  📏 Fix remaining style/security issues manually"
echo "  🔒 Review and fix security issues (run bandit separately if needed)"
echo
echo "Run './scripts/lint-check.sh' to verify all issues are resolved."