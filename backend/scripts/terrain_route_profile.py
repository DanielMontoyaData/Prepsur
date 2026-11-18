#!/usr/bin/env python3
"""Perfil altimétrico y gradientes aproximados de una ruta GeoJSON sobre un DEM."""
import argparse,csv,json,math
from pathlib import Path
import rasterio
from shapely.geometry import shape
from shapely.ops import transform as shp_transform
from pyproj import Transformer

def lines(geom):
    if geom.geom_type=="LineString": return [geom]
    if geom.geom_type=="MultiLineString": return list(geom.geoms)
    if geom.geom_type=="GeometryCollection": return [g for x in geom.geoms for g in lines(x)]
    return []
def main():
    p=argparse.ArgumentParser();p.add_argument("--route",required=True);p.add_argument("--dem",required=True);p.add_argument("--output",default="terrain_route_profile.json");p.add_argument("--interval",type=float,default=30)
    a=p.parse_args()
    if a.interval<=0: raise SystemExit("--interval debe ser positivo.")
    fc=json.loads(Path(a.route).read_text(encoding="utf-8")); feats=[fc] if fc.get("type")=="Feature" else fc.get("features",[])
    with rasterio.open(a.dem) as ds:
        if not ds.crs: raise SystemExit("DEM sin CRS.")
        to_raster=Transformer.from_crs("EPSG:4326",ds.crs,always_xy=True).transform
        to_geo=Transformer.from_crs(ds.crs,"EPSG:4326",always_xy=True).transform
        records=[]
        for fi,f in enumerate(feats):
            if not f.get("geometry"):continue
            geom=shp_transform(to_raster,shape(f["geometry"]))
            for li,line in enumerate(lines(geom)):
                count=max(1,math.ceil(line.length/a.interval))
                for i in range(count+1):
                    pt=line.interpolate(min(line.length,i*a.interval))
                    val=next(ds.sample([(pt.x,pt.y)]))[0]
                    if ds.nodata is not None and val==ds.nodata: elev=None
                    else: elev=float(val)
                    lon,lat=to_geo(pt.x,pt.y)
                    records.append({"feature_index":fi,"part_index":li,"distance_m":round(line.project(pt),1),"lon":lon,"lat":lat,"elevation_m":elev})
        if not records: raise SystemExit("No se encontraron líneas en el archivo.")
    records.sort(key=lambda x:(x["feature_index"],x["part_index"],x["distance_m"]))
    valid=[r for r in records if r["elevation_m"] is not None]
    ascent=descent=0.0; grades=[]; prev=None
    for r in records:
        if r["elevation_m"] is None: prev=None;continue
        if prev:
            d=r["distance_m"]-prev["distance_m"]
            if d>0:
                dz=r["elevation_m"]-prev["elevation_m"]
                if dz>0: ascent+=dz
                else: descent-=dz
                grades.append(abs(dz/d)*100)
        prev=r
    report={"route_file":a.route,"dem_file":a.dem,"sample_interval_m":a.interval,"samples":records,
      "summary":{"valid_samples":len(valid),"min_elevation_m":min((x["elevation_m"] for x in valid),default=None),
      "max_elevation_m":max((x["elevation_m"] for x in valid),default=None),"estimated_ascent_m":round(ascent,1),
      "estimated_descent_m":round(descent,1),"max_absolute_grade_percent":round(max(grades),1) if grades else None},
      "warning":"Perfil aproximado extraído del DEM/DSM suministrado. No valida el sendero, superficie, estabilidad, accesibilidad ni seguridad. El error vertical, vegetación y edificios pueden afectar resultados."}
    Path(a.output).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"Perfil guardado: {a.output}; muestras válidas: {len(valid)}")
if __name__=="__main__":main()
