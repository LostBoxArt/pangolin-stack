#!/bin/bash

# Pangolin Stack Control Script
# Manage individual stacks or all stacks at once

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

STACKS="core security dns observability management dashboard apps"

usage() {
    echo "Usage: $0 <command> [stack]"
    echo ""
    echo "Commands:"
    echo "  status [stack]    Show status of all stacks or a specific stack"
    echo "  start <stack>     Start a specific stack"
    echo "  stop <stack>      Stop a specific stack"
    echo "  restart <stack>   Restart a specific stack"
    echo "  logs <stack>      Show logs for a specific stack"
    echo "  pull [stack]      Pull latest images for all stacks or a specific stack"
    echo "  down              Stop and remove all containers"
    echo ""
    echo "Available stacks: $STACKS"
    exit 1
}

get_compose_cmd() {
    local stack=$1
    echo "docker compose -f stacks/$stack/docker-compose.yml --env-file .env"
}

cmd_status() {
    local stack=$1
    
    if [ -n "$stack" ]; then
        echo -e "${BLUE}=== $stack stack ===${NC}"
        $(get_compose_cmd "$stack") ps
    else
        for s in $STACKS; do
            if [ -f "stacks/$s/docker-compose.yml" ]; then
                echo -e "${BLUE}=== $s stack ===${NC}"
                $(get_compose_cmd "$s") ps 2>/dev/null || echo "  (not running)"
                echo ""
            fi
        done
    fi
}

cmd_start() {
    local stack=$1
    [ -z "$stack" ] && usage
    echo -e "${YELLOW}Starting $stack stack...${NC}"
    $(get_compose_cmd "$stack") up -d --remove-orphans
    echo -e "${GREEN}✓ $stack stack started${NC}"
}

cmd_stop() {
    local stack=$1
    [ -z "$stack" ] && usage
    echo -e "${YELLOW}Stopping $stack stack...${NC}"
    $(get_compose_cmd "$stack") stop
    echo -e "${GREEN}✓ $stack stack stopped${NC}"
}

cmd_restart() {
    local stack=$1
    [ -z "$stack" ] && usage
    echo -e "${YELLOW}Restarting $stack stack...${NC}"
    $(get_compose_cmd "$stack") restart
    echo -e "${GREEN}✓ $stack stack restarted${NC}"
}

cmd_logs() {
    local stack=$1
    [ -z "$stack" ] && usage
    $(get_compose_cmd "$stack") logs -f
}

cmd_pull() {
    local stack=$1
    
    if [ -n "$stack" ]; then
        echo -e "${YELLOW}Pulling images for $stack stack...${NC}"
        $(get_compose_cmd "$stack") pull
    else
        for s in $STACKS; do
            if [ -f "stacks/$s/docker-compose.yml" ]; then
                echo -e "${YELLOW}Pulling images for $s stack...${NC}"
                $(get_compose_cmd "$s") pull
            fi
        done
    fi
    echo -e "${GREEN}✓ Pull complete${NC}"
}

cmd_down() {
    echo -e "${YELLOW}Stopping all stacks...${NC}"
    for stack in $STACKS; do
        if [ -f "stacks/$stack/docker-compose.yml" ]; then
            echo "  Stopping $stack..."
            $(get_compose_cmd "$stack") down 2>/dev/null || true
        fi
    done
    echo -e "${GREEN}✓ All stacks stopped${NC}"
}

# Main
case "${1:-}" in
    status)  cmd_status "$2" ;;
    start)   cmd_start "$2" ;;
    stop)    cmd_stop "$2" ;;
    restart) cmd_restart "$2" ;;
    logs)    cmd_logs "$2" ;;
    pull)    cmd_pull "$2" ;;
    down)    cmd_down ;;
    *)       usage ;;
esac
