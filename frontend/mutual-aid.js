/* PREPPER MAP PRO 1.9 — coordinación intermunicipal local y auditable. */
(()=>{'use strict';
const KEY='prepper-map-mutual-aid-v1', $=id=>document.getElementById(id), now=()=>new Date().toISOString();
const STATES=['solicitada','evaluada','aprobada','asignada','en_transito','recibida','cerrada','rechazada'];
const TRANSITIONS={solicitada:['evaluada','rechazada'],evaluada:['aprobada','solicitada','rechazada'],aprobada:['asignada','evaluada','rechazada'],asignada:['en_transito','aprobada','rechazada'],en_transito:['recibida','asignada'],recibida:['cerrada'],cerrada:[],rechazada:[]};
const LABELS={solicitada:'Solicitada',evaluada:'Evaluada',aprobada:'Aprobada',asignada:'Asignada',en_transito:'En tránsito',recibida:'Recibida',cerrada:'Cerrada',rechazada:'Rechazada'};
let rows=[];
const el=(tag,text,cls)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n;};
const active=x=>!['cerrada','rechazada'].includes(x.status);
function save(){try{localStorage.setItem(KEY,JSON.stringify({schema_version:1,updated_at:now(),requests:rows}));return true;}catch(e){$('maWarnings').textContent=`No se pudo guardar localmente: ${e.message}`;return false;}}
function load(){try{const d=JSON.parse(localStorage.getItem(KEY)||'{"schema_version":1,"requests":[]}');if(d.schema_version!==1||!Array.isArray(d.requests))throw Error('Formato de almacenamiento no reconocido.');rows=d.requests.filter(x=>x&&typeof x.id==='string'&&STATES.includes(x.status)).slice(-1000);}catch(e){rows=[];$('maWarnings').textContent=`No se pudieron leer solicitudes: ${e.message}`;}}
function committedFor(resourceId,unit,provider,exceptId=null){if(!resourceId)return 0;return rows.filter(x=>x.id!==exceptId&&x.resource_id===resourceId&&x.provider===provider&&x.unit===unit&&['asignada','en_transito','recibida'].includes(x.status)).reduce((n,x)=>n+Number(x.committed||0),0);}
function validateCapacity(item,exceptId=null){
 if(!item.resource_id||item.capacity===null||item.capacity===undefined)return null;
 const already=committedFor(item.resource_id,item.unit,item.provider,exceptId);
 const proposed=['asignada','en_transito','recibida'].includes(item.status)?Number(item.committed||0):0;
 if(already+proposed>Number(item.capacity)+1e-9)return `Compromiso excedido: ${already} ${item.unit} ya comprometidos y ${proposed} adicionales; capacidad declarada ${item.capacity}.`;
 return null;
}
function metrics(){
 const open=rows.filter(active), committed=rows.filter(x=>['asignada','en_transito','recibida'].includes(x.status));
 const totalRequested=open.reduce((n,x)=>n+Number(x.requested||0),0), totalCommitted=committed.reduce((n,x)=>n+Number(x.committed||0),0);
 const byMunicipality={};open.forEach(x=>{byMunicipality[x.requester]=(byMunicipality[x.requester]||0)+1;});
 return {open:open.length,committed:committed.length,totalRequested,totalCommitted,byMunicipality};
}
function render(){
 const dash=$('maDashboard'),list=$('maList');dash.replaceChildren();list.replaceChildren();
 const m=metrics();
 [['Solicitudes activas',m.open],['Con compromiso activo',m.committed],['Cantidad solicitada (unidades mixtas)',m.totalRequested],['Cantidad comprometida (unidades mixtas)',m.totalCommitted]].forEach(([k,v])=>{const d=el('div',undefined,'resource');d.append(el('small',k),el('b',Number(v).toLocaleString('es-CO')));dash.append(d);});
 $('maWarnings').textContent=rows.length?`${rows.length} registros locales · ${Object.entries(m.byMunicipality).map(([k,v])=>`${k}: ${v}`).join(' · ')||'Sin solicitudes activas'}. Los totales mezclan unidades distintas y son solo indicadores de volumen, no sumas físicas comparables.`:'Sin solicitudes registradas. No se han creado recursos ni compromisos automáticamente.';
 rows.slice().reverse().slice(0,100).forEach(x=>{
  const card=el('div',undefined,'resource'),head=el('b',`${x.id} · ${x.requester} ← ${x.provider}`),meta=el('div',`${x.description} · ${x.category} · ${x.requested} ${x.unit} solicitados · ${x.status==='solicitada'||x.status==='evaluada'||x.status==='aprobada'?0:Number(x.committed||0)} ${x.unit} comprometidos`),detail=el('small',`Recurso: ${x.resource_id||'sin identificador'} · Capacidad declarada: ${x.capacity??'no informada'} · Roles: ${x.requester_role||'—'} / ${x.provider_role||'—'} · Requerido: ${x.needed_at||'sin fecha'} · Fuente: ${x.source||'no indicada'}`);
  card.append(head,meta,detail);
  if(x.notes)card.append(el('small',`Observaciones: ${x.notes}`));
  const controls=el('div',undefined,'actions');controls.style.marginTop='7px';
  const select=document.createElement('select');select.setAttribute('aria-label',`Estado de ${x.id}`);
  STATES.forEach(s=>{const o=document.createElement('option');o.value=s;o.textContent=LABELS[s];o.selected=x.status===s;select.append(o);});
  select.addEventListener('change',()=>changeState(x.id,select.value));
  const qty=document.createElement('input');qty.type='number';qty.min='0';qty.step='any';qty.value=String(x.committed??'');qty.placeholder='Cantidad comprometida';qty.setAttribute('aria-label',`Cantidad comprometida ${x.id}`);qty.style.maxWidth='150px';
  const commit=el('button','Guardar compromiso');commit.type='button';commit.addEventListener('click',()=>setCommitment(x.id,qty.value));
  controls.append(select,qty,commit);card.append(controls);list.append(card);
 });
 if(rows.length>100)list.append(el('small','Se muestran las 100 solicitudes más recientes.'));
}
function changeState(id,next){
 const x=rows.find(y=>y.id===id);if(!x||!STATES.includes(next))return;
 if(!TRANSITIONS[x.status]?.includes(next)){alert(`Transición no permitida: ${LABELS[x.status]} → ${LABELS[next]}.`);render();return;}
 if(['asignada','en_transito','recibida'].includes(next)&&!(Number(x.committed)>0)){alert('Registra primero una cantidad comprometida mayor que cero.');render();return;}
 const old=x.status;x.status=next;x.updated_at=now();
 const issue=validateCapacity(x,id);
 if(issue){x.status=old;alert(issue);render();return;}
 x.history=Array.isArray(x.history)?x.history:[];x.history.push({at:now(),from:old,to:next,by_role:'Operador local'});
 save();render();
}
function setCommitment(id,value){
 const x=rows.find(y=>y.id===id);if(!x)return;
 const n=Number(value);if(!Number.isFinite(n)||n<0||n>x.requested){alert('La cantidad comprometida debe ser válida y no superar la cantidad solicitada.');render();return;}
 if(['asignada','en_transito','recibida'].includes(x.status)&&n<=0){alert('Una solicitud asignada, en tránsito o recibida debe conservar un compromiso mayor que cero.');render();return;}
 const old=x.committed;x.committed=n;
 const issue=validateCapacity(x,id);if(issue){x.committed=old;alert(issue);render();return;}
 x.updated_at=now();save();render();
}
$('maCreate').addEventListener('click',()=>{
 const requester=$('maRequester').value,provider=$('maProvider').value,description=$('maDescription').value.trim(),resourceId=$('maResourceId').value.trim(),requested=Number($('maRequested').value),unit=$('maUnit').value.trim(),capacityRaw=$('maCapacity').value.trim(),capacity=capacityRaw===''?null:Number(capacityRaw);
 if(requester===provider){alert('El municipio solicitante y el oferente deben ser diferentes.');return;}
 if(!description||!unit||!Number.isFinite(requested)||requested<=0){alert('Completa descripción, unidad y cantidad solicitada válida.');return;}
 if(capacity!==null&&(!Number.isFinite(capacity)||capacity<=0)){alert('La capacidad declarada debe ser mayor que cero.');return;}
 if(capacity!==null&&!resourceId){alert('Para controlar capacidad, registra el identificador del recurso.');return;}
 const item={id:`MA-${now().replace(/[-:.TZ]/g,'').slice(0,14)}-${Math.random().toString(36).slice(2,6).toUpperCase()}`,requester,provider,category:$('maCategory').value,resource_id:resourceId||null,description,requested,committed:0,unit,capacity,requester_role:$('maRequesterRole').value.trim(),provider_role:$('maProviderRole').value.trim(),needed_at:$('maNeededAt').value||null,source:$('maSource').value.trim()||null,notes:$('maNotes').value.trim(),status:'solicitada',created_at:now(),updated_at:now(),history:[{at:now(),from:null,to:'solicitada',by_role:'Operador local'}]};
 rows.push(item);rows=rows.slice(-1000);if(save()){['maResourceId','maDescription','maRequesterRole','maProviderRole','maNeededAt','maSource','maNotes','maCapacity'].forEach(id=>$(id).value='');$('maRequested').value='1';render();}
});
function download(name,obj,type='application/json'){const blob=new Blob([obj],{type}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1500);}
$('maExport').addEventListener('click',()=>download(`prepper-map-coordinacion-${now().slice(0,10)}.json`,JSON.stringify({application:'PREPPER MAP PRO',kind:'intermunicipal_mutual_aid',schema_version:1,exported_at:now(),requests:rows},null,2)));
$('maCSV').addEventListener('click',()=>{const cols=['id','requester','provider','category','resource_id','description','requested','committed','unit','capacity','status','requester_role','provider_role','needed_at','source','created_at','updated_at','notes'];const q=v=>'"'+String(v??'').replace(/"/g,'""')+'"';download(`prepper-map-coordinacion-${now().slice(0,10)}.csv`,[cols.join(','),...rows.map(x=>cols.map(k=>q(x[k])).join(','))].join('\r\n'),'text/csv;charset=utf-8');});
$('maImport').addEventListener('click',()=>$('maFile').click());
$('maFile').addEventListener('change',async e=>{const f=e.target.files?.[0];if(!f)return;try{if(f.size>10*1024*1024)throw Error('Archivo mayor a 10 MB.');const d=JSON.parse(await f.text());if(d.application!=='PREPPER MAP PRO'||d.kind!=='intermunicipal_mutual_aid'||d.schema_version!==1||!Array.isArray(d.requests)||d.requests.length>1000)throw Error('Respaldo de coordinación no válido.');const ids=new Set(rows.map(x=>x.id));let added=0;for(const x of d.requests){if(!x||typeof x.id!=='string'||!STATES.includes(x.status)||ids.has(x.id))continue;const candidate={...x};const issue=validateCapacity(candidate);if(issue)throw Error(`Conflicto en ${x.id}: ${issue}`);rows.push(candidate);ids.add(x.id);added++;}rows=rows.slice(-1000);if(save()){$('maWarnings').textContent=`Importación completada: ${added} registro(s) nuevos. Revisa procedencia y vigencia antes de operar.`;render();}}catch(err){alert(`No se pudo importar: ${err.message}`);}finally{e.target.value='';}});
load();render();
})();