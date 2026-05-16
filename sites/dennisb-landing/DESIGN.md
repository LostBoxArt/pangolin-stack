---
version: "2.0"
name: Dennis B.
description: >
  Personal landing page for Dennis B., an infrastructure engineer and homelab operator.
  Dark editorial aesthetic with a warm gold accent on a deep charcoal foundation.
  Field-notes layout with journal-style entries. Personality: calm, capable, quietly confident.
colors:
  # ── Canvas ──
  bg: "#0d0f0d"
  bg-elevated: "#131512"
  bg-surface: "#181a16"
  # ── Text ──
  text-primary: "#f3eee5"
  text-secondary: "#cfc5b7"
  text-muted: "#897e70"
  text-on-accent: "#0d0f0d"
  # ── Accent (warm gold — the single emotional color) ──
  accent: "#d5a15f"
  accent-hover: "#e0b472"
  accent-hot: "#f4cb88"
  accent-press: "#b88642"
  accent-dim: "#765333"
  accent-subtle: "rgba(213, 161, 95, 0.075)"
  # ── Borders & lines ──
  border: "rgba(213, 161, 95, 0.18)"
  border-soft: "rgba(213, 161, 95, 0.085)"
  border-accent: "rgba(213, 161, 95, 0.44)"
  # ── Semantic ──
  green: "#9ccf92"
  green-glow: "rgba(156, 207, 146, 0.55)"
  # ── Focus ──
  focus-ring: "#f4cb88"
  # ── Overlays ──
  overlay-shadow: "rgba(0, 0, 0, 0.5)"
  overlay-panel: "rgba(19, 18, 14, 0.68)"

typography:
  # ── Display (serif — the name, the brand mark) ──
  display-hero:
    fontFamily: "Playfair Display, Georgia, serif"
    fontSize: "clamp(6rem, 15vw, 13.4rem)"
    fontWeight: 600
    lineHeight: 0.78
    letterSpacing: 0
    note: "Only used once: the name. Never for UI."
  # ── Body (sans-serif — the workhorse) ──
  body-lead:
    fontFamily: "Outfit, system-ui, sans-serif"
    fontSize: "clamp(1.2rem, 2.1vw, 1.62rem)"
    fontWeight: 300
    lineHeight: 1.55
    letterSpacing: "-0.01em"
  body:
    fontFamily: "Outfit, system-ui, sans-serif"
    fontSize: "1.08rem"
    fontWeight: 300
    lineHeight: 1.7
    letterSpacing: 0
  body-sm:
    fontFamily: "Outfit, system-ui, sans-serif"
    fontSize: "0.95rem"
    fontWeight: 300
    lineHeight: 1.6
    letterSpacing: 0
  heading-section:
    fontFamily: "Outfit, system-ui, sans-serif"
    fontSize: "clamp(1.25rem, 2vw, 1.7rem)"
    fontWeight: 600
    lineHeight: 1.08
    letterSpacing: "-0.02em"
  # ── Labels (monospace — the system voice) ──
  label-caps:
    fontFamily: "IBM Plex Mono, ui-monospace, monospace"
    fontSize: "0.78rem"
    fontWeight: 700
    lineHeight: 1.3
    letterSpacing: "0.13em"
    textTransform: uppercase
  label-caps-sm:
    fontFamily: "IBM Plex Mono, ui-monospace, monospace"
    fontSize: "0.72rem"
    fontWeight: 700
    lineHeight: 1.3
    letterSpacing: "0.13em"
    textTransform: uppercase
  meta-caps:
    fontFamily: "IBM Plex Mono, ui-monospace, monospace"
    fontSize: "0.68rem"
    fontWeight: 700
    lineHeight: 1.5
    letterSpacing: "0.08em"
    textTransform: uppercase
  tag-caps:
    fontFamily: "IBM Plex Mono, ui-monospace, monospace"
    fontSize: "0.68rem"
    fontWeight: 700
    lineHeight: 1.3
    letterSpacing: "0.08em"
    textTransform: uppercase
  node-caps:
    fontFamily: "IBM Plex Mono, ui-monospace, monospace"
    fontSize: "0.62rem"
    fontWeight: 700
    lineHeight: 1.3
    letterSpacing: "0.13em"
    textTransform: uppercase
  # ── Data ──
  telemetry-label:
    fontFamily: "IBM Plex Mono, ui-monospace, monospace"
    fontSize: "0.65rem"
    fontWeight: 700
    lineHeight: 1.3
    letterSpacing: "0.13em"
    textTransform: uppercase
  telemetry-value:
    fontFamily: "Outfit, system-ui, sans-serif"
    fontSize: "0.95rem"
    fontWeight: 400
    lineHeight: 1.4
    letterSpacing: 0
  # ── Buttons ──
  button:
    fontFamily: "Outfit, system-ui, sans-serif"
    fontSize: "1rem"
    fontWeight: 600
    lineHeight: 1.0
    letterSpacing: 0

rounded:
  none: 0px
  sm: 4px
  md: 10px
  lg: 22px
  xl: 28px
  portrait-outer: 28px
  portrait-inner: 22px
  pill: 999px

spacing:
  xs: 4px
  sm: 8px
  md: 12px
  lg: 16px
  xl: 20px
  2xl: 24px
  3xl: 32px
  4xl: 48px
  5xl: 64px
  content-x: "calc(100% - 4rem)"
  content-max: 1240px
  hero-gap: "clamp(2.5rem, 6vw, 5.5rem)"

easing:
  default: "cubic-bezier(0.22, 1, 0.36, 1)"
  micro: "cubic-bezier(0.22, 1, 0.36, 1)"
  entrance: "cubic-bezier(0.22, 1, 0.36, 1)"

duration:
  micro: 150ms
  standard: 220ms
  slow: 400ms
  ring-spin: 10s
  route-pulse: 5s

opacity:
  noise: 0.035
  grid-line: 1.0
  grid-line-color: "rgba(213, 161, 95, 0.075)"
  grid-strong: "rgba(213, 161, 95, 0.17)"

components:
  # ── Portrait ring (rotating gold border) ──
  portrait-ring:
    description: "Animated conic-gradient border around the avatar photo."
    type: "pseudo-element (::before)"
    background: "conic-gradient(from 215deg, var(--accent), transparent 18%, transparent 76%, var(--accent-hot))"
    inset: -7px
    border-radius: 35px
    z-index: -1
    animation: "ring-spin 10s linear infinite"
    note: "Avoid @property --ring-angle (Chrome-only). Use a rotating pseudo-element or two overlapping conic-gradients with clip-path for cross-browser compatibility."

  # ── Note rows (field journal entries) ──
  note-row:
    description: "Journal-style content blocks with left gold accent and subtle gradient wash."
    borderLeft: "1px solid var(--accent-dim)"
    borderTop: "1px solid var(--border-soft)"
    background: "linear-gradient(90deg, rgba(213, 161, 95, 0.04), transparent 32%)"
    padding: "1.05rem 1.15rem 1.05rem 1.35rem"
    layout: "two-column (index+title left, body right)"
    accent-marks: "::before and ::after pseudo-elements create gold hairline marks at top-left and bottom-left corners"

  # ── Focus tags (pill labels for skills) ──
  focus-tag:
    description: "Pill-shaped labels for the Signals section."
    border: "1px solid rgba(213, 161, 95, 0.27)"
    background: "rgba(213, 161, 95, 0.045)"
    textColor: "var(--accent-hot)"
    typography: "tag-caps"
    rounded: "pill"
    padding: "0.44rem 0.72rem"

  # ── Buttons ──
  button-default:
    description: "Standard secondary button."
    background: "rgba(13, 15, 13, 0.7)"
    textColor: "var(--text-secondary)"
    border: "1px solid var(--border)"
    rounded: "md"
    padding: "0 1.1rem"
    minHeight: "2.75rem"
    hover:
      textColor: "var(--accent-hot)"
      borderColor: "rgba(244, 203, 136, 0.54)"
      background: "var(--accent-subtle)"
      transform: "translateY(-2px)"
    focus:
      outline: "2px solid var(--focus-ring)"
      outlineOffset: "4px"
    active:
      transform: "translateY(0)"
      background: "rgba(213, 161, 95, 0.12)"

  button-primary:
    description: "Primary CTA (Email). Stronger gold treatment."
    extends: "button-default"
    textColor: "var(--text-primary)"
    borderColor: "rgba(213, 161, 95, 0.58)"
    background: "linear-gradient(180deg, rgba(213, 161, 95, 0.24), rgba(213, 161, 95, 0.08)), rgba(13, 15, 13, 0.78)"
    hover:
      borderColor: "var(--accent-hot)"
      background: "linear-gradient(180deg, rgba(213, 161, 95, 0.35), rgba(213, 161, 95, 0.14)), rgba(13, 15, 13, 0.85)"

  # ── Ops panel (portrait + telemetry card) ──
  ops-panel:
    description: "Infrastructure profile card with topology-map styling."
    border: "1px solid var(--border)"
    background: "linear-gradient(145deg, rgba(243, 238, 229, 0.05), transparent 38%), var(--overlay-panel)"
    boxShadow: "0 26px 80px var(--overlay-shadow)"
    padding: "1.25rem"
    corner-accents: "::before and ::after pseudo-elements draw gold corner brackets at top-left and bottom-right"

  # ── Portrait map ──
  portrait-map:
    description: "Portrait framed with route lines and node labels suggesting a network topology."
    minHeight: 390px
    bg-diamond: "::before draws a rotated square border"
    bg-ring: "::after draws a dashed circle"
    responsive-minHeight: "310px (tablet), 225px (mobile)"

  # ── Telemetry rows ──
  telemetry-row:
    description: "Key-value pairs below the portrait."
    layout: "two-column grid (5rem label + 1fr value)"
    divider: "1px solid var(--border-soft) between rows"
    label: "telemetry-label typography, accent-dim color"
    value: "telemetry-value typography, text-secondary color"

  # ── Status light ──
  status-light:
    description: "Green glowing dot indicating operational status."
    size: 7px
    background: "var(--green)"
    boxShadow: "0 0 18px var(--green-glow)"
    rounded: "50%"

  # ── Topbar nav ──
  nav-link:
    typography: "label-caps-sm"
    color: "var(--text-muted)"
    textDecoration: none
    hover:
      color: "var(--accent-hot)"

  # ── Footer ──
  footer:
    description: "Split layout: status + tagline left, secondary links right."
    borderTop: "1px solid var(--border)"
    typography: "meta-caps"
    color: "var(--text-muted)"

  # ── Route lines (animated connection lines on portrait map) ──
  route-line:
    description: "Subtle pulsing gold gradient lines across the portrait map."
    height: 1px
    background: "linear-gradient(90deg, transparent, var(--border-accent), transparent)"
    animation: "pulse-route 5s var(--ease) infinite"
    stagger: "1s delay between each of 3 routes"

---

## Overview

A single-page dark editorial portfolio for an infrastructure engineer. The aesthetic blends technical precision with warm human touches — structured grids, monospace labels, serif/sans-serif contrast, and restrained gold accents against a near-black canvas.

The personality is calm, capable, and quietly confident. No glassmorphism, no decorative gradients, no flat minimalism. Depth comes from actual layered elements (noise, vignette, subtle radial highlights, structural grid lines) rather than drop shadows alone.

The body content is presented as **field notes** — journal-style entries (Work, Home, AI/agents, Signals) that read like personal observations rather than a resume or portfolio grid.

## Design Principles

### 1. No gradients for elevation
Depth is communicated through background color shifts (bg → bg-elevated → bg-surface), 1px borders, and content density — never through gradient washes or blurred backdrops. This is the single most important constraint. **No glassmorphism. No backdrop-filter. No gradient overlays on cards.**

### 2. 1px borders, not shadows
Card separation uses hairline borders (`var(--border)` or `var(--border-soft)`). Box shadows are reserved for the ops-panel (the single "elevated" surface) and the portrait itself — never for content cards.

### 3. Small palette, single accent
Gold (`--accent`) is the only chromatic color. Everything else is a shade of near-black, warm gray, or the single green status indicator. No blue links, no red errors, no secondary accent colors. This constraint forces intentionality.

### 4. Mono uppercase as the system voice
All labels, navigation, metadata, tags, and structural text use IBM Plex Mono in uppercase with wide letter-spacing. This creates a "terminal / console" register that contrasts with the human body text.

### 5. Typographic contrast through weight, not size
The hero pairs a massive serif (Playfair Display, 13.4rem, weight 600) with thin-weight sans body (Outfit, weight 300). The contrast is extreme but intentional — gravitas vs. readability.

### 6. Flat solids, no decorative gradients
Following The Verge's lead: color is applied in solid blocks, not as washes. The only gradients in the system are functional (road-line fades, button depth, background atmosphere) — never purely decorative.

### 7. Atmospheric depth, not UI depth
The noise overlay, radial background glows, and structural grid lines create atmosphere without adding UI chrome. These are fixed, non-interactive layers.

## Colors

The palette is intentionally small: one warm accent against dark neutrals.

**Canvas layers** (darkest → lightest):
- `--bg` (#0d0f0d) — Deep charcoal page background. Not pure black.
- `--bg-elevated` (#131512) — Slightly lifted surface for cards and panels.
- `--bg-surface` (#181a16) — Highest surface for interactive elements.

**Text hierarchy**:
- `--text-primary` (#f3eee5) — Headlines and key copy. Warm off-white.
- `--text-secondary` (#cfc5b7) — Body text and descriptions.
- `--text-muted` (#897e70) — Metadata, indices, inactive states.
- `--text-on-accent` (#0d0f0d) — Text on gold backgrounds (rare).

**Accent (warm gold)**:
- `--accent` (#d5a15f) — The single emotional color. Used for the "B." initial, note borders, interactive states, portrait ring.
- `--accent-hover` (#e0b472) — Hover state brightening.
- `--accent-hot` (#f4cb88) — Brightest gold: hover/focus text, node labels, the bright edge of the portrait ring.
- `--accent-press` (#b88642) — Pressed/active state (darker gold).
- `--accent-dim` (#765333) — Dim gold for note-row left borders, telemetry labels.
- `--accent-subtle` (rgba(213,161,95,0.075)) — Barely-visible gold wash for button hover backgrounds.

**Borders**:
- `--border` (rgba(213,161,95,0.18)) — Standard card and panel borders.
- `--border-soft` (rgba(213,161,95,0.085)) — Subtle internal dividers, grid lines.
- `--border-accent` (rgba(213,161,95,0.44)) — Brighter borders for route lines, focus states.

**Semantic**:
- `--green` (#9ccf92) — Status dot. The only non-gold color.
- `--green-glow` (rgba(156,207,146,0.55)) — Glow behind the status dot.
- `--focus-ring` (#f4cb88) — Keyboard focus outline color.

**Overlays**:
- `--overlay-shadow` (rgba(0,0,0,0.5)) — Deep shadow for the ops panel and portrait.
- `--overlay-panel` (rgba(19,18,14,0.68)) — Semi-transparent panel background.

## Typography

### Font Families

Three typefaces create hierarchy through contrast:

1. **Playfair Display** (serif) — Used ONLY for the display name. The serif adds editorial gravitas. Never used for UI, headings, or body. If you see Playfair below `clamp(6rem, 15vw, 13.4rem)`, it's a bug.

2. **Outfit** (sans-serif) — The workhorse. Body text, headings, buttons, telemetry values. Clean geometric sans with excellent readability. Weights: 300 (body), 400 (telemetry values), 600 (headings, buttons).

3. **IBM Plex Mono** (monospace) — The system voice. All labels, navigation, metadata, tags, eyebrow text, and structural elements. Always uppercase with wide letter-spacing. Weights: 600–700.

### Type Scale

| Role | Font | Size | Weight | Line Height | Letter Spacing | Transform |
|---|---|---|---|---|---|---|
| Display Hero | Playfair Display | clamp(6rem, 15vw, 13.4rem) | 600 | 0.78 | 0 | none |
| Body Lead | Outfit | clamp(1.2rem, 2.1vw, 1.62rem) | 300 | 1.55 | -0.01em | none |
| Heading Section | Outfit | clamp(1.25rem, 2vw, 1.7rem) | 600 | 1.08 | -0.02em | none |
| Body | Outfit | 1.08rem | 300 | 1.7 | 0 | none |
| Body Small | Outfit | 0.95rem | 300 | 1.6 | 0 | none |
| Label Caps | IBM Plex Mono | 0.78rem | 700 | 1.3 | 0.13em | uppercase |
| Label Caps SM | IBM Plex Mono | 0.72rem | 700 | 1.3 | 0.13em | uppercase |
| Meta Caps | IBM Plex Mono | 0.68rem | 700 | 1.5 | 0.08em | uppercase |
| Tag Caps | IBM Plex Mono | 0.68rem | 700 | 1.3 | 0.08em | uppercase |
| Node Caps | IBM Plex Mono | 0.62rem | 700 | 1.3 | 0.13em | uppercase |
| Telemetry Label | IBM Plex Mono | 0.65rem | 700 | 1.3 | 0.13em | uppercase |
| Telemetry Value | Outfit | 0.95rem | 400 | 1.4 | 0 | none |
| Button | Outfit | 1rem | 600 | 1.0 | 0 | none |

### Principles

- **Playfair is always the hero, never the UI.** If Playfair appears anywhere other than the name, it's wrong.
- **Outfit carries the content.** All readable text uses Outfit at weight 300 for a light, airy feel that contrasts with the heavy serif display.
- **IBM Plex Mono is the uniform.** All labels use mono uppercase. No exceptions. This creates the "terminal" register.
- **Negative letter-spacing on display.** The body-lead uses `-0.01em` for editorial density. The section headings use `-0.02em`. These are small but visible — they tighten the text block.
- **Line heights tell you the role.** Tight (0.78–1.08) = display. Medium (1.3–1.55) = labels and lead body. Relaxed (1.7) = reading body.

## Layout

### Desktop (≥981px)

**Topbar**: Three-column grid — logo mark (left), status indicator (center), nav links (right).

**Hero**: Two-column grid (1.05fr identity / 0.75fr ops-panel).
- Left: Eyebrow label → Display name → Position text → Primary action buttons.
- Right: Portrait map (portrait with route lines + node labels + rotating ring) → Telemetry rows below.

**Field Notes**: Single-column section below hero.
- Header row: "Field notes" label + subtitle text.
- Four note rows with left gold accent border, numbered indices, and two-column internal layout.
- Final row (Signals) contains pill-shaped focus tags.

**Footer**: Flex row — status light + tagline (left), secondary links (right).

### Tablet (620px–980px)

Hero collapses to single column. Ops panel moves above identity. Portrait map shrinks. Telemetry remains visible.

### Mobile (≤619px)

Single column throughout. Telemetry hidden. Buttons stack full-width. Note rows collapse to single column. Footer stacks vertically.

## Depth Layers

Layered from back to front:

1. **Background gradients** — Two radial glows (warm gold at 78%/18%, warm brown at 16%/78%) plus a subtle diagonal gradient. Creates ambient depth on the canvas.

2. **Grid overlay** — Fixed-position structural grid lines (8.333vw × 33.333vh cells) with a radial mask that fades toward the edges. Gold-tinted, very faint.

3. **Noise texture** — 3.5% opacity SVG fractal noise overlay. Film-grain texture that sits above everything.

4. **Content** — All interactive and readable elements sit above these three layers via `z-index: 1` on the main container.

## Motion

**Enabled animations** (respects `prefers-reduced-motion`):
- **Portrait ring** — Conic-gradient border rotates continuously (10s linear loop). See component spec for cross-browser notes.
- **Route lines** — Three gradient lines pulse opacity (5s loop, staggered 1s delays).
- **Button hover** — Lift 2px with border brightening and background shift (220ms ease).
- **Button press** — Immediate drop back to baseline.
- **Nav hover** — Color transition to gold (150ms).

**Disabled** (intentionally absent):
- No scroll-triggered reveals
- No typing effects
- No entrance animations
- No parallax
- No hover effects on non-interactive elements

## Components

### Portrait Ring
The rotating gold border around the avatar photo. Implement via a `::before` pseudo-element on `.portrait`:
- Conic gradient with gold arcs (215deg start → transparent at 18% → transparent at 76% → gold at 100%)
- `inset: -7px` and `border-radius: 35px` to frame the portrait
- `z-index: -1` to sit behind the image
- Animation: rotate the entire pseudo-element via `transform: rotate()` keyframes, or use a clipped approach. **Avoid `@property --ring-angle`** (Chrome-only, breaks Firefox/Safari).

### Note Rows
Journal-style content entries with:
- Left accent border: `1px solid var(--accent-dim)`
- Top hairline: `1px solid var(--border-soft)`
- Subtle gold gradient background: `linear-gradient(90deg, rgba(213,161,95,0.04), transparent 32%)`
- Corner accent marks: `::before` (top-left) and `::after` (bottom-left) pseudo-elements draw 36px gold hairlines
- Two-column internal grid: narrow column (index + h2) + wide column (body + metadata)

### Focus Tags
Pill-shaped labels for skills/interests. Monospace uppercase, gold border, dark background. Displayed in a flex-wrap row with tight gap.

### Buttons
- **Default**: Translucent dark background, muted text, gold border. Hover lifts 2px, brightens border to `accent-hot`, adds subtle gold wash. Focus ring is 2px solid `--focus-ring`.
- **Primary**: Stronger gold gradient background, brighter border. Same hover/focus/active mechanics but with richer gold treatment.

### Ops Panel
The infrastructure profile card in the hero's right column:
- Gold corner bracket accents (::before top-left, ::after bottom-right)
- Linear gradient wash from light gold (top) to transparent
- Deep drop shadow for elevation (the only significant shadow in the system)
- Contains: portrait map → telemetry rows

### Portrait Map
The portrait area within the ops panel:
- Rotated square border (::before, `transform: rotate(45deg)`, 1px `--border`)
- Dashed circle ring (::after, `border: 1px dashed`, 50% radius)
- Three animated route lines crossing at different angles
- Three node labels (Cloud, HPC, Home) positioned around the portrait
- Portrait itself: slightly rotated (-2deg), with the spinning gold ring

### Telemetry Rows
Key-value data below the portrait:
- Top border separates from portrait map
- Each row: 5rem label column + flexible value column
- Subtle bottom border between rows

### Status Light
- 7px green circle with glow (`box-shadow: 0 0 18px var(--green-glow)`)
- Used in topbar and footer

### Topbar Nav
- Mono uppercase links at 0.72rem
- Muted color → gold on hover/focus
- Flex row with responsive gap

### Footer
- Top border separator
- Split layout: status indicator + "Built by me. Hosted at home." left, X + Steam links right
- All text mono uppercase, muted color

## Do's and Don'ts

**Do:**
- Keep the color palette small. Gold is the only color; everything else is charcoal/gray/green.
- Use Playfair Display only for the display name. Everything else uses Outfit or IBM Plex Mono.
- Let the grid be visible but quiet — structural, not decorative.
- Use 1px borders for card separation, not shadows or gradients.
- Animate on interaction (hover, portrait ring) rather than on scroll.
- Respect `prefers-reduced-motion`.
- Keep copy concise and personal — field notes, not resume bullet points.
- Use mono uppercase for ALL labels, navigation, and metadata. No exceptions.
- Use :focus-visible with a visible outline for keyboard accessibility.

**Don't:**
- Add more colors. No blue links, no green indicators beyond the status dot.
- Use glassmorphism or backdrop-filter. Depth comes from actual layered elements.
- Use decorative gradients for elevation or card separation.
- Make the grid dominant. If lines compete with content, they're too bright.
- Add scroll-triggered reveals, typing effects, or entrance animations.
- Use pure black (#000) or pure white (#fff).
- Use `@property` CSS Houdini rules — they're Chrome-only and break Firefox/Safari.
- Add Playfair Display anywhere other than the name.
- Use box shadows on content cards — reserved for the ops panel only.
