import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class MutualAidV19Tests(unittest.TestCase):
    def test_frontend_module_is_loaded_and_cached(self):
        html = (ROOT / "frontend/index.html").read_text()
        sw = (ROOT / "frontend/sw.js").read_text()
        self.assertIn('src="mutual-aid.js"', html)
        self.assertIn("'./mutual-aid.js'", sw)
        self.assertIn('id="mutualAidBox"', html)

    def test_capacity_guard_and_transition_graph_exist(self):
        js = (ROOT / "frontend/mutual-aid.js").read_text()
        self.assertIn("function validateCapacity", js)
        self.assertIn("function committedFor", js)
        self.assertIn("const TRANSITIONS=", js)
        self.assertIn("if(!TRANSITIONS[x.status]?.includes(next))", js)
        self.assertIn("localStorage.setItem(KEY", js)

    def test_release_versions_are_aligned(self):
        package = json.loads((ROOT / "package.json").read_text())
        tauri = json.loads((ROOT / "src-tauri/tauri.conf.json").read_text())
        cargo = (ROOT / "src-tauri/Cargo.toml").read_text()
        self.assertEqual(package["version"], "2.5.0")
        self.assertEqual(tauri["version"], "2.5.0")
        self.assertIn('version = "2.5.0"', cargo)

if __name__ == "__main__":
    unittest.main()
