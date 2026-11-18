import json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class ScenarioLabV21Tests(unittest.TestCase):
 def test_panel_module_and_cache(self):
  h=(ROOT/"frontend/index.html").read_text(); s=(ROOT/"frontend/sw.js").read_text()
  self.assertIn('id="scenarioLab"',h); self.assertIn('src="scenario-lab.js"',h); self.assertIn("'./scenario-lab.js'",s)
 def test_dependency_engine_and_guardrails(self):
  js=(ROOT/"frontend/scenario-lab.js").read_text()
  self.assertIn("function validateGraph",js); self.assertIn("function calculate",js)
  self.assertIn("Math.min(...deps)",js); self.assertIn("no contiene infraestructura real precargada", (ROOT/"frontend/index.html").read_text())
  self.assertIn("No se puede eliminar: otros nodos dependen",js)
 def test_versions(self):
  pkg=json.loads((ROOT/"package.json").read_text()); tauri=json.loads((ROOT/"src-tauri/tauri.conf.json").read_text())
  cargo=(ROOT/"src-tauri/Cargo.toml").read_text()
  self.assertEqual(pkg["version"],"2.5.0"); self.assertEqual(tauri["version"],"2.5.0"); self.assertIn('version = "2.5.0"',cargo)
if __name__=="__main__": unittest.main()
