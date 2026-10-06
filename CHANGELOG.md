# Changelog

## Unreleased

- Replace the unsupported default Spark X2.5 runner with pinned Gemma 3 4B.
- Download and verify the full configured roster, then prove every model loads
  in the installed llama.cpp before starting any timed benchmark.
- Detect usable llama.cpp devices and run the queue on CPU and GPU without
  treating a visible control as proof that a backend exists.
- Add PNG, animated GIF and MP4 saving and clipboard export.
- Keep the completion status line empty; the finished-state glint is the cue.
- Shorten the README and documentation, with Tokey artwork and a support link.

## 0.2.0a3 — 2026-10-05

- Expand the default roster to ten popular Q4 models that individually fit
  comfortably in 16 GB RAM.
- Keep the rabbit easter egg in the example config, but commented out by default.

## 0.2.0a2 — 2026-10-05

- Ship a short, editable config with five current pinned GGUF runners.
- Set the fixed window height once at launch from the configured runner count.
- Run configured models in order and keep each completed result in its row.
- Replace project-planning notes with a concise README and focused technical docs.

## 0.2.0a1 — 2026-10-05

- Add the fixed-width Tokey cockpit in a native GTK4/WebKitGTK window.
- Connect Run/Pause/Resume/Rerun to the verified out-of-process CPU runner.
- Automatically obtain and checksum the pinned starter model.
- Keep unmeasured first-token latency and peak memory visibly unavailable.
- Add completion-gated PNG saving and clipboard copying.
- Preserve the exact mascot, wordmark, completion glints and rabbit easter egg.
- Add `webkitgtk-6.0` as a packaged runtime dependency.

## 0.1.0rc1 — 2026-10-03

First local release candidate. Native GTK4 desktop for Omarchy; dark
Netrunner-derived appearance; responsive setup, results, sample charts,
history, compatible comparisons and privacy-reduced JSON export.

CPU llama-bench integration; three versioned profiles; pinned optional GGUF
starter; before/after model/runtime hashes; raw evidence; independent
statistics; cancellation and bounded subprocess supervision; interrupted-run
recovery; corruption detection. Unsupported measurements remain unavailable.

This is not a broadly validated commercial release. See the validation report
and known limitations before interpreting measurements or distributing it.
