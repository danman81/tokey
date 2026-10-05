"""Exploratory paired headless/background-GUI runs; never a causal overhead certification."""
import argparse
import json
from pathlib import Path
import statistics
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from llm_benchmark.core import PROFILES, Runner, Store, atomic_json

parser = argparse.ArgumentParser()
parser.add_argument("--model", required=True)
args = parser.parse_args()
model = Path(args.model).resolve()
state = ROOT/"validation/overhead-state"
out = ROOT/"validation/overhead"
out.mkdir(parents=True, exist_ok=True)
store = Store(state)
result = {"method": "Three headless/background-GUI pairs in alternating order. Normal desktop, no isolation or causal equivalence claim.",
          "order": ["headless", "gui", "gui", "headless", "headless", "gui"], "runs": []}
for i, mode in enumerate(result["order"]):
    print(f"Overhead probe {i+1}/6: {mode}", flush=True)
    if mode == "headless":
        r = Runner(store).run(model, PROFILES[0], 2)
    else:
        folder = out/f"gui-{i}"
        # json.dumps safely encodes the whole command as a Lua string.
        import shlex
        cmd = ["env", "GDK_BACKEND=wayland", "GDK_SCALE=1", sys.executable, str(ROOT/"scripts/gui_check.py"),
               "--model", str(model), "--state", str(state), "--output", str(folder), "--run", "--no-capture"]
        lua = f'hl.dsp.exec_cmd({json.dumps(shlex.join(cmd))}, {{ workspace = "4 silent", float = true, size = {{1000,620}}, center = true }})'
        subprocess.run(["hyprctl", "dispatch", lua], check=True, stdout=subprocess.DEVNULL)
        deadline = time.monotonic()+90
        while not (folder/"checks.json").exists():
            if time.monotonic() > deadline:
                raise RuntimeError("GUI probe did not finish")
            time.sleep(.2)
        checks = json.loads((folder/"checks.json").read_text())
        if checks["errors"]:
            raise RuntimeError(str(checks["errors"]))
        r = next(r for r in store.history() if r["id"] == checks["run_id"])
    if r["status"] != "complete":
        raise RuntimeError(r.get("error", "Unvalidated run"))
    result["runs"].append({"mode": mode, "id": r["id"], "metrics": r["metrics"]})
    atomic_json(out/"summary.json", result)
result["observations"] = {}
for kind in ("prompt", "generation"):
    means = {mode: [r["metrics"][kind]["mean"] for r in result["runs"] if r["mode"] == mode] for mode in ("headless", "gui")}
    medians = {mode: statistics.median(v) for mode, v in means.items()}
    result["observations"][kind] = {"medians": medians, "gui_vs_headless_percent": (medians["gui"]/medians["headless"]-1)*100,
                                     "note": "Observed association only. Small sample, uncontrolled load and background GUI; not certified visible-UI overhead."}
atomic_json(out/"summary.json", result)
print(json.dumps(result["observations"], indent=2))
