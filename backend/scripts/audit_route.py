#!/usr/bin/env python3
"""Audita intersecciones de una ruta candidata con GeoJSON de amenazas."""
import argparse, json
from pathlib import Path
from shapely.geometry import shape
from shapely.ops import unary_union

def read_features(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if data.get("type") == "Feature":
        return [data]
    if data.get("type") != "FeatureCollection":
        raise ValueError(f"{path}: debe ser Feature o FeatureCollection")
    return data.get("features", [])

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--route", required=True)
    p.add_argument("--hazards", action="append", required=True)
    p.add_argument("--output", default="route_audit.json")
    a = p.parse_args()
    routes = [f for f in read_features(a.route) if f.get("geometry")]
    if not routes:
        raise SystemExit("No hay geometrías de ruta.")
    route_geom = unary_union([shape(f["geometry"]) for f in routes])
    results = []
    for file in a.hazards:
        feats = [f for f in read_features(file) if f.get("geometry")]
        hazards = [(f, shape(f["geometry"])) for f in feats]
        hits = []
        for feature, geom in hazards:
            if route_geom.intersects(geom):
                hits.append({
                    "feature_id": feature.get("id"),
                    "properties": feature.get("properties", {}),
                    "intersection_length_degrees": route_geom.intersection(geom).length
                })
        results.append({"hazard_file": file, "features_tested": len(hazards),
                        "intersections": len(hits), "hits": hits})
    report = {
        "route_file": a.route,
        "method": "geometric intersection of supplied route with supplied hazard polygons",
        "warning": "This is a screening test, not a safety certification, hydrologic/geotechnical model, or official evacuation route.",
        "results": results
    }
    Path(a.output).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Informe guardado: {a.output}")
    for r in results:
        print(f'{r["hazard_file"]}: {r["intersections"]} intersecciones / {r["features_tested"]} polígonos')

if __name__ == "__main__":
    main()
