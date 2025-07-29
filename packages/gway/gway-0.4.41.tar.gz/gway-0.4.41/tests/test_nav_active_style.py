import unittest
import importlib.util
from pathlib import Path
from unittest import mock

# Load projects/web/nav.py dynamically since projects is not a package
nav_path = Path(__file__).resolve().parents[1] / "projects" / "web" / "nav.py"
spec = importlib.util.spec_from_file_location("webnav", nav_path)
nav = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nav)


class FakeQuery:
    def __init__(self, params=None):
        self._params = params or {}
    def get(self, key, default=None):
        return self._params.get(key, default)

class FakeRequest:
    def __init__(self, params=None):
        self.query = FakeQuery(params)

class FakeCookies:
    def __init__(self, store=None):
        self.store = store or {}
    def get(self, name, default=None):
        return self.store.get(name, default)

class FakeApp:
    def __init__(self, enabled=True):
        self.enabled = enabled
    def is_setup(self, name):
        return self.enabled


class ActiveStyleTests(unittest.TestCase):
    def setUp(self):
        # Patch list_styles to return a predictable order
        self.styles = [
            ("global", "classic-95.css"),
            ("global", "dark-material.css"),
        ]
        self.list_patch = mock.patch.object(nav, "list_styles", return_value=self.styles)
        self.list_patch.start()

        # Preserve and replace gw.web components
        self.orig_app = nav.gw.web.app
        self.orig_cookies = nav.gw.web.cookies
        nav.gw.web.app = FakeApp(True)
        nav.gw.web.cookies = FakeCookies()

        # Preserve original request object
        self.orig_request = nav.request

    def tearDown(self):
        self.list_patch.stop()
        nav.gw.web.app = self.orig_app
        nav.gw.web.cookies = self.orig_cookies
        nav.request = self.orig_request

    def test_query_param_overrides_cookie(self):
        nav.gw.web.cookies.store = {"css": "dark-material.css"}
        nav.request = FakeRequest({"css": "classic-95.css"})
        result = nav.active_style()
        self.assertEqual(result, "/static/styles/classic-95.css")

    def test_cookie_used_when_no_query(self):
        nav.gw.web.cookies.store = {"css": "dark-material.css"}
        nav.request = FakeRequest({})
        result = nav.active_style()
        self.assertEqual(result, "/static/styles/dark-material.css")

    def test_fallback_to_first_style(self):
        nav.gw.web.cookies.store = {}
        nav.request = FakeRequest({})
        result = nav.active_style()
        self.assertEqual(result, "/static/styles/classic-95.css")


if __name__ == "__main__":
    unittest.main()

