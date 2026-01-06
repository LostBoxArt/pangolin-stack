#!/bin/bash

# Pangolin Stack Startup Script
# This script starts all services in the Pangolin Stack

set -e

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Pangolin Stack Startup ===${NC}"
echo ""

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}Error: docker-compose.yml not found. Please run this script from the pangolin-stack directory.${NC}"
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

echo -e "${YELLOW}Pulling latest images...${NC}"
echo ""

# Pull latest images
docker compose \
    -f docker-compose.yml \
    -f docker-compose.addons.yml \
    -f docker-compose.tools.yml \
    pull

echo -e "${YELLOW}Starting Pangolin Stack services...${NC}"
echo ""

# Start all services (main stack + addons + tools)
docker compose \
    -f docker-compose.yml \
    -f docker-compose.addons.yml \
    -f docker-compose.tools.yml \
    up -d --remove-orphans

echo ""
echo -e "${GREEN}✓ All services started successfully!${NC}"
echo ""
echo "You can check the status with:"
echo "  docker compose -f docker-compose.yml -f docker-compose.addons.yml -f docker-compose.tools.yml ps"
echo ""
echo "View logs with:"
echo "  docker compose -f docker-compose.yml -f docker-compose.addons.yml -f docker-compose.tools.yml logs -f"
