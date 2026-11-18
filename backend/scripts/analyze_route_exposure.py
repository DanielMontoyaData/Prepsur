#!/usr/bin/env python3
"""PREPPER MAP 1.5: análisis espacial de exposición de rutas a polígonos de amenaza.
No calcula rutas seguras ni sustituye alertas/órdenes oficiales.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
from datetime import datetime, timezone
from shapely.geometry import shape, mapping, LineString, MultiLineString, GeometryCollection
from shapely.ops import transform
from pyproj import Transformer

def load_fc(path: Path):
    data=json.loads(path.read_text(encoding="utf-8"))
    if data.get("type")!="FeatureCollection" or not isinstance(data.get("features"),list):
        raise ValueError(f"{path}: GeoJSON FeatureCollection no válido")
    return data

def line_parts(geom):
    if geom.geom_type=="LineString": return [geom]
    if geom.geom_type=="MultiLineString": return list(geom.geoms)
    if geom.geom_type=="GeometryCollection":
        return [g for x in geom.geoms for g in line_parts(x)]
    return []

def run(route_path, hazard_paths, out_path, source_crs="EPSG:4326", metric_crs="EPSG:9377"):
    routes=load_fc(route_path)
    transformer=Transformer.from_crs(source_crs,metric_crs,always_xy=True)
    project=lambda g: transform(transformer.transform,g)
    route_rows=[]; overlap_features=[]
    hazards=[]
    for hp in hazard_paths:
        fc=load_fc(hp)
        for f in fc["features"]:
            if not f.get("geometry"): continue
            geom=shape(f["geometry"])
            if geom.is_empty: continue
            hazards.append((hp.name,f.get("properties") or {},project(geom)))
    for idx,feature in enumerate(routes["features"],1):
        if not feature.get("geometry"): continue
        original=shape(feature["geometry"])
        parts=line_parts(original)
        if not parts: continue
        route=project(original)
        total=route.length
        if total<=0: continue
        exposures=[]
        for filename,props,hazard in hazards:
            overlap=route.intersection(hazard)
            length=sum(x.length for x in line_parts(overlap))
            if length<=0: continue
            pct=min(100.0,100*length/total)
            exposures.append({"hazard_file":filename,"hazard_label":str(props.get("name") or props.get("tipo") or props.get("risk") or filename),
                              "overlap_m":round(length,1),"route_percent":round(pct,2),
                              "attributes":props})
            for segment in line_parts(overlap):
                if segment.length>0:
                    overlap_features.append({"type":"Feature","geometry":mapping(transform(Transformer.from_crs(metric_crs,source_crs,always_xy=True).transform,segment)),
                        "properties":{"route_index":idx,"hazard_file":filename,"overlap_m":round(segment.length,1),"screening_only":True}})
        route_rows.append({"route_index":idx,"name":(feature.get("properties") or {}).get("name",f"Ruta {idx}"),
            "length_km":round(total/1000,3),"hazard_intersections":len(exposures),"exposures":exposures,
            "interpretation":"Coincidencia cartográfica preliminar. No indica peligro inminente, transitabilidad ni seguridad. Requiere verificación de campo." if exposures else
            "No se detectó intersección con las capas suministradas; la ausencia de coincidencia NO demuestra seguridad.",
            "data_limitations":["Depende de la cobertura, escala, fecha y calidad de las capas suministradas.",
             "No considera cierres, obras, clima actual, caudal, derrumbes recientes ni condiciones de campo."]})
    report={"application":"PREPPER MAP PRO","version":"1.5.0","created_at":datetime.now(timezone.utc).isoformat(),
        "method":{"metric_crs":metric_crs,"length_measure":"longitud de intersección de línea con polígonos",
        "warning":"Herramienta de cribado cartográfico, no enrutador de evacuación ni certificador de rutas seguras.",
        "hazard_files":[str(x) for x in hazard_paths],"route_file":str(route_path)},
        "summary":{"routes_analyzed":len(route_rows),"routes_with_intersections":sum(bool(r["exposures"]) for r in route_rows),
                   "hazard_layers_loaded":len(hazard_paths)},"routes":route_rows}
    out_path.parent.mkdir(parents=True,exist_ok=True)
    out_path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    overlap_path=out_path.with_name(out_path.stem+"_overlaps.geojson")
    overlap_path.write_text(json.dumps({"type":"FeatureCollection","name":"PREPPER MAP route hazard overlaps",
        "features":overlap_features,"metadata":{"created_at":report["created_at"],"screening_only":True}},ensure_ascii=False,indent=2),encoding="utf-8")
    return report,overlap_path

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--routes",required=True,type=Path,help="GeoJSON con LineString/MultiLineString en CRS indicado")
    p.add_argument("--hazard",required=True,action="append",type=Path,help="GeoJSON de polígonos; repetir por cada capa")
    p.add_argument("--out",default=Path("reports/route-exposure-v15.json"),type=Path)
    p.add_argument("--source-crs",default="EPSG:4326")
    p.add_argument("--metric-crs",default="EPSG:9377")
    a=p.parse_args()
    report,overlaps=run(a.routes,a.hazard,a.out,a.source_crs,a.metric_crs)
    print(f"Rutas: {report['summary']['routes_analyzed']} · con intersecciones: {report['summary']['routes_with_intersections']}")
    print(f"Informe: {a.out} · Segmentos coincidentes: {overlaps}")
if __name__=="__main__": main()
