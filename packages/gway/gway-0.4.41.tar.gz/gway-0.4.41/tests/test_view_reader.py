import unittest
import tempfile
import importlib.util
from pathlib import Path
from unittest.mock import patch
from gway import gw

spec = importlib.util.spec_from_file_location(
    "site", Path(__file__).resolve().parents[1] / "projects" / "web" / "site.py"
)
site = importlib.util.module_from_spec(spec)
spec.loader.exec_module(site)


class ViewReaderTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        (self.base / "README.rst").write_text("Test RST resource.")
        (self.base / "README.md").write_text("# Test MD resource")
        self.patcher = patch.object(
            gw,
            "resource",
            side_effect=lambda *p, **k: Path(self.base, *p),
        )
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        self.tmp.cleanup()

    def test_view_reader_renders(self):
        html = site.view_reader(tome="README", origin="root")
        self.assertIn("Test RST resource", html)

    def test_hidden_or_private_denied(self):
        self.assertIn("Access denied", site.view_reader(tome=".secret", origin="root"))
        self.assertIn("Access denied", site.view_reader(tome="_private", origin="root"))

    def test_static_origin_subfolder(self):
        static_dir = self.base / "data" / "static" / "proj"
        static_dir.mkdir(parents=True)
        (static_dir / "README.rst").write_text("Static Doc")
        html = site.view_reader(tome="proj/README", origin="static")
        self.assertIn("Static Doc", html)

    def test_implicit_static_and_directory(self):
        static_dir = self.base / "data" / "static" / "dir"
        static_dir.mkdir(parents=True)
        (static_dir / "README.rst").write_text("Dir Doc")
        html = site.view_reader(tome="dir")
        self.assertIn("Dir Doc", html)

        html = site.view_reader("dir")
        self.assertIn("Dir Doc", html)

        html = site.view_reader(tome="dir/")
        self.assertIn("Dir Doc", html)

        html = site.view_reader("dir/")
        self.assertIn("Dir Doc", html)


if __name__ == "__main__":
    unittest.main()
