#!/bin/bash
# 📊 MONITOR HIVE - Show live logs and status
# Usage: ./monitor_hive.sh

PID_FILE="/workspaces/QL/.hive_pid"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

if [ ! -f "$PID_FILE" ]; then
    echo -e "${RED}❌ Hive not running${NC}"
    exit 1
fi

HIVE_PID=$(cat "$PID_FILE")

echo -e "${BLUE}📊 HIVE MONITORING DASHBOARD${NC}"
echo -e "${BLUE}════════════════════════════${NC}"
echo ""

# Show process info
echo -e "${GREEN}Process Information:${NC}"
ps aux | grep $HIVE_PID | grep -v grep || echo -e "${RED}Process not found${NC}"
echo ""

# Find latest log file
LATEST_LOG=$(ls -t /workspaces/QL/logs/hive_*.log 2>/dev/null | head -1)

if [ -z "$LATEST_LOG" ]; then
    echo -e "${RED}No log files found${NC}"
    exit 1
fi

echo -e "${GREEN}Latest Log: ${LATEST_LOG}${NC}"
echo -e "${BLUE}════════════════════════════${NC}"
echo ""

# Stream the log file
tail -f "$LATEST_LOG"
