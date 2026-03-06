#!/bin/bash
# 🛑 STOP HIVE - Gracefully shutdown the continuous hive
# Usage: ./stop_hive.sh

set -e

PID_FILE="/workspaces/QL/.hive_pid"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

if [ ! -f "$PID_FILE" ]; then
    echo -e "${RED}❌ Hive not running (PID file not found)${NC}"
    exit 1
fi

HIVE_PID=$(cat "$PID_FILE")

echo -e "${YELLOW}🛑 Stopping hive process: ${HIVE_PID}${NC}"

# Gracefully terminate
if kill -0 "$HIVE_PID" 2>/dev/null; then
    kill -TERM "$HIVE_PID"
    
    # Wait for graceful shutdown (up to 30 seconds)
    for i in {1..30}; do
        if ! kill -0 "$HIVE_PID" 2>/dev/null; then
            echo -e "${GREEN}✅ Hive stopped gracefully${NC}"
            rm -f "$PID_FILE"
            exit 0
        fi
        sleep 1
    done
    
    # Force kill if still running
    echo -e "${YELLOW}⚠️  Force killing process...${NC}"
    kill -9 "$HIVE_PID"
    rm -f "$PID_FILE"
    echo -e "${GREEN}✅ Hive force stopped${NC}"
else
    echo -e "${YELLOW}⚠️  Process not found${NC}"
    rm -f "$PID_FILE"
fi
