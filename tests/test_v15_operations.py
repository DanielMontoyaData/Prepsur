import importlib.util, json, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load():
    path=ROOT/'backend/scripts/analyze_route_exposure.py'
    spec=importlib.util.spec_from_file_location('analyze_route_exposure',path)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod

class V15OperationsTests(unittest.TestCase):
    def test_assignment_controls_and_sitrep_are_wired(self):
        html=(ROOT/'frontend/index.html').read_text()
        js=(ROOT/'frontend/ops-center.js').read_text()
        for item in ['icResourceSelect','icAssignmentStatus','icAssignResource','icCopySitrep','icAssignments']:
            self.assertIn(item,html)
            self.assertIn(item,js)
        self.assertIn("prepper-map-resource-registry-v1",js)
        self.assertIn("x.assignments.push(assignment)",js)
    def test_assignment_states_are_documented(self):
        doc=(ROOT/'docs/operations-v15.md').read_text()
        for state in ['solicitado','asignado','en_camino','en_sitio','liberado','cancelado']:
            self.assertIn(state,doc)
    def test_route_exposure_measures_polygon_intersection(self):
        mod=load()
        with tempfile.TemporaryDirectory() as td:
            td=Path(td)
            routes={'type':'FeatureCollection','features':[{'type':'Feature','properties':{'name':'Test route'},'geometry':{'type':'LineString','coordinates':[[-75.60,6.15],[-75.58,6.15]]}}]}
            hazards={'type':'FeatureCollection','features':[{'type':'Feature','properties':{'name':'Flood zone'},'geometry':{'type':'Polygon','coordinates':[[[-75.595,6.145],[-75.585,6.145],[-75.585,6.155],[-75.595,6.155],[-75.595,6.145]]]}}]}
            rp=td/'routes.geojson';hp=td/'hazard.geojson';out=td/'report.json'
            rp.write_text(json.dumps(routes));hp.write_text(json.dumps(hazards))
            report,overlaps=mod.run(rp,[hp],out)
            self.assertEqual(report['summary']['routes_analyzed'],1)
            self.assertEqual(report['summary']['routes_with_intersections'],1)
            self.assertGreater(report['routes'][0]['exposures'][0]['route_percent'],0)
            self.assertTrue(overlaps.exists())
            self.assertIn('No indica peligro',report['routes'][0]['interpretation'])
    def test_route_without_intersection_not_called_safe(self):
        mod=load()
        with tempfile.TemporaryDirectory() as td:
            td=Path(td)
            routes={'type':'FeatureCollection','features':[{'type':'Feature','properties':{},'geometry':{'type':'LineString','coordinates':[[-75.60,6.15],[-75.59,6.15]]}}]}
            hazards={'type':'FeatureCollection','features':[{'type':'Feature','properties':{},'geometry':{'type':'Polygon','coordinates':[[[-75.50,6.10],[-75.49,6.10],[-75.49,6.11],[-75.50,6.11],[-75.50,6.10]]]}}]}
            rp=td/'r.geojson';hp=td/'h.geojson';out=td/'o.json'
            rp.write_text(json.dumps(routes));hp.write_text(json.dumps(hazards))
            report,_=mod.run(rp,[hp],out)
            self.assertEqual(report['summary']['routes_with_intersections'],0)
            self.assertIn('NO demuestra seguridad',report['routes'][0]['interpretation'])
if __name__=='__main__': unittest.main()
