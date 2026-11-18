import json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class SituationBoardV20Tests(unittest.TestCase):
 def test_panel_script_and_cache(self):
  html=(ROOT/"frontend/index.html").read_text()
  js=(ROOT/"frontend/situation-board.js").read_text()
  sw=(ROOT/"frontend/sw.js").read_text()
  self.assertIn('id="situationBoard"',html)
  self.assertIn('src="situation-board.js"',html)
  self.assertIn("'./situation-board.js'",sw)
  self.assertIn("prepper-map-incident-command-v2",js)
  self.assertIn("prepper-map-resource-registry-v1",js)
  self.assertIn("prepper-map-mutual-aid-v1",js)
 def test_read_only_quality_and_export(self):
  js=(ROOT/"frontend/situation-board.js").read_text()
  self.assertIn("function snapshot()",js)
  self.assertIn("stale_verified_resources",js)
  self.assertIn("incidents_without_assignment",js)
  self.assertIn("sitExport",js)
  self.assertNotIn("localStorage.setItem",js)
 def test_versions_aligned(self):
  pkg=json.loads((ROOT/"package.json").read_text())
  tauri=json.loads((ROOT/"src-tauri/tauri.conf.json").read_text())
  cargo=(ROOT/"src-tauri/Cargo.toml").read_text()
  self.assertEqual(pkg["version"],"2.5.0")
  self.assertEqual(tauri["version"],"2.5.0")
  self.assertIn('version = "2.5.0"',cargo)
if __name__=="__main__": unittest.main()
