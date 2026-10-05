# SDLC execution — 0.1.0 release candidate

Product: **Tokey**; executions are **Tokey Runs**. Exact mascot locked in
assets/tokey-mascot.txt; approved ANSI-Compact wordmark locked in
assets/tokey-wordmark.txt. Technical IDs stable.

User authorized implementation and full lifecycle execution on 2026-10-03.
Work is developed in Adam's writable workspace at
`/home/danman/Projects/Omarchy/work/llm-benchmark` and synchronized to the
canonical `/home/danman/Projects/LLM-Benchmark` for delivery.

## Requirements and acceptance

| ID | Requirement | Verification |
|---|---|---|
| ACC-1 | Raw measurements, no invented score | Recalculate each raw nanosecond sample and aggregates independently |
| ACC-2 | Exact workload and runtime identity | Model hash, binary/library hashes, build ID and settings checked |
| ACC-3 | Honest scope | CPU engine throughput, timing exclusions and build warnings visible |
| ACC-4 | Invalid/cancelled work excluded | Negative output, cancellation and mismatched-setting tests |
| UX-1 | Graphical model setup and test flow | Download/browse, Run/Stop, results, history and export smoke checks |
| UX-2 | Netrunner theme and responsive dark UI | Screenshots at wide/narrow sizes; contrast checks |
| OPS-1 | Local evidence, reliable persistence | Atomic saves, corruption rejection, offline engine and export tests |
| OPS-2 | Reproducible installation/removal | User launcher, package recipe, versioned archive and uninstall checks |

## Architecture decision

Use Python standard library for headless benchmark orchestration and validation;
GTK 4 via system PyGObject for a native Wayland UI. GTK, Cairo and llama.cpp
are already installed on this Omarchy host. A worker thread owns a separate
llama-bench process session; the UI only receives bounded phase updates.
No browser runtime, network server or background service is needed.

Prefer installed llama-bench over a new inference implementation. LocalScore
provides a useful precedent but its score/database are not required for this
local product. The custom portion is setup, validation, evidence, comparisons
and presentation. Official references:
https://pygobject.gnome.org/getting_started.html,
https://docs.gtk.org/gtk4/class.DrawingArea.html,
https://github.com/ggml-org/llama.cpp/blob/master/tools/llama-bench/README.md .

## Release scope

CPU-only synthetic prompt processing and token generation; three versioned
profiles, GGUF selection, pinned starter model, raw-evidence history and
compatible-run comparisons. End-to-end first-token latency, measured watts,
GPU benchmarks, model quality and global scores are explicitly unavailable.
The 135M starter checks the application and measures this small model only;
it does not predict performance of large production models. Users can select
their own GGUF for a measured CPU result.

The installed llama.cpp package reports asserts enabled; preserve this caveat
and fingerprint the build. No claim of optimized hardware ranking.

## Lifecycle evidence

1. Requirements/discovery: user priorities, primary-source competitor/reuse
   check and specific Omarchy workflow gap in RESEARCH.md. Commercial demand
   remains unvalidated; this work does not invent customer evidence.
2. Design: headless core, GTK worker/UI boundary, explicit measurement and
   comparison contracts; METHODOLOGY.md and OPERATIONS.md document limits.
3. Implementation: engine adapter, verified download, local evidence, native
   graphical flow, responsive colors/layout, history/comparison/export,
   cancellation/recovery and bounded supervision.
4. Verification: 40 automated cases; all 3 actual workloads; independent
   Decimal audit; source-boundary review; real cancellation and window-close;
   actual wide/narrow screenshots; exploratory paired overhead checks.
5. Release/deployment: versioned user install, preserved rollback, validated
   desktop entry, deterministic archive/local Arch recipe; no external publish.
6. Operations/maintenance: data paths, recovery, install/remove, security
   boundaries, dependency revalidation and suite-version policy documented.

Acceptance interpretation: ACC-1/2/4 and OPS-1 pass within the declared runtime
scope. ACC-3 passes through explicit unavailable measurements/caveats. UX-1/2
pass local functional/visual checks, not independent usability/accessibility
certification. OPS-2 passes user-installer round trips; local package artifacts
passed source-hash verification and an actual makepkg build. VALIDATION.md
links the retained evidence.

Defects found and resolved: inherited X11 scaling, hidden/offscreen screenshot
attempts, upstream integer-duration variance mismatch, comparing a run against
itself, stale evidence during a new run, mismatched/corrupt-history acceptance,
and window-close cleanup. No known failed correctness test is waived.

Release class is deliberately a local candidate. Broader device calibration,
controlled foreground observer-effect tests, accessibility/user study,
large-model/GPU coverage, business terms and public distribution remain future
gates. They are not represented as complete because a local build works.

No public release, purchase, outreach or remote-machine change is authorized
by this local implementation. Release candidate status must reflect actual
tested coverage, not an assertion of universal commercial readiness.
