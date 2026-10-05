```text
 (\_/)
(='.'=) TOKEY
(")_(")
```

# Tokey

A compact Linux benchmark for local language models. Tokey runs pinned GGUF
models with llama.cpp, keeps the raw run evidence, and shows generation speed
without inventing measurements the current runner does not collect.

## Install

Tokey needs Python, GTK4, WebKitGTK 6 and llama.cpp:

```sh
omarchy pkg add python python-gobject python-cairo gtk4 webkitgtk-6.0 llama-cpp coreutils
python3 scripts/install.py
```

Open **Tokey** from the app launcher or run `~/.local/bin/llm-benchmark gui`.

## Config

The shipped config uses five current, practical Q4_K_M models. Copy it before
making changes:

```sh
mkdir -p ~/.config/tokey
cp ~/.local/share/llm-benchmark/app-0.2.0a2/llm_benchmark/default-config.toml ~/.config/tokey/config.toml
```

```toml
# Optional. The rabbit wakes up Tokey's little easter egg.
system_name = "🐇"

runners = [
  "minicpm5-2b",
  "spark-x2.5-4b",
  "qwen3.8-4b",
  "ornith-1.5-9b",
  "qwen3.5-9b",
]
```

Add or remove runner IDs freely. Tokey chooses the window height from that list
when it opens and keeps the size fixed for the rest of the session. The first
run downloads the selected models and verifies every file before use.

## Notes

- CPU runs are supported today; unavailable GPU and NPU controls stay hidden.
- Generation throughput is measured. First-token time and peak memory remain
  blank until their measurement paths are implemented.
- Models live in `~/.local/share/llm-benchmark/models` and results in
  `~/.local/state/llm-benchmark`.
- Nothing is uploaded and no background service is installed.

Run the tests with `python3 -m unittest discover -s tests -v`. Remove the app
with `python3 scripts/install.py --uninstall`; downloaded models and results are
left alone.

See [methodology](docs/METHODOLOGY.md), [validation](docs/VALIDATION.md), and
[operations](docs/OPERATIONS.md) for technical details.
