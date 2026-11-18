#!/usr/bin/env python3
"""Valida FeatureCollections GeoJSON y manifiesto de extracción."""
import json, math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FOLDER = ROOT / "gis/downloaded"
files = sorted(FOLDER.glob("*.geojson"))
errors, warnings, feature_total = [], [], 0

def check_position(pos, context):
    if not isinstance(pos, (list, tuple)) or len(pos) < 2:
        errors.append(f"{context}: posición inválida")
        return
    try:
        lon, lat = float(pos[0]), float(pos[1])
        if not (math.isfinite(lon) and math.isfinite(lat)):
            errors.append(f"{context}: coordenadas no finitas")
        elif not (-180 <= lon <= 180 and -90 <= lat <= 90):
            errors.append(f"{context}: coordenadas fuera de EPSG:4326 ({lon},{lat})")
    except (TypeError, ValueError):
        errors.append(f"{context}: coordenadas no numéricas")

def walk_coords(coords, context):
    if not isinstance(coords, list) or not coords:
        errors.append(f"{context}: geometría sin coordenadas")
    elif isinstance(coords[0], (int, float)):
        check_position(coords, context)
    else:
        for i, child in enumerate(coords):
            walk_coords(child, f"{context}[{i}]")

for path in files:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("type") != "FeatureCollection":
            errors.append(f"{path.name}: no es FeatureCollection")
            continue
        features = data.get("features")
        if not isinstance(features, list):
            errors.append(f"{path.name}: features no es una lista")
            continue
        feature_total += len(features)
        seen = set()
        if not features:
            warnings.append(f"{path.name}: colección vacía")
        for idx, feature in enumerate(features):
            ctx = f"{path.name} feature {idx}"
            if feature.get("type") != "Feature":
                errors.append(f"{ctx}: tipo inválido")
            geom = feature.get("geometry")
            if geom is None:
                warnings.append(f"{ctx}: geometría nula")
                continue
            if geom.get("type") not in {"Point","MultiPoint","LineString","MultiLineString","Polygon","MultiPolygon","GeometryCollection"}:
                errors.append(f"{ctx}: tipo geométrico desconocido")
            if geom.get("type") == "GeometryCollection":
                for gi, sub in enumerate(geom.get("geometries", [])):
                    if "coordinates" in sub:
                        walk_coords(sub["coordinates"], f"{ctx}.geometries[{gi}]")
            else:
                walk_coords(geom.get("coordinates"), f"{ctx}.coordinates")
            fid = feature.get("id")
            if fid is not None:
                if str(fid) in seen:
                    warnings.append(f"{ctx}: ID repetido {fid}")
                seen.add(str(fid))
        metadata = data.get("metadata", {})
        if metadata.get("output_crs") not in (None, "EPSG:4326"):
            warnings.append(f"{path.name}: output_crs no declarado como EPSG:4326")
    except Exception as exc:
        errors.append(f"{path.name}: {exc}")

manifest_path = FOLDER / "manifest.json"
if manifest_path.exists():
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for item in manifest.get("items", []):
            if item.get("status") == "downloaded" and not (ROOT / item.get("file", "")).exists():
                errors.append(f"Manifiesto: falta archivo {item.get('file')}")
    except Exception as exc:
        errors.append(f"Manifiesto inválido: {exc}")
else:
    warnings.append("No existe manifest.json: aún no se han extraído capas.")

print(f"{len(files)} archivos; {feature_total} entidades revisadas; {len(warnings)} advertencias; {len(errors)} errores.")
for warning in warnings: print("AVISO:", warning)
for error in errors: print("ERROR:", error)
raise SystemExit(1 if errors else 0)
