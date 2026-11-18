#!/usr/bin/env python3
"""Extracción reproducible ArcGIS REST -> GeoJSON EPSG:4326 con paginación."""
from __future__ import annotations
import argparse, hashlib, json, re, sys, time, unicodedata
from pathlib import Path
from datetime import datetime, timezone
import requests

ROOT = Path(__file__).resolve().parents[2]
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "PREPPER-MAP-PRO/0.4 civic-resilience-GIS"})

def slug(value):
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "_", value).strip("_")

def get_json(url, params=None, timeout=90, retries=3):
    last = None
    for attempt in range(retries):
        try:
            response = SESSION.get(url, params=params, timeout=timeout)
            response.raise_for_status()
            data = response.json()
            if "error" in data:
                raise RuntimeError(data["error"].get("message", str(data["error"])))
            return data
        except Exception as exc:
            last = exc
            if attempt < retries - 1:
                time.sleep(1.5 * (attempt + 1))
    raise last

def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fetch_features(query_url, object_ids, batch_size, max_features, object_id_field):
    features = []
    if object_ids:
        ids = object_ids[:max_features] if max_features else object_ids
        for start in range(0, len(ids), batch_size):
            batch = ids[start:start + batch_size]
            data = get_json(query_url, {
                "objectIds": ",".join(map(str, batch)),
                "outFields": "*", "returnGeometry": "true",
                "outSR": "4326", "geometryPrecision": "6",
                "returnZ": "false", "returnM": "false", "f": "geojson"
            })
            features.extend(data.get("features", []))
            if max_features and len(features) >= max_features:
                features = features[:max_features]
                break
            print(f"    {min(start + len(batch), len(ids))}/{len(ids)} IDs consultados; {len(features)} geometrías")
    else:
        offset = 0
        pages = 0
        while True:
            params = {
                "where": "1=1", "outFields": "*", "returnGeometry": "true",
                "outSR": "4326", "geometryPrecision": "6",
                "resultOffset": offset, "resultRecordCount": batch_size,
                "returnZ": "false", "returnM": "false", "f": "geojson"
            }
            if object_id_field:
                params["orderByFields"] = object_id_field
            data = get_json(query_url, params)
            batch = data.get("features", [])
            features.extend(batch)
            pages += 1
            if max_features and len(features) >= max_features:
                features = features[:max_features]
                break
            # ArcGIS may report exceededTransferLimit even for a short or empty page.
            # Advance by the requested page size to avoid silently truncating results.
            if data.get("exceededTransferLimit") is True:
                offset += batch_size
                if pages > 100000:
                    raise RuntimeError("Se superó el límite defensivo de 100000 páginas ArcGIS")
                continue
            if len(batch) < batch_size:
                break
            offset += len(batch)
    return features

def extract(source, layer, out_dir, max_features, batch_size):
    layer_url = f'{source["service"].rstrip("/")}/{layer["id"]}'
    meta = get_json(layer_url, {"f": "pjson"})
    query_url = layer_url + "/query"
    object_id_field = meta.get("objectIdField") or meta.get("objectIdFieldName")
    try:
        ids_data = get_json(query_url, {"where": "1=1", "returnIdsOnly": "true", "f": "json"})
        object_ids = ids_data.get("objectIds") or []
    except Exception:
        object_ids = None
    if object_ids:
        features = fetch_features(query_url, sorted(object_ids), batch_size, max_features, object_id_field)
    else:
        # Fallback por paginación cuando el servicio no permite devolver IDs.
        features = fetch_features(query_url, [], batch_size, max_features, object_id_field)
    retrieved = datetime.now(timezone.utc).isoformat()
    feature_collection = {
        "type": "FeatureCollection",
        "name": layer["name"],
        "features": features,
        "metadata": {
            "source_id": source["id"], "municipality": source["municipality"],
            "authority": source.get("authority"), "source_layer_id": layer["id"],
            "source_layer_name": meta.get("name"), "source_geometry_type": meta.get("geometryType"),
            "source_crs": source.get("source_crs"), "output_crs": "EPSG:4326",
            "source_url": layer_url, "scope_note": source.get("scope_note"),
            "retrieved_at": retrieved, "license_note": source.get("license_status"),
            "feature_count": len(features), "truncated": bool(max_features and len(object_ids) > max_features)
        }
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    frontend_data = ROOT / "frontend" / "data"
    frontend_data.mkdir(parents=True, exist_ok=True)
    filename = f'{slug(source["municipality"])}_{layer["id"]}_{slug(layer["theme"])}.geojson'
    content = json.dumps(feature_collection, ensure_ascii=False, separators=(",", ":"))
    out_path = out_dir / filename
    front_path = frontend_data / filename
    out_path.write_text(content, encoding="utf-8")
    front_path.write_text(content, encoding="utf-8")
    digest = sha256_file(out_path)
    truncated = bool(max_features and len(object_ids or []) > max_features)
    return {
        "status": "downloaded", "source_id": source["id"], "municipality": source["municipality"],
        "layer_id": layer["id"], "name": layer["name"], "theme": layer["theme"],
        "features": len(features), "file": f"gis/downloaded/{filename}",
        "frontend_file": f"data/{filename}", "source_url": layer_url,
        "source_crs": source.get("source_crs"), "output_crs": "EPSG:4326",
        "retrieved_at": retrieved, "truncated": truncated,
        "completeness": "truncated_by_user_limit" if truncated else "retrieved_from_service",
        "sha256": digest, "bytes": out_path.stat().st_size,
        "license_note": source.get("license_status")
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="gis/sources/sources.json")
    parser.add_argument("--municipality")
    parser.add_argument("--source")
    parser.add_argument("--layer", type=int)
    parser.add_argument("--max-features", type=int, default=100000)
    parser.add_argument("--batch-size", type=int, default=500)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.max_features < 0 or args.batch_size < 1:
        parser.error("--max-features debe ser >=0 y --batch-size >=1")
    config = json.loads((ROOT / args.config).read_text(encoding="utf-8"))
    output = ROOT / "gis/downloaded"
    output.mkdir(parents=True, exist_ok=True)
    items = []
    for source in config["sources"]:
        if args.municipality and args.municipality.casefold() not in source["municipality"].casefold():
            continue
        if args.source and args.source != source["id"]:
            continue
        for layer in source["layers"]:
            if args.layer is not None and args.layer != int(layer["id"]):
                continue
            record = {"source_id": source["id"], "municipality": source["municipality"],
                      "name": layer["name"], "theme": layer["theme"],
                      "source_url": f'{source["service"].rstrip("/")}/{layer["id"]}'}
            try:
                if args.dry_run:
                    meta = get_json(record["source_url"], {"f": "pjson"})
                    record.update({"status": "metadata_ok", "service_layer_name": meta.get("name"),
                                   "geometry_type": meta.get("geometryType"),
                                   "max_record_count": meta.get("maxRecordCount"),
                                   "object_id_field": meta.get("objectIdField"),
                                   "supports_pagination": meta.get("advancedQueryCapabilities", {}).get("supportsPagination"),
                                   "fields": [f.get("name") for f in meta.get("fields", [])]})
                else:
                    record.update(extract(source, layer, output, args.max_features, args.batch_size))
            except Exception as exc:
                record.update({"status": "failed", "error": str(exc)})
            items.append(record)
            print(record.get("status"), record["municipality"], record["name"],
                  record.get("features", record.get("error", "")))
    manifest = {"project": config["project"], "version": config["version"],
                "created_at": datetime.now(timezone.utc).isoformat(),
                "output_crs": "EPSG:4326", "items": items}
    (output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    frontend_data = ROOT / "frontend" / "data"
    frontend_data.mkdir(parents=True, exist_ok=True)
    (frontend_data / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    failed = [item for item in items if item.get("status") == "failed"]
    print(f"\n{len(items)-len(failed)}/{len(items)} capas procesadas. Manifiesto: {output/'manifest.json'}")
    if failed:
        raise SystemExit(2)

if __name__ == "__main__":
    main()
