---
title: "pocket-id"
slug: cloudnode-pocket-id
type: service
status: active
tags: ["homelab", "cloudnode", "service", "pocket-id"]
aliases: ["pocket-id"]
entities:
  primary: cloudnode-pocket-id
  mentions: []
related: ["./README.md", "./compose-review-2026-04-17.md", "./system-overview.md"]
sources: ["stacks/security/docker-compose.yml"]
confidence: high
audience_level: operator
last_ingested: 2026-09-28
last_lint: 2026-09-28
---
# pocket-id

OIDC / passkey-first identity provider. Used as the SSO gateway behind
Traefik for admin UIs (`auth.example.com`).

- **Image**: `ghcr.io/pocket-id/pocket-id:v2.16.0` (pinned to exact minor)
- **Compose file**: `stacks/security/docker-compose.yml`
- **Internal port**: `1411` (fronted by Traefik)
- **Data**: `/home/jesus/pangolin-stack/data/pocket-id:/app/data` (dedicated Pocket-ID state)

## Upstream Sources

- Reference compose: <https://raw.githubusercontent.com/pocket-id/pocket-id/main/docker-compose.yml>
- Install docs: <https://pocket-id.org/docs/setup/installation>
- Env var reference: <https://pocket-id.org/docs/configuration/environment-variables>

## Upstream Reference Compose

```yaml
services:
  pocket-id:
    image: ghcr.io/pocket-id/pocket-id:v2.16.0
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
in the Pocket-ID install folder. Ours now uses the dedicated
`/home/jesus/pangolin-stack/data/pocket-id/` path.

## Our Compose (relevant slice)

```73:94:stacks/security/docker-compose.yml
  pocket-id:
    image: ghcr.io/pocket-id/pocket-id:v2.16.0
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
      - /home/jesus/pangolin-stack/data/pocket-id:/app/data
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
| Volume | dedicated `./data` | `/home/jesus/pangolin-stack/data/pocket-id` | ✓ isolated 2026-09-28 |
| Env delivery | `env_file: .env` | inlined vars | equivalent (we use repo-wide `.env`) |
| Ports | `1411:1411` published | not published | ✓ Traefik fronts it |
| Healthcheck | same | same | ✓ |

## Findings

### F-POCKETID-1 — shared data directory (`critical` / C1, resolved 2026-09-28)
Resolved 2026-09-28: Pocket-ID was migrated off the shared repo-wide `data/`
directory into the dedicated `data/pocket-id/` path. Its `/app/data` mount is now
`/home/jesus/pangolin-stack/data/pocket-id`, while Dockhand and the log-agent
retain their separate state paths.

Before the migration, Pocket-ID's `/app/data` was mounted from **`../../data`**,
i.e. the repo-wide `data/` folder. That folder also contained:

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

### F-POCKETID-3 — image was pinned to floating `v2` major tag (`medium` / resolved 2026-09-28)
The compose file used `ghcr.io/pocket-id/pocket-id:v2`, a moving major tag. Pocket ID
runs database migrations automatically on startup, so a silent major-tag move can
migrate the schema forward before you have a validated rollback. Now pinned to the
exact `v2.16.0`. Upgrades are `pull` + `up -d` per
<https://pocket-id.org/docs/setup/upgrading> — no manual steps between v2.15.0 and
v2.16.0.

### F-POCKETID-4 — live SQLite DB is WAL-mode; naive file copies are not backups (`medium`)
The live database is `/app/data/pocket-id.db` in WAL mode with an active `-wal`
file, so a plain `cp` is not a valid backup. Use the SQLite online-backup API:

```bash
sqlite3 /home/jesus/pangolin-stack/data/pocket-id/pocket-id.db ".backup /tmp/pocket-id-backup.db"
```

Verified 2026-09-28: `.backup` produced an `integrity_check=ok` snapshot with
matching row counts (2 users, 3 OIDC clients). The pre-existing
`pocket-id.db.bak-20251222_115806` in the same directory is 4 KB — empty — because
it was taken the wrong way. Do not rely on it.

## Remediation

### Fix F-POCKETID-1 — data migration (completed 2026-09-28)

The one-time migration is complete. A verified rollback backup was created before
moving the database, signing keys, and uploads; the live database passed
`integrity_check=ok` with 2 users and 3 OIDC clients after restart.

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
      - /home/jesus/pangolin-stack/data/pocket-id:/app/data
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
  `https://auth.example.com` for us.
