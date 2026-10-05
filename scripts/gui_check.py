"""Real desktop acceptance exercise, isolated from the user's result history."""
import argparse
import json
import os
from pathlib import Path
import sys
import time
import subprocess

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import gi
gi.require_version("Graphene", "1.0")
from llm_benchmark.gui import Gio, GLib, Gtk, Window
from llm_benchmark.core import Store, atomic_json
from gi.repository import Graphene

parser = argparse.ArgumentParser()
parser.add_argument("--model", required=True)
parser.add_argument("--width", type=int, default=1000)
parser.add_argument("--height", type=int, default=620)
parser.add_argument("--output", required=True)
parser.add_argument("--run", action="store_true")
parser.add_argument("--cancel", action="store_true")
parser.add_argument("--close-running", action="store_true")
parser.add_argument("--state", default="validation/state")
parser.add_argument("--visible-check", action="store_true")
parser.add_argument("--no-capture", action="store_true")
args = parser.parse_args()
out = Path(args.output)
out.mkdir(parents=True, exist_ok=True)
app = Gtk.Application(application_id="net.llmbenchmark.Desktop", flags=Gio.ApplicationFlags.NON_UNIQUE)
checks = {"requested_size": [args.width, args.height], "errors": []}
previous_workspace = None
start = time.monotonic()


def capture(window, name):
    try:
        if args.visible_check:
            clients = json.loads(subprocess.check_output(["hyprctl", "clients", "-j"]))
            client = next(c for c in clients if c["pid"] == os.getpid())
            active = json.loads(subprocess.check_output(["hyprctl", "activeworkspace", "-j"]))
            if active["id"] != 4 or client["workspace"]["id"] != 4:
                raise RuntimeError("Workspace changed; capture skipped to avoid unrelated content")
            x, y = client["at"]
            w, h = client["size"]
            subprocess.run(["grim", "-g", f"{x},{y} {w}x{h}", str(out/(name+".png"))], check=True)
            return
        paintable = Gtk.WidgetPaintable.new(window.get_child())
        snapshot = Gtk.Snapshot.new()
        paintable.snapshot(snapshot, window.get_width(), window.get_height())
        node = snapshot.to_node()
        rect = Graphene.Rect().init(0, 0, window.get_width(), window.get_height())
        texture = window.get_renderer().render_texture(node, rect)
        texture.save_to_png(str(out/(name+".png")))
    except Exception as exc:
        checks["errors"].append("capture: " + str(exc))


def activate(application):
    window = Window(application, Store(args.state), args.model, args.width, args.height)
    window.present()
    def begin():
        checks["actual_size"] = [window.get_width(), window.get_height()]
        checks["wayland"] = "Wayland" in type(window.get_display()).__name__
        if args.run or args.cancel or args.close_running:
            window.start_run()
            if args.cancel or args.close_running:
                GLib.timeout_add(1200, lambda: (window.close() if args.close_running else window.stop(), False)[1])
            GLib.timeout_add(100, poll)
        else:
            if window.history:
                window.show_report(next((r for r in window.history if r["status"] == "complete"), window.history[0]))
                window.status.set_text("SAVED RESULT  /  Showing validated local evidence.")
            GLib.timeout_add(750, finish)
        return False

    def poll():
        if time.monotonic() - start > 120:
            checks["errors"].append("Acceptance run timed out")
            window.stop()
        if window.worker and window.worker.is_alive():
            return True
        if not window.report:
            return True
        checks["run_status"] = window.report["status"]
        checks["run_id"] = window.report["id"]
        expected = "cancelled" if args.cancel or args.close_running else "complete"
        if window.report["status"] != expected:
            checks["errors"].append(window.report.get("error", "Unexpected run status"))
        if args.close_running:
            atomic_json(out/"checks.json", checks)
            return False
        if args.no_capture:
            checks["elapsed_s"] = time.monotonic()-start
            atomic_json(out/"checks.json", checks)
            window.close()
            return False
        GLib.timeout_add(300, finish)
        return False

    def finish():
        global previous_workspace
        if args.visible_check and previous_workspace is None:
            previous_workspace = json.loads(subprocess.check_output(["hyprctl", "activeworkspace", "-j"]))["id"]
            subprocess.run(["hyprctl", "dispatch", 'hl.dsp.focus({ workspace = "4" })'], check=True)
            GLib.timeout_add(800, finish)
            return False
        capture(window, "benchmark")
        checks["status_text"] = window.status.get_text()
        if window.report:
            window.store.export(window.report, out/"export.json")
            checks["export_roundtrip"] = window.store.load(out/"export.json")["id"] == window.report["id"]
        if args.visible_check:
            adjustment = window.page_scroll.get_vadjustment()
            adjustment.set_value(max(0, adjustment.get_upper()-adjustment.get_page_size()))
            GLib.timeout_add(400, lower)
        else:
            window.stack.set_visible_child_name("history")
            GLib.timeout_add(400, history)
        return False

    def lower():
        capture(window, "samples-and-notes")
        window.page_scroll.get_vadjustment().set_value(0)
        window.stack.set_visible_child_name("history")
        GLib.timeout_add(400, history)
        return False

    def history():
        capture(window, "history")
        checks["comparison_text"] = window.compare_note.get_text()
        window.stack.set_visible_child_name("evidence")
        GLib.timeout_add(400, evidence)
        return False

    def evidence():
        capture(window, "evidence")
        checks["elapsed_s"] = time.monotonic()-start
        atomic_json(out/"checks.json", checks)
        window.close()
        if previous_workspace and previous_workspace != 4:
            active = json.loads(subprocess.check_output(["hyprctl", "activeworkspace", "-j"]))["id"]
            if active == 4:
                subprocess.run(["hyprctl", "dispatch", f'hl.dsp.focus({{ workspace = "{previous_workspace}" }})'], check=True)
        return False
    GLib.timeout_add(750, begin)


app.connect("activate", activate)
result = app.run([])
if args.close_running:
    records = Store(args.state).history()
    if not records or records[0]["status"] != "cancelled":
        checks["errors"].append("Closing during a run did not preserve cancellation")
    else:
        checks["run_status"] = records[0]["status"]
        checks["run_id"] = records[0]["id"]
atomic_json(out/"checks.json", checks)
raise SystemExit(1 if checks["errors"] else result)
