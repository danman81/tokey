# Local prerelease and third-party notices

Tokey is the user-approved product name. No relationship with UL, 3DMark, Omarchy,
Hugging Face or the llama.cpp authors is implied.

The project owner has not selected a public source license, commercial terms,
or distribution policy. This is a local prerelease; no public redistribution
license is granted by these notes. The packaging label LicenseRef-Proprietary
means there is no public open-source grant, not that business terms are final.

The app invokes the separately installed llama.cpp/ggml packages; their MIT
licenses and upstream notices remain with those packages. GTK/PyGObject/Cairo
remain separately installed system dependencies with their own licenses.
No engine binary or model is included in the source archive.

The optional starter is downloaded only on request from
https://huggingface.co/bartowski/SmolLM2-135M-Instruct-GGUF at the revision and
SHA-256 in llm_benchmark/models.py. Its source model is
https://huggingface.co/HuggingFaceTB/SmolLM2-135M-Instruct, whose model card
identifies Apache-2.0. Review the relevant model/quantization repository
notices before redistributing model files or shipping a commercial bundle.

The interface uses code-native styling and an original SVG icon; no movie
artwork, fonts, logos or other third-party visual assets are bundled.
