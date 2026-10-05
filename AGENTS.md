# Project guidance

Latest direction (2026-10-04): the user rejected 0.1.0rc1's single-model
experience. Strategy for the next version centers popular-model discovery and
actual performance comparisons on the installed machine. Agree the product
flow before another build. Prior test completion is not user acceptance.
See CURRENT-STATE.md and the updated PRODUCT-BRIEF.md; earlier implementation
phase descriptions below are historical.

Product name is Tokey; a benchmark execution is a Tokey Run. Preserve the
locked ASCII mascot exactly in assets/tokey-mascot.txt and docs/BRAND.md.
UI surfaces may render that unchanged mascot at 80% horizontal scale so it
appears slimmer beside the wordmark; do not encode the scaling into the asset.
Use a 4px optical gap between mascot and wordmark in the combined UI logo.
Preserve the approved ANSI-Compact TOKEY wordmark exactly in
assets/tokey-wordmark.txt and docs/BRAND.md. Use Tokey in prose and UI labels;
reserve uppercase TOKEY for the wordmark. Keep technical folder/module/data
IDs stable during this release candidate. Testing windows stay on desktop 4.

Read README.md, CURRENT-STATE.md and DECISIONS.md before substantive work.

Highest-priority user requirement: accurate results, no guessing. Measurement
validity takes precedence over appearance, convenience and scope. Only verified
measurements and transparently derived calculations may appear as benchmark
results. Missing data is unavailable; incomplete/invalid runs must be labeled.
Show uncertainty, preserve raw evidence, and validate the runner before any
comparative score. See docs/BENCHMARK-DESIGN.md.

The user requested a project for a commercial-grade “3DMark for LLMs” after
an exploratory discussion. This establishes product intent and a durable
workspace. On 2026-10-03 the user explicitly authorized implementation through
the full SDLC and a goal was created. Current phase is implementation and
release-candidate validation, superseding the earlier strategy-only phase. The user selected Omarchy
as the target platform and requires accurate, easy-to-use benchmarking with
a graphically beautiful dark interface. Learn from documented predecessor
weaknesses and verify the improvements. Price, license and broader hardware
coverage remain open. Read docs/DESIGN-REQUIREMENTS.md.

The fixed product palette is a somber Cyber Night treatment derived from the
user's desktop and reference capture: `#05090d`, `#0a1318`, `#18323d`,
`#d0d0d0`, `#71848b`, `#3bfb1b`, `#55ead4`, `#3fc2e0` and `#0b6974`.
The mascot and wordmark rest in exact sampled window-highlight green `#3bfb1b`
and use one 0.20-second left-to-right diagonal glint followed by a one-second
clean idle pause. Its fixed ramp is deep ion blue `#168fe8`, electric cyan
`#30cfff`, pale green `#abffbf`, and a dead-center 0.5%-wide pure-white
`#ffffff` core. The full illuminated band retains the approved 22% width. Park
the overlay completely outside the glyphs during the idle gap; active runs and
reduced-motion show clean solid green only. Render the unchanged rabbit at 70%
horizontal scale and keep the 4px optical gap to TOKEY. Use the same sampled green for primary action,
metric/progress bars and sort arrows; device selectors remain darker.
Do not dynamically replace these hard-coded product colors from the desktop
theme; keep dark surfaces and readable data. Design for normal
centered, side-tiled and resized windows without requiring full screen. Read
docs/NETRUNNER-DIRECTION.md; exact window defaults remain undecided.

- Preserve the distinction between user decisions, assistant proposals,
  documented competitor features, measured findings and unknowns.
- Existing benchmark tools can be technically excellent. Do not describe
  competitors as bad or infer customer demand from their mere existence.
- Check supported upstream tools and maintained community projects before
  adding custom benchmark machinery. Prefer reusable engines and documented
  interfaces; record the unmet requirement before extending them.
- Treat measurement validity as a core product feature. Preserve raw metrics,
  run metadata, uncertainty and versioned comparison rules. Never invent
  benchmark results or present estimates as measurements.
- Keep source data, reports and future model downloads local by default;
  sharing is an explicit user action in the proposed product.
- Keep strategy documents current as decisions change. Save substantive
  results and outstanding work in CURRENT-STATE.md and DECISIONS.md.
- Use clear technical explanations with evidence. Do not silently turn a
  proposal into an approved commitment or claim a prototype is production ready.

This project is separate from Omarchy desktop configuration and heal2gether.net.
Its creation does not assign work to other assistants or authorize changes to
other machines, publication, purchases or customer outreach.
