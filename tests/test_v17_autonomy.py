import importlib.util, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load():
 spec=importlib.util.spec_from_file_location('calculate_autonomy',ROOT/'backend/scripts/calculate_autonomy.py')
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
class AutonomyTests(unittest.TestCase):
 def test_exact_target_coverage(self):
  r=load().calculate(2,7,{'water':56,'food':8.4,'energy':7},{'water':4,'food':.6,'energy':.5})
  self.assertEqual(r['resources']['water']['autonomy_days'],7)
  self.assertEqual(r['resources']['water']['deficit'],0)
  self.assertEqual(r['resources']['food']['coverage_percent'],100)
 def test_deficit_calculated_with_shared_extra_consumption(self):
  r=load().calculate(2,5,{'water':20},{'water':3},{'water':2})
  self.assertEqual(r['resources']['water']['daily_consumption'],8)
  self.assertEqual(r['resources']['water']['deficit'],20)
 def test_zero_consumption_is_not_division_error(self):
  r=load().calculate(1,4,{}, {})
  self.assertIsNone(r['resources']['water']['autonomy_days'])
  self.assertEqual(r['resources']['water']['coverage_percent'],100)
 def test_rejects_negative_stock(self):
  with self.assertRaises(ValueError):load().calculate(2,7,{'water':-1},{})
 def test_rejects_invalid_people_and_days(self):
  m=load()
  with self.assertRaises(ValueError):m.calculate(0,7,{}, {})
  with self.assertRaises(ValueError):m.calculate(2,400,{}, {})
if __name__=='__main__':unittest.main()
