"""Tokey's fixed GTK4/WebKit desktop surface.

The benchmark engine remains a separate Python/subprocess boundary.  WebKit is
used only as the GTK presentation widget so the approved HTML/CSS reference is
the executable visual specification rather than something reinterpreted by a
second widget layout.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import threading
import datetime as dt

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("WebKit", "6.0")
from gi.repository import Gdk, Gio, GLib, Gtk, WebKit

from .core import PROFILES, Runner, Store, environment
from .models import MODEL, download_starter, starter_path


WIDTH = 560
HEIGHT = 332


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
        self.set_default_size(WIDTH, HEIGHT)
        self.set_size_request(WIDTH, HEIGHT)
        self.set_resizable(False)

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
        adapter = (_surface_path().with_name("production-adapter.js")).read_text(encoding="utf-8")
        document = (
            "<!doctype html><html><head><meta charset='utf-8'>"
            "<meta name='viewport' content='width=560,initial-scale=1'>"
            "<style>html,body{width:560px;height:332px;margin:0;overflow:hidden;"
            "background:#05090d}#tokey-cockpit{margin:0!important;min-height:332px!important}</style>"
            "</head><body>" + fragment + "<script>" + adapter + "</script></body></html>"
        )
        self.webview.load_html(document, "file:///app/")

    def _deny_navigation(self, _view, decision, decision_type):
        if decision_type == WebKit.PolicyDecisionType.NAVIGATION_ACTION:
            action = decision.get_navigation_action()
            request = action.get_request()
            uri = request.get_uri()
            if uri and not uri.startswith(("about:", "file:///app/")):
                decision.ignore()
                return True
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
        elif action == "copy-caption":
            self.get_clipboard().set(payload.get("text", ""))
            self._publish("Caption copied to clipboard")
        elif action == "save" and payload.get("format") == "PNG":
            self._capture(False)
        elif action == "copy-results" and payload.get("format") == "PNG":
            self._capture(True)

    def _state(self, notice=""):
        running = bool(self.worker and self.worker.is_alive())
        complete = bool(self.report and self.report.get("status") == "complete" and not running)
        generation = self.report.get("metrics", {}).get("generation", {}).get("mean") if complete else None
        model = {
            "name": "SmolLM2",
            "size": "135M",
            "active": running,
            "result": {"generation": generation},
            "tooltip": "\n".join(filter(None, [
                MODEL["name"], "Backend: llama.cpp CPU",
                f"Generation: {generation:.1f} tok/s" if generation is not None else None,
                "First-token latency and peak memory are not measured by this release.",
            ])),
        }
        env = environment()
        return {
            "running": running, "paused": self.pause.is_set(), "complete": complete,
            "progress": 100 if complete else self.progress, "status": self.status,
            "hardware": env["cpu"], "models": [model],
            "generationScale": max(10, (generation or 50) * 1.1), "notice": notice,
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
                self.status = "Resuming measured CPU run…"
            else:
                self.pause.set()
                self.status = "Paused · measured process suspended"
            self._publish()
            return
        self.cancel.clear()
        self.pause.clear()
        self.report = None
        self.progress = 1
        self.status = "Preparing verified starter model…"
        self.worker = threading.Thread(target=self._run, daemon=True)
        self.worker.start()
        self._publish()

    def _run(self):
        try:
            model = download_starter(cancel=self.cancel, progress=self._progress)
            self.report = Runner(self.store).run(model, PROFILES[0], min(2, os.cpu_count() or 1),
                                                 self.cancel, self._progress, self.pause)
            self.status = "Run complete" if self.report["status"] == "complete" else self.report.get("error", "Run ended")
            self.progress = 100 if self.report["status"] == "complete" else self.progress
        except Exception as exc:
            self.report = {"status": "failed", "error": str(exc), "metrics": {}}
            self.status = str(exc)
        GLib.idle_add(self._publish)

    def _capture(self, clipboard: bool):
        if not self.report or self.report.get("status") != "complete":
            self._publish("Complete a run before exporting results")
            return
        self.webview.evaluate_javascript(
            "document.getElementById('tokey-cockpit').dataset.export='true'",
            -1, None, None, None, None,
        )

        def begin():
            self.webview.get_snapshot(WebKit.SnapshotRegion.VISIBLE, WebKit.SnapshotOptions.NONE,
                                      None, finished, None)
            return False

        def finished(view, result, _data):
            try:
                texture = view.get_snapshot_finish(result)
                if clipboard:
                    self.get_clipboard().set_texture(texture)
                    notice = "Results copied to clipboard"
                else:
                    pictures = Path(GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_PICTURES) or Path.home() / "Pictures")
                    pictures.mkdir(parents=True, exist_ok=True)
                    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
                    target = pictures / f"Tokey-{stamp}.png"
                    texture.save_to_png(str(target))
                    notice = f"Saved {target.name}"
            except Exception as exc:
                notice = f"Export failed: {exc}"
            view.evaluate_javascript("delete document.getElementById('tokey-cockpit').dataset.export",
                                     -1, None, None, None, None)
            self._publish(notice)

        GLib.timeout_add(100, begin)


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
