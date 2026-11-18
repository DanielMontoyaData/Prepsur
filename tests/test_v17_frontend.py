import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class AutonomyFrontendTests(unittest.TestCase):
 def test_panel_and_script_loaded(self):
  html=(ROOT/'frontend/index.html').read_text()
  sw=(ROOT/'frontend/sw.js').read_text()
  for token in ['autonomyBox','auPeople','auDays','auCalculate','auExport','autonomy.js']:
   self.assertIn(token,html)
  self.assertIn("'./autonomy.js'",sw)
 def test_scenario_persistence_and_exports(self):
  js=(ROOT/'frontend/autonomy.js').read_text()
  for token in ['localStorage','application/json','text/csv','coverage','deficit']:
   self.assertIn(token,js)
if __name__=='__main__':unittest.main()
