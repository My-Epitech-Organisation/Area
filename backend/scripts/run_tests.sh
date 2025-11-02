#!/bin/bash

# run_tests.sh - Comprehensive Django test runner with coverage
# This script runs all Django tests and generates coverage reports

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"
VENV_PATH="$BACKEND_DIR/venv"

# Parse command line arguments
VERBOSITY=2
FAILFAST=false
KEEPDB=false
PARALLEL=1
SPECIFIC_TEST=""
SKIP_COVERAGE=false
HTML_REPORT=false

print_usage() {
    cat << EOF
${BOLD}Usage:${NC} $0 [OPTIONS] [TEST_PATH]

${BOLD}Description:${NC}
    Run Django tests with coverage reporting for the AREA automation system.

${BOLD}Options:${NC}
    -h, --help          Show this help message
    -v, --verbose       Increase verbosity (1-3, default: 2)
    -f, --failfast      Stop on first test failure
    -k, --keepdb        Preserve test database between runs
    -p, --parallel N    Run tests in N parallel processes
    -s, --skip-coverage Skip coverage report generation
    -H, --html          Generate HTML coverage report
    -q, --quiet         Minimal output (verbosity 0)

${BOLD}Test Paths:${NC}
    Without arguments:    Run all tests
    automations          Run all automations tests
    users                Run all users tests
    automations.tests.test_views
                         Run specific test module
    automations.tests.test_views.ServiceViewSetTest
                         Run specific test class
    automations.tests.test_views.ServiceViewSetTest.test_list_services
                         Run specific test method

${BOLD}Examples:${NC}
    # Run all tests with coverage
    $0

    # Run only automations tests with HTML report
    $0 --html automations

    # Run specific test with failfast and keepdb
    $0 -f -k automations.tests.test_serializers

    # Run tests in parallel without coverage
    $0 --parallel 4 --skip-coverage

    # Quick run with minimal output
    $0 -q -k automations.tests.test_views

EOF
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            print_usage
            exit 0
            ;;
        -v|--verbose)
            VERBOSITY=3
            shift
            ;;
        -q|--quiet)
            VERBOSITY=0
            shift
            ;;
        -f|--failfast)
            FAILFAST=true
            shift
            ;;
        -k|--keepdb)
            KEEPDB=true
            shift
            ;;
        -p|--parallel)
            PARALLEL="$2"
            shift 2
            ;;
        -s|--skip-coverage)
            SKIP_COVERAGE=true
            shift
            ;;
        -H|--html)
            HTML_REPORT=true
            shift
            ;;
        -*)
            echo -e "${RED}❌ Unknown option: $1${NC}"
            print_usage
            exit 1
            ;;
        *)
            SPECIFIC_TEST="$1"
            shift
            ;;
    esac
done

# Banner
echo -e "${BLUE}${BOLD}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║        🧪 AREA Django Test Suite with Coverage             ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check if we're in the backend directory
cd "$BACKEND_DIR"
echo -e "${CYAN}📂 Working directory: ${NC}$BACKEND_DIR"

# Set environment to test mode BEFORE activating venv
export DJANGO_ENV=test
export DJANGO_SETTINGS_MODULE=area_project.settings

# Activate virtual environment if it exists
if [ -d "$VENV_PATH" ]; then
    echo -e "${CYAN}🐍 Activating virtual environment...${NC}"

    # Use the Python binary directly to avoid lib/lib64 issues
    PYTHON_BIN="$VENV_PATH/bin/python"

    if [ -f "$PYTHON_BIN" ]; then
        # Export Python path to use venv directly
        export PATH="$VENV_PATH/bin:$PATH"
        export VIRTUAL_ENV="$VENV_PATH"
        # Unset PYTHONHOME to avoid conflicts
        unset PYTHONHOME
        echo -e "${GREEN}✅ Virtual environment activated${NC}"
    else
        echo -e "${RED}❌ Python binary not found in venv${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠️  No virtual environment found at $VENV_PATH${NC}"
    echo -e "${YELLOW}   Using system Python...${NC}"
    PYTHON_BIN="python3"
fi

# Check if required packages are installed
echo -e "${CYAN}📦 Checking dependencies...${NC}"
if ! $PYTHON_BIN -c "import django" 2>/dev/null; then
    echo -e "${RED}❌ Django not installed${NC}"
    exit 1
fi

if [ "$SKIP_COVERAGE" = false ]; then
    if ! $PYTHON_BIN -c "import coverage" 2>/dev/null; then
        echo -e "${YELLOW}⚠️  Coverage not installed, installing...${NC}"
        $PYTHON_BIN -m pip install coverage 2>&1 | grep -i "successfully installed" || true
    fi
fi

# Display test configuration
echo -e "\n${BOLD}Test Configuration:${NC}"
echo "  • Verbosity: $VERBOSITY"
echo "  • Fail Fast: $FAILFAST"
echo "  • Keep DB: $KEEPDB"
echo "  • Parallel: $PARALLEL processes"
echo "  • Coverage: $([ "$SKIP_COVERAGE" = false ] && echo "Enabled" || echo "Disabled")"
echo "  • HTML Report: $([ "$HTML_REPORT" = true ] && echo "Enabled" || echo "Disabled")"
if [ -n "$SPECIFIC_TEST" ]; then
    echo "  • Test Path: $SPECIFIC_TEST"
else
    echo "  • Test Path: All tests"
fi
echo ""

# Build test command
TEST_CMD="$PYTHON_BIN manage.py test"

if [ -n "$SPECIFIC_TEST" ]; then
    TEST_CMD="$TEST_CMD $SPECIFIC_TEST"
fi

TEST_CMD="$TEST_CMD --verbosity=$VERBOSITY"

if [ "$FAILFAST" = true ]; then
    TEST_CMD="$TEST_CMD --failfast"
fi

if [ "$KEEPDB" = true ]; then
    TEST_CMD="$TEST_CMD --keepdb"
fi

if [ "$PARALLEL" -gt 1 ]; then
    TEST_CMD="$TEST_CMD --parallel=$PARALLEL"
fi

# Run tests with or without coverage
echo -e "${BLUE}${BOLD}Running Tests...${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}\n"

if [ "$SKIP_COVERAGE" = false ]; then
    # Run with coverage
    $PYTHON_BIN -m coverage erase
    $PYTHON_BIN -m coverage run --source='.' manage.py test \
        $([ -n "$SPECIFIC_TEST" ] && echo "$SPECIFIC_TEST") \
        --verbosity=$VERBOSITY \
        $([ "$FAILFAST" = true ] && echo "--failfast") \
        $([ "$KEEPDB" = true ] && echo "--keepdb") \
        $([ "$PARALLEL" -gt 1 ] && echo "--parallel=$PARALLEL")
    TEST_EXIT_CODE=$?
else
    # Run without coverage
    eval $TEST_CMD
    TEST_EXIT_CODE=$?
fi

echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"

# Display results
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}${BOLD}✅ All tests passed!${NC}\n"
else
    echo -e "${RED}${BOLD}❌ Tests failed with exit code: $TEST_EXIT_CODE${NC}\n"
fi

# Generate coverage report
if [ "$SKIP_COVERAGE" = false ] && [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${BLUE}${BOLD}📊 Coverage Report${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}\n"
    
    # Terminal report
    $PYTHON_BIN -m coverage report --skip-empty
    
    echo ""
    
    # HTML report if requested
    if [ "$HTML_REPORT" = true ]; then
        echo -e "${CYAN}📄 Generating HTML coverage report...${NC}"
        $PYTHON_BIN -m coverage html
        HTML_DIR="$BACKEND_DIR/htmlcov"
        if [ -d "$HTML_DIR" ]; then
            echo -e "${GREEN}✅ HTML report generated at: ${BOLD}$HTML_DIR/index.html${NC}"
            echo -e "${CYAN}   Open with: ${NC}firefox $HTML_DIR/index.html"
        fi
        echo ""
    fi
    
    # Get coverage percentage
    COVERAGE_PCT=$($PYTHON_BIN -m coverage report --skip-empty | grep "TOTAL" | awk '{print $4}')
    if [ -n "$COVERAGE_PCT" ]; then
        COVERAGE_NUM=$(echo "$COVERAGE_PCT" | tr -d '%')
        echo -e "${BOLD}Overall Coverage: ${COVERAGE_PCT}${NC}"
        
        # Color-coded coverage assessment
        if (( $(echo "$COVERAGE_NUM >= 80" | bc -l) )); then
            echo -e "${GREEN}🎉 Excellent coverage!${NC}"
        elif (( $(echo "$COVERAGE_NUM >= 60" | bc -l) )); then
            echo -e "${YELLOW}⚠️  Good coverage, but could be improved${NC}"
        else
            echo -e "${RED}❌ Coverage needs improvement${NC}"
        fi
    fi
fi

# Display test summary
echo ""
echo -e "${BLUE}${BOLD}📋 Test Suite Summary${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"

# Count test files
AUTOMATIONS_TESTS=$(find automations/tests -name "test_*.py" 2>/dev/null | wc -l)
USERS_TESTS=$(find users/tests -name "test_*.py" 2>/dev/null | wc -l)
TOTAL_TEST_FILES=$((AUTOMATIONS_TESTS + USERS_TESTS))

echo -e "${BOLD}Test Files:${NC}"
echo "  • automations/tests: $AUTOMATIONS_TESTS files"
echo "  • users/tests: $USERS_TESTS files"
echo "  • Total: $TOTAL_TEST_FILES test files"
echo ""

# List test modules
echo -e "${BOLD}Automations Test Modules:${NC}"
for test_file in $(find automations/tests -name "test_*.py" -type f | sort); do
    test_name=$(basename "$test_file" .py)
    echo "  • $test_name"
done

echo ""
echo -e "${BOLD}Users Test Modules:${NC}"
for test_file in $(find users/tests -name "test_*.py" -type f | sort); do
    test_name=$(basename "$test_file" .py)
    echo "  • $test_name"
done

echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"

# Final status
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}${BOLD}✨ Test run completed successfully!${NC}"
    exit 0
else
    echo -e "${RED}${BOLD}💥 Test run failed!${NC}"
    echo -e "${YELLOW}Tip: Use -f (--failfast) to stop on first failure${NC}"
    echo -e "${YELLOW}Tip: Use -v (--verbose) for more detailed output${NC}"
    exit $TEST_EXIT_CODE
fi
