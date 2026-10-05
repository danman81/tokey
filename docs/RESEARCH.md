# Research and reuse

## Implementation follow-through

Tokey 0.1.0rc1 reuses installed llama-bench JSON instead of writing an inference
engine. GTK4/PyGObject/Cairo are installed, maintained native dependencies;
official APIs provide file dialogs, layout, accessible labels and charts:
https://pygobject.gnome.org/getting_started.html,
https://docs.gtk.org/gtk4/class.FileDialog.html,
https://docs.gtk.org/gtk4/class.DrawingArea.html.
The unmet specific requirement is a guided Netrunner/Omarchy graphical flow
with independently validated samples, local evidence and strict comparison
gates; a configuration binding to a CLI alone does not supply that workflow.
Custom code is limited to orchestration, validation, persistence and that UI.
This does not establish a universal competitor weakness or paying market.

One concrete predecessor issue was reproduced on the actual installed
llama-bench build: integer nanosecond SD uses a sum-of-squares algorithm with
truncated means and possible overflow. First live prompt row reported
6,066,455 ns versus independently computed 6,066,373.357325223 ns. Displayed
Tokey SD uses raw samples; unused upstream discrepancies are flagged. See
METHODOLOGY.md and the exact upstream source commit linked there.

Native per-launch Hyprland rules keep development windows on desktop 4;
no custom tiling system or persistent global window rules:
https://wiki.hypr.land/configuring/core/dispatchers/.

The remainder records earlier source review; commercial research gaps remain.

Primary-source review: 2026-10-03. These are documented features, not hands-on
findings. Adoption, customer satisfaction and willingness to pay were not measured.

| Existing option | Documented relevance | What to investigate |
|---|---|---|
| [Procyon AI Text Generation](https://benchmarks.ul.com/procyon/ai-text-generation-benchmark) | Packaged LLM benchmarks, multiple inference engines, reporting | Actual setup, platform coverage, comparison workflow and commercial fit |
| [LocalScore](https://github.com/cjpais/LocalScore) | Local LLM metrics and public hardware results; README describes single-GPU support | Current client experience, runner provenance, reuse or extension feasibility |
| [Geekbench AI](https://www.geekbench.com/ai/) | General AI workloads across devices and operating systems | Lessons in onboarding, reporting and comparable scores |
| [llama-bench](https://github.com/ggml-org/llama.cpp/blob/master/tools/llama-bench/README.md) | Prompt/generation tests, parameter sweeps, machine-readable output | Measurement boundaries, supported backend builds, repeatability |
| [vLLM Bench](https://github.com/vllm-project/vllm/blob/main/docs/benchmarking/cli.md) | Serving metrics, concurrency and cache-related methodology | Reuse for future server tests |
| [GuideLLM](https://github.com/vllm-project/guidellm) | Endpoint load generation and deployment evaluation | Fit for future advanced mode |
| [MLPerf Inference](https://mlcommons.org/benchmarks/inference-datacenter/) | Controlled scenarios and quality requirements | Lessons for rigorous suite definitions and reporting |

Procyon, LocalScore and llama-bench pages were reopened during project setup.
The remaining sources were reviewed during the preceding landscape discussion.
Pin releases and recheck documentation when selecting implementation dependencies.

## Correction to initial landscape assessment

The earlier discussion suggested that fragmented tooling demonstrates a broad
product gap and that LocalScore demonstrates demand. Those statements were
too strong. Existing projects demonstrate relevant competition and prior work.
The commercial opportunity remains an inference that needs customer evidence.
Several tools are excellent at their intended tasks.

## Reuse recommendation

First evaluate whether a polished client using LocalScore or llama.cpp can
deliver the intended experience. The working hypothesis for custom work is
guided setup, comparison explanations and reliable packaging around those
engines. No hands-on finding yet establishes that these requirements are
unmet; the discovery milestone must establish the gap before major development.

Review the actual runner and dependency licenses, model distribution terms,
upstream maintenance and output stability before choosing integration or fork.
Do not infer permission to use an existing public result service from its
open-source website or a proposed client submission format.

## Discovery worksheet

For each competitor, record exact version, OS and test hardware; steps to first
result; download size; account requirements; supported accelerators; cancellation
and recovery; metrics; repeatability; result export; comparisons; offline use;
license and current price. Mark unknown and untested cells honestly.

Use representative user tasks: first-time setup, compare two runs, explain a
slow result, and reproduce a shared result. A meaningful advantage must be
observed or supported by users, not inferred solely from screenshots.

## Initial predecessor lessons — 2026-10-03

The user requires Omarchy, simple operation, accuracy and beautiful dark
graphics. These rows translate evidence into proposals; none is a reproduced
local failure.

| Evidence / limitation | Proposed improvement | Acceptance evidence |
|---|---|---|
| LocalScore's download page uses terminal commands | Graphical setup, managed downloads and a recommended test | First-time user reaches a useful result without terminal commands |
| llama-bench documents timings that exclude tokenization and sampling | Preserve engine metrics and add separately defined end-to-end timing | Timing boundaries independently checked and clearly labeled |
| vLLM warns prefix-cache reuse can inflate throughput | Explicit cache policy and cached/uncached profiles | Repeat runs verify reset; unknown cache state never earns an uncached label |
| LocalScore's README describes single-GPU support | Publish tested support matrix and detect multiple devices accurately | Unsupported setups explained; multi-GPU support deferred until measured |
| User requires dark, beautiful graphics | Dark design throughout, readable charts and low-overhead progress | Visual QA of startup/loading/errors/results; measured frontend overhead |

Sources: [LocalScore download](https://www.localscore.ai/download),
[LocalScore README](https://github.com/cjpais/LocalScore),
[llama-bench](https://github.com/ggml-org/llama.cpp/blob/master/tools/llama-bench/README.md),
[vLLM benchmark documentation](https://github.com/vllm-project/vllm/blob/main/docs/benchmarking/cli.md).

The dark interface comes from the user's preference; we have not established
that all competitors lack dark mode. Cache reuse is a legitimate optimization;
the problem is an invalid or misleading comparison.

## Omarchy integration and community review

Installed Omarchy 4.0.4-1 and /usr/share/omarchy/bin/omarchy-theme-set were
read without changes. The source and Omarchy skill support user-owned
configuration and theme integration instead of packaged-file edits. The
attempted public manual URL could not be fetched; installed source is the
evidence for this version.

The existing community directory was consulted. [Omarchist](https://github.com/tahayvr/omarchist)
is an Omarchy-specific GUI precedent. Its README describes early development
and some older Waybar-oriented work. It is not a benchmark solution; toolkit
or integration suitability for Omarchy 4 and low-overhead measurement needs
evaluation. The search has not established a complete maintained Omarchy
benchmark product satisfying these requirements, but is not exhaustive.
