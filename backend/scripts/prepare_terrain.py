#!/usr/bin/env python3
"""Deriva pendiente (grados/%) y clases cartográficas desde un DEM GeoTIFF."""
import argparse, json
from pathlib import Path
import numpy as np
import rasterio
from rasterio.features import shapes
from shapely.geometry import shape, mapping
from shapely.ops import transform as shp_transform
from pyproj import Transformer

CLASSES=[(0,5,"0-5%"),(5,15,"5-15%"),(15,30,"15-30%"),(30,45,"30-45%"),(45,float("inf"),">45%")]
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--dem",required=True,help="GeoTIFF DEM/DSM proyectado o geográfico")
    p.add_argument("--out-dir",default="gis/terrain")
    a=p.parse_args(); out=Path(a.out_dir);out.mkdir(parents=True,exist_ok=True)
    with rasterio.open(a.dem) as src:
        if not src.crs: raise SystemExit("El raster debe tener CRS definido.")
        if src.crs.is_geographic: raise SystemExit("Reproyecta el DEM a CRS proyectado en metros (p.ej. MAGNA-SIRGAS / Origen-Nacional EPSG:9377) antes de calcular pendientes.")
        if src.count<1: raise SystemExit("DEM sin bandas.")
        z=src.read(1,masked=True).astype("float64")
        xres=abs(src.transform.a); yres=abs(src.transform.e)
        if not xres or not yres: raise SystemExit("Resolución espacial inválida.")
        # np.gradient: primer resultado filas (sur/norte), segundo columnas (oeste/este)
        dz_dy,dz_dx=np.gradient(z.filled(np.nan),yres,xres)
        slope_pct=np.sqrt(dz_dx**2+dz_dy**2)*100
        slope_deg=np.degrees(np.arctan(np.sqrt(dz_dx**2+dz_dy**2)))
        valid=(~np.ma.getmaskarray(z)) & np.isfinite(slope_pct)
        profile=src.profile.copy();profile.update(dtype="float32",count=1,nodata=-9999,compress="deflate")
        for name,array in [("slope_percent.tif",slope_pct),("slope_degrees.tif",slope_deg)]:
            with rasterio.open(out/name,"w",**profile) as dst:
                dst.write(np.where(valid,array,-9999).astype("float32"),1)
        classes=np.zeros(z.shape,dtype="uint8")
        for idx,(lo,hi,label) in enumerate(CLASSES,1):
            classes[valid & (slope_pct>=lo) & (slope_pct<hi)]=idx
        cls_profile=profile.copy();cls_profile.update(dtype="uint8",nodata=0)
        with rasterio.open(out/"slope_classes.tif","w",**cls_profile) as dst: dst.write(classes,1)
        # Vectorize only coarse classes, then transform to WGS84 for web GIS.
        to_wgs=Transformer.from_crs(src.crs,"EPSG:4326",always_xy=True).transform
        features=[]
        labels={i+1:c[2] for i,c in enumerate(CLASSES)}
        for geom,val in shapes(classes,mask=valid & (classes>0),transform=src.transform):
            poly=shape(geom)
            if poly.area < (xres*yres*2): continue
            features.append({"type":"Feature","geometry":mapping(shp_transform(to_wgs,poly)),
                "properties":{"slope_class":labels[int(val)],"source_dem":str(Path(a.dem).name),
                "verification":"derived_model_not_field_verified"}})
        geo={"type":"FeatureCollection","name":"slope_classes","crs":{"type":"name","properties":{"name":"EPSG:4326"}},"features":features}
        (out/"slope_classes.geojson").write_text(json.dumps(geo,ensure_ascii=False),encoding="utf-8")
        meta={"source_dem":str(Path(a.dem).name),"source_crs":src.crs.to_string(),"pixel_size_m":[xres,yres],
              "valid_pixels":int(valid.sum()),"slope_method":"Horn-like first derivative via numpy.gradient (central differences)",
              "classes":[{"class":c[2],"min_percent":c[0],"max_percent":None if c[1]==float("inf") else c[1]} for c in CLASSES],
              "caveat":"Slope is derived from supplied elevation model. Copernicus GLO-30 is a DSM including buildings/vegetation, not a high-resolution bare-earth DTM. Not suitable alone for engineering or safe-route certification."}
        (out/"terrain_manifest.json").write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"Terreno procesado: {out}; {len(features)} polígonos de clase.")
if __name__=="__main__": main()
