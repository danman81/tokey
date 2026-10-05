# Netrunner visual direction and window layouts

## 2026-10-04 current direction: fixed Cyber Night palette

This supersedes the adaptive and pink/crimson-heavy color proposal below. The
product uses hard-coded colors: background `#05090d`, panel `#0a1318`, edge
`#18323d`, text `#c9d8dc`, muted `#71848b`, green `#39ff14`, cyan `#55ead4`,
blue `#3fc2e0` and deep teal `#0b6974`. Avoid pink/magenta in the primary
identity. The atmosphere is somber nighttime cyberpunk/dystopian; green, cyan
and blue appear as restrained gleams. The rabbit and TOKEY wordmark use the
same diagonal glint. The exact ASCII source assets stay colorless. Respect
reduced motion and disable ornamental animation while a benchmark is measured.
The sections below remain historical evidence for where the colors originated.

User direction and live inspection: 2026-10-03. The proposal below has now
informed Tokey's native GTK4 implementation. See VALIDATION.md for actual
wide/narrow screenshots; proposed interactions not listed there remain future work.

## Intended character

The user likes Omarchy and their current neon theme, and wants this application
very close to that appearance and its colors, with a more stylized cyberpunk /
Blade Runner atmosphere. Treat the current desktop as the visual reference.
Do not substitute a generic blue dashboard or require a full-screen canvas.

Proposed styling: crisp neon linework, fine technical divisions, selected
angular corners, deep red-black layers, and restrained glow on focus or key
data. Use expressive headings and legible measurement typography. Exact font,
geometry, intensity and layouts require visual review. The cinematic influence
is a mood and original visual treatment, not a requirement for film assets.

## Verified local palette

`omarchy theme current` reports Netrunner. Values below come from
`~/.local/state/omarchy/current/theme/colors.toml`, not a screenshot estimate.

| Theme role | Exact color | Proposed use |
|---|---|---|
| background | #0f0508 | Main red-black surface |
| dark_background | #0a0305 | Recessed chart / navigation areas |
| darker_background | #060102 | Deepest surface |
| lighter_background | #1d0a0f | Cards / panels |
| accent / foreground | #c5003c | Crimson identity and selected details |
| light_foreground | #e4356a | Brighter pink-red labels, subject to contrast checks |
| bright_foreground | #ff4d70 | High emphasis |
| muted | #880425 | Decorative secondary lines, not automatically body text |
| yellow | #f3e600 | Sparse emphasis |
| orange | #eb7a00 | Alternate highlight |
| cyan | #55ead4 | Optional secondary chart series with labels |

The user's `~/.config/omarchy/shell.toml` also explicitly overrides bar text to
`#e4356a`. Preserve this distinction between the base palette and user overlay
when making a close visual match. Per-app roles still require contrast testing;
a literal dark-red foreground may not be readable at small sizes.

The desktop also has a previously recorded custom neon-green active border;
it is not one of the base crimson theme roles. Do not infer that all app
borders should be green. Exact window decoration versus internal panel chrome
should be reviewed together.

## Superseded theme integration proposal

Use the supported Omarchy color/template mechanism after checking compatibility
with the chosen toolkit. The app owns its layout, chart design and geometry;
theme tokens supply the colors. For the current theme, closely preserve the
Netrunner appearance. If the user switches to another dark theme, adapt color
roles while retaining the same visual structure. A light or missing theme must
not silently produce white surfaces; retain a dark fallback.

Following the Omarchy skill, use supported user configuration or read-only
theme consumption; do not modify packaged themes or the user's desktop.
Sources: https://omarchy.org/manual/themes/ and
https://github.com/omacom/omarchy/blob/quattro/docs/theming.md . Both opened
successfully in this turn; this supersedes the earlier failed manual URL.
Theme following is a design proposal, not an implemented integration.

## Responsive window proposal

Hyprland reports the active display at 1920 × 1080, scale 1.5, with a
26-logical-pixel top reservation. This gives approximately 1280 × 694 logical
pixels before window decorations and gaps. Do not design a mandatory 1080p
logical dashboard or assume half the physical resolution is usable app width.

- Centered floating concept: begin around 1000 × 620 logical pixels and
  constrain it to the actual work area. A candidate for review, not an enforced
  default. Fit must account for borders, decorations and gaps.
- Side-tiled concept: expect less than 640 logical pixels on this display.
  Collapse navigation, stack metrics, show a primary chart and move comparisons
  into tabs. Preserve Run/Stop and the current test state.
- Expanded concept: use added space for side-by-side comparisons and history.
  Full-screen remains optional.

These are responsive presentations of one application. Resize by reflowing
content, not by shrinking text or cropping controls. Let Hyprland own window
placement and native tiling actions; no custom snapping system is needed.
Choose an opening behavior only after reviewing centered and tiled concepts.

## Performance and validation

Keep glow and decorative motion controlled during measured intervals. Verify
the frontend's overhead, display-scale readability, dark initial frame and
all major states. Judge colors through the user's actual blue-filtered setup;
retain text/shape cues alongside chart colors. No mockup or running UI has yet
been shown, so this document establishes direction, not visual acceptance.
