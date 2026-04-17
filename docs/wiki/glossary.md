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
WireGuard relay on the VPS. VPS Traefik shares Gerbil's network namespace.

## Newt
Remote site connector that links NASUS into the Pangolin-controlled private network.

## Olm
VPS-side tunnel component that provides reachability to the NASUS LAN.

## Traefik
Reverse proxy and TLS terminator. There is one instance on the VPS and another on NASUS.

## CrowdSec
Behavior-based security engine that consumes logs and applies blocking decisions.

## Dockhand
Container-management service used to monitor and manage Docker hosts.

## Hawser
Remote Docker API agent used for NASUS management through Dockhand.

## NASUS
The home server at `192.168.0.10` hosting the media, torrent, and *arr services.

## VPS
The public server at `51.195.100.11` hosting Pangolin, Traefik, CrowdSec, and related edge services.

## `traefik_traefik`
The single shared external Docker network used by NASUS services.

## `pangolin` network
The external Docker network used by non-core VPS stacks.
