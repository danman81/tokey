"""Native GTK 4 desktop frontend. All benchmark work stays off the UI thread."""
from __future__ import annotations

import json
import os
from pathlib import Path
import threading
import time

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
from gi.repository import Gdk, Gio, GLib, Gtk, Pango

from . import __version__
from .core import BenchmarkError, PROFILES, Runner, Store, atomic_json, comparable
from .models import MODEL, download_starter, starter_path
from .theme import read_palette, rgb, stylesheet


def label(text, style=None, wrap=False):
    widget = Gtk.Label(label=text, xalign=0)
    if style:
        for c in style.split():
            widget.add_css_class(c)
    if wrap:
        widget.set_wrap(True)
        widget.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
    return widget


def box(vertical=True, spacing=8):
    return Gtk.Box(orientation=Gtk.Orientation.VERTICAL if vertical else Gtk.Orientation.HORIZONTAL, spacing=spacing)


def button(text, action, style=None):
    widget = Gtk.Button(label=text)
    widget.connect("clicked", action)
    if style:
        widget.add_css_class(style)
    return widget


def flow(children):
    widget = Gtk.FlowBox()
    widget.set_selection_mode(Gtk.SelectionMode.NONE)
    widget.set_column_spacing(10)
    widget.set_row_spacing(8)
    widget.set_min_children_per_line(1)
    widget.set_max_children_per_line(3)
    widget.set_homogeneous(True)
    for child in children:
        widget.insert(child, -1)
    return widget


class SampleChart(Gtk.DrawingArea):
    def __init__(self, palette):
        super().__init__()
        self.palette = palette
        self.metric = None
        self.set_content_height(175)
        self.set_hexpand(True)
        self.set_draw_func(self.draw)
        self.update_property([Gtk.AccessibleProperty.LABEL], ["Per-repetition throughput chart. Exact samples are also in Evidence."])

    def set_metric(self, metric):
        self.metric = metric
        self.queue_draw()

    def draw(self, area, cr, width, height):
        p = self.palette
        cr.set_source_rgb(*rgb(p["dark_background"]))
        cr.paint()
        cr.select_font_face("monospace")
        cr.set_font_size(11)
        if not self.metric:
            cr.set_source_rgb(*rgb(p["secondary"]))
            cr.move_to(22, height / 2 - 4)
            cr.show_text("Your measurements will appear here.")
            cr.move_to(22, height / 2 + 17)
            cr.show_text("No simulated results.")
            return
        values = self.metric["rates"]
        left, top, right, bottom = 58, 22, width - 22, height - 33
        maximum = max(values) * 1.15
        for i in range(5):
            y = bottom - (bottom - top) * i / 4
            cr.set_source_rgba(*rgb(p["accent"]), .20)
            cr.move_to(left, y)
            cr.line_to(right, y)
            cr.stroke()
            cr.set_source_rgb(*rgb(p["secondary"]))
            cr.move_to(7, y + 4)
            cr.show_text(f"{maximum * i / 4:.0f}")
        pts = [(left + (right - left) * i / max(1, len(values) - 1), bottom - v / maximum * (bottom - top)) for i, v in enumerate(values)]
        cr.set_source_rgba(*rgb(p["accent"]), .15)
        cr.move_to(left, bottom)
        for x, y in pts:
            cr.line_to(x, y)
        cr.line_to(right, bottom)
        cr.close_path()
        cr.fill()
        cr.set_line_width(2)
        cr.set_source_rgb(*rgb(p["bright_foreground"]))
        for i, (x, y) in enumerate(pts):
            cr.move_to(x, y) if i == 0 else cr.line_to(x, y)
        cr.stroke()
        for i, (x, y) in enumerate(pts):
            cr.arc(x, y, 3, 0, 6.2832)
            cr.fill()
            cr.set_source_rgb(*rgb(p["secondary"]))
            cr.move_to(x - 3, bottom + 19)
            cr.show_text(str(i + 1))
            cr.set_source_rgb(*rgb(p["bright_foreground"]))
        cr.set_source_rgb(*rgb(p["secondary"]))
        cr.move_to(left, 13)
        cr.show_text("tokens/s  |  repetitions  |  zero-based Y axis")


class Window(Gtk.ApplicationWindow):
    def __init__(self, app, store, model=None, width=1000, height=620):
        super().__init__(application=app, title="Tokey")
        self.store, self.report = store, None
        self.worker = None
        self.cancel = threading.Event()
        self.closing = False
        self.theme_name, self.palette = read_palette()
        self.set_default_size(width, height)
        self.set_size_request(430, 430)
        self.connect("close-request", self.on_close)
        settings = Gtk.Settings.get_default()
        settings.set_property("gtk-application-prefer-dark-theme", True)
        settings.set_property("gtk-enable-animations", False)
        css = Gtk.CssProvider()
        css.load_from_string(stylesheet(self.palette))
        Gtk.StyleContext.add_provider_for_display(self.get_display(), css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        outer = box(spacing=0)
        self.set_child(outer)
        header = Gtk.HeaderBar()
        header.set_title_widget(label("TOKEY   /   OMARCHY", "eyebrow"))
        outer.append(header)
        scroll = Gtk.ScrolledWindow()
        self.page_scroll = scroll
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_vexpand(True)
        outer.append(scroll)
        page = box(spacing=17)
        page.add_css_class("page")
        scroll.set_child(page)

        top = box(False, 12)
        title = box(spacing=4)
        title.set_hexpand(True)
        title.append(label("LOCAL INFERENCE  /  MEASURED", "eyebrow"))
        title.append(label("Know your machine.", "title", True))
        title.append(label("Real samples. Clear comparisons. Your hardware.", "subtitle", True))
        top.append(title)
        top.append(label("CPU\nREFERENCE", "badge"))
        page.append(top)
        rule = Gtk.Separator()
        rule.add_css_class("rule")
        page.append(rule)

        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.NONE)
        switcher = Gtk.StackSwitcher(stack=self.stack)
        switcher.set_halign(Gtk.Align.START)
        page.append(switcher)
        page.append(self.stack)
        bench, history, evidence = box(spacing=14), box(spacing=12), box(spacing=12)
        self.stack.add_titled(bench, "benchmark", "Benchmark")
        self.stack.add_titled(history, "history", "History")
        self.stack.add_titled(evidence, "evidence", "Evidence")

        setup = box(spacing=8)
        setup.add_css_class("card")
        setup.append(label("01  /  CHOOSE YOUR WORKLOAD", "eyebrow"))
        model_row = box(False, 8)
        self.model_entry = Gtk.Entry()
        self.model_entry.set_hexpand(True)
        self.model_entry.set_placeholder_text("Choose a local GGUF model or download the starter")
        self.model_entry.set_text(str(model or (starter_path() if starter_path().exists() else "")))
        self.model_entry.set_tooltip_text("Local GGUF model. The file is hashed before and after every run.")
        self.browse = button("Browse…", self.choose_model)
        model_row.append(self.model_entry)
        model_row.append(self.browse)
        setup.append(model_row)
        self.download = button("Get starter model · 105 MB", self.download_model)
        setup.append(self.download)
        setup.append(label("SmolLM2 135M / Q4_K_M · Hugging Face TB + bartowski · Apache-2.0\nA small-model test, not a prediction of larger-model performance.", "muted small", True))

        profile_box = box(spacing=4)
        profile_box.append(label("TEST PROFILE", "metric-title"))
        self.profile = Gtk.DropDown.new_from_strings([p.name for p in PROFILES])
        self.profile.connect("notify::selected", self.profile_changed)
        profile_box.append(self.profile)
        thread_box = box(spacing=4)
        thread_box.append(label("CPU THREADS", "metric-title"))
        self.threads = Gtk.SpinButton.new_with_range(1, os.cpu_count() or 1, 1)
        self.threads.set_value(min(2, os.cpu_count() or 1))
        thread_box.append(self.threads)
        actions = box(False, 6)
        actions.set_valign(Gtk.Align.END)
        self.run_button = button("Start Tokey Run", self.start_run, "primary")
        self.stop_button = button("Stop", lambda _: self.stop())
        self.stop_button.set_sensitive(False)
        actions.append(self.run_button)
        actions.append(self.stop_button)
        setup.append(flow([profile_box, thread_box, actions]))
        self.profile_info = label("", "muted small", True)
        setup.append(self.profile_info)
        self.profile_changed()
        self.setup_expander = Gtk.Expander(label="WORKLOAD  /  Configure a test")
        self.setup_expander.set_expanded(True)
        self.setup_expander.set_child(setup)
        bench.append(self.setup_expander)

        self.result_identity = label("", "muted small", True)
        bench.append(self.result_identity)

        self.values, self.details = {}, {}
        metrics = []
        for key, name, unit in (("prompt", "PROMPT PROCESSING", "tokens / second"),
                                ("generation", "TOKEN GENERATION", "tokens / second"),
                                ("variation", "GENERATION VARIATION", "coefficient of variation")):
            card = box(spacing=5)
            card.add_css_class("card")
            card.set_size_request(190, -1)
            card.append(label(name, "metric-title"))
            self.values[key] = label("—", "metric")
            card.append(self.values[key])
            self.details[key] = label(unit, "muted small", True)
            card.append(self.details[key])
            metrics.append(card)
        bench.append(flow(metrics))
        chart_head = box(False)
        chart_title = label("02  /  EVERY SAMPLE COUNTS", "eyebrow", True)
        chart_title.set_hexpand(True)
        chart_head.append(chart_title)
        self.chart_kind = Gtk.DropDown.new_from_strings(["Generation", "Prompt"])
        self.chart_kind.connect("notify::selected", lambda *_: self.update_chart())
        chart_head.append(self.chart_kind)
        bench.append(chart_head)
        self.chart = SampleChart(self.palette)
        bench.append(self.chart)
        self.result_note = label("Run a test to collect measured data. No overall score is assigned.", "notice small", True)
        bench.append(self.result_note)
        bench.append(label("Engine throughput only · warmup excluded · no tokenization or sampling.\nFirst-token latency, power, memory peaks and answer quality: not measured.", "muted small", True))

        history.append(label("Compare like with like.", "section-title"))
        history.append(label("Only completed runs with the same model, engine and workload can be ranked.\nVariation and uncontrolled desktop activity still matter.", "muted", True))
        self.history_menu = Gtk.DropDown.new_from_strings(["No saved runs"])
        self.history_menu.connect("notify::selected", self.history_changed)
        history.append(self.history_menu)
        history.append(button("Show selected result", self.show_history))
        history.append(label("BASELINE", "metric-title"))
        self.baseline = Gtk.DropDown.new_from_strings(["No baseline"])
        self.baseline.connect("notify::selected", self.compare_changed)
        history.append(self.baseline)
        self.compare_note = label("Collect two runs to compare.", "notice", True)
        history.append(self.compare_note)

        evidence.append(label("A result you can inspect.", "section-title"))
        evidence.append(label("Raw repetitions, formulas, file hashes, workload settings and warnings.\nChecksum verification detects accidental corruption; it does not certify authenticity.", "muted", True))
        evidence.append(button("Export current result…", self.export))
        text_scroll = Gtk.ScrolledWindow()
        text_scroll.set_min_content_height(300)
        text_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.evidence_text = Gtk.TextView(editable=False, cursor_visible=False, monospace=True)
        text_scroll.set_child(self.evidence_text)
        evidence.append(text_scroll)

        footer = box(spacing=5)
        footer.set_margin_start(22)
        footer.set_margin_end(22)
        footer.set_margin_top(8)
        footer.set_margin_bottom(12)
        self.status = label("READY  /  Choose a model for your Tokey Run.", "status", True)
        footer.append(self.status)
        footer.append(label(f"{self.theme_name}  ·  {__version__}  ·  Local evidence only", "muted small"))
        outer.append(footer)
        self.refresh_history()

    def profile_changed(self, *_):
        if hasattr(self, "profile_info"):
            p = PROFILES[self.profile.get_selected()]
            self.profile_info.set_text(f"{p.prompt} prompt tokens · {p.generation} generation steps · {p.repetitions} repetitions each · CPU only\nSeparate tests; generation starts with an empty context.")

    def choose_model(self, *_):
        dialog = Gtk.FileDialog(title="Choose a GGUF model")
        filters = Gio.ListStore.new(Gtk.FileFilter)
        model_filter = Gtk.FileFilter()
        model_filter.set_name("GGUF models")
        model_filter.add_pattern("*.gguf")
        filters.append(model_filter)
        dialog.set_filters(filters)
        def selected(d, result):
            try:
                f = d.open_finish(result)
                self.model_entry.set_text(f.get_path() or "")
            except GLib.Error:
                pass
        dialog.open(self, None, selected)

    def busy(self, value):
        for widget in (self.model_entry, self.profile, self.threads, self.browse, self.download, self.run_button):
            widget.set_sensitive(not value)
        self.stop_button.set_sensitive(value)

    def progress(self, text):
        # Download progress can be frequent; throttle UI updates to four per second.
        now = time.monotonic()
        if text.startswith("Downloading") and now - getattr(self, "last_progress", 0) < .25:
            return
        self.last_progress = now
        GLib.idle_add(self.status.set_text, text)

    def dispatch(self, operation, done):
        if self.worker and self.worker.is_alive():
            return
        self.cancel = threading.Event()
        self.busy(True)
        def work():
            try:
                value, error = operation(), None
            except Exception as exc:
                value, error = None, str(exc)
            GLib.idle_add(finish, value, error)
        def finish(value, error):
            self.busy(False)
            if error:
                self.status.set_text("ATTENTION  /  " + error)
            else:
                done(value)
            if self.closing:
                self.destroy()
            return False
        self.worker = threading.Thread(target=work, name="benchmark-worker", daemon=False)
        self.worker.start()

    def download_model(self, *_):
        self.status.set_text("Preparing pinned model download…")
        def done(path):
            self.model_entry.set_text(str(path))
            self.status.set_text("READY  /  Starter model checksum verified. You can run a test.")
        self.dispatch(lambda: download_starter(cancel=self.cancel, progress=self.progress), done)

    def start_run(self, *_):
        model = self.model_entry.get_text().strip()
        if not model:
            self.status.set_text("Choose a GGUF file or get the starter model first.")
            return
        profile = PROFILES[self.profile.get_selected()]
        threads = self.threads.get_value_as_int()
        self.report = None
        self.result_identity.set_text("Current measurement has not yet been validated.")
        self.evidence_text.get_buffer().set_text("")
        for value in self.values.values():
            value.set_text("—")
        self.chart.set_metric(None)
        self.result_note.set_text("Measurement in progress. Results appear only after validation.")
        self.dispatch(lambda: Runner(self.store).run(model, profile, threads, self.cancel, self.progress), self.run_done)

    def stop(self):
        self.cancel.set()
        self.stop_button.set_sensitive(False)
        self.status.set_text("STOPPING  /  Finishing evidence cleanup…")

    def run_done(self, report):
        self.show_report(report)
        self.refresh_history()
        if report["status"] == "complete":
            self.status.set_text("COMPLETE  /  Samples validated and saved locally.")
        else:
            self.status.set_text(report["status"].upper() + "  /  " + report.get("error", ""))

    def show_report(self, report):
        self.report = report
        self.result_identity.set_text(f"{report.get('model', {}).get('name', 'No verified model')}\n"
                                      f"{report['profile']['name']} · {report['threads']} CPU threads · {report['started'][:19]} UTC · {report['status']}")
        if report["status"] == "complete":
            self.setup_expander.set_expanded(False)
            for key in ("prompt", "generation"):
                m = report["metrics"][key]
                self.values[key].set_text(f"{m['mean']:.2f}")
                self.details[key].set_text(f"tok/s · SD {m['stdev']:.2f} · n={m['repetitions']}")
            m = report["metrics"]["generation"]
            self.values["variation"].set_text(f"{m['cv_percent']:.1f}%")
            self.details["variation"].set_text("sample variation · not an accuracy bound")
            self.result_note.set_text("\n".join(report["warnings"]))
        else:
            for value in self.values.values():
                value.set_text("—")
            self.result_note.set_text(report.get("error", report["status"]))
        self.evidence_text.get_buffer().set_text(json.dumps(report, indent=2))
        self.update_chart()

    def update_chart(self):
        if hasattr(self, "chart"):
            kind = "generation" if self.chart_kind.get_selected() == 0 else "prompt"
            self.chart.set_metric(self.report.get("metrics", {}).get(kind) if self.report else None)

    def refresh_history(self):
        self.history = self.store.history()
        names = [f"{r['started'][:19].replace('T', ' ')}  ·  {r['profile']['name']}  ·  {r['status']}" for r in self.history]
        self.history_menu.set_model(Gtk.StringList.new(names or ["No saved runs"]))
        self.baseline.set_model(Gtk.StringList.new(names or ["No baseline"]))
        if len(names) > 1:
            self.baseline.set_selected(1)
        self.compare_changed()

    def history_changed(self, *_):
        self.compare_changed()

    def selected_history(self, dropdown):
        index = dropdown.get_selected()
        return self.history[index] if hasattr(self, "history") and index < len(self.history) else None

    def show_history(self, *_):
        if self.worker and self.worker.is_alive():
            self.status.set_text("Wait for the active operation before viewing another result.")
            return
        report = self.selected_history(self.history_menu)
        if report:
            self.show_report(report)
            self.stack.set_visible_child_name("benchmark")

    def compare_changed(self, *_):
        if not hasattr(self, "compare_note"):
            return
        a, b = self.selected_history(self.history_menu), self.selected_history(self.baseline)
        if not a or not b:
            return
        if a["id"] == b["id"]:
            self.compare_note.set_text("Select two different runs to compare.")
            return
        valid, reason = comparable(a, b)
        text = reason
        if valid:
            text += "\n"
            for key, name in (("prompt", "Prompt"), ("generation", "Generation")):
                ma, mb = a["metrics"][key], b["metrics"][key]
                delta = (ma["mean"] / mb["mean"] - 1) * 100
                text += f"\n{name}: {ma['mean']:.2f} vs {mb['mean']:.2f} tok/s ({delta:+.1f}%)"
                text += f"\nVariation: {ma['cv_percent']:.1f}% vs {mb['cv_percent']:.1f}%"
            text += "\n\nObserved difference only; no statistical significance or causal claim."
        self.compare_note.set_text(text)

    def export(self, *_):
        if not self.report:
            self.status.set_text("Run or select a saved result before exporting.")
            return
        report = self.report
        dialog = Gtk.FileDialog(title="Export measured evidence", initial_name=f"llm-benchmark-{report['id']}.json")
        def saved(d, result):
            try:
                path = d.save_finish(result).get_path()
                if path:
                    self.store.export(report, path)
                    self.status.set_text("EXPORTED  /  Result saved with model and command paths removed.")
            except GLib.Error:
                pass
            except (OSError, ValueError) as exc:
                self.status.set_text("Export failed: " + str(exc))
        dialog.save(self, None, saved)

    def on_close(self, *_):
        if self.worker and self.worker.is_alive():
            self.closing = True
            self.stop()
            return True
        return False


def launch(store=None, model=None, width=1000, height=620, smoke_seconds=0, show_latest=False):
    if not Gtk.init_check():
        raise BenchmarkError("No graphical display is available. Launch from your desktop or use the run command.")
    store = store or Store()
    store.recover()
    app = Gtk.Application(application_id="net.llmbenchmark.Desktop", flags=Gio.ApplicationFlags.NON_UNIQUE)
    def activate(application):
        window = Window(application, store or Store(), model, width, height)
        if show_latest and window.history:
            window.show_report(window.history[0])
        window.present()
        if smoke_seconds:
            GLib.timeout_add_seconds(smoke_seconds, lambda: (window.close(), False)[1])
    app.connect("activate", activate)
    return app.run([])
