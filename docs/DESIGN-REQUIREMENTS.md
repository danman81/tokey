# Design requirements — 2026-10-03

Implementation update: Tokey 0.1.0rc1 now implements the CPU reference suite
and dark native desktop. SDLC.md and VALIDATION.md contain actual acceptance
evidence. Strategy-only statements below describe the earlier discovery stage.

## User requirements

Priority clarification: accuracy is the highest requirement. No guessed
benchmark results. The list below is not a priority ranking; visual design and
ease of use must preserve measurement validity. See BENCHMARK-DESIGN.md.

1. Made for Omarchy.
2. Accurate, trustworthy benchmarking.
3. Easy to use.
4. Graphically beautiful, with a dark interface instead of white surfaces.
5. Learn from predecessor faults and develop demonstrably better solutions.

These supersede the earlier undecided launch platform. Engineering and visual
choices below are proposals except the selected fixed Cyber Night identity:
a somber nighttime cyberpunk/dystopian palette using dark blue-black surfaces
and green/cyan/blue highlights. Avoid pink/magenta in the primary identity.
Framework, exact token mapping and window defaults remain open.

## Learn, improve, verify

For each predecessor problem, record the product/version, evidence, affected
user task, proposed improvement and acceptance test. Distinguish documented
limitations, unverified issue reports and reproduced defects. Different scope
is not automatically a fault. Preserve good existing solutions when suitable.
The initial matrix is in RESEARCH.md; hands-on validation remains outstanding.

## Omarchy experience

Design and test on Omarchy's Arch Linux/Hyprland environment. Prefer a normal
standalone desktop app launched through the application menu, with predictable
tiling, keyboard navigation, resizing and fractional scaling. A bar widget
may follow later; benchmark execution should run in a separate worker rather
than inside the desktop shell.

Use supported packaging, desktop entries and user configuration. Do not patch
packaged Omarchy files or change the user's desktop theme. Optional theme
accents should use verified supported interfaces; keep app surfaces dark even
if desktop theme data is absent or the desktop theme is light.

Inspected platform: Omarchy 4.0.4-1. Its theme-set source uses
~/.local/state/omarchy/current/theme; the Omarchy skill describes user-owned
themed templates. Recheck compatibility during implementation. No desktop
configuration was changed in this strategy work.

## Visual direction

Use the fixed Cyber Night palette in BRAND.md: near-black blue/teal surfaces,
cool gray text, and the user's `#39ff14` active-window green with Netrunner
cyan/blue as restrained highlights. Avoid pink/magenta in the primary identity.
The exact rabbit and wordmark share a synchronized diagonal glint. This fixed
product palette supersedes dynamically following Netrunner and the earlier
red/pink direction. See NETRUNNER-DIRECTION.md for historical palette evidence
and responsive layouts. Typography needs review.
Keep the first frame, forms, loading, downloads, tooltips, errors, empty states,
charts and app-rendered reports dark. Check system dialogs separately rather
than claiming their appearance is already controlled.

Charts need units, legends, honest scales and explicit better/worse direction.
Show uncertainty and unavailable data. Use labels/shapes as well as color,
and verify contrast, keyboard focus and display scaling.

For review on the owner's desktop, account for the previously reported
blue-blocking glasses. Blue/cyan must not be the sole essential cue. Verify the fixed palette through
the user's blue-filtered setup; retain redundant labels and shape cues so
color is never the only signal.

## Simple operation

Proposed flow: choose a recommended test, review downloads and expected time,
run, inspect and compare. Detect hardware and offer useful defaults. Keep
detailed controls in an advanced view. Pair plain-language metric descriptions
with their exact units and definitions.

Provide reliable Stop, clear partial-result labeling and actionable recovery
for failed downloads, missing dependencies and insufficient memory. Label
estimates honestly. Evaluate usability with first-time users.

## Graphics and accuracy

The frontend can compete with the benchmark for CPU/GPU resources. Bound
progress updates and pause ornamental animation during measurement. Provide
richer visual exploration afterward. Measure interface and sensor overhead
with controlled repetitions; set an acceptable budget from evidence. Select
the toolkit using these results as well as visual quality.

## Acceptance evidence

- A new Omarchy user completes a standard test and understands its main result
  without a terminal or developer assistance.
- Startup, loading, errors and results remain dark on the tested platform.
- Tiled, narrow and maximized windows work at supported display scales.
- Results retain raw samples and enough metadata to assess comparability.
- Cache state and other test conditions match the declared protocol.
- Measured frontend overhead meets the eventual published budget.
- Every claimed predecessor improvement has evidence and a verification result.

No application, visual mockup or benchmark was executed in this strategy update.
