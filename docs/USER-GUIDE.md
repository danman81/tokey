# Using Tokey

Open Tokey, check the configured runner list, and press **Run Tokey!**. The first
run downloads each missing GGUF and checks its pinned size and SHA-256 before
llama.cpp receives it. Later runs reuse the verified local files.

Pause stops the active benchmark process and Resume continues it. The rerun
button clears the current display and starts the configured queue again.

Tokey measures generation throughput in this release. Blank first-token and
memory cells mean those values were not measured. Quiet the machine before a
comparison and repeat runs when ordinary desktop activity causes variation.

PNG, GIF and MP4 saving and result copying unlock after every configured runner completes.
The caption can be copied at any time. Results stay on the machine unless you
share them yourself.

Edit `~/.config/tokey/config.toml` to change the optional system name or runner
list, then restart Tokey. The window is sized once when it opens.
