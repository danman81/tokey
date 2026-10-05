# Product brief

Status: product redesign discussion, 2026-10-04. The user rejected the first
single-model prototype; implementation success did not satisfy product intent.

## Current product contract

Latest density correction (2026-10-04): user requests a compact cockpit-like
dashboard, minimizing unused space and keeping the main experience in one
shareable view. Supersedes the spacious single-metric layout and separate tall
sharing page. New UI proposal shows ten selectable model rows and simultaneous
generation-speed, first-token and memory columns with bars/units/direction;
compact device/run/progress and same-view sharing. Preserve exact artwork and
current green/cyan styling; reduce padding before sacrificing readability.
Narrow windows reflow rather than forcing the desktop footprint everywhere.
Saved review prototype: [prototypes/tokey-cockpit.html](prototypes/tokey-cockpit.html).
Reuse native column/table patterns (https://docs.gtk.org/gtk4/class.ColumnView.html)
for later desktop integration. Results/export remain explicitly simulated;
no real runner or installed-app change is part of this layout iteration.

Latest sharing update (2026-10-04): user now requests sharing design in the
UI-first simulated prototype. This supersedes the earlier sharing deferral
below for interface design, not public distribution. Proposed flow: Share →
preview → save/copy image or caption. Preview can show all results or an
explicitly labeled top five; preserve metric/units/direction, device scenario,
model variants, included-model scope, partial-run status and simulation warning.
The interactive prototype's save/copy-image buttons simulate actions only;
caption selection permits manual copying. No public links, account connections,
uploads or clipboard writes. For real desktop integration, reuse Gtk.FileDialog
and Gdk.Clipboard; verified hardware, workload, versions and run identity must
accompany measured cards. No personal hostname, username, paths or serials.
Sources: https://docs.gtk.org/gtk4/class.FileDialog.html and
https://docs.gtk.org/gdk4/class.Clipboard.html.

Latest user reversal (2026-10-04): design the interface and workflow first with
simulated runs, then connect real model execution later. This explicitly
supersedes the real-only next-prototype gate below, not the eventual accuracy
requirement. The immediate deliverable is an interactive UI exploration with
fictional model/device results and accelerated timing, all clearly labeled.
Keep simulation isolated from real measurement reports; no fake result may be
presented as evidence. Final catalog, runtime support and measurements remain
unvalidated. Preserve simple start/stop, progressive comparison charts,
CPU/GPU/NPU scenarios and dark Netrunner styling. Social sharing stays deferred.

Superseded immediate prototype requirement (2026-10-04): user explicitly expects a genuinely
working prototype that runs the models, and understands this takes time. A
clickable mock-up or simulated/populated chart does not satisfy the deliverable.
Next prototype must execute the curated model suite end to end: obtain approved
artifacts, verify/load, warm up, perform defined repeated workloads, validate
and persist actual results, and update comparisons as each model completes.
No invented measurements, instant prefilled leaderboard or tiny-model-only
demonstration presented as the requested product.

All models in a run means its clearly disclosed curated lineup; unsupported
models/device paths remain visibly unsupported or failed, not silently skipped
or assigned numbers. Do not imply every online model or every accelerator
combination can run. Show download/setup separately from measured execution,
model X of N and completed results, with reliable Stop. Duration varies with
selected models, hardware, workloads and repetitions. Do not promise a fixed
duration or fabricate a countdown; use measured progress and label any future
evidence-based ETA as an estimate. UI review may assist design but cannot
replace this real benchmark acceptance gate.

Chart/sharing direction (2026-10-04): the user confirms literal side-by-side
model comparison charts as the central readable result, with explicit metric
direction (latency: lower is better; throughput: higher is faster; memory:
lower consumption, not model quality). Only measured local results get bars;
untested models remain labeled. CPU/GPU/NPU execution context stays visible.
User identifies social-media shareability as a benefit but explicitly defers
sharing features until later. Prioritize accurate, clear charts now; polished
share cards/image export are future work, not authorization for account
connections, public uploads, posting or new implementation this strategy turn.

Hardware scope clarification (2026-10-04): CPU, GPU and NPU are all first-class
requirements for the redesigned product, not CPU-only with the others forgotten.
Include hybrid execution where a validated runtime actually uses multiple
devices. This is product scope, not a claim that all devices are implemented.
Default flow should detect hardware and use validated configurations without
requiring users to understand backend names. Optional device comparisons may
show the same supported model/workload across CPU/GPU/NPU, with configuration
and precision differences disclosed rather than labeled pure hardware effects.

Separate device presence, compatible driver/runtime, model support and proven
execution. Never silently fall back to CPU while calling a run an NPU/GPU
benchmark. Mark unsupported/not tested distinctly; disclose CPU assistance or
hybrid execution. Compare measured latency/throughput and energy only where
trustworthy measurement with a stated scope exists. Advertised TOPS are not
model throughput or measured efficiency, and cannot be summed into a score.

NPU reuse research (2026-10-04): Intel offers OpenVINO NPU configuration and
Linux driver integration; AMD documents Linux NPU LLM execution through Ryzen
AI. Inspect device-generation, model, driver and supported-OS requirements
before choosing adapters. Linux availability is not proof of Omarchy support.
Sources: https://docs.openvino.ai/nightly/get-started/install-openvino/configurations/configurations-intel-npu.html
and https://ryzenai.docs.amd.com/en/main/llm_linux.html.
No NPU packages/drivers installed or actual NPU benchmark performed this turn.

Usability correction (2026-10-04): user explicitly rejects file picking and
technical setup in the normal workflow. Apple-like simplicity and cleanliness
are required, while retaining dark Netrunner styling. Design around the user's
question, not engine parameters. This supersedes mandatory model/file/profile/
thread selection and dense dashboard controls in the first release.

Proposed default journey: detect hardware → offer one clear Start Tokey Run
action with a curated comparison suite → disclose any required download size
and obtain approval → run automatically → show understandable local model
comparisons. Users may optionally change included models by friendly names.
Tokey manages verified artifacts and validated runtime settings. Custom GGUF
files, thread counts, quantization controls and raw JSON belong under Advanced
or result details, not the primary path. Reuse validated existing downloads
when discoverable through supported locations/APIs; do not silently scan all
personal files, download large models or change unrelated services.

Simplicity must not hide missing measurements, failed tests or material
comparison caveats. Show an honest empty state until measured, concise
actionable errors and a clear Stop action. Keep detailed evidence accessible.
Acceptance gate before implementation: a first-time nontechnical user can
start the default comparison without knowing filenames, GGUF, threads or
backend terminology. Review the small set of screens before rebuilding.

Tokey should answer: **Which popular models run well on this computer, and how
do they compare?** The comparison is the primary product, not an advanced
feature behind a manual GGUF file picker. Keep the useful measurement core,
but rethink the home screen and workflow rather than merely restyle it.

Optional catalog/custom-comparison flow (not mandatory initial setup):

1. Show detected hardware and clearly separate available from actually used devices.
2. Offer a maintained catalog of popular local model families and exact variants,
   with source/revision/quantization, download size, license and installed state.
3. Select models and run a serial comparison suite, with explicit download/storage
   choices. Do not silently download every popular model or claim that all fit.
4. Show a sortable local leaderboard/charts for verified response latency,
   generation speed, defined memory measurements, repeatability and failures.
   Unimplemented/unsupported metrics remain unavailable, never estimated numbers.
5. Open each result for workload/configuration/raw evidence; compare different
   model variants for user experience, or hold model fixed for hardware changes.

Catalog entries without local runs read Not benchmarked. External/community
numbers, if later supported, live in a separate labeled view. Failed or
unsupported runs stay visible; they do not become zero-performance scores.
Catalog popularity needs a dated documented signal plus curation; popularity
is not quality, compatibility or guaranteed fitness for the user's hardware.

Cross-model fairness: matching synthetic token counts alone does not represent
the same natural-language work across tokenizers. Define common user-task inputs,
context/output policies and report actual token counts/elapsed time; separate
engine-throughput tests. Show precision/quantization/backend settings. Faster
does not mean more capable; any quality evaluation needs its own evidence.

Reuse research refreshed 2026-10-04: LM Studio already offers model search,
downloads and local runtimes (https://lmstudio.ai/docs/app); start from supported
discovery/runtime mechanisms rather than inventing them. LocalScore offers
official model tiers and arbitrary GGUF testing
(https://www.localscore.ai/download). Hugging Face provides model filtering
and trending discovery (https://huggingface.co/models?pipeline_tag=text-generation&sort=trending).
These are useful foundations, not proof of the requested complete local model
comparison experience. No new dependency selection or installation yet.

Next strategy gate: agree the main screen, workloads, initial model coverage
and how measured performance will be distinguished from untested catalog data.

## Earlier brief — retain only where compatible with the correction

Confirmed requirements: made for Omarchy; accurate, easy to use, graphically
beautiful and dark. Learn from predecessor limitations and verify our
improvements. See [design requirements](DESIGN-REQUIREMENTS.md).

## Audience and problem

Candidate initial users are local-AI enthusiasts comparing computers, GPUs,
models and settings. Reviewers and small system builders are a possible paid
audience, to be investigated separately rather than assumed to share the same
needs. Enterprise serving teams have strong existing engineering tools and
are outside the proposed first release.

The product should answer: How well does my system run this workload? How does
it compare with a comparable system? Did my upgrade or configuration change
help? What limits performance, and what evidence supports that explanation?

## Intended experience

1. Open the app and see detected hardware and supported test options.
2. Choose a test; see expected download size, memory needs and run duration.
3. Run it with clear progress and reliable cancellation.
4. Receive understandable results with latency, speed, memory use and variability.
5. Compare with a prior run or genuinely comparable published results.
6. Export or explicitly choose to share a report.

The basic flow should not require a terminal. Technical details remain
available for people who need to audit or reproduce a result.

## Proposed first release

- A standardized local LLM test suite with verified artifacts and a documented
  runtime configuration, reliable installation and recoverable downloads.
- Short interactive and long-input workloads, startup measurement, and an
  optional sustained run.
- Local run history, before/after comparison, raw-data export and a readable report.
- Explicit handling of unsupported hardware, out-of-memory failures, partial
  runs, missing sensors and background interference.
- Clear attribution of the CPU/GPU actually used by each test.

Advanced testing of an existing model server is a candidate later feature.
A public results service, model-fit guidance and additional backends follow
only when the core comparisons are trustworthy. Model intelligence testing,
training benchmarks and image/video generation are expansion options.

## Commercial quality targets

Predictable setup and updates, clean uninstall, responsive cancellation,
repeatable measurements, accessible UI, useful failure messages, a published
support matrix, and regression testing on each claimed hardware/OS family.
Vendor-specific sensors may be unavailable; report that explicitly.

The product must earn trust through transparent methodology. Attractive
charts and a single score alone are insufficient differentiation.

## Business hypotheses to test

A free basic benchmark could encourage comparable community results, while
paid features might include batch runs, deeper comparisons, automated reports
and professional use. An alternative is a paid desktop app with optional
online services. Neither model nor any price is selected.

Discovery should establish who pays, which recurring problem they pay to
solve, and whether support, model delivery and hardware testing costs fit the
revenue model. No market-size or sales estimate is established.

## Open choices

Initial device class on Omarchy; minimum useful differentiation from
LocalScore and Procyon; reference models and redistribution terms; desktop
framework; distribution method; public data policy; pricing and brand.
