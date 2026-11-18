#!/usr/bin/env python3
"""PREPPER MAP 1.6: cribado de afectación territorial alrededor de un incidente."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from datetime import datetime, timezone
from shapely.geometry import shape, Point, mapping
from shapely.ops import transform
from pyproj import Transformer

def read_fc(path):
    obj=json.loads(Path(path).read_text(encoding="utf-8"))
    if obj.get("type")!="FeatureCollection" or not isinstance(obj.get("features"),list):
        raise ValueError(f"{path}: se esperaba GeoJSON FeatureCollection")
    return obj

def assess(lat, lon, radius_m, asset_files, hazard_files, source_crs="EPSG:4326", metric_crs="EPSG:9377"):
    if not (-90<=lat<=90 and -180<=lon<=180): raise ValueError("Coordenadas fuera de rango")
    if not (50<=radius_m<=10000): raise ValueError("Radio permitido: 50 a 10.000 metros")
    to_metric=Transformer.from_crs(source_crs,metric_crs,always_xy=True)
    to_geo=Transformer.from_crs(metric_crs,source_crs,always_xy=True)
    project=lambda g: transform(to_metric.transform,g)
    incident=project(Point(lon,lat))
    buffer=incident.buffer(radius_m)
    categories={}
    assets_out=[]
    for path in asset_files:
        fc=read_fc(path)
        for f in fc["features"]:
            if not f.get("geometry"): continue
            geom=project(shape(f["geometry"]))
            if geom.is_empty: continue
            if geom.geom_type not in ("Point","MultiPoint"):
                geom=geom.representative_point()
            distance=incident.distance(geom)
            if distance<=radius_m:
                props=f.get("properties") or {}
                cat=str(props.get("category") or props.get("tipo") or props.get("type") or Path(path).stem)
                categories[cat]=categories.get(cat,0)+1
                assets_out.append({"source":str(path),"category":cat,"name":str(props.get("name") or props.get("nombre") or "Activo sin nombre"),
                    "distance_m":round(distance,1),"attributes":props,
                    "geometry":mapping(transform(to_geo.transform,geom))})
    hazard_hits=[]
    for path in hazard_files:
        fc=read_fc(path)
        for f in fc["features"]:
            if not f.get("geometry"): continue
            geom=project(shape(f["geometry"]))
            if geom.is_empty: continue
            if geom.intersects(buffer):
                props=f.get("properties") or {}
                hazard_hits.append({"source":str(path),"name":str(props.get("name") or props.get("tipo") or Path(path).stem),
                    "intersection_area_m2":round(geom.intersection(buffer).area,1),"attributes":props})
    assets_out.sort(key=lambda a:a["distance_m"])
    report={"application":"PREPPER MAP PRO","version":"1.6.0","created_at":datetime.now(timezone.utc).isoformat(),
      "incident":{"latitude":lat,"longitude":lon,"screening_radius_m":radius_m,"buffer_geometry":mapping(transform(to_geo.transform,buffer))},
      "summary":{"assets_within_radius":len(assets_out),"assets_by_category":categories,"hazard_polygons_intersecting":len(hazard_hits)},
      "assets":assets_out,"hazard_intersections":hazard_hits,
      "limitations":["Cribado geométrico, no estimación de población afectada ni daños.",
        "Los activos dependen exclusivamente de los GeoJSON suministrados y pueden estar incompletos o desactualizados.",
        "La intersección con una capa de amenaza no equivale a una alerta vigente ni determina severidad.",
        "La distancia es euclidiana en el CRS métrico, no distancia por red vial.",
        "No reemplaza inspección, validación comunitaria ni autoridad competente."]}
    return report

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--lat",type=float,required=True);p.add_argument("--lon",type=float,required=True)
    p.add_argument("--radius-m",type=float,default=500)
    p.add_argument("--assets",type=Path,action="append",default=[])
    p.add_argument("--hazard",type=Path,action="append",default=[])
    p.add_argument("--out",type=Path,default=Path("reports/incident-impact-v16.json"))
    p.add_argument("--source-crs",default="EPSG:4326");p.add_argument("--metric-crs",default="EPSG:9377")
    a=p.parse_args()
    report=assess(a.lat,a.lon,a.radius_m,a.assets,a.hazard,a.source_crs,a.metric_crs)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"Activos dentro del radio: {report['summary']['assets_within_radius']}")
    print(f"Polígonos de amenaza coincidentes: {report['summary']['hazard_polygons_intersecting']}")
    print(f"Informe: {a.out}")
if __name__=="__main__": main()
