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
    pull

echo -e "${YELLOW}Starting Pangolin Stack services...${NC}"
echo ""

# Start all services (main stack + addons)
docker compose \
    -f docker-compose.yml \
    -f docker-compose.addons.yml \
    up -d --remove-orphans

echo ""
echo -e "${YELLOW}Waiting for services to become healthy...${NC}"

compose_files=(-f docker-compose.yml -f docker-compose.addons.yml)
containers=$(docker compose "${compose_files[@]}" ps -q)

if [ -n "$containers" ]; then
    timeout_seconds=300
    interval_seconds=5
    start_time=$(date +%s)

    while true; do
        unhealthy=0
        for container in $containers; do
            status=$(docker inspect -f '{{.State.Status}}' "$container")
            health=$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{end}}' "$container")

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
            break
        fi

        now=$(date +%s)
        if [ $((now - start_time)) -ge "$timeout_seconds" ]; then
            echo -e "${RED}Timed out waiting for healthy services.${NC}"
            echo "Check status with:"
            echo "  docker compose -f docker-compose.yml -f docker-compose.addons.yml ps"
            echo "Inspect logs with:"
            echo "  docker compose -f docker-compose.yml -f docker-compose.addons.yml logs -f"
            exit 1
        fi

        sleep "$interval_seconds"
    done
fi

echo ""
echo -e "${GREEN}✓ All services are running and healthy!${NC}"
echo ""
echo "You can check the status with:"
echo "  docker compose -f docker-compose.yml -f docker-compose.addons.yml ps"
echo ""
echo "View logs with:"
echo "  docker compose -f docker-compose.yml -f docker-compose.addons.yml logs -f"
