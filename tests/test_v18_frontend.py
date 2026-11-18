import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class ZoneCoverageFrontendTests(unittest.TestCase):
 def test_viewer_and_file_import_are_present(self):
  html=(ROOT/'frontend/index.html').read_text();js=(ROOT/'frontend/zone-coverage.js').read_text()
  for item in ['zoneCoverageBox','zcReportFile','zcSummary','zcTable','zone-coverage.js']:self.assertIn(item,html)
  for item in ['JSON.parse','10*1024*1024','resources_inside','limitations']:self.assertIn(item,js)
if __name__=='__main__':unittest.main()
