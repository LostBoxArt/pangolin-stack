---
title: "Fix Pocket-ID shared data path"
slug: runbook-fix-pocket-id-shared-data
type: runbook
status: active
tags: ["homelab", "runbook", "pocket-id", "cloudnode", "data"]
aliases: ["pocket-id data migration"]
entities:
  primary: runbook-fix-pocket-id-shared-data
  mentions: []
related: ["../services/pocket-id.md", "../compose-review-2026-04-17.md", "../hosts/cloudnode.md"]
sources: ["docs/wiki/services/pocket-id.md", "docs/wiki/compose-review-2026-04-17.md"]
confidence: high
audience_level: operator
last_ingested: 2026-04-17
last_lint: 2026-04-17
---
# Fix Pocket-ID shared data path

## When to use this
Use this to remediate `F-POCKETID-1 / C1`, where Pocket-ID mounts the shared repo `data/` directory instead of a dedicated path.

## Prerequisites
- Repo path: `/opt/homelab`
- Security stack downtime accepted
- Backup recommended before moving DB or signing keys

## Procedure
1. Stop the security stack:
   ```bash
   cd /opt/homelab
   ./stackctl.sh stop security
   ```
2. Create the dedicated data directory and move Pocket-ID files:
   ```bash
   mkdir -p data/pocket-id
   sudo mv data/pocket-id.db* data/keys data/uploads data/pocket-id/ 2>/dev/null || true
   ls data/
   ```
3. Update the Pocket-ID compose volume from:
   ```yaml
   - ../../data:/app/data
   ```
   to:
   ```yaml
   - ../../data/pocket-id:/app/data
   ```
4. Start the security stack again:
   ```bash
   ./stackctl.sh start security
   ```

## Verification
- Verify login still works with an existing passkey.
- Confirm Pocket-ID writes only under `data/pocket-id/`.

## Rollback
```bash
./stackctl.sh stop security
sudo mv data/pocket-id/* data/
rmdir data/pocket-id
git restore -- stacks/security/docker-compose.yml
./stackctl.sh start security
```

## Escalation
- Review [[../services/pocket-id.md]] before changing env or encryption settings.

## Last tested
Not recorded in the wiki yet.
