# Decisions

## 2026-10-05 — Ion-blue single-pass glint and slimmer rabbit approved

Supersede the triple emerald burst below. The approved logo treatment uses one
0.20-second left-to-right glint followed by a one-second clean idle pause. Keep
the 22% band and use `#168fe8` → `#30cfff` → `#abffbf` around a 0.5%-wide
dead-center `#ffffff` core. Render the unchanged rabbit at 70% horizontal scale
with the existing 4px optical gap to TOKEY. Reduced-motion and active-run states
remove the overlay. Preserve both canonical ASCII assets byte-for-byte.

## 2026-10-04 — Slimmer display treatment for the canonical rabbit (superseded width)

The original choice rendered the unchanged mascot at 80% horizontal scale in cockpit and workflow
surfaces so it reads slimmer beside TOKEY. Use a 4px optical gap between them
so the artwork reads as one combined logo. Preserve `assets/tokey-mascot.txt`
byte-for-byte; these are reversible CSS treatments, not an asset redesign.

## 2026-10-04 — Matrix-green triple glint with clean pauses (superseded)

The approved idle animation is a synchronized burst across the exact rabbit
and wordmark: three clearly visible left-to-right diagonal glints. Each sweep
lasts 0.20s and all three run back-to-back with an effectively instantaneous
offscreen reset, followed by about 1.00s of rest. One nonrepeating gradient band
prevents overlap. Resting artwork uses exact attachment-sampled
window-highlight green `#3bfb1b`. A reference-sampled electric emerald shine
(`#08e87f`, `#45f0c3`, `#a3fff3`) plus the later reference-line center sample
`#abffbf` appears only on a separate nonrepeating overlay. Its thicker #abffbf
hot core stays brighter than the shoulder, clearly pale green and never yellow.
Its dead-center 1.5% is a narrow `#f3ffff` electrical filament sampled from the
brightest pixel in the later attachment; the #abffbf core remains around it.
The whole band spans 22% of its
gradient and the center spans 4%. Only one sweep may be visible at a time.
During every idle gap, park the overlay fully outside the artwork so no glint
remains on the Y or rabbit edge. Reduced-motion and active measurements remove
the overlay and show clean solid green. The same sampled green is used for the
primary action, metric/progress bars and sort arrows; device selectors stay dark.
The later 2+1 cadence experiment with an 80ms pause before the third glint was
rejected and reverted; retain equal back-to-back timing.

## 2026-10-04 — Fixed Cyber Night palette and synchronized glint

The product identity now uses a hard-coded somber nighttime palette rather than
dynamically following the desktop theme. Fixed colors: `#05090d`, `#0a1318`,
`#18323d`, `#c9d8dc`, `#71848b`, `#39ff14`, `#55ead4`, `#3fc2e0` and
`#0b6974`. The newer Matrix-green decision above supersedes its artwork and
accent-color treatment. Deep teal, cyan and blue remain supporting colors.
Apply the same diagonal glint to the exact
rabbit and wordmark; the newer triple-glint decision above defines its cadence
and supersedes its artwork base color and pause behavior. Keep source ASCII
colorless, respect reduced motion and suspend ornamental animation during
measurements. The simulated workflow now reflects this direction; the
installed measurement app remains unchanged.

## 2026-10-04 — UI/workflow first; simulated runs now authorized

User explicitly reverses the earlier real-only prototype gate: design the
interface/workflow with simulated runs for exploration, then add real model
execution based on the reviewed UI. Clearly label fictional values, timing and
hardware scenarios; keep them out of real report storage. No downloads or
installed-app replacement. Interactive draft lives in the conversation's
visualization directory. Reuse review: LM Studio provides managed model search,
download and local APIs (https://lmstudio.ai/docs/app); LocalScore offers curated
official model suites (https://www.localscore.ai/download). Reuse these concepts
and existing measured-engine work later; only the requested local comparison
UX is prototyped now. No new backend dependency selected.

## 2026-10-04 — ANSI-Compact wordmark approved

The exact three-line ANSI-Compact `TOKEY` artwork is the official README
wordmark. Preserve assets/tokey-wordmark.txt byte-for-byte. Use **Tokey** in
prose and UI labels; reserve uppercase **TOKEY** for the wordmark. The source
asset stays colorless so README and application surfaces can apply their own
theme-derived color without changing the artwork.

## 2026-10-04 — Prototype must perform real multi-model tests (superseded above)

User clarifies that the next prototype must really work, expecting time to
test all included models. A simulated chart or clickable-only deliverable is
insufficient. Preserve the design review step only as support for a functional
end-to-end multi-model benchmark. Make the run's model lineup explicit; test
its supported paths for real and disclose failures/unsupported cases. Show
real progress, keep completed results and allow cancellation. No invented
performance or unsupported runtime promises. Strategy clarification, not a
new installation or benchmark execution in this turn.

## 2026-10-04 — Comparison charts first; social sharing later

User confirms easy-to-read side-by-side model charts and sees social sharing
as a benefit, explicitly deferring the sharing feature. Build strategy centers
clear locally measured comparisons and unambiguous metric direction. Future
shareable result cards should preserve hardware/workload/model context, but no
social integration, upload or posting is authorized or implemented now.

## 2026-10-04 — CPU, GPU and NPU are product requirements

User explicitly adds NPU alongside CPU/GPU to the redesign. Include all three
in discovery, architecture and supported-device benchmarking; don't treat the
CPU-only prototype as the long-term product. Hybrid use must be labeled where
it occurs. Device presence alone is not verified model execution; CPU fallback
must never masquerade as an NPU/GPU result. Compare actual measured workloads,
not marketing TOPS. Simple default UI remains; backend selection/diagnostics
are handled internally or in optional advanced details. Support claims require
per-device/runtime/model/OS validation; no driver or app changes this turn.

## 2026-10-04 — Simple default flow; no mandatory file handling

User rejects current usability and explicitly requests Apple-like simplicity
and cleanliness, questioning why file selection is required. Core path must
hide model-artifact/runtime mechanics, not measurement uncertainty. Propose
one Start Tokey Run action for a curated automatic comparison, with explicit
download disclosure/approval. Named-model customization is optional. Manual
GGUF selection and technical controls move to Advanced; preserve the dark
theme and accessible detailed evidence. Strategy only; installed app unchanged.

## 2026-10-04 — User rejects prototype experience; model comparison is central

The user called the app inadequate and clarified that it should show popular
models and their performance on the installed computer. They want continued
strategy and a new version. This supersedes presenting the delivered single-
model runner as satisfying the product need. Tests prove limited engineering
properties, not product acceptance. Preserve the reusable measurement work.

Confirmed direction: popular-model discovery and real on-machine comparison,
with existing no-guessing, dark Netrunner and Tokey brand requirements intact.
Proposals to discuss: a local leaderboard as the home screen, model catalog,
serial batch testing/download controls and comparable everyday workloads.
Do not conflate catalog presence with an actual local benchmark or speed with
model capability. Cross-model comparisons need different rules from exact-
model hardware comparisons. No implementation or installation change this turn.

## 2026-10-03 — Implementation, measured scope and brand lock

User authorized an explicit goal and full SDLC delivery, superseding the
strategy-only phase. Deliver a local release candidate with reuse of installed
llama-bench plus GTK4/Python. CPU-only reference suite, no invented scores or
unvalidated GPU/TTFT claims. Full commercial release remains subject to broader
hardware/user/security/distribution validation. See docs/SDLC.md.

The coordinating brand task relayed user approval: product **Tokey**, each
execution a **Tokey Run**, exact canonical rabbit in assets/tokey-mascot.txt.
Name primarily derives from token, secondarily Korean tokki rabbit inspiration;
Tokey is not literally the Korean word for rabbit. No art substitution or
animation. ASCII wordmark explicitly pending. See docs/BRAND.md.

Keep LLM-Benchmark filesystem folder, Python module and data IDs stable to
avoid disrupting implementation. Test windows use desktop 4 via native
per-launch rules, without persistent global desktop changes.

Implementation choices: pinned SmolLM2-135M starter, GGUF browsing, 3 CPU
profiles, independent sample statistics, raw evidence, versioned comparisons,
reversible user installer and deterministic local source/Arch packaging.
The engine's integer timing SD discrepancy is flagged; our displayed SD uses
raw samples. No Enoch, other-machine, power/cooling or publication changes.

## 2026-10-03 — Accuracy has highest priority; no guessed results

The user explicitly made result accuracy the most important requirement.
Require actual measurements, traceable calculations, documented uncertainty
and independent validation. Never fill unavailable readings with estimates
or invent scores. Incomplete and invalid runs must not enter comparable rankings.
The initial runner must be verified before its results are treated as trusted.
Visual polish and simplicity cannot override measurement integrity.

## 2026-10-03 — Netrunner visual reference and flexible windows

User direction: very closely match the active neon Netrunner appearance and
colors while adding cyberpunk/Blade Runner styling. Theme-derived colors are
preferred. Full-screen use is unnecessary; centered, side and resized layouts
need evaluation. This supersedes the generic-charcoal proposal and the earlier
statement that copying Netrunner is not required. No precise default size or
position is selected. See docs/NETRUNNER-DIRECTION.md for live evidence and
proposed responsive behavior. Preserve dark surfaces if other theme data is
absent or light. No desktop customization was requested or made.

## 2026-10-03 — Omarchy, dark design and predecessor lessons

User requirements: made for Omarchy; accurate and easy to use; graphically
beautiful dark mode instead of white surfaces; learn from predecessor faults
and develop better solutions. This supersedes platform-open guidance below.
Other platforms are not a launch commitment. See docs/DESIGN-REQUIREMENTS.md.

Proposed implementation: standalone desktop app using supported integration,
dark surfaces, optional compatible theme accents and low-overhead graphics
during measurement. Toolkit and exact palette remain open. Every claimed
improvement should have a problem, evidence, remedy and acceptance test.

## 2026-10-03 — Establish commercial benchmark project

User-approved: create a project with the ambition of a commercial-grade
“3DMark for LLMs.” Establish a durable strategy foundation now.

Administrative choice: use LLM-Benchmark as a neutral workspace name. Branding
remains open. This is a separate project from Omarchy and heal2gether.net.

Assistant recommendations, not final product decisions: focus initially on
local LLM inference; evaluate existing foundations before building; develop
a reproducible benchmark protocol alongside the user experience; validate
the customer problem and willingness to pay before broadening scope.

Correction carried forward: existing tools are often very good. Claims about
an ease-of-use gap and commercial demand must be tested. A public benchmark
project proves prior work exists, not market size or willingness to pay.
