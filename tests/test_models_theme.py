import hashlib
import io
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch

from llm_benchmark import config, core, models, theme


class Response(io.BytesIO):
    def __init__(self, data, status=200, headers=None, url="https://example.invalid/model"):
        super().__init__(data)
        self.status, self.headers, self.url = status, headers or {}, url


class DownloadTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.target = Path(self.tmp.name)/"starter.gguf"
        self.data = b"GGUFtest-only-model"
        self.pin = patch.dict(models.MODEL, {"bytes": len(self.data), "sha256": hashlib.sha256(self.data).hexdigest()})
        self.pin.start()
        self.addCleanup(self.pin.stop)

    def download(self, response):
        with patch.object(models.urllib.request, "urlopen", return_value=response):
            return models.download_starter(self.target)

    def test_valid_download_and_cached_verification(self):
        self.assertEqual(self.download(Response(self.data)).read_bytes(), self.data)
        with patch.object(models.urllib.request, "urlopen") as network:
            self.assertEqual(models.download_starter(self.target), self.target)
            network.assert_not_called()

    def test_bad_hash_rejected(self):
        with self.assertRaises(core.BenchmarkError):
            self.download(Response(b"X"*len(self.data)))
        self.assertFalse(self.target.exists())
        self.assertFalse(self.target.with_suffix(".gguf.part").exists())

    def test_resume_exact_range(self):
        self.target.with_suffix(".gguf.part").write_bytes(self.data[:4])
        self.download(Response(self.data[4:], 206, {"Content-Range": f"bytes 4-{len(self.data)-1}/{len(self.data)}"}))
        self.assertEqual(self.target.read_bytes(), self.data)

    def test_server_ignoring_range_restarts(self):
        self.target.with_suffix(".gguf.part").write_bytes(b"junk")
        self.download(Response(self.data))
        self.assertEqual(self.target.read_bytes(), self.data)

    def test_wrong_range_and_insecure_redirect(self):
        for response in (Response(self.data, 206, {"Content-Range": "wrong"}),
                         Response(self.data, url="http://example.invalid")):
            with self.assertRaises(core.BenchmarkError):
                self.download(response)

    def test_cancel_before_network(self):
        event = threading.Event()
        event.set()
        with patch.object(models.urllib.request, "urlopen") as network, self.assertRaises(core.Cancelled):
            models.download_starter(self.target, event)
        network.assert_not_called()

    def test_corrupt_existing_model_not_overwritten(self):
        self.target.write_bytes(b"user data")
        with self.assertRaises(core.BenchmarkError):
            models.download_starter(self.target)
        self.assertEqual(self.target.read_bytes(), b"user data")


class ThemeTests(unittest.TestCase):
    def test_locked_mascot(self):
        asset = Path(__file__).resolve().parents[1]/"assets/tokey-mascot.txt"
        expected = b"(\\_/)\n(='.'=)\n(\")_(\")\n"
        self.assertEqual(asset.read_bytes(), expected)
        brand = (asset.parent.parent/"docs/BRAND.md").read_text()
        self.assertIn("```text\n"+expected.decode()+"```", brand)

    def test_fallback_text_contrast(self):
        with tempfile.TemporaryDirectory() as root:
            name, p = theme.read_palette(root)
        self.assertEqual(name, "Netrunner fallback")
        for text in ("text", "secondary", "light_foreground", "bright_foreground"):
            for bg in ("background", "lighter_background"):
                self.assertGreaterEqual(theme.contrast(p[text], p[bg]), 4.5)

    def test_theme_is_data_not_css_code(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root)/".local/state/omarchy/current/theme/colors.toml"
            path.parent.mkdir(parents=True)
            path.write_text('mode="dark"\naccent="red; malicious"\nbackground="#100510"\n')
            path.parent.with_name("theme.name").write_text("example")
            name, p = theme.read_palette(root)
        self.assertEqual(name, "Example")
        self.assertEqual(p["background"], "#100510")
        self.assertEqual(p["accent"], theme.FALLBACK["accent"])

    def test_light_theme_keeps_dark_product(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root)/".local/state/omarchy/current/theme/colors.toml"
            path.parent.mkdir(parents=True)
            path.write_text('mode="light"\nbackground="#ffffff"\n')
            _, p = theme.read_palette(root)
        self.assertEqual(p["background"], theme.FALLBACK["background"])

    def test_about_uses_local_coffee_branding_and_accessible_trigger(self):
        assets = Path(__file__).resolve().parents[1] / "llm_benchmark" / "assets"
        surface = (assets / "tokey-cockpit.html").read_text()
        adapter = (assets / "production-adapter.js").read_text()
        self.assertIn('aria-label="About Tokey"', surface)
        self.assertIn('id="tc-about" popover role="dialog"', surface)
        self.assertIn("border:1px solid var(--tc-accent);border-radius:9px", surface)
        self.assertIn('src="kofi-cup.png"', surface)
        self.assertIn('class="tc-about-rabbit-emoji">🐇', surface)
        self.assertIn("#tc-about:popover-open .tc-about-rabbit-emoji{animation:tc-rabbit-dance 2s linear 1.5s infinite}", surface)
        self.assertIn("its maintenance.&nbsp;❤️", surface)
        self.assertIn('id="tc-about-rabbit" class="tc-brand tc-about-brand"', surface)
        self.assertIn(".tc-head .tc-rabbit').cloneNode(true)", adapter)
        self.assertTrue((assets / "kofi-cup.png").is_file())
        self.assertIn("event.key === 'Enter'", adapter)

    def test_all_export_formats_are_available(self):
        assets = Path(__file__).resolve().parents[1] / "llm_benchmark" / "assets"
        surface = (assets / "tokey-cockpit.html").read_text()
        adapter = (assets / "production-adapter.js").read_text()
        for format_name in ("GIF", "PNG", "MP4"):
            self.assertIn(f'<option value="{format_name}"', surface)
        self.assertNotIn("option.disabled", adapter)
        self.assertIn("Copy results · ' + el('format').value", adapter)


class ConfigTests(unittest.TestCase):
    def test_shipped_config_has_current_pinned_runners(self):
        loaded = config.load_config(config.default_config_path())
        self.assertEqual(loaded.system_name, "")
        self.assertEqual(len(loaded.runners), 10)
        self.assertIn("gemma-3-4b", [item.id for item in loaded.runners])
        self.assertNotIn("spark-x2.5-4b", [item.id for item in loaded.runners])
        self.assertTrue(all(len(item.sha256) == 64 and item.bytes > 0 for item in loaded.runners))
        self.assertNotIn("easter", config.default_config_path().read_text().lower())

    def test_empty_optional_values_stay_empty(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "config.toml"
            path.write_text("runners = []\n")
            loaded = config.load_config(path)
        self.assertEqual(loaded.system_name, "")
        self.assertEqual(loaded.runners, ())

    def test_unknown_runner_is_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "config.toml"
            path.write_text('runners = ["made-up"]\n')
            with self.assertRaises(ValueError):
                config.load_config(path)


if __name__ == "__main__":
    unittest.main()
