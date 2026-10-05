# Tokey — locked brand decisions

Approved by the user on 2026-10-03 and 2026-10-04, relayed by the coordinating
brand task.

Product: **Tokey**. One benchmark execution: **Tokey Run**.

Sharing signature (2026-10-04): user wants a recurring rabbit emoji paired
with **#Tokey** in every generated share caption, with occasional other emojis
allowed. Default rendering: **🐇 #Tokey**. Treat this as a recognizable social
signature, not a statement of registered trademark status. Vary caption prose
while keeping this signature consistent; exclude it and mandatory disclosures
from near-duplicate checks. Other emojis are supplementary, not replacements.
This social-caption use does not replace or modify the locked ASCII mascot.
The caption generator is still a design, not implemented functionality.

The name primarily derives from “token,” with secondary rabbit inspiration
from Korean “tokki.” Do not claim “Tokey” literally means rabbit in Korean.

The official mascot is exactly these three ASCII lines; preserve characters
and the leading space byte-for-byte. Canonical source: assets/tokey-mascot.txt.

```text
 (\_/)
(='.'=)
(")_(")
```

Do not substitute Unicode glyphs or add a coin/token to the canonical mascot.
Do not alter either source-text asset to encode colors or animation frames.
UI surfaces may render the unchanged rabbit at 70% horizontal scale to make it
visually slimmer beside the wordmark. Use a 4px optical gap so the rabbit and
TOKEY read as one combined logo. Keep both choices as display-only treatments.

Latest user direction (2026-10-05): incorporate the exact mascot and wordmark
into the UI-first simulated prototype. Render the unchanged text with preserved
whitespace and monospaced glyphs. Use the fixed Cyber Night palette below and
a single 0.20-second left-to-right diagonal glint followed by a one-second clean
idle pause. The resting artwork uses exact attachment-sampled window-highlight
green `#3bfb1b`. The separate moving overlay transitions through ion blue
`#168fe8`, electric cyan `#30cfff`, and pale green `#abffbf` around a narrow
0.5%-wide pure-white `#ffffff` core at dead center. Keep the approved 22% total
band width. Park that
overlay fully outside the glyphs during every idle gap so no glint remains on
the Y or rabbit edge. Reduced-motion and benchmark-running states show the clean
solid-green base with no overlay. The animation is a surface treatment, not a source-
asset change. The installed measurement app remains unchanged.
Its waveform icon is a utility icon, not a replacement mascot.

The exact approved prototype implementation is preserved in
[`docs/prototypes/tokey-cockpit.html`](prototypes/tokey-cockpit.html). It is the
reference for the glint gradient, single-pass keyframes, clean idle interval,
reduced-motion behavior and 70% rabbit display width.

### Fixed Cyber Night product palette

- deepest background `#05090d`
- panel `#0a1318`
- technical edge `#18323d`
- primary text `#c9d8dc`
- muted text `#71848b`
- sampled window-highlight and artwork green `#3bfb1b`
- Netrunner cyan `#55ead4`
- electric blue `#3fc2e0`
- deep teal `#0b6974`

Keep the product identity somber, nighttime, cyberpunk and dystopian. Use the
sampled window-highlight green for the mascot and wordmark base, primary action,
metric/progress bars and sort arrows. Keep device selectors darker. Use the
electric emerald shine with a thicker cyan-white hot core; preserve the
white-hot center with a cyan-green cast and avoid yellow/lime casts.
These colors are intentionally hard-coded product colors rather than
dynamically following the desktop theme.

The official README wordmark is **ANSI-Compact**, generated from the literal
uppercase text `TOKEY`. Preserve these three lines byte-for-byte. Canonical
source: assets/tokey-wordmark.txt.

```text
██████ ▄████▄ ██ ▄█▀ ██████ ██  ██
  ██   ██  ██ ████   ██▄▄    ▀██▀
  ██   ▀████▀ ██ ▀█▄ ██▄▄▄▄   ██
```

The written product name remains **Tokey**; uppercase **TOKEY** is the wordmark.
The source artwork remains colorless. Product surfaces apply the fixed palette
and approved glint without changing the canonical text.

The existing LLM-Benchmark folder, Python module, data directory, desktop ID
and compatibility launcher remain stable during the release candidate. These
technical names are not alternate product branding.
