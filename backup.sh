#!/bin/bash
# =============================================================================
# Pangolin Stack Backup & Restore Tool
# =============================================================================
#
# USAGE:
#   ./backup.sh backup              Create a full backup archive
#   ./backup.sh restore <file>      Restore from a backup archive
#   ./backup.sh prune [days]        Remove backups older than N days (default: 7)
#   ./backup.sh list                List all backups with sizes
#   ./backup.sh install-timer       Install systemd timer for daily backups
#   ./backup.sh help                Show this help message
#
# BACKUP INCLUDES:
#   - Docker Compose files (all configs)
#   - Environment variables (.env with all secrets)
#   - Pangolin database and configuration
#   - Traefik configuration, rules, and certificates
#   - CrowdSec credentials and database
#   - Gerbil WireGuard key
#   - Pocket ID data
#   - Homarr data (from /opt/homarr)
#   - Docker volumes (portainer_data, linkstack_data)
#   - Documentation
#
# RESTORE:
#   Extracts backup and restores all files to their original locations.
#   Docker volumes are re-imported automatically.
#
# AUTOMATION:
#   Run './backup.sh install-timer' to set up daily automated backups
#   with automatic pruning of backups older than 7 days.
#
# =============================================================================

set -e

# Configuration
BACKUP_DIR="/home/jesus/pangolin-stack/backups"
STACK_DIR="/home/jesus/pangolin-stack"
LOG_FILE="${BACKUP_DIR}/backup.log"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
RETAIN_DAYS=${RETAIN_DAYS:-7}  # Default retention: 7 days

# Colors (disabled when not a terminal)
if [ -t 1 ]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    CYAN='\033[0;36m'
    NC='\033[0m'
else
    RED=''
    GREEN=''
    YELLOW=''
    CYAN=''
    NC=''
fi

# =============================================================================
# LOGGING
# =============================================================================
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    # Always write to log file
    mkdir -p "${BACKUP_DIR}"
    echo "[${timestamp}] [${level}] ${message}" >> "${LOG_FILE}"
    
    # Also print to stdout with colors
    case "$level" in
        INFO)  echo -e "${GREEN}[${level}]${NC} ${message}" ;;
        WARN)  echo -e "${YELLOW}[${level}]${NC} ${message}" ;;
        ERROR) echo -e "${RED}[${level}]${NC} ${message}" ;;
        *)     echo "[${level}] ${message}" ;;
    esac
}

# =============================================================================
# HELP
# =============================================================================
show_help() {
    echo -e "${CYAN}========================================${NC}"
    echo -e "${CYAN}  Pangolin Stack Backup & Restore Tool${NC}"
    echo -e "${CYAN}========================================${NC}"
    echo ""
    echo -e "${GREEN}USAGE:${NC}"
    echo "  ./backup.sh backup              Create a full backup"
    echo "  ./backup.sh restore <file>      Restore from backup"
    echo "  ./backup.sh prune [days]        Remove old backups (default: 7 days)"
    echo "  ./backup.sh list                List all backups"
    echo "  ./backup.sh install-timer       Install systemd daily backup timer"
    echo "  ./backup.sh help                Show this help"
    echo ""
    echo -e "${GREEN}EXAMPLES:${NC}"
    echo "  ./backup.sh backup"
    echo "  ./backup.sh restore backups/pangolin-backup_20260106.tar.gz"
    echo "  ./backup.sh prune 14            # Keep 14 days of backups"
    echo "  RETAIN_DAYS=30 ./backup.sh backup  # Override retention"
    echo ""
    echo -e "${GREEN}WHAT GETS BACKED UP:${NC}"
    echo "  ✓ Docker Compose files"
    echo "  ✓ Environment variables (.env)"
    echo "  ✓ Pangolin config + database"
    echo "  ✓ Traefik config, rules, certificates"
    echo "  ✓ CrowdSec credentials + database"
    echo "  ✓ Gerbil WireGuard key"
    echo "  ✓ Pocket ID data"
    echo "  ✓ Homarr data (/opt/homarr)"
    echo "  ✓ Docker volumes (portainer_data, linkstack_data)"
    echo "  ✓ Documentation (README, INFRASTRUCTURE)"
    echo ""
    echo -e "${GREEN}AUTOMATION:${NC}"
    echo "  Run 'sudo ./backup.sh install-timer' to enable daily backups"
    echo "  Backups run at 3:00 AM and auto-prune after ${RETAIN_DAYS} days"
    echo ""
    echo -e "${GREEN}LOG FILE:${NC}"
    echo "  ${LOG_FILE}"
    echo ""
    echo -e "${YELLOW}NOTE:${NC} Run from the pangolin-stack directory"
}

# =============================================================================
# LIST BACKUPS
# =============================================================================
do_list() {
    echo -e "${CYAN}========================================${NC}"
    echo -e "${CYAN}  Available Backups${NC}"
    echo -e "${CYAN}========================================${NC}"
    echo ""
    
    if [ ! -d "${BACKUP_DIR}" ] || [ -z "$(ls -A ${BACKUP_DIR}/*.tar.gz 2>/dev/null)" ]; then
        echo -e "${YELLOW}No backups found in ${BACKUP_DIR}${NC}"
        return 0
    fi
    
    local total_size=0
    local count=0
    
    printf "%-45s %10s %s\n" "BACKUP FILE" "SIZE" "AGE"
    printf "%-45s %10s %s\n" "--------------------------------------------" "----------" "---"
    
    for backup in $(ls -t ${BACKUP_DIR}/pangolin-backup_*.tar.gz 2>/dev/null); do
        local filename=$(basename "$backup")
        local size=$(du -h "$backup" | cut -f1)
        local mtime=$(stat -c %Y "$backup")
        local now=$(date +%s)
        local age_days=$(( (now - mtime) / 86400 ))
        
        printf "%-45s %10s %d days\n" "$filename" "$size" "$age_days"
        
        local size_bytes=$(du -b "$backup" | cut -f1)
        total_size=$((total_size + size_bytes))
        count=$((count + 1))
    done
    
    echo ""
    echo -e "Total: ${CYAN}${count}${NC} backups, ${CYAN}$(numfmt --to=iec ${total_size})${NC}"
    echo -e "Retention policy: ${CYAN}${RETAIN_DAYS}${NC} days"
}

# =============================================================================
# PRUNE OLD BACKUPS
# =============================================================================
do_prune() {
    local days="${1:-$RETAIN_DAYS}"
    
    log INFO "Starting prune: removing backups older than ${days} days"
    
    echo -e "${CYAN}========================================${NC}"
    echo -e "${CYAN}  Pruning Old Backups${NC}"
    echo -e "${CYAN}========================================${NC}"
    echo ""
    
    if [ ! -d "${BACKUP_DIR}" ]; then
        echo -e "${YELLOW}No backup directory found${NC}"
        return 0
    fi
    
    local deleted=0
    local kept=0
    
    for backup in ${BACKUP_DIR}/pangolin-backup_*.tar.gz; do
        [ -f "$backup" ] || continue
        
        local mtime=$(stat -c %Y "$backup")
        local now=$(date +%s)
        local age_days=$(( (now - mtime) / 86400 ))
        local filename=$(basename "$backup")
        
        if [ "$age_days" -gt "$days" ]; then
            echo -e "${YELLOW}Deleting:${NC} ${filename} (${age_days} days old)"
            rm -f "$backup"
            log INFO "Deleted: ${filename} (${age_days} days old)"
            deleted=$((deleted + 1))
        else
            echo -e "${GREEN}Keeping:${NC} ${filename} (${age_days} days old)"
            kept=$((kept + 1))
        fi
    done
    
    echo ""
    echo -e "Deleted: ${RED}${deleted}${NC} | Kept: ${GREEN}${kept}${NC}"
    log INFO "Prune complete: deleted ${deleted}, kept ${kept}"
}

# =============================================================================
# BACKUP
# =============================================================================
do_backup() {
    BACKUP_NAME="pangolin-backup_${TIMESTAMP}"
    BACKUP_PATH="${BACKUP_DIR}/${BACKUP_NAME}"
    
    log INFO "Starting backup: ${BACKUP_NAME}"

    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  Pangolin Stack Full Backup${NC}"
    echo -e "${GREEN}  $(date)${NC}"
    echo -e "${GREEN}========================================${NC}"

    mkdir -p "${BACKUP_PATH}"

    # 1. Docker Compose files
    echo -e "\n${YELLOW}[1/9] Docker Compose files...${NC}"
    cp "${STACK_DIR}/docker-compose.yml" "${BACKUP_PATH}/"
    cp "${STACK_DIR}/docker-compose.addons.yml" "${BACKUP_PATH}/"
    cp "${STACK_DIR}/docker-compose.tools.yml" "${BACKUP_PATH}/" 2>/dev/null || true
    cp "${STACK_DIR}/startup.sh" "${BACKUP_PATH}/" 2>/dev/null || true
    cp "${STACK_DIR}/backup.sh" "${BACKUP_PATH}/" 2>/dev/null || true

    # 2. Environment files
    echo -e "${YELLOW}[2/9] Environment variables...${NC}"
    cp "${STACK_DIR}/.env" "${BACKUP_PATH}/"
    cp "${STACK_DIR}/.env.example" "${BACKUP_PATH}/" 2>/dev/null || true

    # 3. Pangolin (config + database)
    echo -e "${YELLOW}[3/9] Pangolin config and database...${NC}"
    mkdir -p "${BACKUP_PATH}/config/pangolin"
    cp -r "${STACK_DIR}/config/pangolin/"* "${BACKUP_PATH}/config/pangolin/" 2>/dev/null || true
    mkdir -p "${BACKUP_PATH}/config/db"
    cp "${STACK_DIR}/config/db/db.sqlite" "${BACKUP_PATH}/config/db/" 2>/dev/null || true

    # 4. Traefik (config + rules + certs)
    echo -e "${YELLOW}[4/9] Traefik configuration and certificates...${NC}"
    mkdir -p "${BACKUP_PATH}/config/traefik/rules"
    mkdir -p "${BACKUP_PATH}/config/letsencrypt"
    cp "${STACK_DIR}/config/traefik/traefik_config.yml" "${BACKUP_PATH}/config/traefik/" 2>/dev/null || true
    cp -r "${STACK_DIR}/config/traefik/rules/"* "${BACKUP_PATH}/config/traefik/rules/" 2>/dev/null || true
    cp "${STACK_DIR}/config/letsencrypt/acme.json" "${BACKUP_PATH}/config/letsencrypt/" 2>/dev/null || true

    # 5. CrowdSec (credentials + database)
    echo -e "${YELLOW}[5/9] CrowdSec credentials and database...${NC}"
    mkdir -p "${BACKUP_PATH}/config/crowdsec/db"
    cp "${STACK_DIR}/config/crowdsec/"*.yaml "${BACKUP_PATH}/config/crowdsec/" 2>/dev/null || true
    cp -r "${STACK_DIR}/config/crowdsec/db/"* "${BACKUP_PATH}/config/crowdsec/db/" 2>/dev/null || true

    # 6. Gerbil key
    echo -e "${YELLOW}[6/9] Gerbil WireGuard key...${NC}"
    mkdir -p "${BACKUP_PATH}/config"
    cp "${STACK_DIR}/config/key" "${BACKUP_PATH}/config/" 2>/dev/null || true

    # 7. Pocket ID / Data directory
    echo -e "${YELLOW}[7/9] Pocket ID and data directory...${NC}"
    mkdir -p "${BACKUP_PATH}/data"
    cp -r "${STACK_DIR}/data/"* "${BACKUP_PATH}/data/" 2>/dev/null || true

    # 8. Homarr (from /opt/homarr)
    echo -e "${YELLOW}[8/9] Homarr data...${NC}"
    if [ -d "/opt/homarr" ]; then
        mkdir -p "${BACKUP_PATH}/homarr"
        sudo cp -r /opt/homarr/appdata/* "${BACKUP_PATH}/homarr/" 2>/dev/null || true
    fi

    # 9. Docker volumes
    echo -e "${YELLOW}[9/9] Docker volumes...${NC}"
    mkdir -p "${BACKUP_PATH}/volumes"
    
    # Export portainer_data volume
    if docker volume inspect portainer_data >/dev/null 2>&1; then
        docker run --rm -v portainer_data:/data -v "${BACKUP_PATH}/volumes":/backup alpine \
            tar czf /backup/portainer_data.tar.gz -C /data . 2>/dev/null || echo "  (portainer_data: skipped)"
    fi
    
    # Export linkstack_data volume
    if docker volume inspect linkstack_linkstack_data >/dev/null 2>&1; then
        docker run --rm -v linkstack_linkstack_data:/data -v "${BACKUP_PATH}/volumes":/backup alpine \
            tar czf /backup/linkstack_data.tar.gz -C /data . 2>/dev/null || echo "  (linkstack_data: skipped)"
    fi

    # Documentation
    cp "${STACK_DIR}/README.md" "${BACKUP_PATH}/" 2>/dev/null || true
    cp "${STACK_DIR}/INFRASTRUCTURE.md" "${BACKUP_PATH}/" 2>/dev/null || true
    cp "${STACK_DIR}/.gitignore" "${BACKUP_PATH}/" 2>/dev/null || true

    # Create manifest
    cat > "${BACKUP_PATH}/MANIFEST.md" << EOF
# Backup Manifest

**Created:** $(date)
**Server:** $(hostname)
**IP:** $(curl -s ifconfig.me 2>/dev/null || echo "unknown")

## Contents
- Docker Compose files
- Environment (.env)
- Pangolin config + database
- Traefik config + rules + certificates
- CrowdSec credentials + database
- Gerbil WireGuard key
- Pocket ID data
- Homarr data
- Docker volumes (portainer, linkstack)
- Documentation

## Restore Command
\`\`\`bash
./backup.sh restore ${BACKUP_NAME}.tar.gz
\`\`\`
EOF

    # Create archive
    echo -e "\n${YELLOW}Creating compressed archive...${NC}"
    cd "${BACKUP_DIR}"
    tar -czf "${BACKUP_NAME}.tar.gz" "${BACKUP_NAME}"
    rm -rf "${BACKUP_PATH}"

    BACKUP_SIZE=$(du -h "${BACKUP_NAME}.tar.gz" | cut -f1)

    log INFO "Backup complete: ${BACKUP_NAME}.tar.gz (${BACKUP_SIZE})"

    echo -e "\n${GREEN}========================================${NC}"
    echo -e "${GREEN}  Backup Complete!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo -e "\nFile: ${CYAN}${BACKUP_DIR}/${BACKUP_NAME}.tar.gz${NC}"
    echo -e "Size: ${CYAN}${BACKUP_SIZE}${NC}"
    
    # Auto-prune if RETAIN_DAYS is set
    if [ -n "${RETAIN_DAYS}" ] && [ "${RETAIN_DAYS}" -gt 0 ]; then
        echo -e "\n${YELLOW}Auto-pruning backups older than ${RETAIN_DAYS} days...${NC}"
        do_prune "${RETAIN_DAYS}"
    fi
    
    echo -e "\n${YELLOW}Download to local machine:${NC}"
    echo "scp jesus@51.195.100.11:${BACKUP_DIR}/${BACKUP_NAME}.tar.gz ~/Downloads/"
}

# =============================================================================
# RESTORE
# =============================================================================
do_restore() {
    ARCHIVE="$1"

    if [ -z "$ARCHIVE" ]; then
        echo -e "${RED}Error: Please specify backup file${NC}"
        echo "Usage: ./backup.sh restore <backup-file.tar.gz>"
        exit 1
    fi

    if [ ! -f "$ARCHIVE" ]; then
        echo -e "${RED}Error: File not found: $ARCHIVE${NC}"
        exit 1
    fi

    log INFO "Starting restore from: ${ARCHIVE}"

    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  Pangolin Stack Restore${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo -e "\nArchive: ${CYAN}$ARCHIVE${NC}"
    echo -e "\n${RED}WARNING: This will overwrite existing configurations!${NC}"
    read -p "Continue? (y/N): " confirm
    if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
        echo "Aborted."
        log WARN "Restore aborted by user"
        exit 1
    fi

    # Stop services first
    echo -e "\n${YELLOW}Stopping Docker services...${NC}"
    cd "${STACK_DIR}"
    docker compose -f docker-compose.yml -f docker-compose.addons.yml down 2>/dev/null || true

    # Extract archive
    echo -e "${YELLOW}Extracting backup...${NC}"
    TEMP_DIR=$(mktemp -d)
    tar -xzf "$ARCHIVE" -C "$TEMP_DIR"
    BACKUP_FOLDER=$(ls "$TEMP_DIR")
    RESTORE_FROM="${TEMP_DIR}/${BACKUP_FOLDER}"

    # 1. Compose files
    echo -e "\n${YELLOW}[1/9] Restoring Docker Compose files...${NC}"
    cp "${RESTORE_FROM}/docker-compose.yml" "${STACK_DIR}/"
    cp "${RESTORE_FROM}/docker-compose.addons.yml" "${STACK_DIR}/"
    cp "${RESTORE_FROM}/docker-compose.tools.yml" "${STACK_DIR}/" 2>/dev/null || true
    cp "${RESTORE_FROM}/startup.sh" "${STACK_DIR}/" 2>/dev/null || true
    cp "${RESTORE_FROM}/backup.sh" "${STACK_DIR}/" 2>/dev/null || true

    # 2. Environment
    echo -e "${YELLOW}[2/9] Restoring environment variables...${NC}"
    cp "${RESTORE_FROM}/.env" "${STACK_DIR}/"
    chmod 600 "${STACK_DIR}/.env"

    # 3. Pangolin
    echo -e "${YELLOW}[3/9] Restoring Pangolin config and database...${NC}"
    mkdir -p "${STACK_DIR}/config/pangolin" "${STACK_DIR}/config/db"
    cp -r "${RESTORE_FROM}/config/pangolin/"* "${STACK_DIR}/config/pangolin/" 2>/dev/null || true
    cp "${RESTORE_FROM}/config/db/db.sqlite" "${STACK_DIR}/config/db/" 2>/dev/null || true

    # 4. Traefik
    echo -e "${YELLOW}[4/9] Restoring Traefik config and certificates...${NC}"
    mkdir -p "${STACK_DIR}/config/traefik/rules" "${STACK_DIR}/config/letsencrypt"
    cp "${RESTORE_FROM}/config/traefik/traefik_config.yml" "${STACK_DIR}/config/traefik/" 2>/dev/null || true
    cp -r "${RESTORE_FROM}/config/traefik/rules/"* "${STACK_DIR}/config/traefik/rules/" 2>/dev/null || true
    cp "${RESTORE_FROM}/config/letsencrypt/acme.json" "${STACK_DIR}/config/letsencrypt/" 2>/dev/null || true
    chmod 600 "${STACK_DIR}/config/letsencrypt/acme.json" 2>/dev/null || true

    # 5. CrowdSec
    echo -e "${YELLOW}[5/9] Restoring CrowdSec credentials and database...${NC}"
    mkdir -p "${STACK_DIR}/config/crowdsec/db"
    cp "${RESTORE_FROM}/config/crowdsec/"*.yaml "${STACK_DIR}/config/crowdsec/" 2>/dev/null || true
    cp -r "${RESTORE_FROM}/config/crowdsec/db/"* "${STACK_DIR}/config/crowdsec/db/" 2>/dev/null || true

    # 6. Gerbil
    echo -e "${YELLOW}[6/9] Restoring Gerbil WireGuard key...${NC}"
    cp "${RESTORE_FROM}/config/key" "${STACK_DIR}/config/" 2>/dev/null || true
    chmod 600 "${STACK_DIR}/config/key" 2>/dev/null || true

    # 7. Data directory
    echo -e "${YELLOW}[7/9] Restoring data directory...${NC}"
    mkdir -p "${STACK_DIR}/data"
    cp -r "${RESTORE_FROM}/data/"* "${STACK_DIR}/data/" 2>/dev/null || true

    # 8. Homarr
    echo -e "${YELLOW}[8/9] Restoring Homarr data...${NC}"
    if [ -d "${RESTORE_FROM}/homarr" ]; then
        sudo mkdir -p /opt/homarr/appdata
        sudo cp -r "${RESTORE_FROM}/homarr/"* /opt/homarr/appdata/ 2>/dev/null || true
    fi

    # 9. Docker volumes
    echo -e "${YELLOW}[9/9] Restoring Docker volumes...${NC}"
    if [ -f "${RESTORE_FROM}/volumes/portainer_data.tar.gz" ]; then
        docker volume create portainer_data 2>/dev/null || true
        docker run --rm -v portainer_data:/data -v "${RESTORE_FROM}/volumes":/backup alpine \
            sh -c "rm -rf /data/* && tar xzf /backup/portainer_data.tar.gz -C /data" 2>/dev/null || echo "  (portainer_data: skipped)"
    fi
    if [ -f "${RESTORE_FROM}/volumes/linkstack_data.tar.gz" ]; then
        docker volume create linkstack_linkstack_data 2>/dev/null || true
        docker run --rm -v linkstack_linkstack_data:/data -v "${RESTORE_FROM}/volumes":/backup alpine \
            sh -c "rm -rf /data/* && tar xzf /backup/linkstack_data.tar.gz -C /data" 2>/dev/null || echo "  (linkstack_data: skipped)"
    fi

    # Cleanup
    rm -rf "$TEMP_DIR"

    # Create runtime directories
    mkdir -p "${STACK_DIR}/logs"
    mkdir -p "${STACK_DIR}/config/traefik/logs"

    log INFO "Restore complete from: ${ARCHIVE}"

    echo -e "\n${GREEN}========================================${NC}"
    echo -e "${GREEN}  Restore Complete!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo -e "\n${YELLOW}Start services:${NC}"
    echo "cd ${STACK_DIR}"
    echo "docker compose -f docker-compose.yml -f docker-compose.addons.yml up -d"
}

# =============================================================================
# INSTALL SYSTEMD TIMER
# =============================================================================
do_install_timer() {
    echo -e "${CYAN}========================================${NC}"
    echo -e "${CYAN}  Installing Systemd Backup Timer${NC}"
    echo -e "${CYAN}========================================${NC}"
    echo ""
    
    if [ "$EUID" -ne 0 ]; then
        echo -e "${RED}Error: This command requires root privileges${NC}"
        echo "Run: sudo ./backup.sh install-timer"
        exit 1
    fi
    
    # Create service file
    cat > /etc/systemd/system/pangolin-backup.service << 'EOF'
[Unit]
Description=Pangolin Stack Backup
After=docker.service
Wants=docker.service

[Service]
Type=oneshot
User=jesus
Group=jesus
WorkingDirectory=/home/jesus/pangolin-stack
Environment=RETAIN_DAYS=7
ExecStart=/home/jesus/pangolin-stack/backup.sh backup
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

    # Create timer file
    cat > /etc/systemd/system/pangolin-backup.timer << 'EOF'
[Unit]
Description=Daily Pangolin Stack Backup
Requires=pangolin-backup.service

[Timer]
OnCalendar=*-*-* 03:00:00
RandomizedDelaySec=300
Persistent=true

[Install]
WantedBy=timers.target
EOF

    # Reload and enable
    systemctl daemon-reload
    systemctl enable pangolin-backup.timer
    systemctl start pangolin-backup.timer
    
    echo -e "${GREEN}✓ Systemd timer installed and enabled${NC}"
    echo ""
    echo -e "${YELLOW}Timer Status:${NC}"
    systemctl status pangolin-backup.timer --no-pager
    echo ""
    echo -e "${YELLOW}Next scheduled run:${NC}"
    systemctl list-timers pangolin-backup.timer --no-pager
    echo ""
    echo -e "${GREEN}Commands:${NC}"
    echo "  sudo systemctl status pangolin-backup.timer   # Check timer status"
    echo "  sudo systemctl list-timers                    # View all timers"
    echo "  sudo journalctl -u pangolin-backup.service    # View backup logs"
    echo "  sudo systemctl start pangolin-backup.service  # Run backup now"
}

# =============================================================================
# MAIN
# =============================================================================
case "${1:-help}" in
    backup)
        do_backup
        ;;
    restore)
        do_restore "$2"
        ;;
    prune)
        do_prune "$2"
        ;;
    list)
        do_list
        ;;
    install-timer)
        do_install_timer
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        echo "Run './backup.sh help' for usage"
        exit 1
        ;;
esac
