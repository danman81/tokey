```text
 (\_/)    ██████ ▄████▄ ██ ▄█▀ ██████ ██  ██
(='.'=)   ██   ██  ██ ████   ██▄▄    ▀██▀
(")_(")   ██   ▀████▀ ██ ▀█▄ ██▄▄▄▄   ██
```

# Tokey

A small Linux app for comparing local language-model speed with llama.cpp.
Models and results stay on your computer.

## Install

On Omarchy or Arch Linux:

```sh
omarchy pkg add python python-gobject python-cairo gtk4 webkitgtk-6.0 llama-cpp ggml-vulkan ffmpeg coreutils
python3 scripts/install.py
```

Open **Tokey** from the app launcher or run `~/.local/bin/llm-benchmark gui`.

## Config

Tokey ships with ten quantized models chosen for a 16 GB computer. Copy the
config before changing the list:

```sh
mkdir -p ~/.config/tokey
cp ~/.local/share/llm-benchmark/app-0.2.0a3/llm_benchmark/default-config.toml ~/.config/tokey/config.toml
```

```toml
# system_name = "🐇"

runners = [
  "minicpm5-2b",
  "lfm2.5-2.6b",
  "llama-3.2-3b",
  "phi-4-mini",
  "gemma-3-4b",
  "jan-v3.5-4b",
  "qwen3.8-4b",
  "deepseek-r1-7b",
  "ornith-1.5-9b",
  "qwen3.5-9b",
]
```

Add or remove runner IDs, then restart Tokey. The first run downloads and checks
the selected files. The full list uses about 30 GB, so trim it if needed.

## Notes

- CPU is always available. GPU appears when llama.cpp reports a usable Vulkan,
  CUDA, HIP or SYCL device.
- Tokey checks every model before timing starts.
- Generation speed is measured. Unmeasured values stay blank.
- Models live in `~/.local/share/llm-benchmark/models` and results in
  `~/.local/state/llm-benchmark`.
- Nothing is uploaded and no background service is installed.

Run the tests with `python3 -m unittest discover -s tests -v`. Uninstall with
`python3 scripts/install.py --uninstall`; models and results are kept.

See [how measurements work](docs/METHODOLOGY.md) and
[maintenance notes](docs/OPERATIONS.md) for details.

<p align="center">
  <a href="https://ko-fi.com/K6W0277G7B"><img src="llm_benchmark/assets/kofi-cup.png" width="22" alt="Coffee cup"> <strong>Help maintain Tokey</strong></a>
</p>

MIT licensed. See [LICENSE](LICENSE).
