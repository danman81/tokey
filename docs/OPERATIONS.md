# Maintenance notes

`python3 scripts/install.py` installs Tokey under `~/.local`. Reinstalling
moves the previous app files into a dated recovery folder. Uninstalling does the
same; downloaded models and run history are left alone.

Models are stored in `~/.local/share/llm-benchmark/models`. Reports and engine
logs are stored in `~/.local/state/llm-benchmark`. If Tokey or the computer
stops mid-run, the run is recorded as cancelled or failed when possible.
Completed model downloads remain reusable; partial downloads are checked before
they can run.

For a release:

1. Run `python3 -m unittest discover -s tests -v`.
2. Run a real CPU benchmark and every available GPU backend.
3. Check PNG, GIF and MP4 export in the installed app.
4. Run `python3 scripts/package.py` and verify the checksum.

Engine or model changes can alter results. Keep model hashes pinned and rerun
the checks after updating llama.cpp. Tokey does not install a service, updater
or background task.
