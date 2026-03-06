#!/bin/bash
# 🏛️ START HIVE - Continuous Background Operation
# Usage: ./start_hive.sh [batch-size] [interval]

set -e

cd /workspaces/QL

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
BATCH_SIZE=${1:-3}
INTERVAL=${2:-300}
LOG_FILE="/workspaces/QL/logs/hive_$(date +%Y%m%d_%H%M%S).log"

# Create logs directory
mkdir -p /workspaces/QL/logs

echo -e "${BLUE}🏛️  STARTING CONTINUOUS HIVE OPERATION${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Batch Size: ${BATCH_SIZE} surahs${NC}"
echo -e "${GREEN}✓ Interval: ${INTERVAL} seconds${NC}"
echo -e "${GREEN}✓ Log File: ${LOG_FILE}${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""

# Run in the background with nohup
nohup python hive_continuous.py --batch-size $BATCH_SIZE --interval $INTERVAL > "$LOG_FILE" 2>&1 &

HIVE_PID=$!

echo -e "${GREEN}✅ Hive started in background${NC}"
echo -e "${GREEN}   Process ID: ${HIVE_PID}${NC}"
echo -e "${YELLOW}   To stop: kill ${HIVE_PID}${NC}"
echo -e "${YELLOW}   To watch logs: tail -f ${LOG_FILE}${NC}"

# Save PID for later reference
echo $HIVE_PID > /workspaces/QL/.hive_pid

echo ""
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${GREEN}Hive is now running continuously!${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"
