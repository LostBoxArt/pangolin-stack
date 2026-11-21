These files are source-controlled copies of the current HomeNode host-side compose files.

Live host paths:

- `/volume1/docker/config/<service>/docker-compose.yml`
- `/volume1/docker/traefik/docker-compose.yml`

Repo paths:

- `host-configs/homenode/<service>/docker-compose.yml`
- `host-configs/homenode/traefik/docker-compose.yml`

Keep these copies in sync whenever HomeNode host-side compose files change.

## Verified snapshots, 2026-10-27

The added `arr-mcp`, `recyclarr`, `seerr`, `profilarr`, `dashdot`, `newt`, and `hawser` copies
come from the running NAS deployment. Domains and LAN addresses use repository
examples. Secret-bearing config/data files are excluded. These are recovery
references; synchronize from the live host before editing or deploying.

`arr-mcp` remains bound to NAS loopback `6060`; CloudNode reaches it through
the supervised `arr-mcp-tunnel.service`, also bound to loopback `16060`.
The running snapshots pin arr-mcp `1.44.5`, Recyclarr `8.8.0`, and Seerr `v3.5.1`.
No service was upgraded to produce these copies.

Newt's authoritative source is Dockhand's Git stack, not its historical NAS
container label. Its selected deployment copy matched the running image and
environment before sanitization. Newt and Hawser credentials are required
private environment variables in these references; no populated secrets are
included. Hawser's Standard-mode binding is restricted to the NAS LAN address,
which reduces listening interfaces but does not isolate it from LAN clients.

The Dashdot copy includes the repaired read-only host-root mount and retains its
existing privileged mode, matching the upstream setup. ADM's missing
`/etc/os-release` still limits OS identification; see its service page and the
dated review for that separate constraint.

FileFlows was retired on 2026-10-27. Do not restore it from historical archives.
