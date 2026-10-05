# CPU reference suite v1

Scope: llama-engine-cpu-v1, schema 1. System llama-bench JSON backend.
Validated: build 10809, commit 5266f24da7, llama-cpp 0.4.0-1 / ggml 0.23.0-2.

## Work and timing

Prompt and generation are separate rows (P,0) and (0,G), repeated five/seven
times. Depth zero. KV/context memory is cleared before each measured repetition.
One full prompt warmup and one generation-step warmup precede timing; this
does not establish thermal equilibrium.

Exact source confirms all P token IDs are processed in batches with a final
synchronization; generation performs G one-token decodes, synchronizing each.
Decode errors abort the engine; nonzero exit never yields a complete result.
Counts are completed decode operations, not natural-language output tokens.
IDs use the engine's C RNG, not semantic prompts. There is no independent
fixed RNG-stream claim across C libraries/builds; runtime fingerprints bound
comparison. No sampling or answer quality is tested.

Timing includes engine loops, ID construction and synchronization; excludes
loading, warmup, resets outside the loop, tokenization and output sampling.
The engine uses C++ high_resolution_clock, which may be a wall clock on this
toolchain. The app independently measures process time with a monotonic clock,
rejects impossible summed samples and rejects wall/monotonic elapsed mismatch
over 1 ms at process boundaries. This catches large/net clock disturbances,
not every transient anomaly. No external calibration/absolute error bound.

Source: https://github.com/ggml-org/llama.cpp/blob/5266f24da7/tools/llama-bench/llama-bench.cpp
(clock 40–43; loops 2173–2221; warmup/reset/timing 2411–2510).

## Settings and evidence

CPU only (-ngl 0 -dev none); batch 512, microbatch 128, KV f16/f16, attention
off, poll zero, selected threads, offline. Verify settings, CPU/device
declarations, workload, repetitions, positive integer nanoseconds, both rows'
model/build identity and selected model path.

Hash GGUF before/after; conservatively hash system llama/ggml libraries, all
installed CPU backends, libc/libstdc++/libgomp. This is an Arch-system-runtime
fingerprint, not complete supply-chain attestation. Reject custom LD_PRELOAD,
LD_LIBRARY_PATH or GGML_BACKEND_PATH. Runtime/model changes invalidate a run
or comparison key. Other environment effects, power limits, governors, cache
and external work are not controlled or fully recorded. Capture basic system,
package identity and load averages before/after; unknown power is unavailable.

Keep raw stdout/stderr even on failure. Save checksummed JSON atomically.
Loading complete reports checks the digest and recalculates embedded samples.
A checksum detects corruption, not dishonest submissions.

## Statistics

rate_i = token_steps × 10^9 / nanoseconds_i. Report arithmetic mean, median,
min/max, sample SD (n−1), CV = 100 × SD / mean. No slow-sample removal. Mean
of rates is not total tokens/total time; the chosen formula is explicit.
Two-decimal UI formatting does not imply that physical accuracy; raw timings
and full derived values remain available.

Cross-check engine rates and floating rate mean/SD. Relative tolerance 1e-5
accommodates rounded JSON; this is serialization agreement, not a physical
accuracy claim. Duration means allow integer rounding. Independently calculate
duration SD: upstream's integer sum-of-squares truncates intermediate means and
can overflow. Flag a disagreement without relying on that unused aggregate.

Five/seven repetitions do not justify tail percentiles or a confidence interval.
CV >5% flags noise for review, not error bounds. Compare only matching suite,
profile, threads, model hash and runtime fingerprint. Deltas are observed,
not causal or significant by assertion. Development fingerprint revisions can
intentionally make earlier drafts incomparable with final candidate runs.

## Validated scope

Live tests: Intel i7-8650U CPU, Omarchy 4.0.4-1, pinned SmolLM2-135M Q4_K_M.
Host is fanless with a user-reported thermal-pad shelf mount and intentional
unspecified BIOS restriction. No cooling/power changes. Variation is not
diagnosed as throttling. Other CPUs, GPUs, large models, new engines and
sustained serving need separate validation before support claims.
