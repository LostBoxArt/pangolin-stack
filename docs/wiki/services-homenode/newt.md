---
title: "newt"
slug: homenode-newt
type: service
status: active
tags: ["homelab", "homenode", "service", "newt"]
aliases: ["newt"]
entities:
  primary: homenode-newt
  mentions: []
related: ["./README.md", "./homenode-review-2026-04-17.md", "./system-overview.md"]
sources: ["host-configs/homenode/newt/docker-compose.yml"]
confidence: high
audience_level: operator
last_ingested: 2026-10-27
last_lint: 2026-10-27
---

# newt

Newt connects the NAS site to Pangolin. The running image was verified as
`fosrl/newt:1.19.0` on 2026-10-27; no upgrade was performed for this review.
It joins `default` and the external `traefik_traefik` network.

## Source and credentials

Dockhand manages this NAS deployment as Git stack 11, repository 1, with
`newt/docker-compose.yml`. Its current deployment copy is
`/app/data/stacks/Nasus/newt/docker-compose.yml` inside Dockhand. The running
container's older `/data/stacks/newt/` label is not sufficient to identify the
current Git source. Compare the selected source and running configuration
before editing.

The sanitized reference is `host-configs/homenode/newt/docker-compose.yml`.
It requires private `NEWT_ID` and `NEWT_SECRET` variables. Never put their
populated values in this wiki, Git, command arguments, or shared output.
Protect deployment environment files with mode `0600` and include them only
in restricted, encrypted recovery copies.

The older wiki embedded the live secret. Those examples were removed on
2026-10-27; credential rotation and deployment-source synchronization were completed
in the same maintenance. Removing text does not revoke a secret
that remains in Git history. Do not rewrite shared history as routine cleanup.

The canonical Git fix is commit `36ddb834793c5165138c828010e7475b093dadad`.
Dockhand retained both variables as masked secrets. The supported deployment job
succeeded with the same cached image and networks, the same site returned online,
and native Argon2 verification rejected the old secret and accepted the new one.
Forced Olm traffic and the authenticated MCP connection were checked separately.
The original automatic deployment schedule, webhook setting, and image-pull
policy were restored after the controlled deployment.

Rollback image or configuration changes with the current private variables.
Do not revert to a Git revision containing the revoked literal credential.

## Health and recovery

The deployed container has no native Docker healthcheck. A running process is
not proof that the site tunnel works. Check the site's online state in Pangolin,
then test the intended data path and application. Do not add an invented status
URL or restart the NAS Docker daemon based on a log substring.

The existing root cron watchdog is `/usr/local/bin/newt-watchdog.sh`. Keep its
scope bounded; restarting Docker interrupts every NAS container.

## Rotation

Use Pangolin's site credential regeneration API/UI. The handler in the deployed
Pangolin `1.25.3` supports retaining the existing connection while replacing the
secret (`disconnect: false`), allowing the deployment settings to be updated
before a controlled Newt recreation. Preserve the existing site ID, access
rules, image, networks, and other container settings. Old backups containing the
previous secret will need the current credential before Newt can reconnect.

## Upstream sources

- [Newt releases](https://github.com/fosrl/newt/releases)
- [Site credentials and regeneration](https://docs.pangolin.net/manage/sites/credentials)
- [Deployed regeneration handler](https://github.com/fosrl/pangolin/blob/1.25.3/server/routers/re-key/reGenerateSiteSecret.ts)
