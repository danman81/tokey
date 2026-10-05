"""Save repeatable local test evidence; does not run expensive live benchmarks."""
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from llm_benchmark.core import atomic_json, file_hash

p = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], cwd=ROOT, text=True, capture_output=True)
evidence = ROOT/"validation"
evidence.mkdir(exist_ok=True)
(evidence/"unit-tests.txt").write_text(p.stdout+p.stderr)
record = {"test_exit_code": p.returncode, "python": sys.version,
          "source_sha256": {str(f.relative_to(ROOT)): file_hash(f) for base in ("llm_benchmark", "scripts", "tests", "assets", "packaging")
                            for f in sorted((ROOT/base).rglob("*")) if f.is_file() and "__pycache__" not in f.parts}}
atomic_json(evidence/"release-checks.json", record)
print(p.stdout+p.stderr)
raise SystemExit(p.returncode)
