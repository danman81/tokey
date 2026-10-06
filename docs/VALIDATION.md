# Local validation

Tokey is tested on an Intel i7-8650U system running Omarchy. Automated tests
cover model verification, parsing, statistics, cancellation, interrupted runs,
stored-report checks, configuration, installation and UI state.

Real CPU runs pass with the pinned starter model. A real Vulkan run also passes
on the Intel UHD Graphics 620 and records `Vulkan0` as the device. These checks
show that the supported paths work on this machine; they are not a promise that
every driver, GPU or future llama.cpp build behaves identically.

The release checklist also includes opening the installed Wayland app, running
its configured queue, and checking PNG, GIF and MP4 export. Raw reports and
engine logs remain local so failures can be inspected without uploading private
system data.
