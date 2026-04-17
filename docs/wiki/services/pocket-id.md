---
title: "pocket-id"
slug: vps-pocket-id
type: service
status: active
tags: ["homelab", "vps", "service", "pocket-id"]
aliases: ["pocket-id"]
entities:
  primary: vps-pocket-id
  mentions: []
related: ["./README.md", "./compose-review-2026-04-17.md", "./system-overview.md"]
sources: ["stacks/security/docker-compose.yml"]
confidence: high
audience_level: operator
last_ingested: 2026-04-17
last_lint: 2026-04-17
---
# pocket-id

OIDC / passkey-first identity provider. Used as the SSO gateway behind
Traefik for admin UIs (`auth.dennisb.xyz`).

- **Image**: `ghcr.io/pocket-id/pocket-id:v2` (pinned to v2 major)
- **Compose file**: `stacks/security/docker-compose.yml`
- **Internal port**: `1411` (fronted by Traefik)
- **Data**: `../../data:/app/data` ⚠️ **shares whole repo `data/` dir**

## Upstream Sources

- Reference compose: <https://raw.githubusercontent.com/pocket-id/pocket-id/main/docker-compose.yml>
- Install docs: <https://pocket-id.org/docs/setup/installation>
- Env var reference: <https://pocket-id.org/docs/configuration/environment-variables>

## Upstream Reference Compose

```yaml
services:
  pocket-id:
    image: ghcr.io/pocket-id/pocket-id:v2
    restart: unless-stopped
    env_file: .env
    ports:
      - 1411:1411
    volumes:
      - "./data:/app/data"
    healthcheck:
      test: ["CMD", "/app/pocket-id", "healthcheck"]
      interval: 1m30s
      timeout: 5s
      retries: 2
      start_period: 10s
```

Crucial detail: upstream's `./data` is a **Pocket-ID-dedicated directory**
in the Pocket-ID install folder. Ours points at the shared repo-wide `data/`
folder.

## Our Compose (relevant slice)

```73:102:stacks/security/docker-compose.yml
  pocket-id:
    image: ghcr.io/pocket-id/pocket-id:v2
    container_name: pocket-id
    networks:
      - pangolin
    restart: unless-stopped
    environment:
      - APP_URL=${POCKET_ID_APP_URL}
      - ENCRYPTION_KEY=${POCKET_ID_ENCRYPTION_KEY}
      - TRUST_PROXY=${POCKET_ID_TRUST_PROXY}
      - MAXMIND_LICENSE_KEY=${MAXMIND_LICENSE_KEY}
      - MAXMIND_ACCOUNT_ID=${MAXMIND_ACCOUNT_ID}
    volumes:
      - ../../data:/app/data
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.pocketid-redirect.rule=Host(`auth.dennisb.xyz`)"
      - "traefik.http.routers.pocketid-redirect.entrypoints=web"
      - "traefik.http.routers.pocketid-redirect.middlewares=redirect-to-https@file"
      - "traefik.http.routers.pocketid.rule=Host(`auth.dennisb.xyz`)"
      - "traefik.http.routers.pocketid.entrypoints=websecure"
      - "traefik.http.routers.pocketid.tls.certresolver=letsencrypt"
      - "traefik.http.routers.pocketid.middlewares=security-headers@file"
      - "traefik.http.services.pocketid.loadbalancer.server.port=1411"
    healthcheck:
      test: [ "CMD", "/app/pocket-id", "healthcheck" ]
      interval: 1m30s
      timeout: 5s
      retries: 2
      start_period: 10s
```

## Deviations

| Aspect | Upstream | Ours | Intent |
|---|---|---|---|
| Volume | dedicated `./data` | `../../data` (shared with `dockhand/`, `positions/`) | ⚠️ unintentional |
| Env delivery | `env_file: .env` | inlined vars | equivalent (we use repo-wide `.env`) |
| Ports | `1411:1411` published | not published | ✓ Traefik fronts it |
| Healthcheck | same | same | ✓ |

## Findings

### F-POCKETID-1 — shared data directory (`critical` / C1)
Pocket-ID's `/app/data` is mounted from **`../../data`**, i.e. the repo-wide
`data/` folder. That folder also contains:

- `data/dockhand/` — Dockhand's SQLite database
- `data/positions/` — traefik-log-dashboard-agent positions cache

Pocket-ID runs as **root** inside the container and writes at least these
files at this path:

- `pocket-id.db` (SQLite DB, auth + keys)
- `keys/` (Ed25519 signing keypair, **irrecoverable if lost**)
- `uploads/` (profile pictures, SSO icons)

**Impact matrix:**

- Backups / restores become ambiguous: `tar czf data.tgz data/` bundles three
  services' state; restoring on a different host cross-contaminates them.
- Permission changes made by Pocket-ID (chown to root:root) can trip Dockhand
  (which runs with `user: "0:0"` + `group_add: 986`) or the traefik-agent
  (which runs as uid 1000 inside its image).
- If anyone ever `rm -rf data/dockhand/` to reset Dockhand, they are one
  typo away from deleting Pocket-ID's signing keys.

### F-POCKETID-2 — `POCKET_ID_TRUST_PROXY` needs validating
Pocket-ID v2 treats `TRUST_PROXY` strictly — if set to `true` without
`APP_URL` matching the observed host, WebAuthn challenges fail. Not an
action item here, just a sanity reminder.

## Remediation

### Fix F-POCKETID-1 — data migration (the C1 critical fix)

One-time migration (stack **down**):

```bash
./stackctl.sh stop security

# Identify Pocket-ID files currently at ./data root.
# Canonical list (check against your install):
#   pocket-id.db
#   pocket-id.db-shm
#   pocket-id.db-wal
#   keys/
#   uploads/

mkdir -p data/pocket-id
sudo mv data/pocket-id.db* data/keys data/uploads data/pocket-id/ 2>/dev/null || true

# Verify nothing left at data/ root that belongs to pocket-id:
ls data/
```

Compose edit:

```yaml
    volumes:
      - ../../data/pocket-id:/app/data
```

Restart: `./stackctl.sh start security`. Log in with an existing passkey
to verify the DB+keys moved correctly. If login fails, restore from backup
and investigate before editing the compose again — passkey enrollment is
not recoverable from backups easily.

### Prefer `env_file` (optional)

To match upstream 1:1:

```yaml
    env_file: .env
```

Only if repo `.env` already contains the `POCKET_ID_*` + `MAXMIND_*` keys
with the exact names Pocket-ID expects (not `POCKET_ID_APP_URL` but just
`APP_URL`). Mixing the two approaches requires renaming variables — skip
this unless you're doing a full env cleanup.

## Operational Notes

- Secure-context requirement: Pocket-ID's passkey flows need HTTPS. The
  Traefik setup provides this via `letsencrypt` resolver — do not turn off
  the `websecure` router.
- `ENCRYPTION_KEY` rotates the DB on change. Treat it like a root password.
- `APP_URL` must exactly match the user-facing URL including scheme —
  `https://auth.dennisb.xyz` for us.
