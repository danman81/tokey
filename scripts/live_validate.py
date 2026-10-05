"""Run real CPU workloads and a separate Decimal arithmetic audit."""
import argparse
from decimal import Decimal, localcontext
import json
from pathlib import Path
import sys
import threading

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from llm_benchmark.core import PROFILES, Runner, Store, atomic_json

parser = argparse.ArgumentParser()
parser.add_argument("--model", required=True)
parser.add_argument("--state", default="validation/state")
parser.add_argument("--output", default="validation/live-audit.json")
args = parser.parse_args()
store = Store(args.state)
audit = {"method": "Independent Decimal(50-digit) arithmetic on real raw nanoseconds; not a clock calibration", "runs": [], "errors": []}
for profile in PROFILES:
    print("REAL WORKLOAD:", profile.key, flush=True)
    r = Runner(store).run(args.model, profile, 2, progress=lambda s: print(s, flush=True))
    item = {"id": r["id"], "profile": profile.key, "status": r["status"], "metrics": {}}
    if r["status"] != "complete":
        audit["errors"].append(r.get("error", "Run failed"))
    else:
        with localcontext() as context:
            context.prec = 50
            for kind, n in (("prompt", profile.prompt), ("generation", profile.generation)):
                raw = next(row for row in r["raw_rows"] if row["n_prompt" if kind == "prompt" else "n_gen"] == n)
                rates = [Decimal(n) * Decimal(10**9) / Decimal(t) for t in raw["samples_ns"]]
                mean = sum(rates)/len(rates)
                sd = (sum((x-mean)**2 for x in rates)/(len(rates)-1)).sqrt()
                actual = r["metrics"][kind]
                relative = abs(Decimal(str(actual["mean"]))-mean)/mean
                relative_sd = abs(Decimal(str(actual["stdev"]))-sd)/sd if sd else Decimal(0)
                if max(relative, relative_sd) > Decimal("1e-12"):
                    audit["errors"].append(f"Independent arithmetic mismatch: {r['id']} {kind}")
                item["metrics"][kind] = {"mean": float(mean), "sample_sd": float(sd), "cv_percent": actual["cv_percent"],
                                         "mean_relative_difference": str(relative), "sd_relative_difference": str(relative_sd)}
        item["warnings"] = r["warnings"]
    audit["runs"].append(item)
    atomic_json(args.output, audit)

print("REAL CANCELLATION", flush=True)
cancel = threading.Event()
timer = threading.Timer(1.5, cancel.set)
timer.start()
r = Runner(store).run(args.model, PROFILES[2], 2, cancel)
timer.join()
audit["cancelled_run"] = {"id": r["id"], "status": r["status"], "metrics": r["metrics"]}
if r["status"] != "cancelled" or r["metrics"]:
    audit["errors"].append("Cancelled real run improperly produced a complete result")
atomic_json(args.output, audit)
print(json.dumps(audit, indent=2))
raise SystemExit(1 if audit["errors"] else 0)
