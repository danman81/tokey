import argparse
import json
import signal
import sys
import threading

from . import __version__
from .core import PROFILES, Runner, Store
from .models import download_starter


def main():
    parser = argparse.ArgumentParser(description="Tokey — measured inference on Omarchy")
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("--state-dir", help="Isolate evidence/history in this directory")
    sub = parser.add_subparsers(dest="command")
    gui = sub.add_parser("gui")
    gui.add_argument("--model")
    gui.add_argument("--width", type=int, default=1000)
    gui.add_argument("--height", type=int, default=620)
    gui.add_argument("--smoke-seconds", type=int, default=0, help=argparse.SUPPRESS)
    gui.add_argument("--show-latest", action="store_true")
    gui.add_argument("--legacy-ui", action="store_true", help=argparse.SUPPRESS)
    run = sub.add_parser("run")
    run.add_argument("--model", required=True)
    run.add_argument("--profile", choices=[p.key for p in PROFILES], default="quick")
    run.add_argument("--threads", type=int, default=2)
    download = sub.add_parser("download-starter")
    download.add_argument("--destination")
    sub.add_parser("history")
    args = parser.parse_args()
    store = Store(args.state_dir)
    cancel = threading.Event()
    if args.command in ("run", "download-starter"):
        signal.signal(signal.SIGINT, lambda *_: cancel.set())
        signal.signal(signal.SIGTERM, lambda *_: cancel.set())
    try:
        if args.command == "run":
            p = next(p for p in PROFILES if p.key == args.profile)
            report = Runner(store).run(args.model, p, args.threads, cancel, lambda m: print(m, file=sys.stderr))
            print(json.dumps(report, indent=2))
            return 0 if report["status"] == "complete" else 2
        if args.command == "download-starter":
            print(download_starter(args.destination, cancel, lambda m: print(m, file=sys.stderr)))
            return 0
        if args.command == "history":
            print(json.dumps(store.history(), indent=2))
            return 0
        if not getattr(args, "legacy_ui", False):
            from .webapp import launch_web
            return launch_web(store, getattr(args, "smoke_seconds", 0))
        from .gui import launch
        return launch(store, getattr(args, "model", None), getattr(args, "width", 1000),
                      getattr(args, "height", 620), getattr(args, "smoke_seconds", 0), getattr(args, "show_latest", False))
    except Exception as exc:
        print(f"Tokey: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
