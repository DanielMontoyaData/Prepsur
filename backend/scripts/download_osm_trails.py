#!/usr/bin/env python3
"""Descarga selectiva de senderos/caminos OSM mediante Overpass; no usa API de edición."""
from __future__ import annotations
import argparse, json, time
from datetime import datetime, timezone
from pathlib import Path
import requests
from shapely.geometry import LineString, MultiLineString, mapping

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BBOX = "5.95,-75.85,6.35,-75.35"
ENDPOINTS = ["https://overpass-api.de/api/interpreter", "https://overpass.kumi.systems/api/interpreter"]

def parse_bbox(value):
    vals = [float(x.strip()) for x in value.split(",")]
    if len(vals) != 4:
        raise ValueError("bbox debe ser south,west,north,east")
    south, west, north, east = vals
    if not (-90 <= south < north <= 90 and -180 <= west < east <= 180):
        raise ValueError("bbox fuera de rango o invertido")
    return south, west, north, east

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--bbox", default=DEFAULT_BBOX, help="south,west,north,east")
    p.add_argument("--output", default="gis/routes/osm_trails.geojson")
    p.add_argument("--timeout", type=int, default=120)
    args = p.parse_args()
    south, west, north, east = parse_bbox(args.bbox)
    bbox = f"{south},{west},{north},{east}"
    query = "[out:json][timeout:" + str(args.timeout) + "];\n(" + \
        'way["highway"~"^(path|footway|track|steps|bridleway)$"](' + bbox + ");\n" + \
        'relation["route"="hiking"](' + bbox + ");\n);\nout body geom;"
    data = None
    errors = []
    session = requests.Session()
    session.headers.update({"User-Agent": "PREPPER-MAP-PRO/0.7 (civic resilience GIS)"})
    endpoint = None
    for candidate in ENDPOINTS:
        try:
            response = session.post(candidate, data={"data": query}, timeout=args.timeout + 20)
            response.raise_for_status()
            data = response.json()
            endpoint = candidate
            break
        except Exception as exc:
            errors.append(f"{candidate}: {exc}")
            time.sleep(2)
    if data is None:
        raise SystemExit("Overpass no respondió. " + " | ".join(errors))
    elements = data.get("elements", [])
    ways, relations = {}, []
    for element in elements:
        if element.get("type") == "way":
            coords = [(pt["lon"], pt["lat"]) for pt in element.get("geometry", []) if "lon" in pt and "lat" in pt]
            if len(coords) >= 2:
                ways[element["id"]] = (element, coords)
        elif element.get("type") == "relation":
            relations.append(element)
    features = []
    for element, coords in ways.values():
        props = dict(element.get("tags", {}))
        props.update({"osm_type": "way", "osm_id": element["id"], "source": "OpenStreetMap",
                      "source_license": "ODbL", "route_class": "osm_trail_candidate",
                      "verification": "not_field_verified"})
        features.append({"type": "Feature", "id": f'way/{element["id"]}',
                         "geometry": mapping(LineString(coords)), "properties": props})
    for relation in relations:
        lines = []
        for member in relation.get("members", []):
            if member.get("type") != "way":
                continue
            geometry = member.get("geometry", [])
            coords = [(pt["lon"], pt["lat"]) for pt in geometry if "lon" in pt and "lat" in pt]
            if len(coords) >= 2:
                lines.append(LineString(coords))
            elif member.get("ref") in ways:
                lines.append(LineString(ways[member["ref"]][1]))
        if lines:
            props = dict(relation.get("tags", {}))
            props.update({"osm_type": "relation", "osm_id": relation["id"], "source": "OpenStreetMap",
                          "source_license": "ODbL", "route_class": "osm_hiking_relation",
                          "verification": "not_field_verified"})
            features.append({"type": "Feature", "id": f'relation/{relation["id"]}',
                             "geometry": mapping(MultiLineString(lines)), "properties": props})
    retrieved = datetime.now(timezone.utc).isoformat()
    collection = {"type": "FeatureCollection", "name": "OpenStreetMap hiking paths and trails",
                  "metadata": {"source": "OpenStreetMap contributors", "license": "ODbL",
                               "attribution": "© OpenStreetMap contributors", "retrieved_at": retrieved,
                               "bbox_south_west_north_east": [south, west, north, east],
                               "overpass_endpoint": endpoint, "element_count": len(elements),
                               "feature_count": len(features),
                               "warning": "Candidate paths only; not live status, official evacuation route, or field verification."},
                  "features": features}
    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(collection, ensure_ascii=False)
    output.write_text(payload, encoding="utf-8")
    frontend_output = ROOT / "frontend/data/routes" / output.name
    frontend_output.parent.mkdir(parents=True, exist_ok=True)
    frontend_output.write_text(payload, encoding="utf-8")
    print(f"{len(features)} senderos/caminos exportados: {output}")
    print("Atribución obligatoria: © OpenStreetMap contributors · ODbL")
    print("No verificados en terreno. No usar como rutas oficiales de evacuación.")

if __name__ == "__main__":
    main()
