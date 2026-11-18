import json, subprocess, sys, tempfile, unittest
from pathlib import Path
import numpy as np
import rasterio
from rasterio.transform import from_origin
from pyproj import Transformer
ROOT=Path(__file__).resolve().parents[1]
class TerrainToolTests(unittest.TestCase):
 def test_prepare_dem_outputs_slope_products(self):
  with tempfile.TemporaryDirectory() as td:
   td=Path(td); dem=td/'dem.tif'
   arr=np.tile(np.arange(20,dtype='float32'),(20,1))*0.1
   with rasterio.open(dem,'w',driver='GTiff',height=20,width=20,count=1,dtype='float32',crs='EPSG:9377',transform=from_origin(4500000,2200000,30,30),nodata=-9999) as ds: ds.write(arr,1)
   out=td/'terrain'
   subprocess.run([sys.executable,str(ROOT/'backend/scripts/prepare_terrain.py'),'--dem',str(dem),'--out-dir',str(out)],check=True,capture_output=True,text=True)
   self.assertTrue((out/'slope_percent.tif').exists())
   geo=json.loads((out/'slope_classes.geojson').read_text())
   self.assertEqual(geo['type'],'FeatureCollection')
   self.assertTrue((out/'terrain_manifest.json').exists())
 def test_route_profile_outputs_metrics(self):
  with tempfile.TemporaryDirectory() as td:
   td=Path(td); dem=td/'dem.tif'
   arr=np.tile(np.arange(40,dtype='float32'),(20,1))+100
   transform=from_origin(4500000,2200000,30,30)
   with rasterio.open(dem,'w',driver='GTiff',height=20,width=40,count=1,dtype='float32',crs='EPSG:9377',transform=transform,nodata=-9999) as ds:ds.write(arr,1)
   to_wgs=Transformer.from_crs('EPSG:9377','EPSG:4326',always_xy=True)
   a=to_wgs.transform(4500015,2199850);b=to_wgs.transform(4501000,2199850)
   route=td/'route.geojson';route.write_text(json.dumps({'type':'FeatureCollection','features':[{'type':'Feature','geometry':{'type':'LineString','coordinates':[a,b]},'properties':{}}]}))
   out=td/'profile.json'
   subprocess.run([sys.executable,str(ROOT/'backend/scripts/terrain_route_profile.py'),'--route',str(route),'--dem',str(dem),'--output',str(out)],check=True,capture_output=True,text=True)
   data=json.loads(out.read_text());self.assertGreater(data['summary']['valid_samples'],1)
   self.assertIsNotNone(data['summary']['max_elevation_m'])

 def test_trail_network_metrics(self):
  with tempfile.TemporaryDirectory() as td:
   td=Path(td); inp=td/'trails.geojson';out=td/'metrics.json'
   inp.write_text(json.dumps({'type':'FeatureCollection','features':[{'type':'Feature','geometry':{'type':'LineString','coordinates':[[-75.5,6.1],[-75.49,6.1],[-75.48,6.1]]},'properties':{'highway':'path'}}]}))
   subprocess.run([sys.executable,str(ROOT/'backend/scripts/analyze_trail_network.py'),'--input',str(inp),'--output',str(out)],check=True,capture_output=True,text=True)
   data=json.loads(out.read_text());self.assertEqual(data['metrics']['connected_components'],1)
   self.assertEqual(data['metrics']['dead_end_nodes_degree_1'],2)

if __name__=='__main__':unittest.main()
