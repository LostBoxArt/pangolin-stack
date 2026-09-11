#!/bin/sh
# Automatically submit HDR10-compatible Dolby Vision library files to FileFlows.
set -eu

BASE='/volume1/docker/config/fileflows/automation'
HDR10_FLOW_UID='9d97d797-0967-4923-af52-20bc461cd412'
HLG_FLOW_UID='3dacb6dd-25ef-460f-bb73-888ec0a91ab1'
FILEFLOWS_URL='http://127.0.0.1:19200/api/library-file/manually-add'
STABLE_SECONDS=600
MAX_SUBMISSIONS=1
BACKUP_RETENTION_SECONDS=604800
TV_BACKUP_ROOT='/volume1/media/tv/.fileflows-original-backups'
MOVIES_BACKUP_ROOT='/volume1/media/movies/.fileflows-original-backups'
DRY_RUN="${DRY_RUN:-0}"
ALLOW_DAYTIME="${ALLOW_DAYTIME:-1}"
STATE="$BASE/submitted.tsv"
CACHE="$BASE/probe-cache.tsv"
LOG="$BASE/watcher.log"
LOCK="$BASE/.lock"

mkdir -p "$BASE"
touch "$STATE" "$CACHE" "$LOG"
if ! mkdir "$LOCK" 2>/dev/null; then
  exit 0
fi
trap 'rmdir "$LOCK" 2>/dev/null || true' EXIT HUP INT TERM

log() {
  printf '%s %s\n' "$(date '+%Y-%m-%dT%H:%M:%S%z')" "$*" >> "$LOG"
}

# Processing is allowed at any time by default. Set ALLOW_DAYTIME=0 to
# retain the overnight-only 01:00 through 07:59 gate.
if [ "$ALLOW_DAYTIME" != '1' ]; then
  hour=$(docker exec fileflows sh -c 'date +%H' 2>/dev/null || true)
  hour=${hour#0}
  if [ -z "$hour" ]; then
    exit 0
  fi
  if [ "$hour" -lt 1 ] || [ "$hour" -ge 8 ]; then
    exit 0
  fi
fi

if [ "$DRY_RUN" != '1' ]; then
  if command -v curl >/dev/null 2>&1; then
    status=$(curl -fsS 'http://127.0.0.1:19200/api/status' 2>/dev/null || true)
  else
    status=$(docker exec fileflows wget -qO- --timeout=5 'http://127.0.0.1:5000/api/status' 2>/dev/null || true)
  fi
  case "$status" in
    *'"queue":0,"processing":0,'*) ;;
    *)
      log "fileflows-busy status=$status"
      exit 0
      ;;
  esac
fi

stat_size() {
  stat -c '%s' "$1" 2>/dev/null || stat -f '%z' "$1"
}
stat_mtime() {
  stat -c '%Y' "$1" 2>/dev/null || stat -f '%m' "$1"
}
stat_links() {
  stat -c '%h' "$1" 2>/dev/null || stat -f '%l' "$1"
}

submit() {
  flow_uid="$1"
  cpath="$2"
  escaped=$(printf '%s' "$cpath" | sed 's/\\/\\\\/g; s/"/\\"/g')
  body=$(printf '{"FlowUid":"%s","Files":["%s"],"CustomVariables":{}}' "$flow_uid" "$escaped")
  if command -v curl >/dev/null 2>&1; then
    curl -fsS -X POST "$FILEFLOWS_URL" -H 'Content-Type: application/json' --data "$body" >/dev/null
  else
    wget -qO- --header='Content-Type: application/json' --post-data="$body" "$FILEFLOWS_URL" >/dev/null
  fi
}

scan_root() {
  host_root="$1"
  container_root="$2"
  find "$host_root" -path "$host_root/.fileflows-original-backups" -prune -o -type f \( -iname '*.mkv' -o -iname '*.mp4' -o -iname '*.m4v' \) -print 2>/dev/null > "$BASE/scan.list"
  while IFS= read -r file; do
    if [ "$DRY_RUN" != '1' ] && [ "$SUBMITTED_THIS_RUN" -ge "$MAX_SUBMISSIONS" ]; then
      break
    fi
    [ -r "$file" ] || continue
    size=$(stat_size "$file") || continue
    mtime=$(stat_mtime "$file") || continue
    now=$(date '+%s')
    age=$((now - mtime))
    [ "$age" -ge "$STABLE_SECONDS" ] || continue
    links=$(stat_links "$file") || continue
    case "$file" in
      "$host_root"/*) relative=${file#"$host_root"/} ;;
      *) continue ;;
    esac
    cpath="$container_root/$relative"
    key="$size|$mtime|$cpath"

    # Never process the same file state twice.
    grep -F -q "$key|" "$STATE" 2>/dev/null && continue
    if grep -F -q "$key|NO_DV" "$CACHE" 2>/dev/null || grep -F -q "$key|SKIP_" "$CACHE" 2>/dev/null; then
      continue
    fi

    probe=$(docker exec fileflows ffprobe -v error -select_streams v:0 \
      -show_entries 'stream=profile:stream_side_data=side_data_type,dv_profile,dv_level,dv_bl_signal_compatibility_id' \
      -of default=nw=1 "$cpath" 2>/dev/null) || {
        log "probe-error file=$cpath"
        continue
      }
    profile=$(printf '%s\n' "$probe" | sed -n 's/^dv_profile=//p' | head -n 1)
    compat=$(printf '%s\n' "$probe" | sed -n 's/^dv_bl_signal_compatibility_id=//p' | head -n 1)

    if [ "$profile" = '8' ] && { [ "$compat" = '1' ] || [ "$compat" = '4' ]; }; then
      if [ "$compat" = '1' ]; then
        flow_uid="$HDR10_FLOW_UID"
      else
        flow_uid="$HLG_FLOW_UID"
      fi
      # Keep a same-filesystem rollback hardlink only for eligible files.
      case "$file" in
        /volume1/media/tv/*) backup="$TV_BACKUP_ROOT/$relative" ;;
        /volume1/media/movies/*) backup="$MOVIES_BACKUP_ROOT/$relative" ;;
        *) continue ;;
      esac
      if [ "$DRY_RUN" = '1' ]; then
        log "dry-run eligible profile=$profile compat=$compat file=$cpath"
      else
        if [ ! -e "$backup" ]; then
          mkdir -p "$(dirname "$backup")"
          ln "$file" "$backup" || {
            log "backup-failed file=$cpath"
            continue
          }
          log "backup-created links=$links file=$cpath backup=$backup"
        fi
        retention_meta="$backup.retention"
        if [ ! -e "$retention_meta" ]; then
          if ! printf '%s\n' "$(date '+%s')" > "$retention_meta"; then
            log "retention-metadata-failed file=$cpath backup=$backup"
            continue
          fi
          chmod 600 "$retention_meta" 2>/dev/null || true
        fi
        printf '%s|ELIGIBLE\n' "$key" >> "$CACHE"
        if submit "$flow_uid" "$cpath"; then
          printf '%s|SUBMITTED\n' "$key" >> "$STATE"
          log "submitted flow=$flow_uid profile=$profile compat=$compat file=$cpath"
          SUBMITTED_THIS_RUN=$((SUBMITTED_THIS_RUN + 1))
        else
          log "submit-failed profile=$profile compat=$compat file=$cpath"
        fi
      fi
    elif [ -n "$profile" ] || [ -n "$compat" ]; then
      printf '%s|SKIP_DV_PROFILE_%s_COMPAT_%s\n' "$key" "${profile:-unknown}" "${compat:-unknown}" >> "$CACHE"
      log "skip dv-profile=$profile compat=$compat file=$cpath"
    else
      printf '%s|NO_DV\n' "$key" >> "$CACHE"
    fi
  done < "$BASE/scan.list"
  rm -f "$BASE/scan.list"
}

cleanup_one_backup_root() {
  backup_root="$1"
  current_root="$2"
  container_root="$3"
  [ -d "$backup_root" ] || return 0
  now=$(date '+%s')
  find "$backup_root" -type f ! -name '*.retention' -print 2>/dev/null | while IFS= read -r backup; do
    retention_meta="$backup.retention"
    [ -r "$retention_meta" ] || continue
    created=$(cat "$retention_meta" 2>/dev/null || true)
    case "$created" in
      ''|*[!0-9]*) continue ;;
    esac
    [ "$created" -le "$now" ] || continue
    age=$((now - created))
    [ "$age" -ge "$BACKUP_RETENTION_SECONDS" ] || continue
    case "$backup" in
      "$backup_root"/*) relative=${backup#"$backup_root"/} ;;
      *) continue ;;
    esac
    current="$current_root/$relative"
    cpath="$container_root/$relative"
    [ -f "$current" ] || continue
    backup_inode=$(stat -c '%i' "$backup" 2>/dev/null || stat -f '%i' "$backup")
    current_inode=$(stat -c '%i' "$current" 2>/dev/null || stat -f '%i' "$current")
    [ "$backup_inode" != "$current_inode" ] || continue
    probe=$(docker exec fileflows ffprobe -v error -select_streams v:0 \
      -show_entries 'stream=codec_name,profile:stream_side_data=side_data_type,dv_profile,dv_bl_signal_compatibility_id' \
      -of default=nw=1 "$cpath" 2>/dev/null) || continue
    case "$probe" in
      *dv_profile=*|*DOVI*|*dovi*) continue ;;
    esac
    rm -f "$backup" "$retention_meta"
    log "rollback-expired age=$age file=$cpath backup=$backup"
  done
}

cleanup_backups() {
  cleanup_one_backup_root "$TV_BACKUP_ROOT" '/volume1/media/tv' '/media/tv'
  cleanup_one_backup_root "$MOVIES_BACKUP_ROOT" '/volume1/media/movies' '/media/movies'
}

SUBMITTED_THIS_RUN=0
if [ "$DRY_RUN" != '1' ]; then
  cleanup_backups
fi
scan_root '/volume1/media/movies' '/media/movies'
scan_root '/volume1/media/tv' '/media/tv'
