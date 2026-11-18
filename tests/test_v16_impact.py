import importlib.util, json, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load():
    spec=importlib.util.spec_from_file_location('assess_incident_impact',ROOT/'backend/scripts/assess_incident_impact.py')
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod
class IncidentImpactTests(unittest.TestCase):
    def test_counts_assets_and_hazard_intersections(self):
        mod=load()
        with tempfile.TemporaryDirectory() as td:
            td=Path(td)
            assets={'type':'FeatureCollection','features':[
              {'type':'Feature','properties':{'name':'Health post','category':'health'},'geometry':{'type':'Point','coordinates':[-75.60,6.15]}},
              {'type':'Feature','properties':{'name':'Far asset','category':'water'},'geometry':{'type':'Point','coordinates':[-75.40,6.15]}}]}
            hazards={'type':'FeatureCollection','features':[{'type':'Feature','properties':{'name':'Flood zone'},'geometry':{'type':'Polygon','coordinates':[[[-75.605,6.145],[-75.595,6.145],[-75.595,6.155],[-75.605,6.155],[-75.605,6.145]]]}}]}
            ap=td/'assets.geojson';hp=td/'hazard.geojson';ap.write_text(json.dumps(assets));hp.write_text(json.dumps(hazards))
            result=mod.assess(6.15,-75.60,500,[ap],[hp])
            self.assertEqual(result['summary']['assets_within_radius'],1)
            self.assertEqual(result['summary']['assets_by_category']['health'],1)
            self.assertEqual(result['summary']['hazard_polygons_intersecting'],1)
            self.assertTrue(result['limitations'])
    def test_rejects_invalid_radius(self):
        mod=load()
        with self.assertRaises(ValueError): mod.assess(6.15,-75.60,10,[],[])
    def test_rejects_invalid_coordinates(self):
        mod=load()
        with self.assertRaises(ValueError): mod.assess(100,-75.60,500,[],[])
    def test_rejects_non_feature_collection(self):
        mod=load()
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'bad.geojson';p.write_text(json.dumps({'type':'Feature','geometry':None}))
            with self.assertRaises(ValueError): mod.assess(6.15,-75.60,500,[p],[])
if __name__=='__main__':unittest.main()
