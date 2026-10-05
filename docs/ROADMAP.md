# Roadmap

Updated after implementation authorization: CPU reference runner and native
Tokey desktop release candidate are implemented. SDLC.md and VALIDATION.md
record the completed local gates. Broad private-alpha/commercial gates below
remain open; no release dates or cost estimates committed.

Confirmed platform: Omarchy. Accurate, easy operation and a beautiful dark
interface are required. See DESIGN-REQUIREMENTS.md.

| Milestone | Deliverable | Evidence needed to advance |
|---|---|---|
| 0 — Discovery | Competitor weaknesses with evidence, target audience and Omarchy integration | Unmet needs, remedies and acceptance tests, reusable foundation, hardware access and a plausible reason to pay |
| 1 — Measurement prototype | One reproducible workload using an existing engine, raw result format and repeat runs | Timing agrees with an independent check; exact environment captured; variation characterized; failures detected |
| 2 — Desktop experience | Dark Omarchy app: install, choose, run, cancel, inspect and compare | No terminal required; tiling/scaling work; app stays dark through startup/loading/errors; graphics overhead measured; failures recover cleanly |
| 3 — Private alpha | Narrow declared hardware matrix and before/after reports | Reproducibility across tested devices; overhead understood; useful feedback from intended users |
| 4 — Commercial beta | Installers, update path, documentation, support and pricing experiment | Release process works; licenses checked; customers value the differentiated features |
| 5 — Commercial release | Supported product and versioned benchmark methodology | Reliability, performance, usability and support criteria met on the advertised platforms |

The online results database is a separate expansion milestone after local
comparison validity is established. It adds hosting, privacy, validation,
moderation and operational costs; it is not required for the first prototype.

## Immediate backlog

- [ ] Complete the competitor worksheet in RESEARCH.md.
- [ ] Identify a narrow first audience and test the customer-problem hypothesis.
- [x] Select direct installed llama-bench reuse for the CPU reference foundation.
- [x] Record Omarchy as the user-selected target platform.
- [x] Declare locally validated CPU scope and native Omarchy integration.
- [x] Specify pinned model, workloads and result/comparison rules.
- [x] Implement and visually inspect the dark run/result/compare experience.

Strategy-only scope was superseded by explicit full-SDLC implementation.
Local downloads, benchmarks, app development and packaging were authorized;
outreach, purchases, public distribution and other-machine changes were not.
