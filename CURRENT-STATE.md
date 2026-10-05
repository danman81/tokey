# Tokey — current state

Updated 2026-10-05 America/New_York.

## Fixed Cyber Night visual identity

The approved prototype palette is hard-coded: `#05090d`, `#0a1318`,
`#18323d`, `#d0d0d0`, `#71848b`, `#3bfb1b`, `#55ead4`, `#3fc2e0` and
`#0b6974`. It is somber, nighttime and cyberpunk. The exact mascot and wordmark
rest in the attachment-sampled window-highlight green `#3bfb1b`. A separate
ion-blue electrical overlay uses `#168fe8`, `#30cfff`, `#abffbf`, and a
dead-center 0.5%-wide `#ffffff` core. It makes one 0.20-second left-to-right
diagonal sweep followed by a one-second clean idle pause. The illuminated band
retains the approved 22% width. The overlay is completely outside the artwork
during the pause, removing residual glint from the Y and rabbit edge.
Reduced motion and active measurements show clean solid green only. The same
sampled green is the primary action/bar accent while device selectors stay dark.
Canonical ASCII remains colorless.
The cockpit and workflow render the unchanged canonical rabbit at 70%
horizontal scale with a centered CSS transform and a 4px gap to the wordmark,
so both elements read as one logo. The source mascot remains exact.
The finalized cockpit, including the exact approved glint CSS and keyframes, is
saved at `docs/prototypes/tokey-cockpit.html` as the implementation reference.
The interactive workflow prototypes implement this direction; the installed
measurement app is unchanged.

## Brand lock

The exact three-line ANSI-Compact `TOKEY` artwork is the approved official
README wordmark. Use **Tokey** in prose and UI labels; reserve uppercase
**TOKEY** for the wordmark. Preserve assets/tokey-wordmark.txt byte-for-byte.
The source remains colorless; display surfaces may use active theme colors.

## Current direction — product redesign, strategy first

Latest clarification: next prototype must genuinely execute the multi-model
benchmark end to end, not be a simulation/clickable demo. User expects testing
the lineup to take time. Curated lineup, actual repeated model runs, progress,
partial completed results and reliable cancellation are required. No fabricated
numbers or guessed countdown; exact initial lineup/workloads remain to define.

Hardware scope now explicitly includes CPU, GPU and NPU, plus supported hybrid
paths. Detect presence separately from usable runtime/model support and verified
execution. Never label CPU fallback as NPU performance. Preserve simple default
setup; device-specific comparison is optional. Vendor Linux support requires
an Omarchy/device-specific validation matrix; no new backend installed yet.

Latest usability requirement: Apple-like simple, clean normal workflow. No
mandatory file picking or technical configuration. Proposed primary action
starts a curated automatic comparison; approval covers required downloads.
Friendly model selection is optional; custom files/settings/evidence remain
available through Advanced/details. Preserve dark Netrunner styling and
honest measurement/failure labels. Agree the screens before another build.

The user rejected 0.1.0rc1 as an inadequate product experience: Tokey should
show popular models and how they actually perform on the installed machine.
Return to strategy for a new version. Existing measurement tests remain useful
engineering evidence, not evidence of user acceptance. Do not treat the
single-tiny-model interface or CPU-only prototype scope as the product vision.

Core question: which popular local models work well on this machine, and
how do they compare? Proposed experience: hardware summary → browsable model
catalog → select/download/queue models → shared workload suite → local model
leaderboard with latency, throughput, memory scope, variability and failures.
Metrics beyond the existing engine adapter require validation before display.

Catalog coverage is distinct from measured coverage: untested models must say
Not benchmarked, not receive inferred speed. Explicitly identify exact model,
revision/quantization, backend/device and workload. Separate cross-model
application comparison from same-model hardware regression; tokenizers and
quality differ. Retain raw evidence and never substitute speed for intelligence.

Next step: agree the main comparison screen, common workload definitions and
initial catalog policy before rebuilding. No new app code, model downloads,
benchmarks or replacement installation were performed for this correction.

## Previous implementation — retained, not user-accepted

Tokey 0.1.0rc1 is implemented and installed on this Omarchy machine. Native
GTK4/Netrunner-derived dark UI; model browse/pinned starter download; three
CPU profiles; real prompt/generation samples; independent statistics; raw
evidence/history/compatible comparison/export; bounded cancellation/recovery.
No guessed composite score, GPU, TTFT, power, memory-peak or quality readings.

40 automated tests pass. All three real workloads passed a separate Decimal
arithmetic audit. Real GUI completion/export/window-close cancellation and
wide/narrow layouts were checked. Upstream integer-duration SD discrepancies
are flagged instead of reused. Exploratory background-GUI overhead measured,
without causal/zero-overhead claims. Full evidence: docs/VALIDATION.md.

User-local install and a real installed run passed; desktop entry validated.
Launch **Tokey** from the menu or ~/.local/bin/llm-benchmark. A window is left
on desktop 4; test launches use native per-launch workspace rules, not global
configuration. Starter model is already checksum-verified in user data.
An Arch package build passed from the generated source archive. Models/raw
local evidence are not included in distributable source packages.

Canonical project: /home/danman/Projects/LLM-Benchmark. Implementation was
staged at /home/danman/Projects/Omarchy/work/llm-benchmark because this task's
writable project root was Omarchy; use canonical project for subsequent work.
Source/developer/user/operations/validation documents and raw local evidence
are handed off together. No external publication or other-machine changes.

## Locked requirements and brand

Accuracy/no guessing outranks appearance, convenience and feature count.
Made for Omarchy, easy graphical flow, dark cyberpunk styling very close to
Netrunner colors; flexible centered/tiled/resized windows.
Name **Tokey**; each execution **Tokey Run**; exact three-line rabbit in
assets/tokey-mascot.txt and docs/BRAND.md. Preserve byte-for-byte. The
approved ANSI-Compact wordmark is in assets/tokey-wordmark.txt. Existing
folder/module/data/desktop IDs remain stable.

## Boundaries and future gates

Local release candidate, not a fully certified commercial launch. Live scope:
i7-8650U CPU, system llama-bench build 10809/5266f24da7, pinned 135M model.
Actual build asserts enabled; background/power/thermal conditions uncontrolled.
No absolute clock calibration, broad hardware/large-model/GPU support claim,
foreground observer-effect certification, formal accessibility/security audit,
customer research or pricing/license/distribution decision.
Raw variation and unknowns stay visible. No cooling/BIOS/Enoch changes.

Next product gates: independent user feedback, controlled repeatability across
a declared hardware matrix, optimized-engine validation, GPU and chat-latency
protocols with separate evidence, then commercial distribution decisions.
The original strategy-only restriction was superseded by explicit full-SDLC
implementation authorization. See DECISIONS.md and docs/SDLC.md.
