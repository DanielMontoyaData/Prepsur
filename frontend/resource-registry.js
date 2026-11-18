/* PREPPER MAP 1.5 — inventario local de capacidades y recursos. */
(() => {
 'use strict';
 const KEY='prepper-map-resource-registry-v1', $=id=>document.getElementById(id), now=()=>new Date().toISOString();
 let rows=[];
 const node=(tag,text,cls)=>{const e=document.createElement(tag);if(text!==undefined)e.textContent=text;if(cls)e.className=cls;return e;};
 const coord=(a,b)=>Number.isFinite(a)&&Number.isFinite(b)&&a>=-90&&a<=90&&b>=-180&&b<=180;
 function save(){try{localStorage.setItem(KEY,JSON.stringify({schema_version:1,updated_at:now(),resources:rows}));return true;}catch(e){$('rrSummary').textContent=`No se pudo guardar: ${e.message}`;return false;}}
 function load(){try{const d=JSON.parse(localStorage.getItem(KEY)||'{"schema_version":1,"resources":[]}');if(d.schema_version!==1||!Array.isArray(d.resources))throw Error('Formato no reconocido');rows=d.resources.filter(x=>x&&typeof x.id==='string'&&typeof x.name==='string').slice(-500);}catch(e){$('rrSummary').textContent=`No se pudo leer el inventario: ${e.message}`;rows=[];}}
 function markers(){
   const layer=window.PREPPER_MAP_RESOURCE_LAYER;if(!layer||!window.L)return;layer.clearLayers();
   rows.filter(x=>x.status==='verificado'&&x.lat!==null&&x.lat!==undefined&&x.lon!==null&&x.lon!==undefined&&coord(Number(x.lat),Number(x.lon))).forEach(x=>{
     const m=L.circleMarker([Number(x.lat),Number(x.lon)],{radius:6,color:'#38bdf8',fillColor:'#38bdf8',fillOpacity:.8,weight:2});
     const pop=node('div');pop.append(node('b',x.name),node('div',`${x.category} · ${x.municipality}`),node('div',`Estado: ${x.status}`),node('div',x.source||'Fuente no indicada'));
     m.bindPopup(pop);m.addTo(layer);
   });
 }
 function render(){
   const list=$('rrList');list.replaceChildren();
   const counts={verificado:0,por_verificar:0,inactivo:0};rows.forEach(x=>counts[x.status]=(counts[x.status]||0)+1);
   $('rrSummary').textContent=`${rows.length} recursos · ${counts.verificado} verificados · ${counts.por_verificar} por verificar · ${counts.inactivo} inactivos.`;
   rows.slice().reverse().slice(0,60).forEach(x=>{
     const d=node('div',undefined,'resource'),title=node('b',`${x.name} · ${x.status.replaceAll('_',' ')}`);
     d.append(title,node('div',`${x.category} · ${x.municipality} · ${x.capacity||'Capacidad no registrada'}`),node('small',`Fuente: ${x.source||'No indicada'} · ${x.verified_at?new Date(x.verified_at).toLocaleDateString():'Sin fecha de verificación'}`));
     const del=node('button','Eliminar');del.type='button';del.addEventListener('click',()=>{if(!confirm(`¿Eliminar el registro ${x.name}?`))return;rows=rows.filter(y=>y.id!==x.id);save();render();});d.append(del);list.append(d);
   });
   if(rows.length>60)list.append(node('small','Se muestran los 60 registros más recientes.'));
   markers();
 }
 $('rrAdd').addEventListener('click',()=>{
   const name=$('rrName').value.trim(),source=$('rrSource').value.trim(),status=$('rrStatus').value;
   if(!name){alert('Indica el nombre del recurso.');return;}
   if(!source){alert('Indica la fuente verificable o escribe la referencia documental.');return;}
   const lat=$('rrLat').value.trim()===''?null:Number($('rrLat').value),lon=$('rrLon').value.trim()===''?null:Number($('rrLon').value);
   if((lat===null)!==(lon===null)||(lat!==null&&!coord(lat,lon))){alert('Coordenadas incompletas o fuera de rango.');return;}
   if(status==='verificado'&&!confirm('¿Confirmaste directamente la existencia, ubicación y disponibilidad actual del recurso?'))return;
   const item={id:`RR-${Date.now()}-${Math.random().toString(36).slice(2,6)}`,name,category:$('rrCategory').value,municipality:$('rrMunicipality').value,status,capacity:$('rrCapacity').value.trim(),location:$('rrLocation').value.trim(),source,lat,lon,notes:$('rrNotes').value.trim(),created_at:now(),verified_at:status==='verificado'?now():null};
   rows.push(item);rows=rows.slice(-500);
   if(save()){window.dispatchEvent(new CustomEvent('prepper:event',{detail:{event_id:`${item.id}-${item.created_at}`,entity_type:'resource',entity_id:item.id,operation:'create',created_at:item.created_at,source_device:'prepper-webview',schema_version:1,payload:item}}));['rrName','rrCapacity','rrLocation','rrSource','rrLat','rrLon','rrNotes'].forEach(id=>$(id).value='');render();}
 });
 $('rrExport').addEventListener('click',()=>{
   const blob=new Blob([JSON.stringify({application:'PREPPER MAP',kind:'resource_registry',schema_version:1,exported_at:now(),resources:rows},null,2)],{type:'application/json'});
   const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=`prepper-map-recursos-${now().slice(0,10)}.json`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1200);
 });
 $('rrImport').addEventListener('click',()=>$('rrFile').click());
 $('rrFile').addEventListener('change',async e=>{
   const file=e.target.files?.[0];if(!file)return;
   try{const d=JSON.parse(await file.text());if(d.application!=='PREPPER MAP'||d.kind!=='resource_registry'||d.schema_version!==1||!Array.isArray(d.resources)||d.resources.length>500)throw Error('Respaldo de recursos no válido.');
     const ids=new Set(rows.map(x=>x.id));d.resources.forEach(x=>{if(x&&typeof x.id==='string'&&typeof x.name==='string'&&!ids.has(x.id)){rows.push(x);ids.add(x.id);}});rows=rows.slice(-500);if(save())render();
   }catch(err){alert(`No se pudo importar: ${err.message}`);}finally{e.target.value='';}
 });
 load();render();
})();
