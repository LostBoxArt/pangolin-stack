# Dennis B. — Cinematic Living Lab

A static personal site about HPC infrastructure, the home lab, and practical AI
experiments. The visual anchor is an illustrated workbench and rack, with a
small brass giraffe connecting it to the existing personal mark. The existing
portrait provides a real photograph of Dennis.

## Content

- Show the location as **Israel**, without a city.
- Use **Say Hello** for the contact link; use title case for action labels.
- Keep the main work, home lab, and AI content in the HTML. Chapter links are
  normal section anchors without JavaScript and select a chapter with it.
- Keep `#top`, `#world`, `#work`, `#home`, `#agents`, and `#field-notes` working.
- The scheduler example is an illustrative replay of the public HPC talk.
  It does not connect to a cluster or run commands.
- The hero is an illustration, not a photograph of a workplace or home setup.
- Show no uptime metric unless it comes from actual availability measurements.

## Visual system

The CSS is the source of truth for colors and spacing. The palette uses deep
forest charcoal, warm cream, muted green-gray, and copper/gold. Georgia is the
display face; the system sans-serif and monospace stacks cover text and labels.
There are no downloaded fonts, libraries, or build dependencies.

The desktop layout uses a full-width visual hero, three chapter links, a story
and example side by side, two notebook links, and a compact portrait footer.
At small widths the hero copy sits above the image and the content stacks.
Content stays visible without reveal effects. Interactive targets are at least
44 CSS pixels high, and keyboard focus is visible.

## Media and motion

The JPEG poster loads first. The 1536×864 H.264 clip is a 12-second seamless
camera move over the same illustration. Its MP4 metadata comes before its
video data so playback can begin without downloading the whole file.

Motion starts after the page load, only while the hero is visible. It pauses
when the page is hidden. Reduced-motion and data-saving preferences default
to a still image; explicit play remains available. The motion preference is
stored locally when storage is available. Storage failure is harmless.

A failed video leaves the poster intact and removes the unavailable control.
The example can pause and continue; reduced-motion users receive its full
result immediately. With JavaScript unavailable, all chapters and the complete
example remain readable and inactive controls stay hidden.

## Delivery

Only static HTML, CSS, JavaScript, images, and the MP4 are required. Asset
filenames include a SHA-256 content prefix; update the HTML references whenever
an asset changes. The existing Nginx static-file container is sufficient.
Editor APIs, mockup controls, QA fixtures, source artwork, and rendering tools
are not part of the public release.

The document includes its canonical URL, description, social sharing image,
favicon, and a same-origin Content Security Policy. No backend, analytics,
external font requests, or privileged service URLs are used.

## Verification

From the repository root:

```sh
python3 -m unittest discover -s tests -p test_landing.py -v
```

Expected result: four passing tests. They cover public copy and URLs, anchors
and accessibility references, local release assets, JavaScript syntax, and
required motion/focus styles.

For a release, additionally inspect 320, 390, 680, 768, 1024, 1440, and 1920
pixel widths; verify keyboard skip/navigation, motion pause and resume, chapter
deep links, and example pause/continue/replay. Check the no-JavaScript,
reduced-motion, storage-denied, and media-error paths. Before switching the
live HTML, stage the release, retain the previous site, and verify every asset.
After switching, verify the public HTML, MIME types, video range requests,
cache headers, and both desktop and mobile rendering.
