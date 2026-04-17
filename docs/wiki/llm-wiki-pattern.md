---
title: "LLM Wiki Pattern for This Homelab"
slug: llm-wiki-pattern
type: concept
status: active
tags: ["homelab", "wiki", "llm-wiki"]
aliases: ["llm wiki pattern"]
entities:
  primary: llm-wiki-pattern
  mentions: []
related: ["./maintenance-workflow.md", "./llm-wiki-research-and-best-practices.md", "./index.md"]
sources: ["docs/wiki/llm-wiki-research-and-best-practices.md"]
confidence: medium
audience_level: operator
last_ingested: 2026-04-17
last_lint: 2026-04-17
---
# LLM Wiki Pattern for This Homelab

This page records the design principles adopted from current LLM-wiki and
LLM-friendly documentation patterns, then maps them onto this homelab wiki.

## External References Consulted

- Karpathy, "LLM Wiki" gist:
  <https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f>
- llms.txt project:
  <https://llmstxt.org/>
- txt-llms implementation guide:
  <https://txt-llms.com/documentation>

## Best Practices We Are Adopting

### 1. Keep raw sources separate from synthesized knowledge
Pattern:
- raw docs and source files stay immutable
- the wiki is the maintained synthesis layer
- the schema tells the agent how to behave

Applied here:
- raw sources are upstream docs, compose files, and `AGENTS.md`
- synthesized knowledge lives under `docs/wiki/`
- behavior rules live in `AGENTS.md` and
  `docs/wiki/maintenance-workflow.md`

### 2. Make knowledge persistent and cumulative
Pattern:
- do not force the agent to rediscover facts from scratch each session
- turn answers, audits, and maintenance into durable pages

Applied here:
- service pages preserve upstream comparisons and reasoning
- dated reviews preserve audit conclusions
- `docs/wiki/log.md` records structural wiki maintenance

### 3. Maintain a small number of strong entry points
Pattern:
- one content index for humans
- one machine manifest for agents
- one compact handoff file for context-limited runs

Applied here:
- `docs/wiki/README.md` is the human index
- `docs/wiki/llms.txt` is the machine manifest
- `docs/wiki/llms-full.txt` is the compact handoff file

### 4. Prefer explicit structure over clever retrieval
Pattern:
- small, interlinked markdown files often beat re-searching raw docs
- indexes, summaries, and logs reduce guesswork for the next agent

Applied here:
- each service gets a single page with a fixed section order
- findings have stable IDs
- audits summarize the repo-wide state
- `system-overview.md` gives fast orientation before deep dives

### 5. Build in lint and drift detection
Pattern:
- a good LLM wiki has a regular lint pass for contradictions, stale facts,
  missing links, and coverage gaps

Applied here:
- `maintenance-workflow.md` defines a wiki lint checklist
- the self-optimization cron should review the wiki entry points as part of its
  routine

### 6. Keep traceability higher than polish
Pattern:
- a less elegant page with sources and remediation is more valuable than a
  polished but unverifiable summary

Applied here:
- service pages cite upstream references
- audits are dated instead of overwritten
- answers should cite wiki paths directly

## What This Means for Future Improvements

Good next steps:
- add missing NASUS pages only when source-controlled or live evidence is
  available
- keep `llms.txt` and `llms-full.txt` in sync with README
- add new audit files instead of rewriting old ones
- use the log for incremental structural improvements

Bad next steps:
- invent missing NASUS documentation from memory
- let README link to pages that do not exist
- make compose changes without first capturing the reasoning in the wiki


### 7. Use namespaces when duplicate service names exist
Pattern:
- when two hosts run services with the same name, keep them in separate page
  namespaces so links stay unambiguous

Applied here:
- VPS pages live under `docs/wiki/services/`
- NASUS pages live under `docs/wiki/services-nasus/`
- entry-point files must mention both namespaces so agents do not assume a
  single `traefik.md` or `dashdot.md`
