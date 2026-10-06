"""Tokey's GTK4/WebKit desktop window."""
from __future__ import annotations

import json
import os
import base64
from pathlib import Path
import shutil
import subprocess
import tempfile
import threading
import datetime as dt

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
gi.require_version("WebKit", "6.0")
from gi.repository import Gdk, Gio, GLib, Gtk, WebKit

from .core import PROFILES, Runner, Store, environment, parse_engine_devices, probe_model
from .config import load_config
from .models import download_catalog_model
from . import __version__


WIDTH = 560
BASE_HEIGHT = 188
ROW_HEIGHT = 22

RUN_MESSAGES = {
    "download": (
        "Resolving the pinned model revision…",
        "Receiving verified model bytes…",
        "Checking the transfer boundary…",
    ),
    "verify": (
        "Reading the GGUF header…",
        "Hashing the model file…",
        "Comparing the pinned fingerprint…",
        "Recording the engine build…",
    ),
    "measure": (
        "Reading tensor metadata…",
        "Checking quantization layout…",
        "Mapping model weights…",
        "Preparing worker threads…",
        "Sizing attention buffers…",
        "Warming matrix kernels…",
        "Building the prompt batch…",
        "Measuring prompt processing…",
        "Sampling generation throughput…",
    ),
    "validate": (
        "Checking repeat-to-repeat variation…",
        "Validating every timing sample…",
        "Writing local run evidence…",
    ),
}


def window_height(runner_count: int) -> int:
    return BASE_HEIGHT + ROW_HEIGHT * max(1, runner_count)


def _surface_path() -> Path:
    return Path(__file__).with_name("assets") / "tokey-cockpit.html"


class TokeyWindow(Gtk.ApplicationWindow):
    def __init__(self, app: Gtk.Application, store: Store):
        super().__init__(application=app, title="Tokey")
        self.store = store
        self.cancel = threading.Event()
        self.pause = threading.Event()
        self.worker = None
        self.report = None
        self.progress = 0
        self.status = ""
        self.status_model = ""
        self.status_phase = "verify"
        self.status_step = 0
        self.status_timer = 0
        self.config = load_config()
        self.devices = self._detect_devices()
        self.selected_device = "CPU"
        self.running_device = ""
        self.results = {}
        height = window_height(len(self.config.runners))
        self.set_default_size(WIDTH, height)
        self.set_size_request(WIDTH, height)
        self.set_resizable(False)
        self.connect("close-request", self._on_close_request)

        settings = WebKit.Settings()
        settings.set_enable_developer_extras(False)
        settings.set_enable_html5_database(False)
        settings.set_enable_html5_local_storage(False)
        settings.set_enable_offline_web_application_cache(False)
        settings.set_enable_page_cache(False)
        settings.set_enable_write_console_messages_to_stdout(False)

        manager = WebKit.UserContentManager()
        manager.register_script_message_handler("tokey", None)
        manager.connect("script-message-received::tokey", self._on_message)
        self.webview = WebKit.WebView(user_content_manager=manager, settings=settings)
        background = Gdk.RGBA()
        background.parse("#05090d")
        self.webview.set_background_color(background)
        self.webview.connect("decide-policy", self._deny_navigation)
        self.set_child(self.webview)

        fragment = _surface_path().read_text(encoding="utf-8")
        cup = base64.b64encode(_surface_path().with_name("kofi-cup.png").read_bytes()).decode("ascii")
        fragment = fragment.replace('src="kofi-cup.png"', f'src="data:image/png;base64,{cup}"')
        adapter = (_surface_path().with_name("production-adapter.js")).read_text(encoding="utf-8")
        document = (
            "<!doctype html><html><head><meta charset='utf-8'>"
            "<meta name='viewport' content='width=560,initial-scale=1'>"
            f"<style>html,body{{width:560px;height:{height}px;margin:0;overflow:hidden;"
            f"background:#05090d}}#tokey-cockpit{{margin:0!important;height:{height}px!important;"
            f"min-height:{height}px!important;max-height:{height}px!important}}</style>"
            "</head><body>" + fragment + "<script>" + adapter + "</script></body></html>"
        )
        self.webview.load_html(document, "file:///app/")

    @staticmethod
    def _detect_devices():
        devices = [{"key": "CPU", "engine": "CPU", "name": environment()["cpu"]}]
        binary = shutil.which("llama-bench")
        if not binary:
            return devices
        try:
            result = subprocess.run([binary, "--list-devices"], capture_output=True, text=True, timeout=15)
            output = result.stdout + result.stderr
        except (OSError, subprocess.SubprocessError):
            return devices
        for identifier, name in parse_engine_devices(output):
            devices.append({"key": "GPU", "engine": identifier, "name": name})
            break
        return devices

    def _deny_navigation(self, _view, decision, decision_type):
        if decision_type == WebKit.PolicyDecisionType.NAVIGATION_ACTION:
            action = decision.get_navigation_action()
            request = action.get_request()
            uri = request.get_uri()
            if uri and not uri.startswith(("about:", "file:///app/")):
                decision.ignore()
                return True
        return False

    def _on_close_request(self, _window):
        self.cancel.set()
        self.pause.clear()
        return False

    def _on_message(self, _manager, value):
        """Receive future UI commands through one small, auditable bridge."""
        try:
            payload = json.loads(value.to_json(0))
        except (ValueError, TypeError, AttributeError):
            return
        action = payload.get("action")
        if action == "close":
            self.close()
        elif action == "ready":
            self._publish()
        elif action == "toggle":
            self._toggle()
        elif action == "device" and not (self.worker and self.worker.is_alive()):
            requested = payload.get("device")
            if requested in {item["key"] for item in self.devices}:
                self.selected_device = requested
                self._publish()
        elif action == "copy-caption":
            try:
                self.get_clipboard().set(payload.get("text", ""))
                self._publish("Caption copied to clipboard")
            except Exception as exc:
                self._publish(f"Copy failed: {exc}")
        elif action == "open-url":
            url = payload.get("url", "")
            if url in {"https://github.com/danman81", "https://ko-fi.com/K6W0277G7B"}:
                try:
                    Gio.AppInfo.launch_default_for_uri(url, None)
                except GLib.Error as exc:
                    self._publish(f"Could not open link: {exc.message}")
        elif action == "save" and payload.get("format") in {"PNG", "GIF", "MP4"}:
            self._capture(payload["format"], False)
        elif action == "copy-results" and payload.get("format") in {"PNG", "GIF", "MP4"}:
            self._capture(payload["format"], True)

    def _state(self, notice=""):
        running = bool(self.worker and self.worker.is_alive())
        complete = bool(self.report and self.report.get("status") == "complete" and not running)
        models = []
        selected_results = self.results.get(self.selected_device, {})
        for item in self.config.runners:
            report = selected_results.get(item.id)
            generation = report.get("metrics", {}).get("generation", {}).get("mean") if report else None
            models.append({
                "name": item.name, "size": item.size,
                "active": running and self.selected_device == self.running_device and self.status_model == item.name,
                "result": {"generation": generation},
                "tooltip": "\n".join(filter(None, [
                    f"{item.name} {item.size} · Q4_K_M", f"Backend: llama.cpp {self.selected_device}",
                    f"Generation: {generation:.1f} tok/s" if generation is not None else None,
                ])),
            })
        generations = [item["result"]["generation"] for item in models if item["result"]["generation"] is not None]
        env = environment()
        return {
            "version": __version__,
            "running": running, "paused": self.pause.is_set(), "complete": complete,
            "progress": 100 if complete else self.progress, "status": self.status,
            "hardware": next(item["name"] for item in self.devices if item["key"] == self.selected_device),
            "devices": self.devices, "selectedDevice": self.selected_device,
            "systemName": self.config.system_name, "models": models,
            "generationScale": max(10, max(generations, default=50) * 1.1), "notice": notice,
        }

    def _publish(self, notice=""):
        script = "window.TokeyProduction.apply(" + json.dumps(self._state(notice)) + ")"
        self.webview.evaluate_javascript(script, -1, None, None, None, None)

    def _progress(self, message):
        stages = {"Checking": 5, "Downloading": 15, "Verifying downloaded": 25,
                  "Verifying model": 35, "Measuring": 50, "Independently": 90}
        self.progress = next((value for prefix, value in stages.items() if message.startswith(prefix)), self.progress)
        self.status = message
        GLib.idle_add(self._publish)

    def _toggle(self):
        if self.worker and self.worker.is_alive():
            if self.pause.is_set():
                self.pause.clear()
                self.status = "Resuming measured run…"
            else:
                self.pause.set()
                self.status = "Paused · measured process suspended"
            self._publish()
            return
        self.cancel.clear()
        self.pause.clear()
        self.report = None
        self.results = {}
        self.progress = 1
        self.status = "Preparing model queue…"
        self.status_model = ""
        self.status_phase = "verify"
        self.status_step = 0
        # A non-daemon worker gives the cancellation path time to terminate the
        # llama.cpp process group if the window closes during a run.
        self.worker = threading.Thread(target=self._run, daemon=False)
        self.worker.start()
        if not self.status_timer:
            self.status_timer = GLib.timeout_add(900, self._status_tick)
        self._publish()

    def _status_tick(self):
        if not self.worker or not self.worker.is_alive():
            self.status_timer = 0
            return False
        if not self.pause.is_set() and self.status_model:
            messages = RUN_MESSAGES[self.status_phase]
            message = messages[self.status_step % len(messages)]
            self.status_step += 1
            self.status = f"{self.status_model} · {message}"
            self._publish()
        return True

    def _run(self):
        try:
            if not self.config.runners:
                raise ValueError("Add at least one runner to config.toml")
            total = len(self.config.runners)
            models = []
            for index, item in enumerate(self.config.runners):
                self.status_model = item.name
                self.status_step = 0
                def progress(message, current=item, done=index):
                    if message.startswith("Downloading"):
                        self.status_phase = "download"
                    elif message.startswith(("Checking", "Verifying downloaded", "Verifying model")):
                        self.status_phase = "verify"
                    elif message.startswith("Independently"):
                        self.status_phase = "validate"
                    elif message.startswith("Measuring"):
                        self.status_phase = "measure"
                    self.status = f"{current.name} · {message}"
                    stages = {"Checking": 5, "Downloading": 15, "Verifying downloaded": 25,
                              "Verifying model": 35, "Measuring": 50, "Independently": 90}
                    phase = next((value for prefix, value in stages.items() if message.startswith(prefix)), 1)
                    self.progress = int((done + phase / 100) / total * 40)
                    GLib.idle_add(self._publish)
                model = download_catalog_model(item, cancel=self.cancel, progress=progress)
                models.append((item, model))
                self.progress = int((index + 1) / total * 40)
                GLib.idle_add(self._publish)
            binary = Runner(self.store).binary
            work = [(device, item, model) for device in self.devices for item, model in models]
            for index, (device, item, model) in enumerate(work):
                self.selected_device = self.running_device = device["key"]
                self.status_model = item.name
                self.status_phase = "verify"
                self.status = f"{item.name} · Proving {device['key']} compatibility…"
                self.progress = 40 + int((index + 1) / len(work) * 10)
                GLib.idle_add(self._publish)
                probe_model(binary, model, self.cancel, self.pause, device["engine"])
            for index, (device, item, model) in enumerate(work):
                self.selected_device = self.running_device = device["key"]
                self.status_model = item.name
                self.status_phase = "measure"
                self.status_step = 0
                self.progress = 50 + int(index / len(work) * 50)
                GLib.idle_add(self._publish)
                def progress(message, current=item, done=index):
                    self.status_phase = "validate" if message.startswith("Independently") else "measure"
                    self.status = f"{current.name} · {message}"
                    phase = 90 if message.startswith("Independently") else 50
                    self.progress = 50 + int((done + phase / 100) / len(work) * 50)
                    GLib.idle_add(self._publish)
                report = Runner(self.store).run(model, PROFILES[0], min(2, os.cpu_count() or 1),
                                                self.cancel, progress, self.pause, device["engine"])
                self.results.setdefault(device["key"], {})[item.id] = report
                if report["status"] != "complete":
                    raise RuntimeError(report.get("error", "Run ended"))
                self.progress = 50 + int((index + 1) / len(work) * 50)
                GLib.idle_add(self._publish)
            self.report = {"status": "complete", "metrics": {}}
            self.status = ""
            self.running_device = ""
            self.progress = 100
        except Exception as exc:
            self.report = {"status": "failed", "error": str(exc), "metrics": {}}
            self.status = str(exc)
            self.running_device = ""
        GLib.idle_add(self._publish)

    def _capture(self, format_name: str, clipboard: bool):
        if not self.report or self.report.get("status") != "complete":
            self._publish("Complete a run before exporting results")
            return
        suffix = format_name.lower()
        folder = tempfile.TemporaryDirectory(prefix="tokey-export-")
        root = Path(folder.name)
        self.webview.evaluate_javascript(
            f"const r=document.getElementById('tokey-cockpit');r.dataset.export='true';"
            f"r.dataset.exportFormat='{format_name}';"
            "r.getAnimations({subtree:true}).forEach(a=>{a.cancel();a.play()})",
            -1, None, None, None, None,
        )

        def reset():
            self.webview.evaluate_javascript(
                "const r=document.getElementById('tokey-cockpit');delete r.dataset.export;delete r.dataset.exportFormat",
                -1, None, None, None, None,
            )

        def deliver(path: Path):
            try:
                if clipboard:
                    if format_name == "PNG":
                        texture = Gdk.Texture.new_from_filename(str(path))
                        self.get_clipboard().set(texture)
                    else:
                        mime = "image/gif" if format_name == "GIF" else "video/mp4"
                        provider = Gdk.ContentProvider.new_for_bytes(mime, GLib.Bytes.new(path.read_bytes()))
                        if not self.get_clipboard().set_content(provider):
                            raise RuntimeError("clipboard rejected the media type")
                    notice = f"{format_name} copied to clipboard"
                else:
                    pictures = Path(GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_PICTURES)
                                    or Path.home() / "Pictures")
                    pictures.mkdir(parents=True, exist_ok=True)
                    target = pictures / f"Tokey-{dt.datetime.now().strftime('%Y%m%d-%H%M%S')}.{suffix}"
                    shutil.copy2(path, target)
                    notice = f"Saved {target.name}"
            except Exception as exc:
                notice = f"Export failed: {exc}"
            reset()
            folder.cleanup()
            self._publish(notice)
            return False

        def encode():
            target = root / f"tokey.{suffix}"
            source = str(root / "frame-%03d.png")
            if format_name == "GIF":
                command = ["ffmpeg", "-v", "error", "-y", "-framerate", "15", "-i", source,
                           "-filter_complex", "[0:v]split[a][b];[a]palettegen=max_colors=128[p];[b][p]paletteuse=dither=bayer",
                           str(target)]
            else:
                command = ["ffmpeg", "-v", "error", "-y", "-framerate", "15", "-i", source,
                           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(target)]
            try:
                subprocess.run(command, check=True, capture_output=True, timeout=120)
                GLib.idle_add(deliver, target)
            except (OSError, subprocess.SubprocessError) as exc:
                def failed(error=exc):
                    reset()
                    folder.cleanup()
                    self._publish(f"Export failed: {error}")
                    return False
                GLib.idle_add(failed)

        frames = 42 if format_name != "PNG" else 1

        def capture(index=0):
            self.webview.get_snapshot(WebKit.SnapshotRegion.VISIBLE, WebKit.SnapshotOptions.NONE,
                                      None, frame_ready, index)
            return False

        def frame_ready(view, result, index):
            try:
                texture = view.get_snapshot_finish(result)
                path = root / ("tokey.png" if format_name == "PNG" else f"frame-{index:03d}.png")
                texture.save_to_png(str(path))
                if format_name == "PNG":
                    deliver(path)
                elif index + 1 < frames:
                    GLib.timeout_add(67, capture, index + 1)
                else:
                    threading.Thread(target=encode, daemon=True).start()
            except Exception as exc:
                reset()
                folder.cleanup()
                self._publish(f"Export failed: {exc}")

        GLib.timeout_add(100, capture)


class TokeyApplication(Gtk.Application):
    def __init__(self, store: Store, smoke_seconds: int = 0):
        super().__init__(application_id="net.llmbenchmark.Desktop", flags=Gio.ApplicationFlags.DEFAULT_FLAGS)
        self.store = store
        self.smoke_seconds = smoke_seconds

    def do_activate(self):
        window = self.props.active_window or TokeyWindow(self, self.store)
        window.present()
        if self.smoke_seconds:
            GLib.timeout_add_seconds(self.smoke_seconds, self.quit)


def launch_web(store: Store, smoke_seconds: int = 0) -> int:
    return TokeyApplication(store, smoke_seconds).run(None)
