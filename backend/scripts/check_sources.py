#!/usr/bin/env python3
"""Audita metadatos de servicios/capas ArcGIS REST; no descarga geometrías."""
from __future__ import annotations
import argparse, json, time
from datetime import datetime, timezone
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parents[2]
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "PREPPER-MAP-PRO/0.4 (civic-resilience-GIS)"})

def get_json(url: str, timeout: int = 30, retries: int = 2):
    last = None
    for attempt in range(retries + 1):
        try:
            response = SESSION.get(url, params={"f": "pjson"}, timeout=timeout)
            response.raise_for_status()
            data = response.json()
            if "error" in data:
                raise RuntimeError(data["error"])
            return data
        except Exception as exc:
            last = str(exc)
            if attempt < retries:
                time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(last)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="gis/sources/sources.json")
    parser.add_argument("--timeout", type=int, default=30)
    args = parser.parse_args()
    config = json.loads((ROOT / args.config).read_text(encoding="utf-8"))
    report = {
        "project": config.get("project"),
        "version": config.get("version"),
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "items": []
    }
    for source in config.get("sources", []):
        try:
            service_meta = get_json(source["service"], args.timeout)
            service_layers = {int(x["id"]): x for x in service_meta.get("layers", [])}
            service_status = "online"
            service_error = None
        except Exception as exc:
            service_layers, service_status, service_error = {}, "unreachable", str(exc)
        for layer in source.get("layers", []):
            row = {
                "source_id": source["id"],
                "municipality": source["municipality"],
                "authority": source.get("authority"),
                "layer_id": layer["id"],
                "configured_name": layer["name"],
                "theme": layer["theme"],
                "url": f'{source["service"].rstrip("/")}/{layer["id"]}',
                "service_status": service_status,
                "status": "unverified",
                "scope_note": source.get("scope_note"),
            }
            if service_status != "online":
                row.update(status="unreachable", error=service_error)
            elif int(layer["id"]) not in service_layers:
                row.update(status="layer_missing", error="ID no aparece en el catálogo actual del servicio")
            else:
                actual = service_layers[int(layer["id"])]
                try:
                    meta = get_json(row["url"], args.timeout)
                    row.update({
                        "status": "metadata_ok",
                        "service_layer_name": actual.get("name"),
                        "geometry_type": meta.get("geometryType"),
                        "max_record_count": meta.get("maxRecordCount", service_meta.get("maxRecordCount")),
                        "object_id_field": meta.get("objectIdField"),
                        "fields": [f.get("name") for f in meta.get("fields", [])],
                        "spatial_reference": meta.get("extent", {}).get("spatialReference", service_meta.get("spatialReference")),
                        "supports_pagination": meta.get("advancedQueryCapabilities", {}).get("supportsPagination"),
                    })
                except Exception as exc:
                    row.update(status="metadata_error", error=str(exc))
            report["items"].append(row)
            print(f'{row["status"]:16} {row["municipality"]:20} {row["layer_id"]:>3} {row["configured_name"]}')
    out = ROOT / "gis/audit"
    out.mkdir(parents=True, exist_ok=True)
    path = out / "source_audit.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    ok = sum(x["status"] == "metadata_ok" for x in report["items"])
    print(f"\n{ok}/{len(report['items'])} capas con metadatos disponibles. Informe: {path}")
    if ok != len(report["items"]):
        raise SystemExit(2)

if __name__ == "__main__":
    main()
