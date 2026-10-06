"""Headless measurement, validation and evidence persistence (stdlib only)."""
from __future__ import annotations

import copy
import dataclasses
import datetime as dt
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import re
import selectors
import shutil
import signal
import statistics
import subprocess
import tempfile
import threading
import time
import uuid

from . import __version__

SCHEMA = 1
SUITE = "llama-engine-cpu-v1"
MAX_OUTPUT = 8 * 1024 * 1024


class BenchmarkError(Exception):
    pass


class Cancelled(BenchmarkError):
    pass


@dataclasses.dataclass(frozen=True)
class Profile:
    key: str
    name: str
    prompt: int
    generation: int
    repetitions: int
    depth: int = 0


PROFILES = (
    Profile("quick", "Quick check", 128, 32, 5),
    Profile("standard", "Standard", 512, 128, 7),
    Profile("long", "Long input", 2048, 128, 7),
)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def file_hash(path, cancel=None):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(1024 * 1024):
            if cancel and cancel.is_set():
                raise Cancelled("Cancelled while verifying files.")
            h.update(chunk)
    return h.hexdigest()


def state_home():
    return Path(os.environ.get("XDG_STATE_HOME", str(Path.home() / ".local/state"))) / "llm-benchmark"


def data_home():
    return Path(os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local/share"))) / "llm-benchmark"


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    tmp = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    try:
        with open(tmp, "x", encoding="utf-8") as f:
            os.chmod(tmp, 0o600)
            json.dump(value, f, indent=2, allow_nan=False)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)


def environment():
    cpu = "Unavailable"
    try:
        cpu = next(line.split(":", 1)[1].strip() for line in Path("/proc/cpuinfo").read_text().splitlines()
                   if line.startswith("model name"))
    except (OSError, StopIteration):
        pass
    packages = "Unavailable"
    try:
        p = subprocess.run(["pacman", "-Q", "llama-cpp", "ggml"], capture_output=True, text=True, timeout=5)
        packages = p.stdout.strip() or "Unavailable"
    except (OSError, subprocess.SubprocessError):
        pass
    return {"cpu": cpu, "logical_cpus": os.cpu_count(), "system": platform.system(),
            "kernel": platform.release(), "architecture": platform.machine(),
            "engine_packages": packages, "load_average": list(os.getloadavg()),
            "power_mode": "Unavailable", "background_activity": "Not isolated; desktop applications may affect performance"}


def engine_files(binary, cancel=None):
    """Fingerprint dynamically loaded ggml backends too, not just the launcher."""
    paths = {Path(binary).resolve()}
    for pattern in ("libllama*.so*", "libggml*.so*", "ggml/libggml*.so*"):
        paths.update(p.resolve() for p in Path("/usr/lib").glob(pattern) if p.is_file())
    for name in ("libc.so.6", "libstdc++.so.6", "libgomp.so.1"):
        path = Path("/usr/lib") / name
        if path.is_file():
            paths.add(path.resolve())
    return {str(p): file_hash(p, cancel) for p in sorted(paths)}


def validate_model(path):
    path = Path(path).expanduser().resolve(strict=True)
    if not path.is_file():
        raise BenchmarkError("Select a GGUF model file.")
    with open(path, "rb") as f:
        if f.read(4) != b"GGUF":
            raise BenchmarkError("This file is not a GGUF model.")
    return path


def build_command(binary, model, profile, threads, device="CPU"):
    if type(threads) is not int or not 1 <= threads <= (os.cpu_count() or 1):
        raise BenchmarkError("Thread count is outside this computer's available range.")
    if profile not in PROFILES:
        raise BenchmarkError("Unknown benchmark profile.")
    if device == "CPU":
        offload = ["-ngl", "0", "-dev", "none"]
    elif isinstance(device, str) and device:
        offload = ["-ngl", "999", "-dev", device]
    else:
        raise BenchmarkError("Unknown execution device.")
    return [str(binary), "-m", str(model), "-p", str(profile.prompt), "-n", str(profile.generation),
            "-r", str(profile.repetitions), "-d", str(profile.depth), "-t", str(threads),
            "-b", "512", "-ub", "128", *offload, "--poll", "0",
            "-fa", "off", "-ctk", "f16", "-ctv", "f16", "-o", "json", "--offline"]


def probe_model(binary, model, cancel=None, pause=None, device="CPU"):
    """Prove the installed engine can load a model before timed work starts."""
    cancel = cancel or threading.Event()
    model = validate_model(model)
    if not binary:
        raise BenchmarkError("llama-bench is missing. Install the Omarchy/Arch llama-cpp package.")
    offload = ["-ngl", "0", "-dev", "none"] if device == "CPU" else ["-ngl", "999", "-dev", device]
    command = [str(binary), "-m", str(model), "-p", "1", "-n", "0", "-r", "1",
               "-t", "1", "-b", "128", "-ub", "128", *offload,
               "--poll", "0", "-fa", "off", "-ctk", "f16", "-ctv", "f16",
               "-o", "json", "--offline"]
    with tempfile.TemporaryDirectory(prefix="tokey-probe-") as folder:
        root = Path(folder)
        try:
            raw, _log, _wall = process(command, cancel, root / "engine.json", root / "engine.log",
                                       timeout=180, pause=pause)
        except Cancelled:
            raise
        except BenchmarkError as exc:
            raise BenchmarkError(f"{model.name} is not compatible with the installed llama.cpp engine.") from exc
    try:
        rows = json.loads(raw)
    except (ValueError, TypeError) as exc:
        raise BenchmarkError(f"{model.name} compatibility probe returned invalid evidence.") from exc
    if (not isinstance(rows, list) or len(rows) != 1 or rows[0].get("n_prompt") != 1
            or rows[0].get("n_gen") != 0 or rows[0].get("model_filename") != str(model)
            or type(rows[0].get("model_n_params")) is not int or rows[0]["model_n_params"] <= 0):
        raise BenchmarkError(f"{model.name} compatibility probe could not verify a successful load.")


def _number(value):
    return type(value) in (int, float) and math.isfinite(value)


def validate_output(raw, profile, threads, device="CPU"):
    """Recalculate rates from integer nanoseconds; refuse unverified rows."""
    try:
        rows = json.loads(raw, parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))
    except (ValueError, TypeError) as exc:
        raise BenchmarkError("Engine returned incomplete or invalid JSON.") from exc
    if not isinstance(rows, list) or len(rows) != 2:
        raise BenchmarkError("Expected exactly one prompt and one generation result.")
    results, seen = {}, set()
    for row in rows:
        if not isinstance(row, dict):
            raise BenchmarkError("Invalid engine result row.")
        if any(type(row.get(key)) is not int for key in ("n_prompt", "n_gen")):
            raise BenchmarkError("Invalid completed-work counters.")
        pair = (row.get("n_prompt"), row.get("n_gen"))
        if pair == (profile.prompt, 0):
            name, tokens = "prompt", profile.prompt
        elif pair == (0, profile.generation):
            name, tokens = "generation", profile.generation
        else:
            raise BenchmarkError("Engine performed a different workload than requested.")
        if name in seen:
            raise BenchmarkError("Duplicate workload result.")
        seen.add(name)
        gpu = device != "CPU"
        expected = {"n_threads": threads, "n_gpu_layers": 999 if gpu else 0, "n_batch": 512, "n_ubatch": 128,
                    "n_depth": profile.depth, "poll": 0, "type_k": "f16", "type_v": "f16"}
        for key, value in expected.items():
            if type(row.get(key)) is not type(value) or row.get(key) != value:
                raise BenchmarkError(f"Engine setting mismatch: {key}.")
        if (not gpu and (row.get("backends") != "CPU" or row.get("devices") != "none")) or \
                (gpu and (device not in str(row.get("devices")) or row.get("backends") == "CPU")):
            raise BenchmarkError("Execution device could not be verified.")
        if row.get("flash_attn") not in (False, 0):
            raise BenchmarkError("Attention configuration could not be verified.")
        if not isinstance(row.get("build_commit"), str) or not row["build_commit"] or type(row.get("model_n_params")) is not int or row["model_n_params"] <= 0:
            raise BenchmarkError("Missing engine/model identity.")
        ns, engine_rates = row.get("samples_ns"), row.get("samples_ts")
        if not isinstance(ns, list) or len(ns) != profile.repetitions or any(type(x) is not int or x <= 0 for x in ns):
            raise BenchmarkError("Missing or invalid raw timing repetitions.")
        if not isinstance(engine_rates, list) or len(engine_rates) != len(ns):
            raise BenchmarkError("Missing per-repetition throughput evidence.")
        rates = [tokens * 1e9 / elapsed for elapsed in ns]
        for rate, reported in zip(rates, engine_rates):
            if not _number(reported) or not math.isclose(rate, reported, rel_tol=1e-5, abs_tol=1e-5):
                raise BenchmarkError("Engine throughput disagrees with raw time and token count.")
        mean, sd = statistics.mean(rates), statistics.stdev(rates)
        # Upstream's integer nanosecond variance loses precision (and can
        # overflow). Never use stddev_ns as a statistical source of truth.
        for key, calculated in (("avg_ts", mean), ("stddev_ts", sd), ("avg_ns", statistics.mean(ns))):
            if not _number(row.get(key)) or not math.isclose(row[key], calculated, rel_tol=1e-5, abs_tol=1 if key.endswith("_ns") else 1e-5):
                raise BenchmarkError(f"Engine aggregate failed independent recalculation: {key}.")
        results[name] = {"tokens_per_repetition": tokens, "samples_ns": ns, "rates": rates,
                         "mean": mean, "median": statistics.median(rates), "stdev": sd,
                         "min": min(rates), "max": max(rates), "cv_percent": sd / mean * 100,
                         "repetitions": len(ns), "unit": "tokens/s"}
    for key in ("build_commit", "build_number", "model_n_params", "model_filename", "model_size", "model_type"):
        if rows[0].get(key) != rows[1].get(key):
            raise BenchmarkError("Engine/model identity changed between workloads.")
    return rows, results


def process(command, cancel, stdout_path, stderr_path, timeout=1800, lease_fd=None, pause=None):
    start = time.perf_counter_ns()
    realtime_start = time.time_ns()
    timeout_binary = shutil.which("timeout")
    if not timeout_binary:
        raise BenchmarkError("GNU timeout is required to bound the engine even if the app crashes.")
    supervised = [timeout_binary, "--signal=TERM", "--kill-after=3s", f"{timeout}s", *command]
    proc = subprocess.Popen(supervised, stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True,
                            pass_fds=(() if lease_fd is None else (lease_fd,)), env={**os.environ, "LC_ALL": "C"})
    suspended = False
    selector = selectors.DefaultSelector()
    selector.register(proc.stdout, selectors.EVENT_READ, "out")
    selector.register(proc.stderr, selectors.EVENT_READ, "err")
    chunks = {"out": bytearray(), "err": bytearray()}
    try:
        while selector.get_map():
            if cancel.is_set():
                raise Cancelled("Benchmark stopped. Partial data is not a completed result.")
            should_pause = bool(pause and pause.is_set())
            if should_pause != suspended:
                os.killpg(proc.pid, signal.SIGSTOP if should_pause else signal.SIGCONT)
                suspended = should_pause
            if suspended:
                time.sleep(0.05)
                continue
            if (time.perf_counter_ns() - start) / 1e9 > timeout:
                raise BenchmarkError(f"Benchmark exceeded its {timeout:g}-second limit.")
            for key, _ in selector.select(0.1):
                data = os.read(key.fileobj.fileno(), 65536)
                if data:
                    chunks[key.data].extend(data)
                    if sum(map(len, chunks.values())) > MAX_OUTPUT:
                        raise BenchmarkError("Engine output exceeded the evidence size limit.")
                else:
                    selector.unregister(key.fileobj)
        code = proc.wait(timeout=3)
        if cancel.is_set():
            raise Cancelled("Benchmark stopped.")
        if code != 0:
            raise BenchmarkError(f"Engine exited with code {code}. See the saved engine log.")
        realtime_elapsed = time.time_ns() - realtime_start
        wall_ns = time.perf_counter_ns() - start
        if abs(realtime_elapsed - wall_ns) > 1000000:
            raise BenchmarkError("System-clock elapsed time differs from monotonic time by over 1 ms. Result rejected; rerun after clock synchronization settles.")
        return bytes(chunks["out"]).decode("utf-8"), bytes(chunks["err"]).decode("utf-8", errors="replace"), wall_ns
    finally:
        if suspended and proc.poll() is None:
            os.killpg(proc.pid, signal.SIGCONT)
        if proc.poll() is None:
            try:
                os.killpg(proc.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            try:
                proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                proc.wait(timeout=3)
        selector.close()
        proc.stdout.close()
        proc.stderr.close()
        Path(stdout_path).write_bytes(chunks["out"])
        Path(stderr_path).write_bytes(chunks["err"])


class Store:
    def __init__(self, root=None):
        self.root = Path(root) if root else state_home()
        self.runs = self.root / "runs"
        self.runs.mkdir(parents=True, exist_ok=True, mode=0o700)

    def save(self, report):
        if not re.fullmatch(r"[0-9]{8}T[0-9]{6}Z-[a-f0-9]{8}", report["id"]):
            raise BenchmarkError("Invalid report identifier.")
        atomic_json(self.runs / report["id"] / "report.json", {"sha256": digest(report), "report": report})

    def load(self, path):
        envelope = json.loads(Path(path).read_text())
        report = envelope["report"]
        if envelope["sha256"] != digest(report) or report.get("schema") != SCHEMA:
            raise BenchmarkError("Report integrity check failed.")
        if not re.fullmatch(r"[0-9]{8}T[0-9]{6}Z-[a-f0-9]{8}", report.get("id", "")):
            raise BenchmarkError("Invalid report identifier.")
        if not isinstance(report.get("started"), str) or not isinstance(report.get("profile", {}).get("name"), str):
            raise BenchmarkError("Invalid report structure.")
        if report.get("status") not in ("preparing", "complete", "failed", "cancelled", "interrupted"):
            raise BenchmarkError("Invalid report status.")
        if report["status"] == "complete":
            profile = Profile(**report["profile"])
            if profile not in PROFILES or report.get("suite") != SUITE or not report.get("comparison_key"):
                raise BenchmarkError("Unrecognized completed benchmark.")
            _, metrics = validate_output(json.dumps(report["raw_rows"]), profile, report["threads"],
                                         report.get("device", "CPU"))
            if metrics != report["metrics"]:
                raise BenchmarkError("Stored metrics do not match raw evidence.")
        return report

    def recover(self):
        """A killed app must not leave an old run looking active or complete."""
        with open(self.root / "runner.lock", "a+") as lock:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                return
            for report in self.history():
                if report["status"] == "preparing":
                    report["status"] = "interrupted"
                    report["error"] = "Previous process ended before validation. No result is ranked."
                    self.save(report)

    def history(self):
        rows = []
        for path in self.runs.glob("*/report.json"):
            try:
                rows.append(self.load(path))
            except (OSError, ValueError, KeyError, TypeError, AttributeError, BenchmarkError):
                continue
        return sorted(rows, key=lambda r: r["started"], reverse=True)

    def export(self, report, path):
        value = copy.deepcopy(report)
        value.pop("command", None)
        value.get("model", {}).pop("path", None)
        value.get("engine", {}).pop("binary", None)
        if "error" in value:
            value["error"] = "Run did not complete. Detailed error retained only in local history."
        for row in value.get("raw_rows", []):
            row["model_filename"] = value["model"]["name"]
        if "files" in value.get("engine", {}):
            value["engine"]["files"] = {Path(k).name: v for k, v in value["engine"]["files"].items()}
        value["export_note"] = "Local absolute model/command paths removed. Hardware and measurements included. Checksums detect corruption, not authenticity."
        atomic_json(path, {"sha256": digest(value), "report": value})


def comparable(a, b):
    if a.get("status") != "complete" or b.get("status") != "complete":
        return False, "Both runs must be complete and validated."
    if not a.get("comparison_key") or a.get("comparison_key") != b.get("comparison_key"):
        return False, "Model, engine, settings or suite differ. Numerical ranking is disabled."
    return True, "Same measured workload and engine. Review environment and variability before attributing differences to hardware."


class Runner:
    def __init__(self, store=None, binary=None):
        self.store = store or Store()
        self.binary = binary or shutil.which("llama-bench")

    def run(self, model, profile, threads, cancel=None, progress=None, pause=None, device="CPU"):
        cancel = cancel or threading.Event()
        progress = progress or (lambda message: None)
        lock = open(self.store.root / "runner.lock", "a+")
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            lock.close()
            raise BenchmarkError("Another benchmark is already running in this data directory.") from exc
        run_id = dt.datetime.now(dt.UTC).strftime("%Y%m%dT%H%M%SZ-") + uuid.uuid4().hex[:8]
        folder = self.store.runs / run_id
        folder.mkdir(mode=0o700)
        report = {"schema": SCHEMA, "id": run_id, "app_version": __version__, "suite": SUITE,
                  "started": dt.datetime.now(dt.UTC).isoformat(), "status": "preparing",
                  "profile": dataclasses.asdict(profile), "threads": threads, "warnings": [], "metrics": {}}
        try:
            if not self.binary:
                raise BenchmarkError("llama-bench is missing. Install the Omarchy/Arch llama-cpp package.")
            if any(os.environ.get(key) for key in ("LD_PRELOAD", "LD_LIBRARY_PATH", "GGML_BACKEND_PATH")):
                raise BenchmarkError("Custom library-loading overrides are unsupported by this reference suite. Start without LD_PRELOAD, LD_LIBRARY_PATH or GGML_BACKEND_PATH.")
            model = validate_model(model)
            command = build_command(self.binary, model, profile, threads, device)
            progress("Verifying model and engine fingerprints…")
            before = model.stat()
            report["model"] = {"name": model.name, "path": str(model), "bytes": before.st_size, "sha256": file_hash(model, cancel)}
            files = engine_files(self.binary, cancel)
            report["engine"] = {"binary": str(self.binary), "files": files}
            report["environment"] = environment()
            report["command"] = command
            self.store.save(report)
            if cancel.is_set():
                raise Cancelled("Cancelled before measurement.")
            progress("Measuring prompt processing and generation. Warmup is excluded by the engine…")
            raw, log, wall_ns = process(command, cancel, folder / "engine.json", folder / "engine.log", lease_fd=lock.fileno(), pause=pause)
            progress("Independently validating every timing sample…")
            rows, metrics = validate_output(raw, profile, threads, device)
            if any(row.get("model_filename") != str(model) for row in rows):
                raise BenchmarkError("Engine did not report the selected model path.")
            if sum(sum(m["samples_ns"]) for m in metrics.values()) > wall_ns:
                raise BenchmarkError("Engine timings exceed the independently measured process duration.")
            after = model.stat()
            if (before.st_size, before.st_mtime_ns, before.st_ino) != (after.st_size, after.st_mtime_ns, after.st_ino):
                raise BenchmarkError("Model changed during the run.")
            if file_hash(model, cancel) != report["model"]["sha256"] or engine_files(self.binary, cancel) != files:
                raise BenchmarkError("Model or engine fingerprint changed during the run.")
            report["raw_rows"], report["metrics"] = rows, metrics
            report["duration_statistics"] = {key: {"mean_ns": statistics.mean(m["samples_ns"]),
                                                   "sample_stdev_ns": statistics.stdev(m["samples_ns"])}
                                              for key, m in metrics.items()}
            for row in rows:
                calculated_sd = statistics.stdev(row["samples_ns"])
                if not _number(row.get("stddev_ns")) or not math.isclose(row["stddev_ns"], calculated_sd, rel_tol=1e-5, abs_tol=1):
                    report["warnings"].append("Engine integer-duration SD differs from independent calculation. Displayed statistics use raw samples, not that engine aggregate.")
                    break
            report["process_wall_ns"] = wall_ns
            report["formula"] = "rate_i = tokens_per_repetition * 1e9 / sample_ns_i; mean = arithmetic mean of rates; SD = sample SD (n-1); CV = 100 * SD / mean"
            report["environment_after"] = environment()
            report["engine"]["build_commit"] = rows[0]["build_commit"]
            report["device"] = device
            report["comparison_key"] = digest({"suite": SUITE, "profile": report["profile"], "threads": threads,
                                               "model": report["model"]["sha256"], "engine": files,
                                               "commit": rows[0]["build_commit"], "device": device})
            if "asserts enabled" in log:
                report["warnings"].append("Engine asserts are enabled; these results describe this build, not an optimized-build rating.")
            if any(m["cv_percent"] > 5 for m in metrics.values()):
                report["warnings"].append("Run-to-run variation exceeds 5%. This is a review flag, not an accuracy confidence bound. Repeat under quieter conditions.")
            report["warnings"].append("Synthetic engine workload. Excludes tokenization, sampling, model loading and end-to-end first-token latency. Does not measure answer quality.")
            report["warnings"].append("Desktop activity and power/thermal conditions are not controlled. No universal hardware score is assigned.")
            report["measurement_limits"] = "Engine high_resolution_clock timings checked against monotonic process duration and a 1 ms wall/monotonic drift guard. No external timer calibration or absolute accuracy certification; sample variation is not measurement accuracy."
            report["status"] = "complete"
        except Cancelled as exc:
            report["status"], report["error"] = "cancelled", str(exc)
        except (BenchmarkError, OSError, ValueError, subprocess.SubprocessError) as exc:
            report["status"], report["error"] = "failed", str(exc)
        finally:
            report["finished"] = dt.datetime.now(dt.UTC).isoformat()
            try:
                self.store.save(report)
            finally:
                fcntl.flock(lock, fcntl.LOCK_UN)
                lock.close()
        return report
