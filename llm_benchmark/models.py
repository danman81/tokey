"""Pinned model downloads; no server or account required."""
import fcntl
from pathlib import Path
import threading
import urllib.request

from .core import BenchmarkError, Cancelled, data_home, file_hash
from .config import Model

MODEL = {
    "name": "SmolLM2 135M · Q4_K_M",
    "filename": "SmolLM2-135M-Instruct-Q4_K_M.gguf",
    "repository": "bartowski/SmolLM2-135M-Instruct-GGUF",
    "revision": "09816acd5d99df7be770d85ea30822623dab342c",
    "sha256": "2e8040ceae7815abe0dcb3540b9995eaa1fa0d2ca9e797d0a635ae4433c68c2d",
    "bytes": 105454432,
    "license": "Apache-2.0 (model card)",
    "source_model": "HuggingFaceTB/SmolLM2-135M-Instruct",
}
MODEL["url"] = f"https://huggingface.co/{MODEL['repository']}/resolve/{MODEL['revision']}/{MODEL['filename']}"


def starter_path():
    return data_home() / "models" / MODEL["filename"]


def download_starter(destination=None, cancel=None, progress=None):
    return download_model(MODEL, destination, cancel, progress)


def model_path(model: Model):
    return data_home() / "models" / model.filename


def download_catalog_model(model: Model, destination=None, cancel=None, progress=None):
    pin = {
        "name": f"{model.name} {model.size} · Q4_K_M",
        "filename": model.filename,
        "repository": model.repository,
        "revision": model.revision,
        "sha256": model.sha256,
        "bytes": model.bytes,
        "url": model.url,
    }
    return download_model(pin, destination or model_path(model), cancel, progress)


def download_model(pin, destination=None, cancel=None, progress=None):
    cancel = cancel or threading.Event()
    progress = progress or (lambda value: None)
    destination = Path(destination) if destination else starter_path()
    destination.parent.mkdir(parents=True, exist_ok=True)
    part = destination.with_suffix(".gguf.part")
    with open(destination.with_suffix(".lock"), "a+") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise BenchmarkError("Another model download is running.") from exc
        if destination.exists():
            progress("Checking existing model…")
            if destination.stat().st_size == pin["bytes"] and file_hash(destination, cancel) == pin["sha256"]:
                return destination
            raise BenchmarkError("The existing model failed verification. Remove that file before retrying.")
        offset = part.stat().st_size if part.exists() else 0
        if offset >= pin["bytes"]:
            if offset == pin["bytes"] and file_hash(part, cancel) == pin["sha256"]:
                part.replace(destination)
                return destination
            part.unlink()
            offset = 0
        if cancel.is_set():
            raise Cancelled("Download cancelled.")
        headers = {"User-Agent": "LLM-Benchmark/0.1", "Accept-Encoding": "identity"}
        if offset:
            headers["Range"] = f"bytes={offset}-"
        req = urllib.request.Request(pin["url"], headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            if not response.url.startswith("https://"):
                raise BenchmarkError("Download was redirected to an insecure URL.")
            if response.status == 206:
                expected = f"bytes {offset}-{pin['bytes'] - 1}/{pin['bytes']}"
                if response.headers.get("Content-Range") != expected:
                    raise BenchmarkError("Server returned an unexpected download range.")
                mode = "ab"
            elif response.status == 200:
                mode, offset = "wb", 0
            else:
                raise BenchmarkError("Unexpected download response.")
            with open(part, mode) as f:
                while True:
                    if cancel.is_set():
                        raise Cancelled("Download stopped. Verified download can resume next time.")
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    offset += len(chunk)
                    if offset > pin["bytes"]:
                        raise BenchmarkError("Downloaded file exceeds the pinned model size.")
                    f.write(chunk)
                    progress(f"Downloading {pin['name']} · {offset / 1e6:.1f} / {pin['bytes'] / 1e6:.1f} MB")
        progress("Verifying downloaded model SHA-256…")
        if offset != pin["bytes"] or file_hash(part, cancel) != pin["sha256"]:
            part.unlink(missing_ok=True)
            raise BenchmarkError("Download checksum or size did not match. The file was rejected; retry the download.")
        part.replace(destination)
        return destination
