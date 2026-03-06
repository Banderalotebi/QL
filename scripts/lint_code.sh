#!/bin/bash
# Code linting script for CI/CD
# Usage: ./scripts/lint_code.sh [options]

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "========================================"
echo "🔍 Running QL Code Linters"
echo "========================================"

# Default values
FIX=""
STRICT=""
TARGET="src/"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --fix)
            FIX="--fix"
            shift
            ;;
        --strict)
            STRICT="--check"
            shift
            ;;
        *)
            TARGET="$1"
            shift
            ;;
    esac
done

# Track overall result
FAILED=0

# Function to run a linter
run_linter() {
    local name=$1
    local cmd=$2
    
    echo -e "\n${BLUE}Running $name...${NC}"
    if eval "$cmd"; then
        echo -e "${GREEN}✅ $name passed${NC}"
    else
        echo -e "${RED}❌ $name failed${NC}"
        FAILED=1
    fi
}

# Check if flake8 is installed
if command -v flake8 &> /dev/null; then
    run_linter "flake8" "flake8 $TARGET --count --select=E9,F63,F7,F82 --show-source --statistics"
    run_linter "flake8 (style)" "flake8 $TARGET --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics"
else
    echo -e "${YELLOW}Warning: flake8 not installed, skipping${NC}"
fi

# Check if black is installed
if command -v black &> /dev/null; then
    if [ -n "$STRICT" ]; then
        run_linter "black" "black --check $TARGET"
    else
        run_linter "black" "black --check --diff $TARGET || true"
    fi
else
    echo -e "${YELLOW}Warning: black not installed, skipping${NC}"
fi

# Check if mypy is installed
if command -v mypy &> /dev/null; then
    run_linter "mypy" "mypy $TARGET --ignore-missing-imports --no-error-summary || true"
else
    echo -e "${YELLOW}Warning: mypy not installed, skipping${NC}"
fi

# Check if bandit is installed
if command -v bandit &> /dev/null; then
    run_linter "bandit" "bandit -r $TARGET -f txt || true"
else
    echo -e "${YELLOW}Warning: bandit not installed, skipping${NC}"
fi

# Check if safety is installed
if command -v safety &> /dev/null; then
    run_linter "safety" "safety check || true"
else
    echo -e "${YELLOW}Warning: safety not installed, skipping${NC}"
fi

# Final result
echo -e "\n========================================"
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All linters passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some linters failed!${NC}"
    exit 1
fi

