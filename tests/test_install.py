import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import os

ROOT = Path(__file__).resolve().parents[1]


class InstallTests(unittest.TestCase):
    def test_install_launch_reinstall_and_recoverable_uninstall(self):
        with tempfile.TemporaryDirectory() as root:
            prefix = Path(root)/"local"
            fake_bin = Path(root)/"bin"
            fake_bin.mkdir()
            fake_engine = fake_bin/"llama-bench"
            fake_engine.write_text("#!/bin/sh\nexit 0\n")
            fake_engine.chmod(0o755)
            env = {**os.environ, "PATH": str(fake_bin) + os.pathsep + os.environ.get("PATH", "")}
            cmd = [sys.executable, str(ROOT/"scripts/install.py"), "--prefix", str(prefix)]
            subprocess.run(cmd, check=True, capture_output=True, env=env)
            launcher = prefix/"bin/llm-benchmark"
            version = subprocess.check_output([str(launcher), "--version"], text=True).strip()
            self.assertEqual(version, "0.2.0a2")
            subprocess.run(["desktop-file-validate", str(prefix/"share/applications/net.llmbenchmark.Desktop.desktop")], check=True)
            model = prefix/"share/llm-benchmark/models/user-model.txt"
            model.parent.mkdir()
            model.write_text("preserve")
            subprocess.run(cmd, check=True, capture_output=True, env=env)
            self.assertTrue(list((prefix/"share/llm-benchmark").glob("previous-*")))
            subprocess.run(cmd+["--uninstall"], check=True, capture_output=True, env=env)
            self.assertFalse(launcher.exists())
            self.assertEqual(model.read_text(), "preserve")
            self.assertTrue(list((prefix/"share/llm-benchmark").glob("removed-*/bin/llm-benchmark")))

    def test_untracked_target_preserved(self):
        with tempfile.TemporaryDirectory() as root:
            prefix = Path(root)/"local"
            target = prefix/"bin/llm-benchmark"
            target.parent.mkdir(parents=True)
            target.write_text("user-owned")
            p = subprocess.run([sys.executable, str(ROOT/"scripts/install.py"), "--prefix", str(prefix)], capture_output=True)
            self.assertNotEqual(p.returncode, 0)
            self.assertEqual(target.read_text(), "user-owned")


if __name__ == "__main__":
    unittest.main()
