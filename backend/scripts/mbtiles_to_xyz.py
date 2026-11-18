#!/usr/bin/env python3
"""Convierte un MBTiles raster a teselas XYZ locales para PREPPER MAP.

No descarga cartografía. Requiere un MBTiles obtenido legalmente y con licencia
compatible. MBTiles almacena tile_row en esquema TMS; el script invierte Y.
"""
from __future__ import annotations
import argparse, json, sqlite3, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def convert(source: Path, destination: Path, provider: str, license_name: str, attribution: str):
    if not source.is_file():
        raise FileNotFoundError(source)
    if not provider.strip() or not license_name.strip() or not attribution.strip():
        raise ValueError("Proveedor, licencia y atribución son obligatorios.")
    db = sqlite3.connect(f"file:{source.resolve()}?mode=ro", uri=True)
    try:
        metadata = dict(db.execute("SELECT name, value FROM metadata"))
        fmt = metadata.get("format", "").lower()
        ext = {"png":"png", "jpg":"jpg", "jpeg":"jpg", "webp":"webp"}.get(fmt)
        if not ext:
            raise ValueError(f"Formato raster no compatible: {fmt or 'desconocido'}. No se admiten PBF/vector tiles.")
        rows = db.execute("SELECT zoom_level, tile_column, tile_row, tile_data FROM tiles")
        destination.mkdir(parents=True, exist_ok=True)
        count, minz, maxz = 0, 99, -1
        tile_paths = []
        for z, x, tms_y, blob in rows:
            y = (2 ** int(z) - 1) - int(tms_y)
            if z < 0 or x < 0 or y < 0:
                raise ValueError("Coordenadas de tesela inválidas.")
            out = destination / str(z) / str(x) / f"{y}.{ext}"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(blob)
            tile_paths.append(out.relative_to(destination).as_posix())
            count += 1
            minz, maxz = min(minz, int(z)), max(maxz, int(z))
        if not count:
            raise ValueError("El MBTiles no contiene teselas.")
        manifest = {
            "schema_version": 1, "name": metadata.get("name", source.stem),
            "provider": provider, "license": license_name, "attribution": attribution,
            "format": ext, "scheme": "xyz", "tile_count": count,
            "minzoom": minz, "maxzoom": maxz,
            "bounds": metadata.get("bounds"), "center": metadata.get("center"),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source_file": source.name,
            "warning": "Instantánea cartográfica. No contiene alertas ni actualizaciones en vivo."
        }
        (destination / "tile-index.json").write_text(json.dumps({"schema_version": 1, "tiles": tile_paths}, ensure_ascii=False), encoding="utf-8")
        (destination / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        return manifest
    finally:
        db.close()

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("mbtiles", type=Path)
    p.add_argument("--output", type=Path, default=ROOT / "frontend" / "offline-tiles")
    p.add_argument("--provider", required=True)
    p.add_argument("--license", dest="license_name", required=True)
    p.add_argument("--attribution", required=True)
    a = p.parse_args()
    result = convert(a.mbtiles, a.output, a.provider, a.license_name, a.attribution)
    print(json.dumps(result, ensure_ascii=False, indent=2))
if __name__ == "__main__":
    main()
