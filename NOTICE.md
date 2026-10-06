# Third-party notices

Tokey is the product name. No relationship with UL, 3DMark, Omarchy,
Hugging Face or the llama.cpp authors is implied.

Tokey is open-source software under the MIT License. See `LICENSE` for the
permission grant and conditions.

The app invokes the separately installed llama.cpp/ggml packages; their MIT
licenses and upstream notices remain with those packages. GTK/PyGObject/Cairo
remain separately installed system dependencies with their own licenses.
No engine binary or model is included in the source archive.

Configured models are downloaded only when a run needs them. Their repositories,
revisions, sizes and SHA-256 hashes are pinned in `llm_benchmark/config.py`.
Review each model card and quantization repository before redistributing files.

The interface uses code-native styling and an original SVG icon; no movie
artwork, fonts, logos or other third-party visual assets are bundled.
