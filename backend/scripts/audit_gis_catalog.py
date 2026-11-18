#!/usr/bin/env python3
"""Validate municipal ArcGIS catalog locally or remotely; optionally extract each layer."""
import argparse, json, hashlib, subprocess, sys, time
from pathlib import Path
from datetime import datetime, timezone
import requests
ROOT=Path(__file__).resolve().parents[2]
S= requests.Session(); S.headers['User-Agent']='PREPPER-MAP-PRO/2.2 public-sector-GIS-catalog-audit'
def main():
 p=argparse.ArgumentParser(); p.add_argument('--config',default='gis/sources/sources.json'); p.add_argument('--municipality'); p.add_argument('--remote',action='store_true'); p.add_argument('--download',action='store_true'); p.add_argument('--max-features',type=int,default=0); p.add_argument('--timeout',type=int,default=25); a=p.parse_args()
 cfg=json.loads((ROOT/a.config).read_text(encoding='utf8')); out=[]
 for src in cfg.get('sources',[]):
  if a.municipality and a.municipality.casefold() not in src.get('municipality','').casefold(): continue
  base=src.get('service','').rstrip('/'); row={'source_id':src.get('id'),'municipality':src.get('municipality'),'authority':src.get('authority'),'service':base,'scope_note':src.get('scope_note'),'layers':[]}
  if not base.startswith('https://'): row['service_status']='invalid_non_https'
  elif a.remote:
   try:
    r=S.get(base,params={'f':'pjson'},timeout=a.timeout); r.raise_for_status(); meta=r.json()
    if meta.get('error'): raise RuntimeError(meta['error'].get('message','ArcGIS error'))
    row['service_status']='reachable'; row['service_name']=meta.get('mapName'); row['service_description']=meta.get('serviceDescription')
   except Exception as e: row['service_status']='failed'; row['error']=str(e)
  else: row['service_status']='not_checked_remote'
  for lyr in src.get('layers',[]):
   item={'id':lyr.get('id'),'name':lyr.get('name'),'theme':lyr.get('theme'),'url':f"{base}/{lyr.get('id')}"}
   if a.remote and row['service_status']=='reachable':
    try:
     r=S.get(item['url'],params={'f':'pjson'},timeout=a.timeout); r.raise_for_status(); m=r.json()
     if m.get('error'): raise RuntimeError(m['error'].get('message','Layer error'))
     item.update(status='metadata_ok',service_layer_name=m.get('name'),geometry_type=m.get('geometryType'),max_record_count=m.get('maxRecordCount'),object_id_field=m.get('objectIdField') or m.get('objectIdFieldName'),supports_pagination=m.get('advancedQueryCapabilities',{}).get('supportsPagination'))
    except Exception as e: item.update(status='failed',error=str(e))
   else: item['status']='not_checked_remote' if a.remote else 'catalog_only'
   row['layers'].append(item)
   if a.download and item.get('status')=='metadata_ok':
    cmd=[sys.executable,str(ROOT/'backend/scripts/extract_arcgis.py'),'--source',src['id'],'--layer',str(lyr['id']),'--max-features',str(a.max_features),'--batch-size','500']
    result=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True)
    item['download_exit_code']=result.returncode; item['download_log']=(result.stdout+'\n'+result.stderr)[-4000:]
    item['download_status']='downloaded' if result.returncode==0 else 'failed'
   time.sleep(.08)
  out.append(row)
 report={'project':'PREPPER MAP PRO','version':'2.2.0','generated_at':datetime.now(timezone.utc).isoformat(),'remote_checked':a.remote,'download_requested':a.download,'scope':'Metadatos de servicios; no certifica vigencia temática ni precisión de campo.','summary':{'sources':len(out),'layers':sum(len(x['layers']) for x in out),'reachable_services':sum(x.get('service_status')=='reachable' for x in out),'failed_services':sum(x.get('service_status')=='failed' for x in out),'failed_layers':sum(l.get('status')=='failed' for x in out for l in x['layers'])},'sources':out}
 target=ROOT/'gis/audits'; target.mkdir(parents=True,exist_ok=True); dest=target/('catalog-audit-remote-latest.json' if a.remote else 'catalog-audit-local-latest.json'); dest.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
 print(json.dumps(report['summary'],ensure_ascii=False)); print(f'Reporte: {dest}')
 if report['summary']['failed_services'] or report['summary']['failed_layers']: return 2
 return 0
if __name__=='__main__': raise SystemExit(main())
