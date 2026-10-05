"""Create a deterministic source archive without models, secrets or local results."""
import gzip
import hashlib
import io
from pathlib import Path
import sys
import tarfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from llm_benchmark import __version__

name = "llm-benchmark-"+__version__
files = [ROOT/p for p in ("README.md", "LICENSE", "NOTICE.md", "CHANGELOG.md")]
for directory in ("llm_benchmark", "assets", "packaging", "scripts", "tests", "docs"):
    files += [p for p in (ROOT/directory).rglob("*") if p.is_file() and "__pycache__" not in p.parts]
buffer = io.BytesIO()
with tarfile.open(fileobj=buffer, mode="w", format=tarfile.PAX_FORMAT) as archive:
    for path in sorted(files):
        data = path.read_bytes()
        entry = tarfile.TarInfo(name+"/"+str(path.relative_to(ROOT)))
        entry.size, entry.mtime, entry.mode = len(data), 0, 0o644
        archive.addfile(entry, io.BytesIO(data))
dist = ROOT/"dist"
dist.mkdir(exist_ok=True)
target = dist/(name+".tar.gz")
target.write_bytes(gzip.compress(buffer.getvalue(), mtime=0))
sha = hashlib.sha256(target.read_bytes()).hexdigest()
(dist/(name+".sha256")).write_text(f"{sha}  {target.name}\n")
(dist/"PKGBUILD").write_text((ROOT/"packaging/PKGBUILD").read_text().replace("REPLACE_WITH_RELEASE_SHA256", sha))
print(target)
print(sha)
