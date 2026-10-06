# How Tokey measures speed

Tokey runs `llama-bench` directly. It measures prompt processing and generation
separately, warms up the model first, and keeps every raw sample. The number in
the app is the arithmetic mean; no slow samples are removed.

CPU runs explicitly disable GPU offload. GPU runs select the exact device
reported by `llama-bench --list-devices` and offload all supported layers. The
saved report records which backend actually ran. Tokey rejects a result if the
engine output does not match the selected device.

Before a run, Tokey checks every configured model. Files must match their pinned
size and SHA-256, and the engine must be able to load them. Reports also record
the model, llama.cpp build, runtime libraries and system details so unlike runs
are not quietly compared.

Generation speed is supported today. First-token time and peak memory stay
blank because Tokey does not estimate values it did not measure.

Desktop load, power limits, temperature and other system activity can affect a
benchmark. Close unnecessary programs and repeat a run before drawing a strong
conclusion. Tokey reports observations, not a guarantee of hardware performance.

The implementation uses llama.cpp's official `llama-bench` tool:
https://github.com/ggml-org/llama.cpp/tree/master/tools/llama-bench
