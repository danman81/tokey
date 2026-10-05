# Tokey user guide

Open Tokey in Omarchy's application menu. Get the pinned 105 MB starter or
Browse for a trusted GGUF. Downloads use HTTPS, resume partial bytes and verify
exact size/hash. Only explicit download needs network; engine runs are offline.
Choose profile/threads, then Start Tokey Run. Settings disable during work.
Stop/close cancels; incomplete work cannot become a ranked result.

For quieter measurements close unrelated heavy jobs yourself. Tokey never
closes other apps or changes cooling, BIOS, power or services. Check RAM needs
before selecting large models. Trusted GGUFs/engine packages are assumed;
the native engine is not a malicious-model sandbox.

Completed results collapse setup; expand WORKLOAD to run again. The identity
line names model, profile, threads, UTC time and status. Rates show sample SD
and n; CV describes variation, not accuracy. The zero-based chart shows every
repetition; switch Prompt/Generation or inspect exact Evidence. Small windows
scroll vertically to charts and warnings.

History compares two different compatible runs. Matching settings still do not
control background load, temperature, power or caches. Positive percentages
do not prove hardware improvement. Repeat quietly and consider variation.
Tiny-model results do not predict larger models or answer quality.

Export is checksummed JSON without absolute model/command paths. Filenames
and CPU/model identity remain; inspect before sharing. No upload or untrusted
leaderboard import. Corrupt local records are excluded, not deleted or repaired.

Current dark Omarchy colors are read at launch; missing/malformed/light data
falls back to Netrunner. Restart after theme changes. Global configuration is
untouched. Contrast checks and text avoid color-only status meaning. No
benchmark animations or live sensor polling.

Native window controls work: on this installation Super+T toggles floating,
Super+Alt+F maximizes, Super+F optionally fills the screen. Requested default
1000×620 logical; minimum 430×430. Tiling may override size. Development test
windows stay on desktop 4; installed app does not force a workspace.

## Failures

- Missing engine: install llama-cpp with Omarchy's package manager.
- Failed run: inspect its engine.log. No score is produced.
- Model mismatch: retry verified download or select the correct artifact;
  never bypass checksums.
- High variation: investigate conditions and repeat; cause is not guessed.
- Clock mismatch: allow synchronization to settle and repeat.
- Engine update breaks parsing: validate a new adapter; don't weaken checks blindly.
- Library override: start without the specified LD/ggml variable; reference
  suite supports system packages, not untracked custom runtimes.

A crash leaves an interrupted record. GNU timeout bounds an orphaned engine
to 30 minutes; its inherited advisory lock blocks another run in the same
state directory meanwhile. Separate state directories/external engines are
not isolated. See OPERATIONS.md for data paths, removal and recovery.
