#!/bin/bash
# CrowdSec Blocklist Import Script
# Imports 60k+ IPs from 28 public threat feeds into CrowdSec
# Run manually or add to cron for daily updates
#
# Usage: ./scripts/blocklist-import.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="${SCRIPT_DIR}/../logs"
LOG_FILE="${LOG_DIR}/blocklist-import.log"

mkdir -p "$LOG_DIR"

echo "[$(date +'%Y-%m-%d %H:%M:%S')] Starting blocklist import..." | tee -a "$LOG_FILE"

# Run the import script
curl -sL https://raw.githubusercontent.com/wolffcatskyy/crowdsec-blocklist-import/main/import.sh | \
    MODE=docker CROWDSEC_CONTAINER=crowdsec bash 2>&1 | tee -a "$LOG_FILE"

echo "[$(date +'%Y-%m-%d %H:%M:%S')] Import complete" | tee -a "$LOG_FILE"
