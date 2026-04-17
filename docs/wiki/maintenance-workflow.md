---
title: "Maintenance Workflow"
slug: maintenance-workflow
type: workflow
status: active
tags: ["homelab", "wiki", "workflow"]
aliases: ["wiki maintenance workflow"]
entities:
  primary: maintenance-workflow
  mentions: []
related: ["./README.md", "./llm-wiki-pattern.md", "./index.md"]
sources: ["AGENTS.md", "docs/wiki/README.md"]
confidence: high
audience_level: operator
last_ingested: 2026-04-17
last_lint: 2026-04-17
---
# Maintenance Workflow

How agents should maintain and use this wiki.

This workflow builds on the current service pages and audits, but it also adds
LLM-wiki discipline so the knowledge base compounds instead of drifting.

## The Three Layers

### 1. Raw sources
Immutable evidence:
- upstream docs and reference compose files
- repo compose files under `stacks/`
- repo briefing in `AGENTS.md`
- dated review documents under `docs/wiki/`
- service pages under `docs/wiki/services/` and `docs/wiki/services-homenode/`

### 2. The wiki
Persistent synthesized knowledge:
- `docs/wiki/README.md`
- `docs/wiki/system-overview.md`
- `docs/wiki/compose-review-*.md`
- `docs/wiki/services/*.md`
- `docs/wiki/services-homenode/*.md`
- `docs/wiki/llms.txt`
- `docs/wiki/llms-full.txt`
- `docs/wiki/index.md`
- `docs/wiki/glossary.md`
- `docs/wiki/log.md`

### 3. The schema
Behavior and rules that tell an agent how to use the wiki:
- `AGENTS.md`
- this file

## Preferred Reading Order

### For answering questions
1. `AGENTS.md`
2. `docs/wiki/README.md`
3. the relevant dated review under `docs/wiki/`
   - CloudNode work: `docs/wiki/compose-review-2026-04-17.md`
   - HomeNode work: `docs/wiki/homenode-review-2026-04-17.md`
4. relevant `docs/wiki/services/<service>.md` or
   `docs/wiki/services-homenode/<service>.md`
5. compose file only after the wiki page

### For editing the wiki
1. read the relevant service page or audit
2. verify the source file or upstream reference if needed
3. update the wiki page
4. append a note to `docs/wiki/log.md`

### For editing compose files
1. read the relevant service page first
2. if an existing finding already covers the change, apply that remediation
3. if not, research upstream first and add a new finding to the service page
4. edit the compose file only after the wiki captures the reasoning
5. update the service page in the same change
6. for HomeNode, update the live HomeNode file, `host-configs/homenode/<service>/docker-compose.yml`, and the matching `services-homenode` page together

## Answering Rules

- Cite wiki paths directly in answers.
- Use the deviations table's `Intent` column before assuming a difference is a
  mistake.
- If the wiki does not cover a request, say so plainly.
- Do not invent upstream behavior or undocumented service facts.

## Writing Rules

### Keep pages easy for humans and agents to scan
- one service per page
- stable section order
- short tables over long prose when possible
- concrete finding IDs like `F-TRAEFIK-1` and `F-N-TRAEFIK-2`
- copy-pasteable remediation blocks

### Preserve traceability
- dated review files are append-only audit artifacts
- do not rewrite history in old audits except for obvious factual repair
- use `docs/wiki/log.md` for structural wiki updates and maintenance passes

### Keep compiled entry points current
- `docs/wiki/README.md` is the human index
- `docs/wiki/llms.txt` is the machine-oriented manifest
- `docs/wiki/llms-full.txt` is the compact one-file context handoff

## Lint Pass Checklist

A wiki lint pass should check for:
- broken links or references to files that do not exist
- service pages missing required sections
- findings without remediation snippets
- stale links to upstream docs
- critical rules present in `AGENTS.md` but absent from the wiki entry points
- audits that no longer match the current service-page findings
- missing cross-links from audits to service pages and back
- README references to HomeNode pages that do not exist, or service pages that exist but are missing from the TOC
- machine entry points (`llms.txt`, `llms-full.txt`) drifting from README

## Safe Improvements Without Further Research

These are usually safe to do during maintenance:
- fix broken internal links
- improve indexes and page maps
- refresh `llms.txt` and `llms-full.txt`
- add or update `docs/wiki/log.md`
- clarify coverage gaps already visible in the repo
- refresh HomeNode indexes and service-page lists after new `services-homenode/` pages land
- add cross-links between existing wiki pages

## Changes That Need Evidence First

Do not make these changes from intuition:
- changing service facts
- changing findings severity
- changing remediation commands
- adding new upstream claims
- editing compose files

For those, verify against upstream docs or the repo state first.

## Daily Maintenance Expectation

A maintenance pass should treat the wiki as a living compiled artifact:
- check whether the top-level wiki entry points are still accurate
- tighten wording where ambiguity could mislead a future agent
- add newly discovered durable operational rules only when traceable
- prefer small, safe improvements over broad speculative rewrites


## Current lint tooling

A mechanical lint pass can be run with `python3 scripts/wiki_lint.py`.

It currently checks:
- mandatory frontmatter presence
- broken relative markdown links
- duplicate slugs
- missing service entries in `index.md`
- required top-level entry points


### Additional high-value page families
- Concepts explain recurring topology or operational patterns such as port ownership.
- Decisions capture stable architecture choices and why they exist.
