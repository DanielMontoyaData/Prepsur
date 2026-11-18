#!/usr/bin/env python3
"""Empaqueta aplicación y datos locales existentes; no descarga teselas."""
import argparse, json, zipfile
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output", default="dist/prepper-map-offline.zip")
    a = p.parse_args()
    output = ROOT / a.output
    output.parent.mkdir(parents=True, exist_ok=True)
    included, skipped = [], []
    include_roots = [ROOT / "frontend", ROOT / "docs", ROOT / "gis" / "routes", ROOT / "gis" / "terrain"]
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as z:
        for base in include_roots:
            if not base.exists(): continue
            for path in base.rglob("*"):
                if not path.is_file(): continue
                rel = path.relative_to(ROOT)
                if any(part in {".git", "__pycache__", "node_modules"} for part in rel.parts):
                    skipped.append(str(rel)); continue
                z.write(path, rel.as_posix()); included.append(str(rel))
        gis = ROOT / "gis" / "downloaded"
        if gis.exists():
            for path in gis.glob("*.geojson"):
                rel = path.relative_to(ROOT)
                z.write(path, rel.as_posix()); included.append(str(rel))
            manifest = gis / "manifest.json"
            if manifest.exists():
                z.write(manifest, manifest.relative_to(ROOT).as_posix())
                included.append(str(manifest.relative_to(ROOT)))
        report = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "included_files": included,
            "skipped_files": skipped,
            "offline_limitations": [
                "No incluye teselas base salvo que se incorporen con licencia válida.",
                "Incluye capas GeoJSON y derivados de terreno locales si existen en gis/routes y gis/terrain.",
                "No recibe alertas nuevas ni consulta servicios remotos sin internet.",
                "La última descarga puede estar desactualizada; revisar su fecha."
            ]
        }
        z.writestr("OFFLINE_PACKAGE_MANIFEST.json", json.dumps(report, ensure_ascii=False, indent=2))
    print(f"Paquete: {output}")
    print(f"Archivos incluidos: {len(included)}")
    print("Nota: es un paquete de datos y aplicación; no garantiza cartografía base offline.")
if __name__ == "__main__":
    main()
