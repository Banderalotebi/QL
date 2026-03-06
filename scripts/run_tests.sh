#!/bin/bash
# Test execution script for CI/CD
# Usage: ./scripts/run_tests.sh [options]

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================"
echo "🧪 Running QL Test Suite"
echo "========================================"

# Default values
VERBOSE=""
COVERAGE=""
MARKERS=""
PARALLEL=""
TEST_PATH="tests/"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -v|--verbose)
            VERBOSE="-v"
            shift
            ;;
        --coverage)
            COVERAGE="--cov=src --cov-report=term-missing --cov-report=xml"
            shift
            ;;
        --fast)
            MARKERS="-m 'not slow'"
            shift
            ;;
        --slow)
            MARKERS="-m 'slow'"
            shift
            ;;
        --parallel)
            PARALLEL="-n auto"
            shift
            ;;
        --security)
            MARKERS="-m 'security'"
            shift
            ;;
        *)
            TEST_PATH="$1"
            shift
            ;;
    esac
done

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}Error: pytest is not installed${NC}"
    echo "Install with: pip install pytest pytest-cov pytest-xdist"
    exit 1
fi

# Run tests
echo -e "\n${GREEN}Running tests...${NC}"
pytest $TEST_PATH $VERBOSE $COVERAGE $MARKERS $PARALLEL --tb=short

# Check result
if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✅ All tests passed!${NC}"
    exit 0
else
    echo -e "\n${RED}❌ Some tests failed!${NC}"
    exit 1
fi

