---
version: alpha
name: Dennis B.
description: Personal landing page for Dennis B., an infrastructure engineer and homelab operator. Dark editorial aesthetic with warm gold accents on a deep charcoal foundation.
colors:
  background: "#121212"
  text-primary: "#f0ece6"
  text-secondary: "#c4bdb4"
  text-muted: "#8a827a"
  accent: "#d4a574"
  accent-dim: "#a07850"
  accent-glow: "rgba(212, 165, 116, 0.15)"
  grid-line: "rgba(212, 165, 116, 0.08)"
  grid-strong: "rgba(212, 165, 116, 0.16)"
  border: "rgba(212, 165, 116, 0.12)"
  vignette: "rgba(0, 0, 0, 0.35)"
  orb-1: "rgba(212, 165, 116, 0.10)"
  orb-2: "rgba(180, 130, 90, 0.08)"
  orb-3: "rgba(220, 180, 130, 0.06)"
  on-accent: "#121212"
typography:
  display:
    fontFamily: "Playfair Display, Georgia, serif"
    fontSize: "clamp(4.5rem, 11vw, 11rem)"
    fontWeight: 300
    lineHeight: 0.9
    letterSpacing: "-0.02em"
  body:
    fontFamily: "Outfit, system-ui, sans-serif"
    fontSize: "1.125rem"
    fontWeight: 300
    lineHeight: 1.75
    letterSpacing: "0"
  label-caps:
    fontFamily: "Outfit, system-ui, sans-serif"
    fontSize: "0.75rem"
    fontWeight: 500
    lineHeight: 1.2
    letterSpacing: "0.2em"
    fontFeature: "c2sc"
  index:
    fontFamily: "Outfit, system-ui, sans-serif"
    fontSize: "0.9rem"
    fontWeight: 400
    lineHeight: 1.4
    letterSpacing: "0.15em"
  role:
    fontFamily: "Outfit, system-ui, sans-serif"
    fontSize: "1.125rem"
    fontWeight: 300
    lineHeight: 1.4
    letterSpacing: "0.02em"
  location:
    fontFamily: "Outfit, system-ui, sans-serif"
    fontSize: "0.975rem"
    fontWeight: 300
    lineHeight: 1.4
    letterSpacing: "0.1em"
    fontFeature: "c2sc"
  tag:
    fontFamily: "Outfit, system-ui, sans-serif"
    fontSize: "0.825rem"
    fontWeight: 500
    lineHeight: 1.2
    letterSpacing: "0.08em"
    fontFeature: "c2sc"
  link:
    fontFamily: "Outfit, system-ui, sans-serif"
    fontSize: "0.975rem"
    fontWeight: 400
    lineHeight: 1.2
    letterSpacing: "0"
  footer:
    fontFamily: "Outfit, system-ui, sans-serif"
    fontSize: "0.75rem"
    fontWeight: 300
    lineHeight: 1.4
    letterSpacing: "0.1em"
    fontFeature: "c2sc"
rounded:
  pill: "100px"
  circle: "50%"
  dot: "50%"
spacing:
  content-x: "8.333vw"
  content-y: "4rem"
  content-y-bottom: "3rem"
  hero-gap: "4rem"
  body-gap: "6rem"
  block-gap: "2.5rem"
  tag-gap: "0.625rem"
  link-gap: "0.625rem"
easing:
  default: "cubic-bezier(0.22, 1, 0.36, 1)"
components:
  focus-tag:
    backgroundColor: "rgba(212, 165, 116, 0.03)"
    textColor: "{colors.accent-dim}"
    borderColor: "{colors.border}"
    rounded: "{rounded.pill}"
    padding: "0.5rem 1rem"
    border: "1px solid {colors.border}"
  focus-tag-hover:
    backgroundColor: "rgba(212, 165, 116, 0.08)"
    textColor: "{colors.accent}"
    borderColor: "{colors.accent}"
    transform: "translateY(-2px)"
    boxShadow: "0 4px 16px rgba(212, 165, 116, 0.08)"
  social-link:
    backgroundColor: "rgba(212, 165, 116, 0.02)"
    textColor: "{colors.text-secondary}"
    borderColor: "{colors.border}"
    rounded: "{rounded.pill}"
    padding: "0.7rem 0.6rem"
    border: "1px solid {colors.border}"
  social-link-hover:
    backgroundColor: "rgba(212, 165, 116, 0.06)"
    textColor: "{colors.accent}"
    borderColor: "{colors.accent}"
    transform: "translateY(-2px)"
    boxShadow: "0 6px 20px rgba(212, 165, 116, 0.10)"
  avatar:
    borderColor: "rgba(212, 165, 116, 0.25)"
    border: "2px solid rgba(212, 165, 116, 0.25)"
    boxShadow: "0 20px 60px rgba(0, 0, 0, 0.5)"
    rounded: "{rounded.circle}"
---

## Overview

A dark editorial portfolio page for an infrastructure engineer. The aesthetic blends technical precision with warm human touches — structured grid systems, serif/sans-serif contrast, and restrained gold accents against a near-black canvas. The goal is to feel like a premium technical document that happens to be alive: subtle motion, depth layers, and interactive feedback without noise.

The personality is calm, capable, and quietly confident. No glassmorphism, no gradients as decoration, no flat minimalism. Depth comes from actual layered elements (noise, vignette, aurora orbs) rather than drop shadows alone.

## Colors

The palette is intentionally small. One warm accent against a dark neutral foundation.

- **Background (#121212):** Deep charcoal, not pure black. Provides warmth and prevents the harsh contrast of #000.
- **Text Primary (#f0ece6):** Warm off-white for body copy and headlines. Softer than pure white.
- **Text Secondary (#c4bdb4):** Muted warm gray for supporting text and descriptions.
- **Text Muted (#8a827a):** Dimmer gray for metadata, indices, and inactive states.
- **Accent (#d4a574):** Warm muted gold — the single emotional color. Used sparingly for the name initial, labels, interactive borders, and ambient glows.
- **Accent Dim (#a07850):** A darker, more subdued gold for secondary accents (pipes, cursors, footer dots).
- **Grid Lines (rgba 8-16%):** Very faint gold-tinted lines that structure the space without dominating it.

## Typography

Two typefaces create hierarchy through contrast:

- **Playfair Display (serif)** for the display name. Large, light weight, tight leading. The serif adds gravitas and editorial texture.
- **Outfit (sans-serif)** for everything else. Clean, geometric, readable at small sizes. Used for body, labels, tags, and links.

Label text uses small caps (`font-feature-settings: c2sc`) with wide tracking (`0.2em`). This gives section headers a technical, indexed feel.

The display name uses a shimmer gradient animation that sweeps a lighter gold (`#e8c9a0`) across the text. This is the one allowed moment of flash — everything else stays static or subtly reactive.

## Layout

The page uses a **12-column mental grid** expressed through faint vertical lines at 8.333%, 25%, 50%, 75%, and 91.666%. Horizontal lines at 33.333% and 66.666% divide the vertical space. Grid intersection points are marked with tiny gold dots.

Content sits in a single centered column with generous side padding (`8.333vw`). The layout is two-column at desktop:
- **Hero:** 1.2fr left (identity) + auto right (avatar)
- **Body:** 1fr + 1fr (about/focus left, homelab/links right)
- **Footer:** Full width, left-aligned with a status dot

The avatar breaks the grid slightly — it sits in the upper right, creating asymmetry and visual interest.

## Elevation & Depth

Depth is achieved through layered atmospheric effects, not shadows:

1. **Aurora Orbs (z-index 0):** Three large blurred circles in warm gold tones, slowly drifting. They provide ambient color and prevent the background from feeling dead.
2. **Grid Lines (z-index 0):** Faint structural lines and intersection dots.
3. **Noise Overlay (z-index 1):** 3% opacity SVG fractal noise. Adds film grain texture that makes digital flatness disappear.
4. **Spotlight (z-index 1):** Mouse-tracking radial gradient with warm gold at very low opacity (7%). Follows the cursor on desktop.
5. **Vignette (z-index 1):** Radial darkening at the edges. Draws the eye inward.
6. **Helix Canvas (z-index 3):** A subtle animated DNA helix rendered in Canvas 2D. Gold dots on sine waves, depth-based opacity. Positioned behind the content but in front of the grid.
7. **Content Layer (z-index 2):** All text and interactive elements. Sits above everything except the helix.

Corner brackets (top-left and bottom-right) in faint gold reinforce the technical drafting aesthetic.

## Shapes

- **Pill shapes (border-radius: 100px):** Used for focus tags and social link buttons. Creates a soft, button-like feel without harsh corners.
- **Circles:** Avatar image, pulse dots, status indicators, aurora orbs.
- **Lines:** Section label underlines (24px wide, 1px tall, gold at 40% opacity), grid lines, borders.
- **Organic:** The helix is the only non-geometric element — a flowing sine wave that softens the rigid structure.

## Components

### Focus Tags
Small pill labels for skills/interests. Default state has a faint gold border and near-transparent background. On hover, the border brightens, the tag lifts 2px, and a soft shadow appears. The transition uses the custom easing curve.

### Social Links
Icon + text buttons arranged in a centered 3+2 grid. Same pill shape as tags but larger. Hover adds a radial gradient highlight from the top center, creating a subtle "lit from above" effect.

### Avatar
Circular photo with a thin gold border and deep drop shadow. Two ambient effects surround it:
- **Rotating ring:** A conic gradient that slowly spins, creating a halo of gold light.
- **Pulsing glow:** A radial gradient that breathes in and out, suggesting active presence.

### Footer
Left-aligned with a small pulsing gold dot as a status indicator. The text is tiny, uppercase, tracked wide — almost like a hardware serial number.

## Do's and Don'ts

**Do:**
- Keep the color palette small. The only "color" is gold; everything else is a shade of gray.
- Use the serif font only for the display name. Everywhere else stays sans-serif.
- Let the grid be visible but quiet. It should feel structural, not decorative.
- Animate on interaction (hover, mouse move) rather than on load. Avoid scroll-triggered animations.
- Respect `prefers-reduced-motion`. All animations should disable cleanly.

**Don't:**
- Add more colors. No blue links, no green status indicators, no red alerts.
- Use glassmorphism or backdrop blur. The depth comes from actual layered elements.
- Make the grid dominant. If the lines compete with the content, they're too bright.
- Add scroll-triggered reveal animations or typing effects. The page should feel still until interacted with.
- Use pure black (#000) or pure white (#fff). The warmth of the off-shades is intentional.
