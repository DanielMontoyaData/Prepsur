#!/usr/bin/env python3
"""Auditoría reproducible del inventario GIS local sin fingir datos disponibles."""
import argparse, hashlib, json, math
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def positions(geom):
    if not isinstance(geom, dict):
        raise ValueError('geometría inválida')
    if geom.get('type') == 'GeometryCollection':
        for sub in geom.get('geometries', []):
            yield from positions(sub)
        return
    def walk(coords):
        if not isinstance(coords, list) or not coords:
            raise ValueError('coordenadas vacías o inválidas')
        if isinstance(coords[0], (int, float)):
            if len(coords) < 2 or any(not isinstance(x, (int,float)) or not math.isfinite(x) for x in coords[:2]):
                raise ValueError('posición no finita')
            lon,lat=coords[:2]
            if not (-180<=lon<=180 and -90<=lat<=90):
                raise ValueError('coordenadas fuera de EPSG:4326')
            yield lon,lat
        else:
            for c in coords: yield from walk(c)
    yield from walk(geom.get('coordinates'))

def audit(root=ROOT, max_age_days=180, now=None):
    root=Path(root); now=now or datetime.now(timezone.utc)
    manifest_path=root/'frontend/data/manifest.json'
    manifest=json.loads(manifest_path.read_text(encoding='utf-8')) if manifest_path.exists() else {'items':[]}
    catalog_path=root/'gis/sources/sources.json'
    catalog=json.loads(catalog_path.read_text(encoding='utf-8')) if catalog_path.exists() else {'sources':[]}
    records=list(manifest.get('items',[]))
    known={(x.get('source_id'),str(x.get('layer_id'))) for x in records}
    for source in catalog.get('sources',[]):
        for layer in source.get('layers',[]):
            key=(source['id'],str(layer['id']))
            if key not in known:
                records.append({'source_id':source['id'],'layer_id':layer['id'],'municipality':source['municipality'],
                    'name':layer['name'],'theme':layer['theme'],'status':'not_downloaded',
                    'source_url':source['service'].rstrip('/')+'/'+str(layer['id']),
                    'license_note':source.get('license_status')})
    items=[]; errors=0; warnings=0
    for item in records:
        row={k:item.get(k) for k in ('municipality','name','theme','status','source_url','retrieved_at','license_note')}
        row['issues']=[]
        if item.get('status')!='downloaded':
            row['issues'].append('no_descargado')
        else:
            rel=item.get('frontend_file','')
            path=(root/'frontend'/rel).resolve()
            if not path.is_relative_to((root/'frontend').resolve()) or not path.is_file():
                row['issues'].append('archivo_faltante_o_ruta_insegura')
            else:
                try:
                    raw=path.read_bytes(); data=json.loads(raw)
                    if data.get('type')!='FeatureCollection' or not isinstance(data.get('features'),list):
                        raise ValueError('no es FeatureCollection')
                    bounds=[180,90,-180,-90]; n=0
                    for f in data['features']:
                        if f.get('type')!='Feature': raise ValueError('elemento no Feature')
                        if f.get('geometry') is None: continue
                        for x,y in positions(f['geometry']):
                            bounds=[min(bounds[0],x),min(bounds[1],y),max(bounds[2],x),max(bounds[3],y)];n+=1
                    row.update(features=len(data['features']),size_bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),bbox=bounds if n else None)
                    if item.get('features') is not None and item['features']!=len(data['features']):row['issues'].append('conteo_inconsistente')
                    if not data['features']:row['issues'].append('coleccion_vacia')
                except (ValueError,KeyError,TypeError,json.JSONDecodeError) as e:
                    row['issues'].append('geojson_invalido:'+str(e)[:120])
            try:
                dt=datetime.fromisoformat(item['retrieved_at'].replace('Z','+00:00'))
                if dt.tzinfo is None: raise ValueError('sin zona horaria')
                row['age_days']=max(0,(now-dt).days)
                if row['age_days']>max_age_days:row['issues'].append('dato_antiguo')
            except (KeyError,AttributeError,ValueError):row['issues'].append('fecha_desconocida')
            if item.get('truncated'):row['issues'].append('descarga_incompleta')
            if not item.get('license_note'):row['issues'].append('licencia_no_documentada')
            if not item.get('source_url'):row['issues'].append('fuente_no_documentada')
        row['quality']='no_disponible' if 'no_descargado' in row['issues'] else ('revisar' if row['issues'] else 'consistente')
        errors+=sum(x.startswith(('geojson_invalido','archivo_faltante','conteo_inconsistente')) for x in row['issues'])
        warnings+=len(row['issues'])
        items.append(row)
    return {'schema_version':1,'generated_at':now.isoformat(),'max_age_days':max_age_days,'summary':{'catalog_entries':len(items),'downloaded':sum(x['status']=='downloaded' for x in items),'consistent':sum(x['quality']=='consistente' for x in items),'errors':errors,'issues':warnings},'items':items,'disclaimer':'Consistencia de datos, no certificación de seguridad, completitud ni actualidad de amenazas.'}

def main():
    p=argparse.ArgumentParser();p.add_argument('--max-age-days',type=int,default=180);p.add_argument('--output',default='frontend/data/quality-report.json');p.add_argument('--strict',action='store_true');a=p.parse_args()
    if a.max_age_days<0:p.error('max-age-days debe ser >= 0')
    result=audit(max_age_days=a.max_age_days);path=ROOT/a.output;path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result['summary'],ensure_ascii=False))
    if a.strict and result['summary']['errors']:raise SystemExit(1)
if __name__=='__main__':main()
