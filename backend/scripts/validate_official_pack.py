#!/usr/bin/env python3
"""Valida integridad, trazabilidad y completitud de un paquete GIS descargado."""
from __future__ import annotations
import argparse, hashlib, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def validate(manifest_path: Path):
    data = json.loads(manifest_path.read_text(encoding='utf-8'))
    items = data.get('items', [])
    issues, checked = [], 0
    for item in items:
        if item.get('status') != 'downloaded':
            issues.append(f"{item.get('municipality')} / {item.get('name')}: estado {item.get('status', 'sin estado')}")
            continue
        rel = item.get('file')
        if not rel:
            issues.append(f"{item.get('name')}: manifiesto sin ruta de archivo")
            continue
        path = (ROOT / rel).resolve()
        if not path.is_relative_to(ROOT.resolve()):
            issues.append(f"{item.get('name')}: ruta fuera del proyecto rechazada")
            continue
        if not path.is_file():
            issues.append(f"{item.get('name')}: archivo ausente ({rel})")
            continue
        try:
            geo = json.loads(path.read_text(encoding='utf-8'))
        except Exception as exc:
            issues.append(f"{item.get('name')}: GeoJSON ilegible ({exc})")
            continue
        if geo.get('type') != 'FeatureCollection' or not isinstance(geo.get('features'), list):
            issues.append(f"{item.get('name')}: estructura GeoJSON inválida")
            continue
        actual_hash = digest(path)
        if item.get('sha256') and item['sha256'] != actual_hash:
            issues.append(f"{item.get('name')}: SHA-256 no coincide")
        if item.get('features') != len(geo['features']):
            issues.append(f"{item.get('name')}: recuento del manifiesto no coincide")
        if item.get('truncated') or item.get('completeness') == 'truncated_by_user_limit':
            issues.append(f"{item.get('name')}: descarga truncada por límite configurado")
        if geo.get('metadata', {}).get('output_crs') != 'EPSG:4326':
            issues.append(f"{item.get('name')}: CRS de salida no documentado como EPSG:4326")
        checked += 1
    return checked, issues

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--manifest', default='gis/downloaded/manifest.json')
    args = ap.parse_args()
    path = ROOT / args.manifest
    if not path.is_file():
        print(f'No existe manifiesto de descargas: {path}')
        return 2
    checked, issues = validate(path)
    print(f'Capas descargadas e inspeccionadas: {checked}')
    if issues:
        print(f'Observaciones/bloqueos: {len(issues)}')
        for issue in issues:
            print(f'- {issue}')
        return 1
    print('Paquete íntegro según manifiesto. La integridad no certifica vigencia ni exactitud de campo.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
