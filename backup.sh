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
BACKUP_DIR="/opt/homelab/backups"
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
    
    python3 - "${BACKUP_DIR}" "$days" <<'PYPRUNE'
import gzip
import pathlib
import re
import sqlite3
import sys
import tarfile
import tempfile
import time

root = pathlib.Path(sys.argv[1])
if not re.fullmatch(r"[0-9]+", sys.argv[2]):
    raise ValueError("retention must be a nonnegative number of days")
days = int(sys.argv[2])
if days == 0:
    print("Pruning disabled; all archives retained")
    sys.exit(0)
archives = sorted(root.glob("pangolin-backup_????????_??????.tar.gz"), key=lambda path: (path.stat().st_mtime, path.name), reverse=True)
if not archives:
    print("No completed archives; nothing to prune")
    sys.exit(0)
newest = archives[0]
age = time.time() - newest.stat().st_mtime
if not 0 <= age <= 26 * 3600:
    raise RuntimeError("no fresh completed archive; all recovery copies retained")
# Refuse deletion unless both protected generations validate.
def validate_archive(archive):
    with gzip.open(archive, "rb") as stream:
        while stream.read(1024 * 1024):
            pass
    with tarfile.open(archive) as saved, tempfile.TemporaryDirectory(prefix="prune-validation-") as temporary:
        prefix = archive.name.removesuffix(".tar.gz")
        saved.getmember(prefix + "/MANIFEST.md")
        member = saved.extractfile(prefix + "/config/db/db.sqlite")
        database = pathlib.Path(temporary) / "db.sqlite"
        with database.open("wb") as output:
            while chunk := member.read(1024 * 1024):
                output.write(chunk)
        with database.open("rb") as header:
            if header.read(16) != b"SQLite format 3\x00":
                raise ValueError("invalid archived SQLite header; all archives retained")
        with sqlite3.connect(database) as connection:
            if connection.execute("PRAGMA quick_check").fetchall() != [("ok",)]:
                raise ValueError("newest database validation failed; all archives retained")
for protected in archives[:2]:
    validate_archive(protected)

deleted = 0
for archive in archives[2:]:
    if time.time() - archive.stat().st_mtime > days * 86400:
        archive.unlink()
        deleted += 1
print(f"Deleted: {deleted} | Kept: {len(archives) - deleted}; newest two generations protected")
PYPRUNE
}

# =============================================================================
# BACKUP
# =============================================================================
# Take an independently consistent SQLite snapshot without stopping the application.
snapshot_sqlite_db() {
    python3 - "$1" "$2" <<'PYSQLITE'
import os
import pathlib
import sqlite3
import sys
import time

source = pathlib.Path(sys.argv[1])
target = pathlib.Path(sys.argv[2])
partial = target.with_name(target.name + ".partial")
try:
    with source.open("rb") as stream:
        if stream.read(16) != b"SQLite format 3\x00":
            raise ValueError("invalid SQLite header")
    deadline = time.monotonic() + 120
    def check_progress(status, remaining, total):
        if time.monotonic() > deadline:
            raise TimeoutError("database snapshot timed out")
    with sqlite3.connect(source.resolve().as_uri() + "?mode=ro", uri=True) as live:
        with sqlite3.connect(partial) as snapshot:
            live.backup(snapshot, pages=256, progress=check_progress)
            if snapshot.execute("PRAGMA quick_check").fetchall() != [("ok",)]:
                raise ValueError("database snapshot validation failed")
    os.chmod(partial, 0o600)
    os.replace(partial, target)
    # Never replay copied recovery files against this independent snapshot.
    for suffix in ("-wal", "-shm", "-journal"):
        target.with_name(target.name + suffix).unlink(missing_ok=True)
except Exception as error:
    partial.unlink(missing_ok=True)
    print(f"SQLite snapshot failed: {source.name} ({type(error).__name__})", file=sys.stderr)
    sys.exit(1)
PYSQLITE
}

copy_private_tree() {
    local source="$1"
    local target="$2"
    shift 2
    mkdir -p "${target}"
    if ! (set -o pipefail; docker run --rm --pull=never --network none --read-only --cap-drop ALL --cap-add DAC_OVERRIDE --security-opt no-new-privileges --mount "type=bind,source=${source},target=/source,readonly" --entrypoint /bin/tar alpine@sha256:be2656061b536c1883c4034790e21d0a09c5aaaf51968b89368a3c0371ea2c9a "$@" -C /source -cf - . | tar -xf - -C "${target}/"); then
        log ERROR "Private data export failed: ${source}"
        return 1
    fi
}

capture_runtime() {
    mkdir -p "$1"
    python3 - "${STACK_DIR}" "$1/services.json" <<'PYRUNTIME'
import json
import hashlib
import os
import pathlib
import subprocess
import sys
import tarfile

stack = pathlib.Path(sys.argv[1])
services = {}
for name in ["pangolin", "gerbil", "traefik", "pocket-id", "dockhand", "homarr", "crowdsec", "crowdsec-web-ui", "landing", "qbit-proxy", "dashdot", "traefik-agent", "traefik-dashboard"]:
    data = json.loads(subprocess.check_output(["docker", "inspect", name]))[0]
    image = json.loads(subprocess.check_output(["docker", "image", "inspect", data["Image"]]))[0]
    services[name] = {
        "image_id": data["Image"],
        "repo_digests": image.get("RepoDigests", []),
        "config": {key: data["Config"].get(key) for key in ["Image", "User", "Env", "Entrypoint", "Cmd", "WorkingDir", "Healthcheck"]},
        "mounts": [{key: mount.get(key) for key in ["Type", "Source", "Destination", "RW"]} for mount in data["Mounts"]],
    }
databases = {}
for service, source, archived in [
    ("pangolin", stack / "config/db/db.sqlite", "config/db/db.sqlite"),
    ("crowdsec", stack / "config/crowdsec/db/crowdsec.db", "config/crowdsec/db/crowdsec.db"),
    ("crowdsec-web-ui", stack / "config/crowdsec-web-ui/crowdsec.db", "config/crowdsec-web-ui/crowdsec.db"),
    ("pocket-id", stack / "data/pocket-id/pocket-id.db", "data/pocket-id/pocket-id.db"),
    ("dockhand", stack / "data/dockhand/db/dockhand.db", "data/dockhand/db/dockhand.db"),
    ("homarr", pathlib.Path("/opt/homarr/appdata/db/db.sqlite"), "homarr/db/db.sqlite"),
]:
    info = source.stat()
    databases[service] = {"archive_path": archived, "uid": info.st_uid, "gid": info.st_gid, "mode": info.st_mode & 0o777}
target = pathlib.Path(sys.argv[2])
image_path = target.parent / "qbit-proxy-image.tar"
subprocess.run(["docker", "image", "save", "--output", str(image_path), services["qbit-proxy"]["image_id"]], check=True, stdout=subprocess.DEVNULL)
os.chmod(image_path, 0o600)
def sha256(stream):
    digest = hashlib.sha256()
    for chunk in iter(lambda: stream.read(1024 * 1024), b""):
        digest.update(chunk)
    return digest.hexdigest()
with tarfile.open(image_path) as saved:
    manifest = json.load(saved.extractfile("manifest.json"))
    if len(manifest) != 1:
        raise ValueError("unexpected local image archive")
    for name in [manifest[0]["Config"], *manifest[0]["Layers"]]:
        if not saved.getmember(name).isfile():
            raise ValueError("missing local image layer")
    expected = services["qbit-proxy"]["image_id"]
    config_digest = "sha256:" + sha256(saved.extractfile(manifest[0]["Config"]))
    # Classic Docker identifies the config; containerd image stores identify an OCI manifest.
    if config_digest != expected:
        manifest_blob = "blobs/sha256/" + expected.removeprefix("sha256:")
        if "sha256:" + sha256(saved.extractfile(manifest_blob)) != expected:
            raise ValueError("local image identity mismatch")
with image_path.open("rb") as stream:
    local_image = {"service": "qbit-proxy", "archive_path": "runtime/qbit-proxy-image.tar", "sha256": sha256(stream)}
target.write_text(json.dumps({"version": 1, "services": services, "databases": databases, "local_images": [local_image]}, indent=2))
os.chmod(target, 0o600)
PYRUNTIME
}

export_host_recovery() {
    local target="$1"
    local mounts=(
        --mount "type=bind,source=/root/.config/olm-client/config.json,target=/export/root/.config/olm-client/config.json,readonly"
        --mount "type=bind,source=/etc/systemd/system/olm.service,target=/export/etc/systemd/system/olm.service,readonly"
        --mount "type=bind,source=/etc/systemd/system/arr-mcp-tunnel.service,target=/export/etc/systemd/system/arr-mcp-tunnel.service,readonly"
        --mount "type=bind,source=/etc/systemd/system/olm-watchdog.service,target=/export/etc/systemd/system/olm-watchdog.service,readonly"
        --mount "type=bind,source=/etc/systemd/system/olm-watchdog.timer,target=/export/etc/systemd/system/olm-watchdog.timer,readonly"
        --mount "type=bind,source=/usr/local/sbin/olm-watchdog.sh,target=/export/usr/local/sbin/olm-watchdog.sh,readonly"
        --mount "type=bind,source=/usr/local/sbin/homarr-appdata-tar,target=/export/usr/local/sbin/homarr-appdata-tar,readonly"
        --mount "type=bind,source=/etc/crowdsec/bouncers/crowdsec-firewall-bouncer.yaml,target=/export/etc/crowdsec/bouncers/crowdsec-firewall-bouncer.yaml,readonly"
        --mount "type=bind,source=/etc/systemd/system/crowdsec-firewall-bouncer.service,target=/export/etc/systemd/system/crowdsec-firewall-bouncer.service,readonly"
    )
    mkdir -p "${target}"
    if ! (set -o pipefail; docker run --rm --pull=never --network none --read-only --cap-drop ALL "${mounts[@]}" --entrypoint /bin/tar alpine@sha256:be2656061b536c1883c4034790e21d0a09c5aaaf51968b89368a3c0371ea2c9a -C /export -cf - . | tar -xf - -C "${target}/"); then
        log ERROR "Host recovery export failed"
        return 1
    fi
}

do_backup() {
    umask 077
    if [ -f "${LOG_FILE}" ]; then
        chmod 600 "${LOG_FILE}"
    fi
    BACKUP_NAME="pangolin-backup_${TIMESTAMP}"
    BACKUP_PATH="${BACKUP_DIR}/${BACKUP_NAME}"
    
    log INFO "Starting backup: ${BACKUP_NAME}"

    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  Pangolin Stack Full Backup${NC}"
    echo -e "${GREEN}  $(date)${NC}"
    echo -e "${GREEN}========================================${NC}"

    mkdir -p "${BACKUP_PATH}"

    # 1. Stack compose files
    echo -e "\n${YELLOW}[1/9] Stack compose files...${NC}"
    cp -r "${STACK_DIR}/stacks" "${BACKUP_PATH}/"
    cp -a "${STACK_DIR}/scripts" "${BACKUP_PATH}/"
    cp -a "${STACK_DIR}/docs" "${STACK_DIR}/tests" "${BACKUP_PATH}/"
    cp -a "${STACK_DIR}/sites" "${STACK_DIR}/qbit-proxy" "${BACKUP_PATH}/"
    cp "${STACK_DIR}/startup.sh" "${BACKUP_PATH}/" 2>/dev/null || true
    cp "${STACK_DIR}/stackctl.sh" "${BACKUP_PATH}/" 2>/dev/null || true
    cp "${STACK_DIR}/backup.sh" "${BACKUP_PATH}/" 2>/dev/null || true

    # 2. Environment files
    echo -e "${YELLOW}[2/9] Environment variables...${NC}"
    cp "${STACK_DIR}/.env" "${BACKUP_PATH}/"
    cp "${STACK_DIR}/.env.example" "${BACKUP_PATH}/" 2>/dev/null || true

    # 3. Pangolin (config + database)
    echo -e "${YELLOW}[3/9] Pangolin config and database...${NC}"
    mkdir -p "${BACKUP_PATH}/config/pangolin"
    cp -r "${STACK_DIR}/config/pangolin/." "${BACKUP_PATH}/config/pangolin/"
    cp "${STACK_DIR}/config/config.yml" "${BACKUP_PATH}/config/"
    mkdir -p "${BACKUP_PATH}/config/db"
    snapshot_sqlite_db "${STACK_DIR}/config/db/db.sqlite" "${BACKUP_PATH}/config/db/db.sqlite"

    # 4. Traefik (config + rules + certs)
    echo -e "${YELLOW}[4/9] Traefik configuration and certificates...${NC}"
    mkdir -p "${BACKUP_PATH}/config/traefik/rules"
    mkdir -p "${BACKUP_PATH}/config/letsencrypt"
    cp "${STACK_DIR}/config/traefik/traefik_config.yml" "${BACKUP_PATH}/config/traefik/" 2>/dev/null || true
    cp -r "${STACK_DIR}/config/traefik/rules/"* "${BACKUP_PATH}/config/traefik/rules/" 2>/dev/null || true
    cp "${STACK_DIR}/config/letsencrypt/acme.json" "${BACKUP_PATH}/config/letsencrypt/" 2>/dev/null || true

    # 5. CrowdSec (credentials + database)
    echo -e "${YELLOW}[5/9] CrowdSec credentials and database...${NC}"
    mkdir -p "${BACKUP_PATH}/config/crowdsec"
    if ! (set -o pipefail; docker exec crowdsec tar -C /etc/crowdsec -cf - . | tar -xf - -C "${BACKUP_PATH}/config/crowdsec/"); then
        echo -e "${RED}ERROR: CrowdSec configuration backup failed${NC}" >&2
        exit 1
    fi

    snapshot_sqlite_db "${STACK_DIR}/config/crowdsec/db/crowdsec.db" "${BACKUP_PATH}/config/crowdsec/db/crowdsec.db"
    copy_private_tree "${STACK_DIR}/config/crowdsec-web-ui" "${BACKUP_PATH}/config/crowdsec-web-ui" --exclude=./crowdsec.db --exclude=./crowdsec.db-wal --exclude=./crowdsec.db-shm
    snapshot_sqlite_db "${STACK_DIR}/config/crowdsec-web-ui/crowdsec.db" "${BACKUP_PATH}/config/crowdsec-web-ui/crowdsec.db"

    # 6. Gerbil key
    echo -e "${YELLOW}[6/9] Gerbil WireGuard key...${NC}"
    mkdir -p "${BACKUP_PATH}/config"
    cp "${STACK_DIR}/config/key" "${BACKUP_PATH}/config/" 2>/dev/null || true

    # 7. Pocket ID / Data directory
    echo -e "${YELLOW}[7/9] Pocket ID and data directory...${NC}"
    mkdir -p "${BACKUP_PATH}/data"
    copy_private_tree "${STACK_DIR}/data" "${BACKUP_PATH}/data"
    for database in pocket-id/pocket-id.db dockhand/db/dockhand.db; do
        snapshot_sqlite_db "${STACK_DIR}/data/${database}" "${BACKUP_PATH}/data/${database}"
    done
    if [ -f "${STACK_DIR}/data/pocketid/pocket-id.db" ]; then
        snapshot_sqlite_db "${STACK_DIR}/data/pocketid/pocket-id.db" "${BACKUP_PATH}/data/pocketid/pocket-id.db"
    fi

    # 8. Homarr (from /opt/homarr)
    echo -e "${YELLOW}[8/9] Homarr data...${NC}"
    if [ -d "/opt/homarr" ]; then
        mkdir -p "${BACKUP_PATH}/homarr"
        if ! (set -o pipefail; sudo -n /usr/local/sbin/homarr-appdata-tar | tar -xf - -C "${BACKUP_PATH}/homarr/"); then
            echo -e "${RED}ERROR: Homarr data backup failed${NC}" >&2
            exit 1
        fi
        snapshot_sqlite_db "/opt/homarr/appdata/db/db.sqlite" "${BACKUP_PATH}/homarr/db/db.sqlite"
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
    cp "${STACK_DIR}/AGENTS.md" "${BACKUP_PATH}/"
    cp "${STACK_DIR}/.gitignore" "${BACKUP_PATH}/" 2>/dev/null || true

    # Preserve private runtime settings and the exact allowlisted host recovery files.
    capture_runtime "${BACKUP_PATH}/runtime"
    export_host_recovery "${BACKUP_PATH}/host-configs/cloudnode"
    mkdir -p "${BACKUP_PATH}/host-configs/cloudnode/systemd"
    cp -a "${STACK_DIR}/host-configs/cloudnode/systemd/user" "${BACKUP_PATH}/host-configs/cloudnode/systemd/"
    mkdir -p "${BACKUP_PATH}/host-configs/cloudnode/user-backup"
    cp "${HOME}/.config/homelab-backups/offsite.env" "${HOME}/.config/homelab-backups/restic-version.json" "${BACKUP_PATH}/host-configs/cloudnode/user-backup/"
    mkdir -p "${BACKUP_PATH}/traefik-plugins"
    if ! (set -o pipefail; docker exec traefik tar -C /plugins-storage -cf - . | tar -xf - -C "${BACKUP_PATH}/traefik-plugins/"); then
        log ERROR "Traefik plugin cache backup failed"
        exit 1
    fi

    # Create manifest
    cat > "${BACKUP_PATH}/MANIFEST.md" << EOF
# Backup Manifest

**Created:** $(date)
**Server:** $(hostname)
**IP:** $(curl -s ifconfig.me 2>/dev/null || echo "unknown")

## Contents
- Docker Compose files, landing sites, and qbit-proxy build context
- Environment (.env)
- Pangolin config + database
- Traefik config + rules + certificates
- CrowdSec credentials + database
- Gerbil WireGuard key
- Pocket ID data
- Homarr data
- Docker volumes (portainer, linkstack)
- Documentation
- Private runtime environment, image digests, and database ownership metadata
- Allowlisted CloudNode service units, watchdog/helper scripts, and Olm credentials
- Exact Traefik plugin cache for isolated/offline recovery

## Database Consistency
Pangolin, Pocket ID, Dockhand, Homarr, CrowdSec, and CrowdSec Web UI databases
use validated online SQLite snapshots; their staged WAL/SHM sidecars are removed.
Each database is independently consistent; this is not a global transaction
across applications. An isolated application restore test is still required.

## Restore Command
\`\`\`bash
sudo ./backup.sh restore ${BACKUP_NAME}.tar.gz
\`\`\`
EOF

    # Create archive
    echo -e "\n${YELLOW}Creating compressed archive...${NC}"
    cd "${BACKUP_DIR}"
    tar -czf "${BACKUP_NAME}.tar.gz.partial" "${BACKUP_NAME}"
    tar -tzf "${BACKUP_NAME}.tar.gz.partial" >/dev/null
    chmod 600 "${BACKUP_NAME}.tar.gz.partial"
    mv "${BACKUP_NAME}.tar.gz.partial" "${BACKUP_NAME}.tar.gz"
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
    echo "scp admin@203.0.113.1:${BACKUP_DIR}/${BACKUP_NAME}.tar.gz ~/Downloads/"
}

# =============================================================================
# RESTORE
# =============================================================================
prepare_restore_databases() {
    python3 - "$1" <<'PYMETADATA'
import json
import pathlib
import subprocess
import sys

root = pathlib.Path(sys.argv[1])
runtime = root / "runtime/services.json"
captured = json.loads(runtime.read_text()).get("databases", {}) if runtime.exists() else {}
if runtime.exists():
    for service in json.loads(runtime.read_text())["services"].values():
        result = subprocess.run(["docker", "image", "inspect", service["image_id"]], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if result.returncode:
            raise RuntimeError("recorded image is unavailable; load its verified digest before restoring")
else:
    print("Legacy archive: no image metadata; restore files only and review image versions before starting services.", file=sys.stderr)
databases = []
for service, relative in [
    ("pangolin", "config/db/db.sqlite"),
    ("crowdsec", "config/crowdsec/db/crowdsec.db"),
    ("crowdsec-web-ui", "config/crowdsec-web-ui/crowdsec.db"),
    ("pocket-id", "data/pocket-id/pocket-id.db"),
    ("dockhand", "data/dockhand/db/dockhand.db"),
    ("homarr", "homarr/db/db.sqlite"),
    ("pocket-id-legacy", "data/pocketid/pocket-id.db"),
]:
    source = root / relative
    if not source.exists():
        if service == "pangolin" or service in captured:
            raise RuntimeError("required restored database is missing")
        continue
    info = source.stat()
    item = captured.get(service, {"uid": info.st_uid, "gid": info.st_gid, "mode": info.st_mode & 0o777})
    databases.append({"archive_path": relative, **{key: item[key] for key in ["uid", "gid", "mode"]}})
(root / ".restore-databases.json").write_text(json.dumps(databases))
PYMETADATA
    # Normalize legacy WAL archives into self-contained snapshots in the private extraction.
    while IFS= read -r relative; do
        snapshot_sqlite_db "$1/${relative}" "$1/${relative}"
    done < <(python3 -c 'import json,sys; print("\n".join(x["archive_path"] for x in json.load(open(sys.argv[1]))))' "$1/.restore-databases.json")
}

restore_database_files() {
    python3 - "$1" "$2" "$3" "$4" <<'PYRESTORE'
import json
import os
import pathlib
import sys

source, stack, homarr = map(pathlib.Path, sys.argv[1:4])
operation = sys.argv[4]
for item in json.loads((source / ".restore-databases.json").read_text()):
    relative = item["archive_path"]
    target = homarr / relative.removeprefix("homarr/") if relative.startswith("homarr/") else stack / relative
    if operation == "clear-sidecars":
        for suffix in ["-wal", "-shm", "-journal"]:
            target.with_name(target.name + suffix).unlink(missing_ok=True)
        continue
    directory = target.parent.parent if relative == "data/dockhand/db/dockhand.db" else target.parent
    if relative == "homarr/db/db.sqlite":
        directory = homarr
    # SQLite also needs write access to its directory for WAL/SHM files.
    for parent, directories, files in os.walk(directory, followlinks=False):
        for path in [pathlib.Path(parent), *(pathlib.Path(parent) / name for name in directories + files)]:
            os.chown(path, item["uid"], item["gid"], follow_symlinks=False)
    os.chmod(directory, directory.stat().st_mode & 0o777 | 0o700)
    os.chmod(target, item["mode"])
PYRESTORE
}

do_restore() {
    if [ "$EUID" -ne 0 ]; then
        echo "Restore requires root to preserve application ownership; run sudo ./backup.sh restore <archive>" >&2
        return 1
    fi
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

    # Validate the private extraction before stopping or overwriting services.
    echo -e "${YELLOW}Extracting backup...${NC}"
    TEMP_DIR=$(mktemp -d)
    tar -xzf "$ARCHIVE" -C "$TEMP_DIR"
    BACKUP_FOLDER=$(ls "$TEMP_DIR")
    RESTORE_FROM="${TEMP_DIR}/${BACKUP_FOLDER}"
    prepare_restore_databases "${RESTORE_FROM}"

    echo -e "\n${YELLOW}Stopping Docker services...${NC}"
    cd "${STACK_DIR}"
    if ! ./stackctl.sh down; then
        log ERROR "Stack shutdown failed; no live files restored"
        exit 1
    fi
    python3 - <<'PYSTOPPED'
import subprocess
running = set(subprocess.check_output(["docker", "ps", "--format", "{{.Names}}"], text=True).splitlines())
stack = {"pangolin", "gerbil", "traefik", "crowdsec", "crowdsec-web-ui", "pocket-id", "dockhand", "homarr", "landing", "termix", "qbit-proxy", "dashdot", "traefik-agent", "traefik-dashboard", "adguard-home"}
if running & stack:
    raise RuntimeError("stack containers are still running; no live files restored")
PYSTOPPED

    # 1. Stack compose files
    echo -e "\n${YELLOW}[1/9] Restoring stack compose files...${NC}"
    cp -r "${RESTORE_FROM}/stacks" "${STACK_DIR}/"
    for component in sites qbit-proxy scripts docs tests; do
        if [ -d "${RESTORE_FROM}/${component}" ]; then
            cp -a "${RESTORE_FROM}/${component}" "${STACK_DIR}/"
        fi
    done
    cp "${RESTORE_FROM}/startup.sh" "${STACK_DIR}/" 2>/dev/null || true
    cp "${RESTORE_FROM}/stackctl.sh" "${STACK_DIR}/" 2>/dev/null || true
    # Keep this validated recovery tool when restoring older archives.
    chmod +x "${STACK_DIR}/startup.sh" "${STACK_DIR}/stackctl.sh" "${STACK_DIR}/backup.sh" 2>/dev/null || true

    if [ -f "${RESTORE_FROM}/AGENTS.md" ]; then
        cp "${RESTORE_FROM}/AGENTS.md" "${STACK_DIR}/"
    fi

    # 2. Environment
    echo -e "${YELLOW}[2/9] Restoring environment variables...${NC}"
    cp "${RESTORE_FROM}/.env" "${STACK_DIR}/"
    chmod 600 "${STACK_DIR}/.env"

    # 3. Pangolin
    echo -e "${YELLOW}[3/9] Restoring Pangolin config and database...${NC}"
    mkdir -p "${STACK_DIR}/config/pangolin" "${STACK_DIR}/config/db"
    cp -r "${RESTORE_FROM}/config/pangolin/"* "${STACK_DIR}/config/pangolin/" 2>/dev/null || true
    cp -a "${RESTORE_FROM}/config/db/db.sqlite" "${STACK_DIR}/config/db/"
    if [ -f "${RESTORE_FROM}/config/config.yml" ]; then
        cp "${RESTORE_FROM}/config/config.yml" "${STACK_DIR}/config/"
    fi

    # 4. Traefik
    echo -e "${YELLOW}[4/9] Restoring Traefik config and certificates...${NC}"
    mkdir -p "${STACK_DIR}/config/traefik/rules" "${STACK_DIR}/config/letsencrypt"
    cp "${RESTORE_FROM}/config/traefik/traefik_config.yml" "${STACK_DIR}/config/traefik/" 2>/dev/null || true
    cp -r "${RESTORE_FROM}/config/traefik/rules/"* "${STACK_DIR}/config/traefik/rules/" 2>/dev/null || true
    cp "${RESTORE_FROM}/config/letsencrypt/acme.json" "${STACK_DIR}/config/letsencrypt/" 2>/dev/null || true
    chmod 600 "${STACK_DIR}/config/letsencrypt/acme.json" 2>/dev/null || true

    # 5. CrowdSec
    echo -e "${YELLOW}[5/9] Restoring CrowdSec credentials and database...${NC}"
    mkdir -p "${STACK_DIR}/config/crowdsec"
    cp -a "${RESTORE_FROM}/config/crowdsec/." "${STACK_DIR}/config/crowdsec/"
    if [ -d "${RESTORE_FROM}/config/crowdsec-web-ui" ]; then
        mkdir -p "${STACK_DIR}/config/crowdsec-web-ui"
        cp -a "${RESTORE_FROM}/config/crowdsec-web-ui/." "${STACK_DIR}/config/crowdsec-web-ui/"
    fi

    # 6. Gerbil
    echo -e "${YELLOW}[6/9] Restoring Gerbil WireGuard key...${NC}"
    cp "${RESTORE_FROM}/config/key" "${STACK_DIR}/config/" 2>/dev/null || true
    chmod 600 "${STACK_DIR}/config/key" 2>/dev/null || true

    # 7. Data directory
    echo -e "${YELLOW}[7/9] Restoring data directory...${NC}"
    mkdir -p "${STACK_DIR}/data"
    cp -a "${RESTORE_FROM}/data/." "${STACK_DIR}/data/"

    # 8. Homarr
    echo -e "${YELLOW}[8/9] Restoring Homarr data...${NC}"
    if [ -d "${RESTORE_FROM}/homarr" ]; then
        sudo mkdir -p /opt/homarr/appdata
        sudo cp -a "${RESTORE_FROM}/homarr/." /opt/homarr/appdata/
    fi
    restore_database_files "${RESTORE_FROM}" "${STACK_DIR}" /opt/homarr/appdata clear-sidecars
    restore_database_files "${RESTORE_FROM}" "${STACK_DIR}" /opt/homarr/appdata ownership

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

    # Keep sensitive recovery metadata outside the repository; never install host units automatically.
    RECOVERY_PATH="${BACKUP_DIR}/restored-recovery_${TIMESTAMP}"
    mkdir -p "${RECOVERY_PATH}"
    chmod 700 "${RECOVERY_PATH}"
    for component in runtime host-configs traefik-plugins; do
        if [ -d "${RESTORE_FROM}/${component}" ]; then
            cp -a "${RESTORE_FROM}/${component}" "${RECOVERY_PATH}/"
        fi
    done
    echo "Private host recovery files and runtime metadata: ${RECOVERY_PATH}"

    # Cleanup
    rm -rf "$TEMP_DIR"

    # Create runtime directories
    mkdir -p "${STACK_DIR}/logs"
    mkdir -p "${STACK_DIR}/config/traefik/logs"

    log INFO "Restore complete from: ${ARCHIVE}"

    echo -e "\n${GREEN}========================================${NC}"
    echo -e "${GREEN}  Restore Complete!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo -e "\n${YELLOW}Services remain stopped.${NC}"
    echo "Review recorded images and docs/wiki/runbooks/backup-recovery.md before starting services."
    echo "Use exact image overrides with --pull never --no-build; do not run startup.sh for recovery."
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
User=admin
Group=admin
WorkingDirectory=/opt/homelab
Environment=RETAIN_DAYS=7
UMask=0077
ExecStart=/opt/homelab/backup.sh backup
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
