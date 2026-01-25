#!/bin/bash

# Pangolin Stack Startup Script
# Starts all stacks in dependency order

set -e

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "${GREEN}=== Pangolin Stack Startup ===${NC}"
echo ""

# Check if stacks directory exists
if [ ! -d "stacks" ]; then
    echo -e "${RED}Error: stacks/ directory not found. Please run this script from the pangolin-stack directory.${NC}"
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

# Stack startup order (dependencies first)
STACKS_PHASE1="core"
STACKS_PHASE2="security dns management"
STACKS_PHASE3="observability dashboard apps"

start_stack() {
    local stack=$1
    local compose_file="stacks/$stack/docker-compose.yml"
    
    if [ ! -f "$compose_file" ]; then
        echo -e "${YELLOW}Warning: $compose_file not found, skipping...${NC}"
        return 0
    fi
    
    echo -e "${YELLOW}Starting $stack stack...${NC}"
    docker compose -f "$compose_file" --env-file .env pull
    docker compose -f "$compose_file" --env-file .env up -d --remove-orphans
}

wait_for_healthy() {
    local stack=$1
    local compose_file="stacks/$stack/docker-compose.yml"
    local timeout_seconds=120
    local interval_seconds=5
    local start_time=$(date +%s)
    
    containers=$(docker compose -f "$compose_file" --env-file .env ps -q 2>/dev/null || true)
    
    if [ -z "$containers" ]; then
        return 0
    fi
    
    while true; do
        unhealthy=0
        for container in $containers; do
            status=$(docker inspect -f '{{.State.Status}}' "$container" 2>/dev/null || echo "unknown")
            health=$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{end}}' "$container" 2>/dev/null || true)
            
            if [ "$status" != "running" ]; then
                unhealthy=1
                break
            fi
            
            if [ -n "$health" ] && [ "$health" != "healthy" ]; then
                unhealthy=1
                break
            fi
        done
        
        if [ "$unhealthy" -eq 0 ]; then
            echo -e "${GREEN}  ✓ $stack stack is healthy${NC}"
            return 0
        fi
        
        now=$(date +%s)
        if [ $((now - start_time)) -ge "$timeout_seconds" ]; then
            echo -e "${RED}  ✗ Timed out waiting for $stack stack${NC}"
            return 1
        fi
        
        sleep "$interval_seconds"
    done
}

echo -e "${YELLOW}Phase 1: Starting core infrastructure...${NC}"
for stack in $STACKS_PHASE1; do
    start_stack "$stack"
    wait_for_healthy "$stack"
done

echo ""
echo -e "${YELLOW}Phase 2: Starting security and management...${NC}"
for stack in $STACKS_PHASE2; do
    start_stack "$stack"
done
for stack in $STACKS_PHASE2; do
    wait_for_healthy "$stack"
done

echo ""
echo -e "${YELLOW}Phase 3: Starting remaining stacks...${NC}"
for stack in $STACKS_PHASE3; do
    start_stack "$stack"
done
for stack in $STACKS_PHASE3; do
    wait_for_healthy "$stack"
done

echo ""
echo -e "${GREEN}✓ All stacks are running!${NC}"
echo ""
echo "Stack status commands:"
echo "  ./stackctl.sh status          # View all stack status"
echo "  ./stackctl.sh logs <stack>    # View stack logs"
echo "  ./stackctl.sh restart <stack> # Restart a stack"
