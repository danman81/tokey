#!/usr/bin/env python3
"""Reversible user-local installer. Never removes models or result history."""
import argparse
import datetime
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from llm_benchmark import __version__

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--prefix", type=Path, default=Path.home()/".local")
parser.add_argument("--uninstall", action="store_true", help="Move only app-owned installation files into a recovery folder")
args = parser.parse_args()
prefix = args.prefix.expanduser().resolve()
if prefix in (Path("/"), Path.home(), ROOT):
    parser.error("Choose a dedicated installation prefix, not a home, project or filesystem root")
app_root = prefix/"share/llm-benchmark"
manifest = app_root/"install-manifest.json"
version_dir = app_root/("app-"+__version__)
launcher = prefix/"bin/llm-benchmark"
desktop = prefix/"share/applications/net.llmbenchmark.Desktop.desktop"
icon = prefix/"share/icons/hicolor/scalable/apps/net.llmbenchmark.Desktop.svg"
stamp = datetime.datetime.now(datetime.UTC).strftime("%Y%m%dT%H%M%S%fZ")

if args.uninstall:
    if not manifest.exists():
        parser.error("No installer manifest found; nothing removed")
    record = json.loads(manifest.read_text())
    paths = [Path(p) for p in record["paths"]]
    approved = {launcher, desktop, icon}
    for path in paths:
        if path not in approved and not (path.parent == app_root and path.name.startswith("app-")):
            parser.error("Manifest contains an unexpected path; removal refused")
    recovery = app_root/("removed-"+stamp)
    recovery.mkdir(parents=True)
    for path in [*paths, manifest]:
        if path.exists():
            target = recovery/path.relative_to(prefix)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(path), str(target))
    print(f"App files moved to {recovery}. Models and benchmark history were preserved.")
    raise SystemExit(0)

subprocess.run([sys.executable, "-c", "import gi, cairo; gi.require_version('Gtk','4.0'); from gi.repository import Gtk"], check=True)
if not shutil.which("llama-bench") or not shutil.which("timeout"):
    parser.error("Install llama-cpp and coreutils through Omarchy's package manager first")

# Do not overwrite an unrelated executable or desktop launcher.
if not manifest.exists() and any(p.exists() for p in (launcher, desktop, icon, version_dir)):
    parser.error("An untracked installation target exists. Inspect it before installation")
backup = app_root/("previous-"+stamp)
for path in (version_dir, launcher, desktop, icon, manifest):
    if path.exists():
        target = backup/path.relative_to(prefix)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(path), str(target))

(version_dir/"llm_benchmark").mkdir(parents=True)
for path in (ROOT/"llm_benchmark").glob("*.py"):
    shutil.copy2(path, version_dir/"llm_benchmark"/path.name)
shutil.copytree(ROOT/"llm_benchmark"/"assets", version_dir/"llm_benchmark"/"assets")
for path in (launcher, desktop, icon):
    path.parent.mkdir(parents=True, exist_ok=True)
launcher.write_text("#!/usr/bin/python3\nimport os, sys\n"
                    "if os.environ.get('WAYLAND_DISPLAY'):\n"
                    "    os.environ['GDK_BACKEND'] = 'wayland'\n"
                    "    os.environ.pop('GDK_SCALE', None)\n"
                    f"sys.path.insert(0, {str(version_dir)!r})\n"
                    "from llm_benchmark.__main__ import main\nraise SystemExit(main())\n")
launcher.chmod(0o755)
text = (ROOT/"packaging/net.llmbenchmark.Desktop.desktop").read_text()
if any(c in str(launcher) for c in ('"', '\\', '%', '\n', '`', '$')):
    parser.error("Installation path contains unsupported desktop-entry characters")
desktop.write_text(text.replace("Exec=llm-benchmark gui", f'Exec="{launcher}" gui'))
shutil.copy2(ROOT/"assets/net.llmbenchmark.Desktop.svg", icon)
manifest.write_text(json.dumps({"version": __version__, "paths": list(map(str, (version_dir, launcher, desktop, icon)))}, indent=2)+"\n")
if shutil.which("desktop-file-validate"):
    subprocess.run(["desktop-file-validate", str(desktop)], check=True)
if shutil.which("update-desktop-database"):
    subprocess.run(["update-desktop-database", str(desktop.parent)], check=True)
print(f"Installed Tokey {__version__}. Launch {launcher} or find Tokey in the application menu.")
print("Models and history remain separate. Installer rollback copies:", backup if backup.exists() else "none needed")
