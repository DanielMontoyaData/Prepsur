import importlib.util, json, sqlite3, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/'backend/scripts'/f'{name}.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
class ReleaseQualityTests(unittest.TestCase):
    def test_catalog_audit_distinguishes_unavailable_data(self):
        report=load('quality_report').audit(ROOT)
        self.assertEqual(report['summary']['catalog_entries'],26)
        self.assertEqual(report['summary']['downloaded'],0)
        self.assertTrue(all(x['quality']=='no_disponible' for x in report['items']))
    def test_geojson_bbox_and_integrity(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/'frontend/data').mkdir(parents=True)
            gj={'type':'FeatureCollection','features':[{'type':'Feature','geometry':{'type':'Point','coordinates':[-75.6,6.15]},'properties':{}}]}
            (root/'frontend/data/one.geojson').write_text(json.dumps(gj))
            manifest={'items':[{'status':'downloaded','frontend_file':'data/one.geojson','features':1,'source_url':'https://example.org','license_note':'test','retrieved_at':'2026-11-17T00:00:00+00:00'}]}
            (root/'frontend/data/manifest.json').write_text(json.dumps(manifest))
            result=load('quality_report').audit(root,max_age_days=365)
            self.assertEqual(result['items'][0]['bbox'],[-75.6,6.15,-75.6,6.15])
            self.assertEqual(len(result['items'][0]['sha256']),64)
    def test_rejects_path_traversal(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/'frontend/data').mkdir(parents=True)
            (root/'frontend/data/manifest.json').write_text(json.dumps({'items':[{'status':'downloaded','frontend_file':'../../secret'}]}))
            result=load('quality_report').audit(root)
            self.assertIn('archivo_faltante_o_ruta_insegura',result['items'][0]['issues'])
    def test_mbtiles_converter_emits_tile_index(self):
        with tempfile.TemporaryDirectory() as td:
            td=Path(td);src=td/'test.mbtiles';out=td/'tiles';db=sqlite3.connect(src)
            db.execute('CREATE TABLE metadata (name TEXT,value TEXT)')
            db.execute('CREATE TABLE tiles (zoom_level INTEGER,tile_column INTEGER,tile_row INTEGER,tile_data BLOB)')
            db.execute('INSERT INTO metadata VALUES (?,?)',('format','png'))
            db.execute('INSERT INTO tiles VALUES (2,1,2,?)',(b'fake',));db.commit();db.close()
            load('mbtiles_to_xyz').convert(src,out,'Proveedor','Licencia','Atribución')
            index=json.loads((out/'tile-index.json').read_text())
            self.assertEqual(index['tiles'],['2/1/1.png'])
    def test_release_preflight_does_not_claim_ready(self):
        report=load('check_release').check(ROOT)
        self.assertFalse(report['ready_for_public_release'])
        self.assertTrue(report['pending'])
if __name__=='__main__':unittest.main()


class IncidentCommandTests(unittest.TestCase):
    def test_incident_command_module_is_loaded(self):
        html=(ROOT/'frontend/index.html').read_text()
        self.assertIn('ops-center.js',html)
        sw=(ROOT/'frontend/sw.js').read_text()
        self.assertIn("'./ops-center.js'",sw)
        self.assertIn("const VERSION='2.5'",sw)
        self.assertIn('incidentCommandBox',html)
    def test_incident_module_has_local_backup_and_validation(self):
        js=(ROOT/'frontend/ops-center.js').read_text()
        self.assertIn('localStorage',js)
        self.assertIn('schema_version:2',js)
        self.assertIn('prepper-map-bitacora-',js)
        self.assertIn('icImportFile',js)
    def test_municipal_catalog_has_26_layers_and_new_medellin_themes(self):
        catalog=json.loads((ROOT/'gis/sources/sources.json').read_text())
        count=sum(len(x['layers']) for x in catalog['sources'])
        self.assertEqual(count,26)
        med=next(x for x in catalog['sources'] if x['id']=='medellin_dagrd')
        themes={x['theme'] for x in med['layers']}
        self.assertIn('wildfire_hazard',themes)
        self.assertIn('technological_hazard',themes)


class CommandMapAndResourceTests(unittest.TestCase):
    def test_incident_georeference_and_comms_are_present(self):
        js=(ROOT/'frontend/ops-center.js').read_text()
        html=(ROOT/'frontend/index.html').read_text()
        self.assertIn('PREPPER_MAP_INCIDENT_LAYER',html)
        self.assertIn('icLat',html)
        self.assertIn('icLon',html)
        self.assertIn('icAddComms',html)
        self.assertIn('icShowMap',html)
        self.assertIn('validCoord',js)
        self.assertIn('communications',js)
    def test_resource_registry_is_local_and_verification_aware(self):
        js=(ROOT/'frontend/resource-registry.js').read_text()
        html=(ROOT/'frontend/index.html').read_text()
        self.assertIn('localStorage',js)
        self.assertIn('status===\'verificado\'',js)
        self.assertIn('rrSource',html)
        self.assertIn('rrExport',html)
        self.assertIn('resource-registry.js',html)
    def test_service_worker_caches_new_modules(self):
        sw=(ROOT/'frontend/sw.js').read_text()
        self.assertIn("const VERSION='2.5'",sw)
        self.assertIn("'./resource-registry.js'",sw)
