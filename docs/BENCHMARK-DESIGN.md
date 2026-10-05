# Benchmark design principles

Status: design principles and future workload candidates. A working CPU
reference implementation now exists; docs/METHODOLOGY.md is the authoritative
0.1.0rc1 protocol and docs/VALIDATION.md records actual tests and limitations.
The candidate workloads below are not claims of implemented measurements.

## Highest-priority requirement: accurate results, no guessing

User directive, 2026-10-03. Accuracy takes precedence over convenience,
appearance, feature count and speed of delivery. This is a requirement, not
evidence that an unbuilt benchmark is already accurate.

- Every result must trace to actual observations and a documented formula.
  For example, throughput uses verified completed work and measured elapsed
  time. Do not substitute requested token counts or streamed chunk counts for
  actual token counts without verifying their equivalence.
- Use appropriate monotonic clocks and defined measurement boundaries. Where
  device work is asynchronous, verify completion before timing stops.
- Preserve raw samples, actual workload completion, errors and exact runtime,
  model and test conditions. Missing sensors or unknown conditions remain
  unavailable/unknown; never estimate them into a result.
- Repeat tests to quantify variation. Show sample counts and justified
  uncertainty; use precision supported by the instrument and protocol. A
  repeatable number can still be systematically wrong, so repetition alone
  does not establish accuracy.
- Independently check timers, work counts, aggregation and report rendering.
  Agreement with another tool is meaningful only when both measure the same
  work and boundaries. Test failure and cancellation paths as well as success.
- Verify output validity and detect skipped work, truncation and unreported
  fallback. Incomplete or invalid runs may retain labeled raw evidence but
  cannot enter completed benchmark comparisons.
- Measure frontend/monitoring overhead. If the measured disturbance compromises
  the protocol, reduce it or mark the run unsuitable for comparison.
- Introduce an overall score only after documenting and validating its formula,
  reference data, weights and comparison rules. It remains a derived index,
  not a universal measure of all AI performance.
- Do not present guessed bottlenecks, model-fit predictions or extrapolated
  performance as measured conclusions. Keep any future predictions explicitly
  separate from benchmark results and validate them independently.

Release evidence must include independent measurement checks, controlled
repetitions, known failure cases, environment records and the measured impact
of UI/sensors. Acceptance thresholds and sample sizes still need a defensible
protocol; do not invent an accuracy percentage now. No physical measurement
has unlimited precision, so disclose limitations rather than promise perfection.

## Measurement scope

A benchmark measures a configured system: hardware, driver, runtime and model
together. Even a controlled suite cannot isolate pure hardware independently
of software. Comparable results require the same suite definition and a
documented policy for backend variants and versions.

A future standard mode would control the model artifact, workload and runtime
settings. An experimental mode could measure a user's own configuration.
Results need distinct comparison groups whenever settings change materially.

## Candidate workloads

| Workload | Primary measurements | Conditions to document |
|---|---|---|
| Startup | Model-ready time and first usable response | Fresh process; filesystem cache state separately identified |
| Short chat | First-token latency and generation rate | Fixed prompt/output policy, one user, warm model |
| Long input | First-token latency and prompt processing | Fixed context occupancy, cache policy and memory settings |
| Sustained generation | Speed over time and stability | Defined duration, power mode, temperatures where available |

Concurrency and serving saturation are later extensions. Avoid demanding every
possible workload in the first prototype.

## Reproducibility

Record suite and runner version, model checksum, quantization, tokenizer,
prompt/template identifiers, requested and actual token counts, random seeds,
sampling settings, runtime build, backend, offload, context and KV settings,
driver, OS, devices, power mode and timestamps. Capture raw samples and errors.

Define warmup, repetition, prefix-cache reset and aggregation explicitly.
Record cache uncertainty rather than calling every new process a cold start.
Show variation; do not silently discard slow samples. Tail percentiles require
enough observations to support them and should not be inferred from a few runs.

## Timing and correctness

Define the start and end of every metric. Client-observed first-token latency
includes different work from an engine's internal prompt-processing timer.
llama-bench omits tokenization and sampling in its documented measurements;
end-to-end interactive claims need separate instrumentation.

Validate that the intended model and backend executed, the required work
completed, output was not truncated unexpectedly, and no fallback was hidden.
These checks establish workload validity; they do not establish model intelligence.
Report failures as failures, never as unusually fast scores.

Tokens depend on the tokenizer. Restrict speed comparisons to compatible
workloads/models and report elapsed completion time alongside token rates.

## Sensors and interpretation

Label sensor scope: process, GPU device, CPU package or whole system. Unified
memory and dedicated VRAM are different accounting models. Device power is
not whole-system energy. Missing readings are unavailable, not zero.

Keep monitoring overhead small and measure its effect. A temperature alone
does not prove thermal throttling; diagnosis needs supporting telemetry.
Distinguish a measured bottleneck from a suggested explanation.

## Scores and results

Begin with raw metrics and comparable test profiles. Introduce a composite
score only after selecting and publishing normalization, reference results,
weights and suite-version rules. Never combine results from incompatible
suites merely because they share a product version or model name.

Public submissions are untrusted data. Checksums identify artifacts and
detect accidental corruption, but do not prove a client ran honestly. A later
results service needs validation, anomaly detection and transparent trust
labels; do not claim cheat-proof results.

## Foundation candidates

Evaluate llama.cpp/llama-bench and LocalScore before writing a new runner.
Use their supported output formats where possible. A later API adapter may
reuse GuideLLM or vLLM benchmark concepts. Version and license checks apply to
the actual executable, dependencies and models, not just a similarly named
website repository. See RESEARCH.md.
