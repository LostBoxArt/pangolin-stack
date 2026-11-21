---
title: "Glossary"
slug: wiki-glossary
type: glossary
status: active
tags: ["homelab", "wiki", "glossary"]
aliases: ["terms"]
entities:
  primary: wiki-glossary
  mentions: []
related: ["./README.md", "./system-overview.md", "./index.md"]
sources: ["AGENTS.md", "docs/wiki/system-overview.md"]
confidence: high
audience_level: operator
last_ingested: 2026-04-17
last_lint: 2026-04-17
---

# Glossary

Short definitions for recurring Pangolin homelab terms.

## Pangolin
Control plane for the public edge and private-resource publishing model.

## Gerbil
WireGuard relay on the CloudNode. CloudNode Traefik shares Gerbil's network namespace.

## Newt
Remote site connector that links HomeNode into the Pangolin-controlled private network.

## Olm
CloudNode-side tunnel component that provides reachability to the HomeNode LAN.

## Traefik
Reverse proxy and TLS terminator. There is one instance on the CloudNode and another on HomeNode.

## CrowdSec
Behavior-based security engine that consumes logs and applies blocking decisions.

## Dockhand
Container-management service used to monitor and manage Docker hosts.

## Hawser
Remote Docker API agent used for rammus management through Dockhand. Binds
`192.168.0.12:2375` only and requires a token.

## HomeNode / NASUS
Two names for the same box: the ASUSTOR NAS at `192.168.0.10`. Since 2026-11-21
it is **storage only** — it exports NFS and runs **zero containers**.

## Rammus
The compute host at `192.168.0.12` (ASUS PN62, formerly named `pn62`). Since
2026-11-21 it runs **every** application: media, torrent, *arr, the tunnel, and
the LAN reverse proxy. Its old name in the docs is `HomeNode` — that usage is
historical and now refers to NASUS.

## CloudNode
The public server at `203.0.113.1` hosting Pangolin, Traefik, CrowdSec, and related edge services.

## `traefik_traefik`
The single shared external Docker network used by HomeNode services.

## `pangolin` network
The external Docker network used by non-core CloudNode stacks.
