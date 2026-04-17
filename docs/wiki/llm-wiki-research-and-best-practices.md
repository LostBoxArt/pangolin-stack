---
title: "LLM-Wiki — Research, Best Practices, and Utopia Reference Architecture"
slug: llm-wiki-research-and-best-practices
type: research-note
status: reference
tags: [llm-wiki, knowledge-base, agent, homelab, rag, context-engineering, utopia]
aliases: ["llm wiki research", "utopia reference architecture"]
entities:
  primary: llm-wiki-research-and-best-practices
  mentions: []
related:
  - docs/wiki/llm-wiki-pattern.md
  - docs/wiki/README.md
  - docs/wiki/llms.txt
  - docs/wiki/llms-full.txt
  - docs/wiki/maintenance-workflow.md
  - AGENTS.md
  - INFRASTRUCTURE.md
  - README.md
sources:
  - https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
  - docs/wiki/llm-wiki-pattern.md
confidence: high
audience_level: operator
audience: homelab operator, AI coding agent
generated: 2026-04-17
last_ingested: 2026-04-17
last_lint: 2026-04-17
scope: >
  Consolidated external research on the "LLM-Wiki" pattern plus the
  optimal, end-state design for a homelab-focused wiki that an AI agent
  can ingest, query, and maintain. Read-only reference — does NOT change
  any existing files in this repository.
---

> "The wiki is a persistent, compounding artifact. The cross-references are already there. The contradictions have already been flagged. The synthesis already reflects everything you've read."
> — Andrej Karpathy, [`llm-wiki` gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f), April 2026

# 0. How to read this document

This is a **research + design note**, not an implementation. It distills ~20 primary and secondary sources on the LLM-Wiki pattern, agent-friendly documentation, context engineering, hybrid retrieval, agent memory architectures, homelab runbook hygiene, and secrets handling. The goal is to describe the **utopia end-state** for an LLM-Wiki serving an AI coding/operations agent that helps you run this Pangolin homelab stack, then to justify every design choice against the literature so future changes can be made on evidence rather than vibes.

Structure:

1. North-star definition and why the pattern exists
2. Architecture: the three layers and three operations (what every source agrees on)
3. Points of disagreement and how the sources reconcile
4. Directory layout and file-naming conventions for the utopia build
5. Frontmatter schema and page-type templates
6. Indexing, logging, and the `llms.txt` surface for agents
7. Agent memory model mapped onto wiki artifacts
8. Retrieval pipeline (chunking + hybrid search + RRF + rerank)
9. Context-engineering discipline (context rot, lost-in-the-middle)
10. Homelab-specific adaptations (service inventory, ports, runbooks, incidents)
11. Security hygiene (secrets, redaction, git-safety)
12. MCP surface and tool contracts
13. Self-healing loop: `wiki-lint` design
14. Quality gates, metrics, and SLOs for the wiki itself
15. Anti-patterns and common failure modes
16. Tooling stack recommendations
17. Phased roadmap from today → utopia
18. Source bibliography
19. Changelog of this document

---

# 1. North-star definition

An **LLM-Wiki** is a git-versioned directory of markdown files that sits **between** you and your raw sources, maintained almost entirely by an LLM agent. Unlike vanilla RAG, which re-derives knowledge from raw chunks on every query, an LLM-Wiki **compiles knowledge once on ingest** into durable, interlinked pages and only queries against the compiled artifact afterwards.

The three non-negotiable properties every source agrees on:

| Property | What it means | Why it matters |
|---|---|---|
| **Persistent** | Knowledge lives in markdown files, version-controlled | Git history is free ADR, free backup, free collaboration |
| **Compounding** | Each new source updates multiple existing pages | Second source is cheaper than the first; tenth is almost free |
| **Human-readable** | Pages render in any markdown viewer | Obsidian is the IDE, agent is the programmer, wiki is the codebase |

For a **homelab** the translation is: every compose change, every Pangolin route, every Traefik middleware tweak, every restore drill is filed into pages the agent already knows how to read. When you ask "why is `recyclarr` on this network?" the agent doesn't re-read 80 compose files — it reads one concept page and one service page.

Karpathy's original framing of the **division of labor** is the cleanest:

- **You**: curate sources, explore, ask questions, set direction.
- **LLM**: summarize, cross-reference, file, bookkeep, flag contradictions.
- **Tools** (Obsidian / qmd / MCP): present the wiki and give the LLM first-class access to it.

---

# 2. Architecture — three layers, three operations

Every mature implementation converges on the same shape:

## 2.1 Layers

```
┌──────────────────────────────────────────────────────────┐
│  SCHEMA LAYER   AGENTS.md / CLAUDE.md / skills/*.md      │
│                 How the agent behaves (procedural memory) │
├──────────────────────────────────────────────────────────┤
│  WIKI LAYER     docs/wiki/**/*.md  (agent-owned)          │
│                 index.md · log.md · entities/ · concepts/ │
│                 services/ · runbooks/ · decisions/        │
├──────────────────────────────────────────────────────────┤
│  RAW LAYER      docs/wiki/raw/ · config/** · stacks/**    │
│                 Immutable sources; LLM reads, never writes│
└──────────────────────────────────────────────────────────┘
```

Reading the stack **top-down**:

- **Schema** is the *behavioural contract*. It is small (<200 lines), hand-maintained, and rarely changes. It answers: "Given a new source, which pages do I touch? What frontmatter do I emit? What style do I use? What must I never do?" This is the LLM's **procedural memory**.
- **Wiki** is the *synthesized long-term memory*. The LLM owns it completely; you read it. It is the semantic + episodic memory of the homelab.
- **Raw** is *ground truth*. It is the homelab itself (compose files, configs, traefik rules, logs) plus anything you clip in (articles, vendor docs, GitHub READMEs). It is immutable from the wiki's perspective — the wiki cites raw sources but never mutates them.

> **Homelab-specific**: the raw layer is unusual here because large parts of it are already code in this repo (`stacks/`, `config/`, `AGENTS.md`, `INFRASTRUCTURE.md`). The wiki treats these as first-class sources and the agent's ingest flow is *code-change-aware*: a PR that edits `stacks/arrs/docker-compose.yml` should trigger a re-ingest of the `services/arrs.md` page.

## 2.2 Operations

Every source (Karpathy gist, `kenhuangus/llm-wiki`, `SamurAIGPT/llm-wiki-agent`, BrainDB, ToolHalla, ThePromptShelf, GitHub Blog on AGENTS.md) distills the agent's job into the same three verbs:

### 2.2.1 Ingest
Input: a new raw source (URL, compose change, incident postmortem, CVE, vendor doc).
Output: mutations across the wiki that preserve invariants.

Canonical ingest flow:

1. **Read** the source in full.
2. **Classify** it (entity, concept, service, incident, decision, how-to, reference).
3. **Discuss** key takeaways with the operator (optional but recommended for early wiki).
4. **Write** a source page in `docs/wiki/sources/<slug>.md`.
5. **Update** every entity/concept/service page the source touches (typical 10–15 pages).
6. **Cross-link** with `<<wikilinks>>` in both directions.
7. **Flag contradictions** where new data disagrees with existing pages.
8. **Append** to `log.md` with a parseable `## [YYYY-MM-DD] ingest | <title>` heading.
9. **Update** `index.md` with the new page entries.

### 2.2.2 Query
Input: a natural-language question.
Output: an answer with citations, optionally filed back as a new wiki page.

The crucial, frequently missed insight from the Karpathy gist: **"good answers can be filed back into the wiki as new pages."** A comparison table you asked for, a diagnosis of last night's incident, a decision rationale — these are valuable. They should compound just like ingested sources do, not evaporate into chat scrollback.

### 2.2.3 Lint
Input: the current wiki.
Output: a report of health issues + optional auto-fixes.

This is the step most amateur implementations skip and is the reason home-grown wikis rot. Details in §13.

---

# 3. Points of disagreement and how to reconcile them

Five places the sources genuinely diverge and the opinionated choice for this homelab:

| Question | Camp A | Camp B | Recommendation here | Why |
|---|---|---|---|---|
| **Do you need embeddings?** | Karpathy gist: "at moderate scale (~100 sources, hundreds of pages) the index file alone is enough." | BrightCoding / QMD / AgentWiki: "hybrid BM25+vector from day one." | Start with `index.md` + ripgrep. Add `qmd` hybrid search only when the wiki exceeds ~150 pages or query latency climbs. | Context rot research (ToolHalla, Chroma) shows small, targeted context beats huge retrieval. |
| **AGENTS.md vs CLAUDE.md** | Single file (`AGENTS.md`) is the Linux-Foundation-backed standard. | Split files per agent. | One canonical `AGENTS.md` at root; agent-specific overrides only if behaviour truly differs. | The Prompt Shelf + GitHub Blog (2,500-repo study) both show consolidation wins. |
| **Flat vs hierarchical wiki** | Flat (everything in `wiki/`). | Deeply nested by domain. | Shallow hierarchy: one level deep max (`entities/`, `services/`, etc.). | Obsidian graph view and grep both degrade with depth; agents confuse deep paths. |
| **YAML frontmatter everywhere?** | Frontmatter-first: "reduce tokens by up to 85%" (SteakHouse, Hannecke). | Pure body, no metadata. | Mandatory frontmatter on every wiki page. Optional on raw. | Retrieval accuracy, agent cost, and Dataview plugin support all require it. |
| **Lint frequency** | On-demand only. | Scheduled nightly + after every ingest. | Mechanical pass on every ingest; semantic pass weekly; structural review monthly. | `/wiki-lint` blog, BrainDB "2 AM fact-check", Wikipedia CLAIRE study (3.3% contradiction rate). |

---

# 4. Utopia directory layout

This is the target, not the current state. Existing files in this repo are *not* moved by this document.

```
pangolin-stack/
├── AGENTS.md                 ← schema (procedural memory, <200 lines)
├── README.md                 ← human-first project intro
├── INFRASTRUCTURE.md         ← human-first architecture overview (also raw)
│
├── docs/
│   └── wiki/
│       ├── README.md         ← human-facing "how to use the wiki"
│       ├── llms.txt          ← AI business card (500–2000 words)
│       ├── llms-full.txt     ← deep overview (2000–10000 words)
│       │
│       ├── index.md          ← content catalog, updated on every ingest
│       ├── log.md            ← append-only ingest/query/lint journal
│       ├── glossary.md       ← homelab jargon, one-line each
│       │
│       ├── raw/              ← immutable clipped sources
│       │   ├── assets/       ← images downloaded for offline agent use
│       │   ├── vendor/       ← vendor docs (Pangolin, Traefik, qBit…)
│       │   ├── articles/     ← blog posts, CVEs, postmortems
│       │   └── transcripts/  ← chat logs, meeting notes
│       │
│       ├── sources/          ← one page per raw source (LLM-written)
│       ├── entities/         ← people, vendors, projects, domains
│       ├── concepts/         ← tunneling, mTLS, GitOps, zero-trust…
│       ├── services/         ← one page per compose service (utopia)
│       ├── hosts/            ← one page per physical/virtual host
│       ├── networks/         ← docker networks, VLANs, Pangolin tunnels
│       ├── runbooks/         ← how-to: restore, rotate, upgrade, debug
│       ├── decisions/        ← ADRs — every non-trivial choice
│       ├── incidents/        ← postmortems, even for 5-minute blips
│       └── experiments/      ← scratchpads with TTL (90 days)
```

Why this shape:

- **Shallow.** Agents and `rg` stay fast; Obsidian graph stays legible.
- **Type-prefixed directories.** Every page's *kind* is inferable from its path — no guessing.
- **`experiments/` is TTL'd.** Prevents the "everything ends up in the wiki forever" failure mode flagged by the `dev.to/tadmstr` memory-TTL article.
- **`raw/` mirrors the rest of the repo.** The compose files in `stacks/` are also raw sources; a symlink or a source page per compose file closes the loop.

---

# 5. Frontmatter schema and page templates

## 5.1 Universal frontmatter

Every wiki page — without exception — begins with YAML frontmatter. This is the single biggest token-efficiency lever available (Hannecke reports ~85% reduction in local-LLM workflows; SteakHouse reports 40% fewer retrieval failures). Treat it as a machine-readable API surface.

```yaml
---
title: "<human-readable title>"
slug: <kebab-case-filename-without-extension>
type: source | entity | concept | service | host | network | runbook | decision | incident | experiment | glossary
status: draft | active | deprecated | superseded
tags: [homelab, pangolin, traefik, ...]        # 3–7 max; tag inflation is worse than no tags
aliases: ["alt-name-1", "alt-name-2"]          # for wikilink disambiguation
entities:                                      # explicit entities disambiguate for RAG
  primary: <slug>
  mentions: [<slug>, <slug>]
related: [<wikilink>, <wikilink>]              # 3–10; pages with >20 are hubs → split them
sources: [<path-or-url>, <path-or-url>]        # raw sources this page is derived from
confidence: low | medium | high                # epistemic honesty; drives lint priority
audience_level: operator | contributor | visitor
last_ingested: 2026-04-17
last_lint: 2026-04-17
---
```

Fields `type`, `status`, `last_ingested`, and `last_lint` are load-bearing for the lint pass. Omit them and the agent cannot tell stale pages from healthy ones.

## 5.2 Page-type templates

Each template starts with the frontmatter above plus a canonical body skeleton. **Stability of heading anchors** is critical — lint, Dataview, and grep all key off them.

### 5.2.1 Source page (`sources/<slug>.md`)

```
## Summary        # 5–10 sentences, neutral, no opinions
## Key Claims     # bulleted, each claim has <<citation>>
## Key Quotes     # verbatim, ≤3, with location
## Connections    # <<entities>>, <<concepts>>, <<services>> touched
## Contradictions # pages whose claims this source disagrees with
## Open Questions # gaps the agent wants to fill on next ingest
```

### 5.2.2 Entity page (`entities/<slug>.md`)

```
## Definition
## Identifiers      # domains, emails, GitHub handles, vendor IDs
## Role in this homelab
## Services         # <<services/*>> this entity owns or depends on
## History          # time-ordered one-liners
## References       # <<sources/*>>
```

### 5.2.3 Concept page (`concepts/<slug>.md`)

```
## TL;DR            # one paragraph
## Definition       # formal
## How it applies here
## Gotchas
## Related concepts
## References
```

### 5.2.4 Service page (`services/<slug>.md`) — homelab-critical

```
## What it does
## Where it lives          # host, network, compose path
## Ports & endpoints       # internal, pangolin-exposed, traefik rule
## Depends on              # <<services/*>>
## Depended on by
## Volumes & data
## Secrets                 # reference, never literal — see §11
## Runbooks                # <<runbooks/*>>
## Known issues
## Change log              # append-only, dated
```

### 5.2.5 Host page (`hosts/<slug>.md`)

```
## Identity              # hostname, role, location
## Hardware
## OS & kernel
## Services hosted       # <<services/*>>
## Networks              # IPs, VLANs, tunnel interfaces
## Backup strategy       # <<runbooks/backup-*>>
## Access                # SSH keys, console, IPMI
```

### 5.2.6 Runbook page (`runbooks/<slug>.md`) — follow Diátaxis "How-to"

```
## When to use this
## Prerequisites
## Procedure             # numbered, copy-pastable commands
## Verification
## Rollback
## Escalation
## Last tested           # date + outcome
```

### 5.2.7 Decision page (`decisions/NNNN-<slug>.md`) — MADR-lite

```
## Status             # Proposed | Accepted | Deprecated | Superseded by <<>>
## Context
## Decision
## Consequences       # positive, negative, neutral
## Alternatives considered
## References
```

ADRs are *immutable*: to change a decision, write a new ADR that supersedes the old one, then update frontmatter `status: superseded`.

### 5.2.8 Incident page (`incidents/YYYY-MM-DD-<slug>.md`)

```
## Timeline           # UTC timestamps, one line each
## Impact
## Root cause
## Contributing factors
## What went well
## What went badly
## Action items       # each links to a <<decisions/*>> or <<runbooks/*>>
```

---

# 6. Indexing, logging, and the `llms.txt` surface

## 6.1 `index.md` — content-oriented

Flat catalog. One H2 per page-type, one bullet per page, one-line descriptions. The agent reads this *first* on every query — it is the wiki's table of contents and the main reason moderate-scale wikis don't need a vector DB.

```
## Services
- <<services/pangolin>> — WireGuard+Traefik tunnel control plane
- <<services/gerbil>>    — WireGuard interface manager
...

## Runbooks
- <<runbooks/restore-acme-json>> — recover lost Let's Encrypt certs
...
```

Updated on every ingest. Lint flags any wiki page not appearing here.

## 6.2 `log.md` — time-oriented

Append-only. Every entry starts with `## [YYYY-MM-DD HH:MM] <op> | <title>` so `grep "^## \[" log.md | tail` gives a CLI summary. Example:

```
## [2026-04-17 09:22] ingest | Pangolin 1.4.0 release notes
- Updated <<services/pangolin>> version field 1.3.1 → 1.4.0
- Flagged contradiction with <<concepts/tunnel-architecture>> re: UDP 21820 behaviour
- Added <<sources/pangolin-140-release>>

## [2026-04-17 11:03] query  | "why does my letsencrypt cert keep renewing?"
- Synthesized from <<services/traefik>>, <<runbooks/restore-acme-json>>
- Filed answer as <<concepts/acme-renewal-thrash>>

## [2026-04-17 14:00] lint   | weekly semantic pass
- 0 broken wikilinks, 2 stale pages, 1 contradiction (see <<decisions/0042-…>>)
```

## 6.3 `llms.txt` and `llms-full.txt` — agent landing page

Treat the wiki as a "website for AIs." Two file variant (per the llms-txt standard):

- `llms.txt` (500–2000 words): one-line description, stack summary, top 20 links into the wiki. This is what a fresh agent reads *before* anything else.
- `llms-full.txt` (2000–10000 words): full narrative of the homelab, all major concepts, every service with one paragraph. Designed to fit in a single context window with room to spare — explicitly under 30K tokens to dodge the Chroma/ToolHalla "context rot cliff" (see §9).

You already have `docs/wiki/llms.txt` and `docs/wiki/llms-full.txt` — keep them; the utopia version only tightens what they include.

---

# 7. Agent memory model mapped onto wiki artifacts

Cognitive-science memory taxonomy (Chaitanya Prabuddha, arXiv 2603.07670) maps onto wiki artifacts very cleanly. Getting this map right is the difference between an agent that feels amnesiac and one that feels competent.

| Memory type | Lifespan | Where it lives in the wiki |
|---|---|---|
| **Working** | current turn | context window; seeded from `llms.txt` + `index.md` + specific wikilinks |
| **Episodic** | time-indexed | `log.md` + `incidents/` + `experiments/` |
| **Semantic** | fact-indexed | `entities/` + `concepts/` + `services/` + `glossary.md` |
| **Procedural** | versioned, always-loaded | `AGENTS.md` + `.cursor/skills/**` + `runbooks/` |

**Anti-pattern** (common): stuffing everything into one vector store. This conflates episodic recency-decay with semantic permanence and tanks retrieval quality for both. Keep the four stores physically separate; let retrieval policies differ per store.

**TTL discipline** (from `dev.to/tadmstr`): `experiments/` and `raw/transcripts/` are candidates for 90-day TTL. Everything else is permanent until explicitly superseded.

---

# 8. Retrieval pipeline

For wikis smaller than ~150 pages, `index.md` + `grep`/`rg` is enough and provably superior in latency and determinism. Past that scale, add hybrid search.

## 8.1 Chunking (only matters once embeddings are in play)

Consensus across MLExpert, BrightCoding, aiwikiproject.com:

- **Respect markdown structure.** Use `MarkdownHeaderTextSplitter` or equivalent; never split across an H2.
- **Target 500–1500 characters per chunk** for balance; 200–500 for high-precision Q&A; 1500+ only for long narrative pages.
- **10–20% overlap.**
- **Embed metadata into every chunk**: source path, section heading, page-level tags. Losing context is the #1 RAG failure.
- **AST-aware chunking for code** (`qmd` uses tree-sitter) if your wiki includes embedded compose/YAML snippets.

## 8.2 Hybrid search

One ranker is not enough:

- **BM25 / FTS5** wins on: exact names (`gerbil`), port numbers, error codes, command flags, acronyms.
- **Dense vectors** win on: paraphrase ("my cert won't update" → "acme renewal thrash"), cross-language, conceptual similarity.

Combine with **Reciprocal Rank Fusion**: `RRF(d) = Σ 1/(k + rank_i(d))`, `k=60`. The liamca/sqlite-hybrid-search repo reports ~40% accuracy lift over vector-only, sub-100ms latency, single-file deployment. This is the right fit for a homelab.

## 8.3 Rerank

Position-aware RRF plus a small cross-encoder rerank (e.g. `qwen3-reranker-0.6b`) on the top 20 → top 5. `qmd` does exactly this on-device; it is the recommended retrieval tool for this wiki once it outgrows `index.md`.

## 8.4 Putting it together

```
query
  │
  ├─► expand (lex variant, hyde variant, verbatim)
  │
  ├─► FTS5 top-50    ┐
  │                  ├─► RRF merge (k=60, position-aware) ─► top-20
  ├─► ANN top-50     ┘
  │
  ├─► cross-encoder rerank ─► top-5
  │
  └─► LLM synthesis with citations ─► (optionally file back as wiki page)
```

---

# 9. Context-engineering discipline

Three empirical findings from 2026 research dominate this section:

## 9.1 Context rot (Chroma, ToolHalla, Wire)

Every frontier model degrades from ~95% → 60–70% accuracy as input grows from 10K → 100K tokens. The "cliff" usually falls around 32K–64K tokens. A 200K-claimed model is typically unreliable past ~130K. The math is simple — attention is n² — and no model escapes it.

**Design implications for the wiki:**
- `llms-full.txt` must stay under ~30K tokens.
- Never stuff the agent with the whole wiki. Always retrieve a subset.
- Favour many small pages over few large ones. Target < 1500 words per page; split when a page exceeds 2500.

## 9.2 Lost in the middle (Liu et al., reproduced widely)

U-shaped attention: tokens at positions 0–15% and 85–100% of the context get strong attention; middle content (40–60%) drops 15–20 points in accuracy. Design the retrieved prompt so the most load-bearing evidence is at the start **and** the end, with lower-priority supporting evidence in the middle.

## 9.3 Entropy reduction (Sangshetti, meta-intelligence)

Context engineering is the discipline of transforming "high-entropy, ambiguous human contexts into low-entropy, machine-interpretable representations." Concretely:

- Prefer bulleted claims over narrative paragraphs in wiki pages.
- Prefer tables for comparisons.
- Prefer frontmatter over body for facts the agent needs to filter on.
- Prefer explicit `<<wikilinks>>` over implicit "see above."

Entropy-reduction is also why the wiki is valuable *to humans*: once the agent has compressed knowledge into well-shaped pages, you read them faster too.

---

# 10. Homelab-specific adaptations

Everything up to this point is domain-agnostic. The following is what makes this wiki useful *for this homelab*.

## 10.1 Service inventory as first-class citizen

One page per compose service, one page per host, one page per docker network. The lint pass reads `stacks/**/docker-compose.yml` and flags any service without a wiki page (or any wiki service whose compose file has disappeared). This is directly borrowed from NetBox/Kuwaiba DCIM practice — your docker-compose **is** your CMDB.

## 10.2 Port matrix

A single page `concepts/port-matrix.md` with a table of every exposed port, which host/service owns it, whether Pangolin tunnels it, and the Traefik rule. This is the page an agent hits first for "why can I not reach service X." It is regenerable from compose + Traefik config — make regeneration a lint pass.

## 10.3 Runbooks tied to real drills

Every runbook has `last_tested:` in frontmatter. Any runbook untested for >90 days is lint-flagged. Borrowed from Google SRE's drill discipline: an untested runbook is a wish, not a procedure.

## 10.4 Ingest triggers wired to git

On any git commit that touches `stacks/`, `config/`, or `AGENTS.md`, a pre-commit (or post-merge) hook re-ingests the changed paths. The wiki never lags the real infrastructure by more than one commit.

## 10.5 Incident-driven learning loop

Every incident → incident page → at least one action item → that action item becomes either a runbook update or an ADR. This is the single most valuable compounding loop in a homelab wiki because incidents are the exact events you never want to re-debug from scratch.

## 10.6 Vendor surface watchlist

A `concepts/vendor-watch.md` page lists every upstream project you depend on (Pangolin, Gerbil, Traefik, qBit, \*arr stack, Cloudflare, Let's Encrypt) with their release feeds. The ingest operation watches these feeds and files a source page on every release. This is how BrainDB gets its "fact-checks itself at 2AM" property.

---

# 11. Security hygiene

The LLM-Wiki lives in git. Therefore **no secret ever appears in the wiki, even obfuscated.** The rules:

1. **Reference, don't literal.** A service page names the secret (`POSTGRES_PASSWORD`), its source file (`.env`), and its rotation runbook (`<<runbooks/rotate-postgres>>`). It never shows the value.
2. **Pre-commit redaction.** Use `gitleaks` (or equivalent) as a pre-commit hook on `docs/wiki/**`. Belt-and-suspenders against an ingest slip.
3. **SOPS + age** for anything that *must* live in git encrypted (rare for wiki content; common for configs). The wiki documents *that* SOPS is in use and *where* keys live, never the keys themselves.
4. **Agent-level redaction.** The ingest prompt explicitly instructs the agent: "If a source contains credentials, API keys, or private tokens, write the wiki page without them and note their redaction in a `## Redacted` section." Buildkite's redactor patterns are a fine starting set.
5. **Append-only audit log.** `log.md` is the access trail. Don't rewrite history; use supersede-by-new-entry.

The combination of these five makes the wiki safe to push to a public git remote if you ever want to. For this homelab, private remote is still the default — but the discipline is the same.

---

# 12. MCP surface and tool contracts

Once the wiki is non-trivial, expose it to the agent as MCP resources and tools, not as raw files.

**Resources** (read-only):
- `wiki://index` — serves `index.md`
- `wiki://page/<slug>` — serves a single page with resolved wikilinks
- `wiki://search?q=...` — hybrid-search entrypoint

**Tools** (write-capable, agent-triggerable):
- `wiki.ingest(source_uri)` — runs the full ingest flow, returns the diff.
- `wiki.query(question)` — runs the retrieval pipeline, returns answer + citations.
- `wiki.file_back(title, body, type)` — promotes a chat answer into a wiki page.
- `wiki.lint(scope)` — runs mechanical+semantic lint; `scope` is `all`, `since <date>`, or a path.
- `wiki.supersede(old_slug, new_slug)` — marks an ADR/page superseded.

`qmd` already provides `query`, `get`, `multi_get`, and `status` via MCP; extend it for ingest/lint. The MCP's **Knowledge Graph Memory Server** can store cross-session entity→relation→observation triples for things that don't deserve a markdown page yet — a holding pen before promotion.

---

# 13. Self-healing: the `wiki-lint` loop

This is the operation most implementations skip. Without it, every wiki rots within six months. Design it as three passes, run them on different cadences:

## 13.1 Pass 1 — Mechanical (every ingest, <5 s)

Pure script, no LLM:
- Orphan pages (no inbound wikilinks)
- Broken wikilinks (target slug doesn't exist)
- Missing mandatory frontmatter fields
- Duplicate slugs
- Pages older than N days without `last_lint` refresh
- Services in `stacks/` with no wiki page
- Runbooks with `last_tested:` older than 90 days

## 13.2 Pass 2 — Semantic (weekly, LLM-driven)

LLM reads a sample (recently-updated + random stratified sample) and checks for:
- Contradictions between pages (CLAIRE-style; Wikipedia study shows 3.3% baseline rate)
- Stale claims superseded by newer sources
- Concepts mentioned in 3+ pages without their own concept page
- Entities referenced by name but not wikilinked
- Missing cross-references between obviously-related pages

## 13.3 Pass 3 — Structural (monthly, human-in-the-loop)

Review the graph:
- Hubs (pages with >20 inbound links) — consider splitting
- Islands (connected components disconnected from the main graph) — stitch or document why
- Tag drift (synonymous tags diverging) — canonicalize
- Directory creep (are any types overdue for promotion out of `experiments/`?)

## 13.4 Report format

Every lint run emits a single `logs/lint/YYYY-MM-DD.md` file grouped by severity (critical / warning / info), each item with a one-click `<<fix>>` wikilink into the remediation runbook. Append a `## [YYYY-MM-DD HH:MM] lint | …` entry to `log.md`.

---

# 14. Quality gates, metrics, and SLOs

You manage what you measure. Track these against `log.md` + lint reports:

| Metric | Target | Why |
|---|---|---|
| **Wiki freshness** | p95 `last_ingested` < 30 days | Stale pages mislead the agent |
| **Orphan rate** | < 2% of pages | Orphans waste tokens on retrieval |
| **Broken wikilink rate** | 0 | Broken links are a code bug |
| **Contradiction rate** | < 1% after semantic lint | Directly impacts answer accuracy |
| **Runbook drill coverage** | 100% tested in last 90 days | Untested runbooks are theatre |
| **Services-without-page rate** | 0 | Blind spots for the agent |
| **Tokens/page p95** | < 1500 | Context-rot discipline |
| **Retrieval latency p95** | < 500 ms | Agent UX |
| **Answer citation rate** | 100% | Every claim traceable to a raw source |
| **Time-to-ingest** | < 5 min per source | Friction kills the habit |

---

# 15. Anti-patterns (collected from every failure mode the sources describe)

1. **The Bloat Spiral.** Ingesting everything. Solution: a source must earn its page; low-value sources go to `raw/` only, no wiki page.
2. **The Monolith Page.** One `homelab.md` with everything. Solution: aggressive splitting at ~1500 words; one topic per page.
3. **Frontmatter Tag Inflation.** 20 tags per page, all near-synonyms. Solution: canonical tag list in `glossary.md`, lint enforces it.
4. **Chat-Answer Evaporation.** Good answers never filed back. Solution: `wiki.file_back()` tool; make it one command.
5. **The Undocumented Decision.** Changes land in `stacks/` without ADRs. Solution: git pre-push hook: "does this diff need an ADR?" prompt; block or warn.
6. **Untested Runbooks.** `last_tested` unset forever. Solution: lint warning at 60 days, error at 90.
7. **The Secrets Leak.** An env file gets ingested verbatim. Solution: pre-commit gitleaks + agent-prompt redaction rule.
8. **The Rogue Refactor.** Agent decides to "improve" the schema mid-session. Solution: `AGENTS.md` is sacred; schema changes require explicit human approval.
9. **Context Stuffing.** Pasting the whole wiki into context. Solution: retrieval-first discipline; never exceed ~30K of retrieved context.
10. **The Empty Graph.** No `<<wikilinks>>`; pages are islands. Solution: lint rule — every non-glossary page must have ≥2 outbound and ≥1 inbound link.

---

# 16. Tooling stack recommendations

Opinionated shortlist, mapped to lifecycle stage:

**Day-zero (≤50 pages):**
- Markdown + git + `rg` + `AGENTS.md`
- Obsidian for browsing (optional)
- Nothing else.

**Day-one (≤150 pages):**
- `qmd` for hybrid search (local-first, MCP-native, on-device embeddings)
- `gitleaks` pre-commit for secret scanning
- A `wiki-lint` shell script for the mechanical pass

**Day-two (>150 pages):**
- Formal MCP server exposing the `wiki.*` tools
- Scheduled lint (systemd timer / cron) for semantic pass
- A small dashboard (one HTML page generated from `index.md` + lint reports) showing the SLO table
- Optional: `Archgate` for executable ADRs if decisions materially affect code-gen

**Experimental / only-if-needed:**
- Full knowledge graph (Neo4j / MegaMem) — only if page count > 500 and semantic queries become the bottleneck
- Obsidian Dataview plugin — for humans who want live tables off frontmatter

---

# 17. Phased roadmap from today → utopia

Do not try to build everything at once. Each phase earns the right to the next.

**Phase 0 — today.** `docs/wiki/` exists with `README.md`, `llm-wiki-pattern.md`, `llms.txt`, `llms-full.txt`, `log.md`, `maintenance-workflow.md`, `system-overview.md`, plus `services/` and `services-homenode/`. Good foundation.

**Phase 1 — schema lock (week 1).**
- Finalize `AGENTS.md` schema section (page-type list, frontmatter contract, ingest/query/lint SOPs).
- Write `index.md` as the content catalog.
- Ensure every current page has the universal frontmatter from §5.1.

**Phase 2 — operational pages (weeks 2–3).**
- One service page per compose service.
- One host page per host.
- One network page per docker network and per Pangolin tunnel.
- `concepts/port-matrix.md`.
- At least three runbooks, each with a real `last_tested:` date.

**Phase 3 — decisions + incidents (weeks 3–4).**
- Seed `decisions/` with the 5–10 biggest historical choices (why Pangolin? why Traefik? why this backup strategy?).
- Create `incidents/` with even tiny past incidents; format now, reuse later.

**Phase 4 — automation (weeks 4–6).**
- Pre-commit hook: changes under `stacks/`, `config/`, or `AGENTS.md` prompt ingest.
- Mechanical lint on every commit.
- Weekly semantic lint via cron/systemd.

**Phase 5 — retrieval (weeks 6–8, only if wiki > 150 pages).**
- Deploy `qmd` locally.
- Expose MCP resources/tools from §12.
- Measure retrieval latency and answer citation rate against SLOs in §14.

**Phase 6 — compounding (ongoing).**
- Vendor watchlist ingest.
- Answer-filing habit: any non-trivial agent answer becomes a wiki page.
- Quarterly structural review.

---

# 18. Source bibliography

Primary:
- Andrej Karpathy — [`llm-wiki` gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) (April 2026)
- `SamurAIGPT/llm-wiki-agent` — AGENTS.md / CLAUDE.md exemplars
- `kenhuangus/llm-wiki` — full Python reference implementation
- `llmwiki.lol` — "build a living wiki, not another RAG dump"

Architecture & operations:
- dev.to/futhgar — "Building Karpathy's LLM Wiki: A Production Homelab Implementation"
- dev.to/fex_beck — "BrainDB: 5,420 memories, 6 AI agents, self-healing knowledge graph"
- dev.to/kunal — "LLM Wiki: I Set Up Karpathy's Local Knowledge Base — 2026 Guide"
- alirezarezvani/claude-skills — `/wiki-lint` slash command

Agent instruction files:
- agentsmd.io — AGENTS.md best practices
- The Prompt Shelf — AGENTS.md structure & scope
- GitHub Blog — "How to write a great agents.md: lessons from 2,500 repos"
- agentsmd.online — complete reference

Context engineering & RAG:
- meta-intelligence.tech — "Context Engineering Guide 2026"
- Medium / Sangshetti — "Advanced Context Engineering Techniques"
- MLExpert — Effective Chunking Strategies
- aiwikiproject.com — RAG Architecture and Patterns
- BrightCoding — SQLite-Powered RAG with Hybrid Search
- liamca/sqlite-hybrid-search — BM25+Vector+RRF reference
- ceaksan.com — Hybrid Search with FTS5+Vector+RRF
- `qmd` — local hybrid search + rerank

Context rot & lost-in-the-middle:
- ToolHalla — "Context Rot: Why Your AI Agent Gets Dumber Over Time"
- Chroma research summary (via ToolHalla)
- Understanding Data — Lost-in-the-Middle mitigation
- Zylos Research — LLM Context Window Management 2026
- Wire Blog — Context Rot in production

Agent memory:
- arXiv:2603.07670 — "Memory for Autonomous LLM Agents"
- Chaitanya Prabuddha — AI Agent Memory Architectures
- Mindra — "The Memory Problem"

Frontmatter & llms.txt:
- SteakHouse — Markdown-First Semantics for RAG
- Hannecke (Medium) — Frontmatter-First for local LLMs
- AICrawlerCheck — llms.txt guide
- Firecrawl — create-llmstxt-py

Homelab & IaC:
- HomeLab Starter — Documenting Your Home Lab Setup Effectively
- HomeLab Starter — Terraform + Proxmox
- Homelab-IaC (readthedocs)
- aleksander-urbaniak/homelab, gr8monk3ys/homelab
- Wade Woolwine (Medium) — "Make Your Homelab AI Agent Ready"
- ANTLATT — Self-Hosted Secrets Management; GitOps for Homelabs
- Pangolin docs (docs.pangolin.net, docs.digpangolin.com)
- RamNode — Zero-Trust Homelab: Pangolin Setup

Secrets & safety:
- Buildkite agent redactor
- `joelhooks/agent-secrets`
- SOPS + age (Mozilla)

Knowledge graphs & MCP:
- modelcontextprotocol.io — Architecture overview
- MCP Knowledge Graph Memory Server
- C-Bjorn/MegaMem — Obsidian → temporal KG with MCP
- obra/knowledge-graph — Obsidian vault → graph + embeddings
- junhewk/simple-graph-builder — LLM entity extraction, 10-type ontology

Decision records:
- Archgate — executable ADRs
- Michel Lutz — ADR practical guide
- AI Advances (Faisal Feroz) — AGENTS.md vs ADRs

Documentation methodology:
- Diátaxis (diataxis.fr)
- Wikitech / NetBox; Kuwaiba; XWiki — operational documentation references

---

# 19. Changelog

```
2026-04-17: Added — initial research + utopia reference architecture. No existing files modified.
```
