---
title: "badger"
slug: cloudnode-badger
type: service
status: active
tags: ["homelab", "cloudnode", "service", "badger"]
aliases: ["badger"]
entities:
  primary: cloudnode-badger
  mentions: []
related: ["./README.md", "./compose-review-2026-04-17.md", "./system-overview.md", "./crowdsec.md"]
sources: ["config/traefik/traefik_config.yml"]
confidence: high
audience_level: operator
last_ingested: 2026-04-21
last_lint: 2026-04-21
---

# badger

Traefik CrowdSec bouncer plugin. Not a container — it runs as a plugin inside
Traefik and communicates with the CrowdSec LAPI to block malicious IPs at the
edge.

- **Type**: Traefik plugin (not a standalone container)
- **Config**: `config/traefik/traefik_config.yml`
- **Version**: `v1.4.0`
- **LAPI key**: Issued by `cscli bouncers add traefik-badger`

## Upstream Sources

- Releases: <https://github.com/fosrl/badger/releases>

## Our Configuration

Badger is registered in `config/traefik/traefik_config.yml` under the
`experimental.plugins` and `http.middlewares` sections.

```yaml
experimental:
  plugins:
    badger:
      moduleName: github.com/fosrl/badger
      version: v1.4.0

http:
  middlewares:
    crowdsec:
      plugin:
        badger:
          crowdsecLapiKey: <CROWDSEC_AGENT_KEY>
          crowdsecLapiHost: crowdsec:8080
```

## Deviations

| Aspect | Upstream | Ours | Intent |
|---|---|---|---|
| Version | latest | pinned `v1.4.0` | aligned with Pangolin 1.17.x — ✓ |

## Findings

None currently documented.

## Operational Notes

- If CrowdSec container exits, the Badger plugin fails closed (blocks all
traffic) because the LAPI becomes unreachable. This was the root cause of the
2026-04-21 global 403 incident. See `docs/wiki/runbooks/403-all-sites.md`.
- The plugin is loaded by Traefik at startup. Changing the config requires a
Traefik restart or dynamic config reload.
