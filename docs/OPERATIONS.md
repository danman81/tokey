# Installation, release and maintenance

`python3 scripts/install.py` checks dependencies, copies a versioned app,
installs a user launcher/icon/desktop entry and refreshes the app database.
No root/packaged-file edits, daemon, bar or startup changes. Persistence uses
ordinary XDG integration; no physical reboot test has been performed.

Default ~/.local paths:

- share/llm-benchmark/app-0.2.0a2/llm_benchmark
- bin/llm-benchmark (stable technical launcher for Tokey)
- share/applications/net.llmbenchmark.Desktop.desktop
- share/icons/hicolor/scalable/apps/net.llmbenchmark.Desktop.svg
- share/llm-benchmark/install-manifest.json

Untracked existing targets stop installation. Reinstallation moves previous
owned files to dated previous-* recovery folders. Mid-copy disk failure may
require a rerun/recovery; this is not a fully transactional package manager.
Uninstall with `python3 scripts/install.py --uninstall`: move only app-owned
paths to removed-*; retain models/history. Restore a chosen recovery tree's
bin/share files under the original prefix after reviewing its manifest.
Never delete the whole user data/home directory. Use --prefix /tmp/test-prefix
for isolated installation verification.

## Release

Run tests, live workload audit and UI checks; inspect warnings. Run
`python3 scripts/package.py`: deterministic source archive, SHA-256 and local
PKGBUILD with real archive hash. Source, docs, tests and assets only;
no models, credentials, local evidence or upstream research source copy.
From dist, `makepkg --nodeps` builds the local Arch package. Use either it or
the user installation, not both.

## Maintenance and security

Engine updates change fingerprints and may invalidate comparisons. Re-run
parser, negative, workload/statistics, cancellation and UI checks on each
intended supported build. Changed measured work needs a new suite/key. No
opaque updater or promise of compatibility with all future engine versions.

Model paths are argument-list values, never shell interpolation. A separate
process session/GNU timeout bounds the engine. Stop terminates its group,
escalating after a grace period. An inherited lock survives frontend death.
Output capped at 8 MiB. Native engine/system packages remain trusted, not
sandboxed against hostile GGUFs or supply-chain compromises.

Theme TOML is data with hex-only colors. HTTPS model bytes must match pinned
size/hash; partial files cannot run. No account/API key/browser data/other
project service is consulted. No automatic history deletion. Keep enough RAM
and disk for chosen models. Reports are local/owner-only; exports still identify
hardware. Checksums are corruption checks, not anti-cheat certification; any
future public result service needs separate security/privacy design.
