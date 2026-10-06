import copy
import dataclasses
import json
import os
from pathlib import Path
import statistics
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

from llm_benchmark import core


def fixture():
    """Synthetic test data only: never bundled into production history."""
    rows = []
    for tokens, kind in ((128, "prompt"), (32, "generation")):
        ns = [1000000000, 1100000000, 1200000000, 1000000000, 900000000]
        rates = [tokens * 1e9 / n for n in ns]
        rows.append(dict(n_prompt=tokens if kind == "prompt" else 0,
                         n_gen=tokens if kind == "generation" else 0,
                         n_threads=2, n_gpu_layers=0, n_batch=512, n_ubatch=128,
                         n_depth=0, poll=0, type_k="f16", type_v="f16", backends="CPU",
                         devices="none", flash_attn=0, build_commit="test-fixture",
                         model_n_params=100, model_filename="/private/test.gguf",
                         samples_ns=ns, samples_ts=rates, avg_ns=int(statistics.mean(ns)),
                         stddev_ns=int(statistics.stdev(ns)), avg_ts=statistics.mean(rates),
                         stddev_ts=statistics.stdev(rates)))
    return rows


def report():
    rows, metrics = core.validate_output(json.dumps(fixture()), core.PROFILES[0], 2)
    return dict(schema=1, id="20261003T000000Z-aaaaaaaa", started="2026-10-03T00:00:00Z",
                status="complete", suite=core.SUITE, threads=2,
                profile=dataclasses.asdict(core.PROFILES[0]), raw_rows=rows, metrics=metrics,
                comparison_key="test-only", model={"path": "/private/test.gguf", "name": "test.gguf"},
                command=["/private/engine"], engine={"binary": "/private/engine", "files": {"/private/lib.so": "123"}})


class CalculationTests(unittest.TestCase):
    def validate(self, rows):
        return core.validate_output(json.dumps(rows), core.PROFILES[0], 2)

    def test_recalculate_exact_samples(self):
        _, metrics = self.validate(fixture())
        self.assertAlmostEqual(metrics["prompt"]["rates"][1], 128 / 1.1)
        self.assertAlmostEqual(metrics["generation"]["mean"], statistics.mean([32 / x for x in (1, 1.1, 1.2, 1, .9)]))

    def test_reject_bad_workload_settings(self):
        for key, bad in (("n_threads", 4), ("n_gpu_layers", 1), ("n_prompt", 127),
                         ("n_batch", 1024), ("n_ubatch", 512), ("n_depth", 1),
                         ("poll", 50), ("type_k", "q8_0"), ("type_v", "q8_0"),
                         ("backends", "CUDA"), ("devices", "GPU0"), ("flash_attn", 1)):
            with self.subTest(key=key):
                rows = fixture()
                rows[0][key] = bad
                with self.assertRaises(core.BenchmarkError):
                    self.validate(rows)

    def test_boolean_counts_not_accepted_as_integers(self):
        rows = fixture()
        rows[0]["n_gen"] = False
        with self.assertRaises(core.BenchmarkError):
            self.validate(rows)

    def test_gpu_execution_identity_is_verified(self):
        rows = fixture()
        for row in rows:
            row.update(n_gpu_layers=999, backends="Vulkan", devices="Vulkan0")
        _, metrics = core.validate_output(json.dumps(rows), core.PROFILES[0], 2, "Vulkan0")
        self.assertIn("generation", metrics)
        rows[0]["devices"] = "none"
        with self.assertRaises(core.BenchmarkError):
            core.validate_output(json.dumps(rows), core.PROFILES[0], 2, "Vulkan0")

    def test_reject_invalid_samples(self):
        for value in ([], [1], [0]*5, [-1]*5, [True]*5, [1.2]*5, None):
            with self.subTest(value=value):
                rows = fixture()
                rows[0]["samples_ns"] = value
                with self.assertRaises(core.BenchmarkError):
                    self.validate(rows)

    def test_reject_corrupted_aggregates(self):
        for key in ("avg_ns", "avg_ts", "stddev_ts"):
            rows = fixture()
            rows[0][key] *= 2
            with self.subTest(key=key), self.assertRaises(core.BenchmarkError):
                self.validate(rows)

    def test_upstream_integer_duration_sd_not_used(self):
        rows = fixture()
        rows[0]["stddev_ns"] = 99999999999999
        _, metrics = self.validate(rows)
        self.assertAlmostEqual(metrics["prompt"]["stdev"], statistics.stdev(rows[0]["samples_ts"]))

    def test_reject_sample_rate_disagreement(self):
        rows = fixture()
        rows[0]["samples_ts"][0] += 1
        with self.assertRaises(core.BenchmarkError):
            self.validate(rows)

    def test_reject_changed_identity(self):
        rows = fixture()
        rows[1]["build_commit"] = "different"
        with self.assertRaises(core.BenchmarkError):
            self.validate(rows)

    def test_reject_incomplete_duplicate_and_nan(self):
        for rows in (fixture()[:1], [fixture()[0]]*2, {}, [None, None]):
            with self.subTest(rows=rows), self.assertRaises(core.BenchmarkError):
                self.validate(rows)
        with self.assertRaises(core.BenchmarkError):
            core.validate_output('[NaN,NaN]', core.PROFILES[0], 2)

    def test_reject_injection_and_bad_threads(self):
        for threads in (0, -1, True, "2", 100000):
            with self.assertRaises(core.BenchmarkError):
                core.build_command("llama-bench", "model.gguf", core.PROFILES[0], threads)
        cmd = core.build_command("llama-bench", "model;not-a-command.gguf", core.PROFILES[0], 1)
        self.assertEqual(cmd[2], "model;not-a-command.gguf")
        self.assertIn("--offline", cmd)

    def test_comparisons_fail_closed(self):
        a = report()
        b = copy.deepcopy(a)
        self.assertTrue(core.comparable(a, b)[0])
        b["comparison_key"] = "different"
        self.assertFalse(core.comparable(a, b)[0])
        b["status"] = "cancelled"
        self.assertFalse(core.comparable(a, b)[0])
        self.assertFalse(core.comparable({"status": "complete"}, {"status": "complete"})[0])


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.store = core.Store(self.tmp.name)

    def test_roundtrip_and_privacy(self):
        r = report()
        self.store.save(r)
        self.assertEqual(self.store.history(), [r])
        target = Path(self.tmp.name)/"export.json"
        self.store.export(r, target)
        self.assertNotIn("/private", target.read_text())
        self.assertEqual(target.stat().st_mode & 0o777, 0o600)
        self.assertEqual(self.store.load(target)["metrics"], r["metrics"])

    def test_corruption_is_not_loaded(self):
        self.store.save(report())
        path = next(self.store.runs.glob("*/report.json"))
        content = json.loads(path.read_text())
        content["report"]["metrics"]["prompt"]["mean"] += 1
        core.atomic_json(path, content)
        self.assertEqual(self.store.history(), [])

    def test_forged_checksum_does_not_skip_calculation(self):
        r = report()
        r["metrics"]["generation"]["mean"] += 1
        self.store.save(r)
        self.assertEqual(self.store.history(), [])

    def test_path_traversal_rejected(self):
        r = report()
        r["id"] = "../../outside"
        with self.assertRaises(core.BenchmarkError):
            self.store.save(r)

    def test_interrupted_run_recovery(self):
        r = report()
        r["status"] = "preparing"
        self.store.save(r)
        self.store.recover()
        self.assertEqual(self.store.history()[0]["status"], "interrupted")

    def test_recovery_respects_active_lock(self):
        r = report()
        r["status"] = "preparing"
        self.store.save(r)
        with open(self.store.root/"runner.lock", "a+") as lock:
            core.fcntl.flock(lock, core.fcntl.LOCK_EX | core.fcntl.LOCK_NB)
            self.store.recover()
            self.assertEqual(self.store.history()[0]["status"], "preparing")
            with self.assertRaises(core.BenchmarkError):
                core.Runner(self.store).run("anything", core.PROFILES[0], 1)

    def test_missing_model_fails_with_no_metrics(self):
        r = core.Runner(self.store).run("/does-not-exist.gguf", core.PROFILES[0], 1)
        self.assertEqual(r["status"], "failed")
        self.assertEqual(r["metrics"], {})
        self.assertEqual(self.store.history()[0]["status"], "failed")

    def test_invalid_gguf_is_rejected(self):
        path = Path(self.tmp.name)/"invalid.gguf"
        path.write_bytes(b"not a model")
        with self.assertRaises(core.BenchmarkError):
            core.validate_model(path)

    def test_error_paths_removed_from_export(self):
        r = report()
        r.update(status="failed", error="Failed to read /private/secret/file")
        target = Path(self.tmp.name)/"export.json"
        self.store.export(r, target)
        self.assertNotIn("/private", target.read_text())


class ProcessTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def run_process(self, program, event=None, timeout=2):
        return core.process([sys.executable, "-c", program], event or threading.Event(),
                            self.root/"out", self.root/"err", timeout)

    def test_output_and_monotonic_elapsed(self):
        out, err, elapsed = self.run_process("import sys; print('ok'); print('warning',file=sys.stderr)")
        self.assertEqual(out, "ok\n")
        self.assertEqual(err, "warning\n")
        self.assertGreater(elapsed, 0)

    def test_timeout_is_bounded(self):
        start = time.monotonic()
        with self.assertRaises(core.BenchmarkError):
            self.run_process("import time; time.sleep(20)", timeout=.1)
        self.assertLess(time.monotonic()-start, 4)

    def test_cancel_preserves_raw_evidence(self):
        event = threading.Event()
        timer = threading.Timer(.2, event.set)
        timer.start()
        with self.assertRaises(core.Cancelled):
            self.run_process("import time; print('partial',flush=True); time.sleep(20)", event)
        timer.join()
        self.assertIn("partial", (self.root/"out").read_text())

    def test_nonzero_exit_fails(self):
        with self.assertRaises(core.BenchmarkError):
            self.run_process("raise SystemExit(3)")

    def test_clock_jump_is_rejected(self):
        with patch.object(core.time, "time_ns", side_effect=[0, 1000000000000]), self.assertRaises(core.BenchmarkError):
            self.run_process("print('ok')")

    def test_no_supervisor_fails_closed(self):
        with patch.object(core.shutil, "which", return_value=None), self.assertRaises(core.BenchmarkError):
            self.run_process("print('ok')")

    def test_flood_output_is_bounded(self):
        with patch.object(core, "MAX_OUTPUT", 1000), self.assertRaises(core.BenchmarkError):
            self.run_process("print('x'*10000)")


class CompatibilityProbeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.model = Path(self.tmp.name) / "model.gguf"
        self.model.write_bytes(b"GGUF" + b"test")

    def test_success_requires_load_evidence_for_exact_model(self):
        row = {"n_prompt": 1, "n_gen": 0, "model_filename": str(self.model.resolve()),
               "model_n_params": 100}
        with patch.object(core, "process", return_value=(json.dumps([row]), "", 1)) as run:
            core.probe_model("/engine", self.model)
        command = run.call_args.args[0]
        self.assertIn("--offline", command)
        self.assertEqual(command[command.index("-n") + 1], "0")

    def test_gpu_probe_requests_full_offload_and_exact_device(self):
        row = {"n_prompt": 1, "n_gen": 0, "model_filename": str(self.model.resolve()),
               "model_n_params": 100}
        with patch.object(core, "process", return_value=(json.dumps([row]), "", 1)) as run:
            core.probe_model("/engine", self.model, device="Vulkan0")
        command = run.call_args.args[0]
        self.assertEqual(command[command.index("-ngl") + 1], "999")
        self.assertEqual(command[command.index("-dev") + 1], "Vulkan0")

    def test_engine_failure_is_reported_as_incompatibility(self):
        with patch.object(core, "process", side_effect=core.BenchmarkError("exit 1")), \
                self.assertRaisesRegex(core.BenchmarkError, "not compatible"):
            core.probe_model("/engine", self.model)

    def test_cancellation_is_not_misreported_as_incompatibility(self):
        with patch.object(core, "process", side_effect=core.Cancelled("stopped")), \
                self.assertRaises(core.Cancelled):
            core.probe_model("/engine", self.model)


if __name__ == "__main__":
    unittest.main()
