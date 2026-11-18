import json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class MultiPlatformConfigTests(unittest.TestCase):
 def test_tauri_config_has_app_identity_and_frontend(self):
  c=json.loads((ROOT/'src-tauri/tauri.conf.json').read_text())
  self.assertEqual(c['identifier'],'org.preppermap.resiliencia')
  self.assertEqual(c['build']['frontendDist'],'../frontend')
  self.assertIn('nsis',c['bundle']['targets'])
 def test_frontend_uses_local_map_libraries(self):
  html=(ROOT/'frontend/index.html').read_text()
  self.assertIn('vendor/leaflet/leaflet.js',html)
  self.assertIn('vendor/esri-leaflet/esri-leaflet.js',html)
  self.assertNotIn('unpkg.com/leaflet',html)
 def test_android_ios_workflows_exist(self):
  self.assertTrue((ROOT/'.github/workflows/build-android.yml').exists())
  self.assertTrue((ROOT/'.github/workflows/build-windows.yml').exists())
 def test_offline_geojson_library_is_present(self):
  html=(ROOT/'frontend/index.html').read_text()
  self.assertIn('indexedDB.open(OFFLINE_DB,1)',html)
  self.assertIn('validateOfflineGeoJSON',html)
  self.assertIn('offlineGeoFile',html)
  sw=(ROOT/'frontend/sw.js').read_text()
  self.assertIn("const VERSION='2.5'",sw)
 def test_pwa_has_install_icons(self):
  m=json.loads((ROOT/'frontend/manifest.webmanifest').read_text())
  sizes={x['sizes'] for x in m['icons']}
  self.assertIn('192x192',sizes);self.assertIn('512x512',sizes)
if __name__=='__main__':unittest.main()


class OfflineBasemapTests(unittest.TestCase):
 def test_mbtiles_converter_tms_to_xyz_and_metadata(self):
  import importlib.util, sqlite3, tempfile
  spec=importlib.util.spec_from_file_location('mbtiles_to_xyz', ROOT/'backend/scripts/mbtiles_to_xyz.py')
  mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
  with tempfile.TemporaryDirectory() as td:
   td=Path(td); source=td/'sample.mbtiles'; output=td/'tiles'
   db=sqlite3.connect(source)
   db.execute('CREATE TABLE metadata (name TEXT, value TEXT)')
   db.execute('CREATE TABLE tiles (zoom_level INTEGER, tile_column INTEGER, tile_row INTEGER, tile_data BLOB)')
   db.executemany('INSERT INTO metadata VALUES (?,?)',[('name','Prueba'),('format','png')])
   db.execute('INSERT INTO tiles VALUES (1,1,0,?)',(b'fake-png-tile',));db.commit();db.close()
   manifest=mod.convert(source,output,'Proveedor','Licencia','Atribución')
   self.assertTrue((output/'1'/'1'/'1.png').exists())
   self.assertEqual(manifest['tile_count'],1)
   self.assertEqual(manifest['scheme'],'xyz')
   with self.assertRaises(ValueError):
    mod.convert(source,output,'','Licencia','Atribución')
 def test_frontend_supports_local_xyz_basemap(self):
  html=(ROOT/'frontend/index.html').read_text()
  self.assertIn('offline-tiles/{z}/{x}/{y}.',html)
  self.assertIn('useOfflineBasemap',html)
  self.assertIn('useOnlineBasemap',html)
 def test_service_worker_caches_offline_tile_requests(self):
  sw=(ROOT/'frontend/sw.js').read_text()
  self.assertIn("url.pathname.includes('/offline-tiles/')",sw)
