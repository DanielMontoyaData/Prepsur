import importlib.util, json, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load():
 spec=importlib.util.spec_from_file_location('assess_zone_coverage',ROOT/'backend/scripts/assess_zone_coverage.py')
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
class ZoneCoverageTests(unittest.TestCase):
 def test_zone_counts_resource_and_population_based_demand(self):
  m=load()
  with tempfile.TemporaryDirectory() as td:
   td=Path(td)
   zones={'type':'FeatureCollection','features':[{'type':'Feature','properties':{'name':'Sector A','population':100},'geometry':{'type':'Polygon','coordinates':[[[-75.61,6.14],[-75.59,6.14],[-75.59,6.16],[-75.61,6.16],[-75.61,6.14]]]}}]}
   resources={'type':'FeatureCollection','features':[{'type':'Feature','properties':{'name':'Puesto salud','category':'health'},'geometry':{'type':'Point','coordinates':[-75.60,6.15]}},{'type':'Feature','properties':{'name':'Tanque','category':'water'},'geometry':{'type':'Point','coordinates':[-75.70,6.15]}}]}
   zp=td/'zones.geojson';rp=td/'resources.geojson';zp.write_text(json.dumps(zones));rp.write_text(json.dumps(resources))
   result=m.analyze(zp,rp,demand_rates={'water':4})
   z=result['zones'][0]
   self.assertEqual(z['resources_inside'],1)
   self.assertEqual(z['resources_by_category']['health'],1)
   self.assertEqual(z['estimated_demand']['water']['estimated_daily_requirement'],400)
   self.assertGreater(z['nearest_resource_distance_m_by_category']['water'],0)
 def test_missing_population_is_not_fabricated(self):
  m=load()
  with tempfile.TemporaryDirectory() as td:
   td=Path(td);zp=td/'z.json';rp=td/'r.json'
   zp.write_text(json.dumps({'type':'FeatureCollection','features':[{'type':'Feature','properties':{'name':'No census'},'geometry':{'type':'Polygon','coordinates':[[[-75.61,6.14],[-75.59,6.14],[-75.59,6.16],[-75.61,6.16],[-75.61,6.14]]]}}]}))
   rp.write_text(json.dumps({'type':'FeatureCollection','features':[]}))
   z=m.analyze(zp,rp)['zones'][0]
   self.assertIsNone(z['population'])
   self.assertFalse(z['data_quality']['population_available'])
 def test_invalid_population_rejected(self):
  m=load()
  with tempfile.TemporaryDirectory() as td:
   td=Path(td);zp=td/'z.json';rp=td/'r.json'
   zp.write_text(json.dumps({'type':'FeatureCollection','features':[{'type':'Feature','properties':{'population':-1},'geometry':{'type':'Polygon','coordinates':[[[-75.61,6.14],[-75.59,6.14],[-75.59,6.16],[-75.61,6.16],[-75.61,6.14]]]}}]}))
   rp.write_text(json.dumps({'type':'FeatureCollection','features':[]}))
   with self.assertRaises(ValueError):m.analyze(zp,rp)
if __name__=='__main__':unittest.main()
