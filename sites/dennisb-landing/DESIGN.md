---
version: alpha
name: Dennis B.
description: Personal landing page for Dennis B., an infrastructure engineer and homelab operator. Dark technical aesthetic with warm gold accents on a deep charcoal foundation. Field-notes layout with journal-style entries.
colors:
  background: "#0d0f0d"
  text-primary: "#f3eee5"
  text-secondary: "#cfc5b7"
  text-muted: "#897e70"
  accent: "#d5a15f"
  accent-hot: "#f4cb88"
  accent-dim: "#765333"
  green: "#9ccf92"
  grid-line: "rgba(213, 161, 95, 0.075)"
  grid-strong: "rgba(213, 161, 95, 0.17)"
  border: "rgba(213, 161, 95, 0.17)"
  vignette: "rgba(0, 0, 0, 0.5)"
  panel: "rgba(19, 18, 14, 0.68)"
  on-accent: "#0d0f0d"
typography:
  display:
    fontFamily: "Playfair Display, Georgia, serif"
    fontSize: "clamp(6rem, 15vw, 13.4rem)"
    fontWeight: 600
    lineHeight: 0.78
  body:
    fontFamily: "Outfit, system-ui, sans-serif"
    fontSize: "1rem"
    fontWeight: 300
    lineHeight: 1.7
  label-caps:
    fontFamily: "IBM Plex Mono, ui-monospace, monospace"
    fontSize: "0.72rem"
    fontWeight: 700
    letterSpacing: "0.13em"
    textTransform: uppercase
  note-meta:
    fontFamily: "IBM Plex Mono, ui-monospace, monospace"
    fontSize: "0.68rem"
    fontWeight: 700
    letterSpacing: "0.08em"
    textTransform: uppercase
  tag:
    fontFamily: "IBM Plex Mono, ui-monospace, monospace"
    fontSize: "0.68rem"
    fontWeight: 700
    letterSpacing: "0.08em"
    textTransform: uppercase
rounded:
  portrait: 28px
  portrait-inner: 22px
  pill: 999px
  button: 10px
spacing:
  content-x: "calc(100% - 4rem)"
  content-max: 1240px
  hero-gap: "clamp(2.5rem, 6vw, 5.5rem)"
easing:
  default: "cubic-bezier(0.22, 1, 0.36, 1)"
components:
  portrait-ring:
    type: pseudo-element
    background: conic-gradient(from 215deg, accent, transparent 18%, transparent 76%, accent-hot)
    animation: ring-spin 10s linear infinite
    border-radius: 35px
    inset: -7px
  tag-pill:
    borderColor: "rgba(213, 161, 95, 0.27)"
    textColor: accent-hot
    backgroundColor: "rgba(213, 161, 95, 0.045)"
    rounded: pill
    padding: "0.44rem 0.72rem"
  note-row:
    borderLeft: "1px solid accent-dim"
    borderTop: "1px solid line-soft"
    background: "linear-gradient(90deg, rgba(213, 161, 95, 0.04), transparent 32%)"
    padding: "1.05rem 1.15rem 1.05rem 1.35rem"
---

## Overview

A dark editorial portfolio page for an infrastructure engineer. The aesthetic blends technical precision with warm human touches — structured grid systems, monospace labels, serif/sans-serif contrast, and restrained gold accents against a near-black canvas.

The personality is calm, capable, and quietly confident. No glassmorphism, no decorative gradients, no flat minimalism. Depth comes from actual layered elements (noise, vignette, subtle radial highlights) rather than drop shadows alone.

The body content is presented as **field notes** — journal-style entries (Work, Home, AI/agents, Signals) that read like personal observations rather than a resume or portfolio grid.

## Colors

The palette is intentionally small. One warm accent against a dark neutral foundation.

- **Background (#0d0f0d):** Deep charcoal, not pure black. Provides warmth and prevents harsh contrast.
- **Text Primary (#f3eee5):** Warm off-white for headlines and key copy.
- **Text Secondary (#cfc5b7):** Muted warm gray for body text and descriptions.
- **Text Muted (#897e70):** Dimmer gray for metadata, indices, and inactive states.
- **Accent (#d5a15f):** Warm muted gold — the single emotional color. Used sparingly for the name initial, note borders, interactive states, and the rotating portrait ring.
- **Accent Hot (#f4cb88):** Brighter gold for hover/focus states and the bright side of the portrait ring.
- **Green (#9ccf92):** Status dot indicator — the only non-gold color, used minimally.

## Typography

Three typefaces create hierarchy through contrast:

- **Playfair Display (serif)** for the display name. Large, tight leading, weight 600. The serif adds editorial gravitas.
- **Outfit (sans-serif)** for body copy, headings, and buttons. Clean, geometric, readable at all sizes.
- **IBM Plex Mono (monospace)** for labels, tags, telemetry, and note metadata. Caps with wide tracking gives everything a technical, indexed feel.

The display name "B." is colored with the accent gold for a subtle visual anchor.

## Layout

The page uses a two-column hero split at desktop:

- **Left (identity):** Name, eyebrow label (Cloud / Lab / Home), position/tagline text, primary action buttons (Email, GitHub, LinkedIn).
- **Right (ops-panel):** Portrait framed with route lines and node labels (Cloud, HPC, Home) suggesting a network topology diagram. Telemetry rows below (Base, Role, Stack).

Below the hero, a full-width **field notes** section replaces the traditional card grid:
- **Header:** "Field notes" label + "Not a resume. Just the stuff I keep coming back to."
- **Four note rows** with numbered indexes, two-column layout (index+title left, body right):
  - 01 Work — Linux, storage, shared services, reliability
  - 02 Home — reverse proxies, tunnels, dashboards, media
  - 03 AI/agents — local models, tool use, coding assistants
  - 04 Signals — focus tags as pill-shaped labels

Footer is split: status dot + "Built by me. Hosted at home." on the left, secondary links (X, Steam) on the right.

## Depth Layers

1. **Grid overlay** — fixed-position, faint gold-tinted structural lines with a radial mask that fades toward the edges.
2. **Noise texture** — 3.5% opacity SVG fractal noise overlay for film-grain texture.
3. **Radial lighting** — two radial gradients (warm gold at 78%/18% and warm brown at 16%/78%) creating ambient depth.
4. **Vignette** — not explicit, achieved via the gradient background composition.

## Motion

- **Portrait ring** — a conic-gradient ring on a `::before` pseudo-element sweeps gold arcs around the portrait border (10s linear loop). Uses CSS `@property --ring-angle` for GPU-friendly angle animation.
- **Route lines** — three subtle pulse animations on the portrait-map route lines (5s staggered).
- **Button hover** — lift 2px with border brightening and background shift.
- **All animations** respect `prefers-reduced-motion` and disable cleanly.

## Components

### Portrait Ring
The rotating gold border around the avatar photo. Implemented as a `::before` pseudo-element with:
- Conic gradient (gold at 215deg → transparent at 18% → transparent at 76% → gold at 100%)
- `animation: ring-spin 10s linear infinite` animating the `--ring-angle` custom property
- `inset: -7px` and `border-radius: 35px` to sit outside the portrait padding
- `z-index: -1` so it sits behind the image but above the portrait background

### Note Rows
Journal-style entries with:
- Left accent border (1px solid var(--accent-dim))
- Top hairline (1px solid var(--line-soft))
- Subtle gold gradient background (4% opacity at left edge, fades to transparent)
- Two-column grid: narrow label column + wide body column
- Numbered index in monospace + h2 title stacked vertically in the label column
- Body text + metadata tags in the body column

### Focus Tags
Pill-shaped labels for skills/interests in the Signals note. Monospace, uppercase, gold border, dark background. Tight spacing in a flex-wrap row.

### Action Buttons
Email, GitHub, and LinkedIn buttons in the hero. Gold-accented primary for Email, standard for the rest. Inline SVG icons, lift on hover.

### Footer
Split layout: status indicator + tagline left, X and Steam links right. Monospace, muted, small.

## Do's and Don'ts

**Do:**
- Keep the color palette small. Gold is the only color; everything else is a shade of gray or green (status dot).
- Use Playfair Display only for the display name. Everything else stays sans or mono.
- Let the grid be visible but quiet — structural, not decorative.
- Animate on interaction (hover, portrait ring) rather than scroll.
- Respect `prefers-reduced-motion`.
- Keep copy concise and personal — field notes, not resume bullet points.

**Don't:**
- Add more colors. No blue links, no green indicators beyond the status dot.
- Use glassmorphism or backdrop blur. Depth comes from actual layered elements.
- Make the grid dominant. If lines compete with content, they're too bright.
- Add scroll-triggered reveals or typing effects. The page should feel still until interacted with.
- Use pure black (#000) or pure white (#fff).
