#!/usr/bin/env python3
"""Preflight de distribución: evita anunciar cartografía offline inexistente."""
import json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def check(root=ROOT):
    root=Path(root); issues=[]; notes=[]
    cfg=json.loads((root/'src-tauri/tauri.conf.json').read_text());pkg=json.loads((root/'package.json').read_text())
    if pkg['version']!=cfg['version']:issues.append('versiones de package.json y Tauri distintas')
    if not (root/'frontend/vendor/leaflet/leaflet.js').is_file():notes.append('vendor JS no instalado: ejecutar npm install y npm run sync:vendor')
    tile=root/'frontend/offline-tiles/manifest.json'
    if tile.exists():
        m=json.loads(tile.read_text());idx=root/'frontend/offline-tiles/tile-index.json'
        if not idx.exists():issues.append('paquete cartográfico sin tile-index.json')
        if not all(m.get(k) for k in ('provider','license','attribution')):issues.append('faltan metadatos de licencia de mapas')
    else:notes.append('no hay mapas base offline regionales incluidos')
    data=json.loads((root/'frontend/data/manifest.json').read_text())
    if not any(x.get('status')=='downloaded' for x in data.get('items',[])):notes.append('no hay capas GIS oficiales descargadas')
    if not __import__('os').getenv('PREPPER_TOKENS'):notes.append('API de sincronización deshabilitada hasta provisionar tokens/roles/tenant')
    if not (root/'src-tauri/target').exists():notes.append('no hay binarios nativos compilados y probados')
    if not (root/'gis/audits/catalog-audit-remote-latest.json').exists():notes.append('no hay auditoría remota reciente de disponibilidad de servicios GIS')
    notes.append('sin adaptadores completos de aplicación de eventos ni resolución de conflictos multiusuario')
    notes.append('sin identidad corporativa/MFA ni prueba de penetración')
    return {'ready_for_public_release':not issues and not notes,'blocking_issues':issues,'pending':notes}
if __name__=='__main__':
    result=check();print(json.dumps(result,ensure_ascii=False,indent=2));sys.exit(1 if result['blocking_issues'] else 0)
