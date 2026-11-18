#!/usr/bin/env python3
"""PREPPER MAP PRO 1.8 — análisis de cobertura y brechas por zona."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from datetime import datetime, timezone
from shapely.geometry import shape, Point
from shapely.ops import transform
from pyproj import Transformer

def read_fc(path):
    obj=json.loads(Path(path).read_text(encoding="utf-8"))
    if obj.get("type")!="FeatureCollection" or not isinstance(obj.get("features"),list):
        raise ValueError(f"{path}: se esperaba GeoJSON FeatureCollection")
    return obj

def analyze(zones_path, resources_path, population_field="population",
            category_field="category", name_field="name",
            source_crs="EPSG:4326", metric_crs="EPSG:9377",
            demand_rates=None):
    zones=read_fc(zones_path); resources=read_fc(resources_path)
    tx=Transformer.from_crs(source_crs,metric_crs,always_xy=True)
    project=lambda g: transform(tx.transform,g)
    points=[]
    for f in resources["features"]:
        if not f.get("geometry"): continue
        g=project(shape(f["geometry"]))
        if g.geom_type!="Point":
            raise ValueError("Todos los recursos deben ser puntos; convierte o depura el GeoJSON.")
        props=f.get("properties") or {}
        points.append({"geometry":g,"category":str(props.get(category_field) or "sin_categoria"),
            "name":str(props.get(name_field) or "Recurso sin nombre"),"properties":props})
    output=[]
    rates=demand_rates or {}
    for idx,f in enumerate(zones["features"],1):
        if not f.get("geometry"): continue
        geom=project(shape(f["geometry"]))
        if geom.is_empty or not geom.is_valid: continue
        props=f.get("properties") or {}
        name=str(props.get(name_field) or props.get("nombre") or f"Zona {idx}")
        population=props.get(population_field)
        if population is not None:
            try:
                population=float(population)
                if population<0: raise ValueError()
            except (TypeError,ValueError):
                raise ValueError(f"Población inválida en {name}: debe ser un número no negativo.")
        else: population=None
        center=geom.representative_point()
        inside=[p for p in points if geom.covers(p["geometry"])]
        cats={}
        for p in inside: cats[p["category"]]=cats.get(p["category"],0)+1
        nearest={}
        for cat in sorted({p["category"] for p in points}):
            candidates=[p for p in points if p["category"]==cat]
            if candidates:
                nearest[cat]=round(min(center.distance(p["geometry"]) for p in candidates),1)
        demand={}
        if population is not None:
            for cat,rate in rates.items():
                rate=float(rate)
                if rate<0: raise ValueError(f"Tasa negativa para {cat}")
                demand[cat]={"estimated_daily_requirement":round(population*rate,3),"rate_per_person_day":rate}
        output.append({"zone_id":str(props.get("id") or idx),"zone_name":name,
            "population":population,"population_field":population_field if population is not None else None,
            "resources_inside":len(inside),"resources_by_category":cats,
            "nearest_resource_distance_m_by_category":nearest,
            "estimated_demand":demand,
            "data_quality":{"population_available":population is not None,
                "resource_points_loaded":len(points),
                "warning":"El conteo refleja únicamente los puntos suministrados y no confirma capacidad, operación ni acceso."}})
    summary={"zones_analyzed":len(output),"zones_without_any_registered_resource":sum(x["resources_inside"]==0 for x in output),
        "zones_without_population_data":sum(x["population"] is None for x in output),
        "resource_points_loaded":len(points)}
    return {"application":"PREPPER MAP PRO","version":"1.8.0","created_at":datetime.now(timezone.utc).isoformat(),
      "method":{"zone_file":str(zones_path),"resource_file":str(resources_path),"source_crs":source_crs,
        "metric_crs":metric_crs,"population_field":population_field,"category_field":category_field,
        "demand_rates_per_person_day":rates,
        "distance_method":"distancia euclidiana desde punto representativo de zona al recurso más cercano de cada categoría",
        "scope":"cribado de cobertura cartográfica, no certificación de acceso ni capacidad"},
      "summary":summary,"zones":output,
      "limitations":["Un recurso dentro de una zona no implica que tenga capacidad disponible o esté operativo.",
        "La distancia es euclidiana, no distancia por vías ni tiempo de desplazamiento.",
        "La ausencia de puntos puede reflejar falta de datos, no ausencia real de servicios.",
        "La población solo se informa si el archivo contiene el campo indicado; no se imputan valores.",
        "Las necesidades son estimaciones según tasas que aporta el operador, no estándares universales.",
        "No usar para ordenar evacuaciones, negar asistencia o reemplazar decisiones de autoridades."]}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--zones",required=True,type=Path)
    p.add_argument("--resources",required=True,type=Path)
    p.add_argument("--population-field",default="population")
    p.add_argument("--category-field",default="category")
    p.add_argument("--name-field",default="name")
    p.add_argument("--rate",action="append",default=[],help="Categoría=tasa por persona/día; repetir")
    p.add_argument("--source-crs",default="EPSG:4326");p.add_argument("--metric-crs",default="EPSG:9377")
    p.add_argument("--out",type=Path,default=Path("reports/zone-coverage-v18.json"))
    a=p.parse_args();rates={}
    for item in a.rate:
        if "=" not in item: p.error("--rate debe ser categoría=valor")
        k,v=item.split("=",1);rates[k]=float(v)
    report=analyze(a.zones,a.resources,a.population_field,a.category_field,a.name_field,a.source_crs,a.metric_crs,rates)
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(report["summary"],ensure_ascii=False))
    print(f"Informe: {a.out}")
if __name__=="__main__":main()
