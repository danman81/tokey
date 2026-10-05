# Tokey

A commercial desktop benchmarking product made for Omarchy, for people who
run local language models. “3DMark for LLMs” describes the intended experience;
it is not the product name or a claim of affiliation.

Created 2026-10-03. Version 0.2.0a1 is the first public-alpha candidate of the
approved compact cockpit. It is a native GTK4/WebKitGTK Linux app with a real,
verified llama.cpp CPU workload. Generation throughput is measured; unsupported
first-token and peak-memory cells remain unavailable rather than receiving
estimated values. PNG save/copy is implemented. GIF, MP4, GPU, NPU and the
larger curated model catalog remain post-alpha work, not implied capabilities.

Product name: Tokey. A benchmark execution is a **Tokey Run**. The exact
rabbit mascot and ANSI-Compact ASCII wordmark are locked. Use **Tokey** in
prose and uppercase **TOKEY** for the wordmark. See [brand rules](docs/BRAND.md).
The LLM-Benchmark folder and technical IDs remain stable.

## Start

Dependencies are already installed here. On a new Omarchy machine:

```sh
omarchy pkg add python python-gobject python-cairo gtk4 webkitgtk-6.0 llama-cpp coreutils
python3 scripts/install.py
```

Open **Tokey** from the application menu or run `~/.local/bin/llm-benchmark`.
Select **Run Tokey!**. Tokey verifies or downloads the pinned 105 MB starter,
runs the measured CPU workload outside the UI process, independently validates
the raw repetitions and enables PNG sharing only after completion.
No root service, login job, telemetry or automatic upload.

Prompt processing and generation are separate synthetic CPU tests, not a chat
conversation. Tokenization, sampling, loading, TTFT, quality, power and memory
peaks are not measured. The tiny starter does not predict large-model speed.
Mean, sample SD and CV are derived from raw nanoseconds; CV is not an accuracy
bound. Model/runtime hashes and settings determine compatible comparisons.

See [user guide](docs/USER-GUIDE.md), [methodology](docs/METHODOLOGY.md),
[validation](docs/VALIDATION.md), [operations](docs/OPERATIONS.md) and [SDLC](docs/SDLC.md).

```sh
python3 -m llm_benchmark --state-dir /tmp/my-llm-results run \
  --model /absolute/path/model.gguf --profile quick --threads 2
python3 -m unittest discover -s tests -v
python3 scripts/package.py
```

The cockpit currently uses the Quick 128/32 tokens × 5 profile with two CPU
threads; GPU devices/offload are disabled and therefore hidden. Developer GUI:
`GDK_BACKEND=wayland python3 -m llm_benchmark gui`; installed launcher selects
native Wayland/compositor scaling automatically.

Evidence defaults to ~/.local/state/llm-benchmark; models to
~/.local/share/llm-benchmark/models (XDG overrides supported). Export removes
absolute model/command paths but retains hardware/model identity; inspect
before sharing. Uninstall recoverably with `python3 scripts/install.py --uninstall`;
models and history remain intact.

## Product promise

Understand how well your computer runs local AI, compare results fairly, and
see which changes improve your experience.

The ambition is commercial quality: approachable setup, credible measurements,
polished results, reliable releases, and sustainable maintenance. Demand and
willingness to pay remain hypotheses to validate.

## Project documents

- [Design requirements](docs/DESIGN-REQUIREMENTS.md): Omarchy, dark appearance, usability and predecessor lessons.
- [Product brief](docs/PRODUCT-BRIEF.md): audience, experience, scope and business hypotheses.
- [Benchmark design](docs/BENCHMARK-DESIGN.md): candidate methodology and technical principles.
- [Research and reuse](docs/RESEARCH.md): competitors, sources and open questions.
- [Roadmap](docs/ROADMAP.md): milestones and evidence required to advance.
- [Current state](CURRENT-STATE.md): approved direction, completed work and next steps.
- [Decisions](DECISIONS.md): confirmed choices versus proposals.

Full SDLC implementation was authorized after strategy. GPU/cross-machine
coverage, user research, pricing/license terms and public distribution remain
separate commercial gates. See NOTICE.md before distribution.
