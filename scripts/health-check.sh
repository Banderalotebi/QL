#!/bin/bash

# ==============================================================================
# Health Check Script for Railway Deployment
# ==============================================================================
# Monitor the health of deployed services on Railway
#
# Usage:
#   ./scripts/health-check.sh [options]
#
# Options:
#   --url <url>         API base URL (default: http://localhost:8000)
#   --interval <secs>   Check interval in seconds (default: 30)
#   --verbose           Show detailed response
#   --continuous        Run continuous checks
#   --help              Show this help message
# ==============================================================================

set -e

# Configuration
API_URL="${API_URL:-http://localhost:8000}"
CHECK_INTERVAL=30
VERBOSE=false
CONTINUOUS=false
COLORS=true

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --url)
      API_URL="$2"
      shift 2
      ;;
    --interval)
      CHECK_INTERVAL="$2"
      shift 2
      ;;
    --verbose)
      VERBOSE=true
      shift
      ;;
    --continuous)
      CONTINUOUS=true
      shift
      ;;
    --no-color)
      COLORS=false
      shift
      ;;
    --help)
      head -20 "$0" | tail -19
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Color codes
if [ "$COLORS" = true ]; then
  GREEN='\033[0;32m'
  RED='\033[0;31m'
  YELLOW='\033[1;33m'
  BLUE='\033[0;34m'
  NC='\033[0m'
else
  GREEN=''
  RED=''
  YELLOW=''
  BLUE=''
  NC=''
fi

# Health check function
check_health() {
  local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
  
  echo -e "${BLUE}[$timestamp]${NC} Checking health: $API_URL/system/health"
  
  # Make the request
  response=$(curl -s -w "\n%{http_code}" "$API_URL/system/health" 2>/dev/null || echo -e "\n000")
  
  # Split response and status code
  http_code=$(echo "$response" | tail -n1)
  body=$(echo "$response" | sed '$d')
  
  # Check status code
  if [ "$http_code" = "200" ]; then
    echo -e "${GREEN}✓ API responding (HTTP 200)${NC}"
  else
    echo -e "${RED}✗ API error (HTTP $http_code)${NC}"
    return 1
  fi
  
  # Parse JSON response if jq is available
  if command -v jq &> /dev/null && [ -n "$body" ]; then
    status=$(echo "$body" | jq -r '.status' 2>/dev/null || echo "unknown")
    echo -e "${GREEN}✓ System status: $status${NC}"
    
    if [ "$VERBOSE" = true ]; then
      echo ""
      echo "Response:"
      echo "$body" | jq '.' 2>/dev/null || echo "$body"
      echo ""
    fi
    
    # Check individual components
    if echo "$body" | jq -e '.components' > /dev/null 2>&1; then
      echo "Components:"
      echo "$body" | jq -r '.components | to_entries[] | "  \(.key): \(.value)"' 2>/dev/null
    fi
    
    # Show metrics
    if echo "$body" | jq -e '.metrics' > /dev/null 2>&1; then
      echo "Metrics:"
      echo "$body" | jq -r '.metrics | to_entries[] | "  \(.key): \(.value)"' 2>/dev/null
    fi
  else
    [ -n "$body" ] && echo "Response: $body"
  fi
  
  echo ""
  return 0
}

# Check other endpoints
check_endpoints() {
  echo -e "${BLUE}Additional Endpoint Checks:${NC}"
  
  endpoints=(
    "/system/info"
    "/research/status"
    "/patterns/statistics"
  )
  
  for endpoint in "${endpoints[@]}"; do
    http_code=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL$endpoint" 2>/dev/null || echo "000")
    
    if [ "$http_code" = "200" ]; then
      echo -e "${GREEN}✓${NC} $endpoint (HTTP 200)"
    else
      echo -e "${RED}✗${NC} $endpoint (HTTP $http_code)"
    fi
  done
  
  echo ""
}

# Main execution
main() {
  echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
  echo -e "${BLUE}Health Check: Muqattaat Lab${NC}"
  echo -e "${BLUE}API URL: $API_URL${NC}"
  echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
  echo ""
  
  if [ "$CONTINUOUS" = true ]; then
    echo "Continuous monitoring (interval: ${CHECK_INTERVAL}s, press Ctrl+C to stop)"
    echo ""
    
    while true; do
      check_health || echo -e "${YELLOW}⚠ Health check failed${NC}"
      check_endpoints
      
      if [ "$CONTINUOUS" = true ]; then
        echo -e "${YELLOW}Waiting ${CHECK_INTERVAL}s for next check...${NC}"
        sleep "$CHECK_INTERVAL"
      fi
    done
  else
    check_health && check_endpoints
  fi
}

# Run main
main
