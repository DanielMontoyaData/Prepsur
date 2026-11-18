/* PREPPER MAP PRO 2.0 — consolidated local operational picture; read-only. */
(()=>{'use strict';
const $=id=>document.getElementById(id), now=()=>new Date(), keys={
 incidents:'prepper-map-incident-command-v2',
 resources:'prepper-map-resource-registry-v1',
 mutual:'prepper-map-mutual-aid-v1',
 autonomy:'prepper-map-autonomy-v1'
};
const municipalities=['Envigado','Itagüí','Sabaneta','La Estrella','Caldas','Medellín'];
const read=(key,field)=>{try{const x=JSON.parse(localStorage.getItem(key)||'{}');return Array.isArray(x[field])?x[field]:[];}catch(_){return [];}};
const date=x=>{const d=new Date(x);return Number.isFinite(d.getTime())?d:null;};
const ageDays=x=>{const d=date(x);return d?Math.max(0,(now()-d)/86400000):null;};
const fresh=(x,days)=>{const a=ageDays(x);return a!==null&&a<=days;};
const node=(tag,text,cls)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n;};
let latest=null;
function snapshot(){
 const municipality=$('sitMunicipality').value, days=Math.max(1,Math.min(365,Number($('sitFreshDays').value)||7));
 const allInc=read(keys.incidents,'incidents'), allRes=read(keys.resources,'resources'), allMut=read(keys.mutual,'requests');
 const filter=x=>municipality==='todos'||x.municipality===municipality||x.requester===municipality||x.provider===municipality;
 const incidents=allInc.filter(filter), resources=allRes.filter(filter), requests=allMut.filter(filter);
 const activeInc=incidents.filter(x=>!['cerrado','cerrada','resuelto','finalizado'].includes(String(x.status||'').toLowerCase()));
 const p1=activeInc.filter(x=>x.priority==='P1');
 const unlocated=activeInc.filter(x=>x.lat===null||x.lat===undefined||x.lon===null||x.lon===undefined);
 const unassigned=activeInc.filter(x=>!Array.isArray(x.assignments)||!x.assignments.some(a=>['asignado','en_camino','en_sitio'].includes(a.status)));
 const verified=resources.filter(x=>x.status==='verificado');
 const staleVerified=verified.filter(x=>!fresh(x.verified_at,days));
 const missingSource=resources.filter(x=>!String(x.source||'').trim());
 const openReq=requests.filter(x=>!['cerrada','rechazada'].includes(x.status));
 const pendingReq=openReq.filter(x=>['solicitada','evaluada','aprobada'].includes(x.status));
 const activeCommit=requests.filter(x=>['asignada','en_transito','recibida'].includes(x.status));
 const noCommit=pendingReq.filter(x=>!(Number(x.committed)>0));
 const missingIncidentInfo=activeInc.filter(x=>!String(x.situation||'').trim()||!String(x.lead||'').trim());
 const freshness={days,incidentsFresh:activeInc.filter(x=>fresh(x.updated_at,days)).length,incidentsStale:activeInc.filter(x=>!fresh(x.updated_at,days)).length,resourcesFresh:verified.filter(x=>fresh(x.verified_at,days)).length,resourcesStale:staleVerified.length};
 const result={application:'PREPPER MAP PRO',version:'2.0.0',generated_at:now().toISOString(),scope:municipality,filter_days:days,summary:{active_incidents:activeInc.length,p1_incidents:p1.length,verified_resources:verified.length,open_mutual_aid_requests:openReq.length,pending_requests:pendingReq.length,active_commitments:activeCommit.length,incidents_without_location:unlocated.length,incidents_without_assignment:unassigned.length,verified_resources_stale:staleVerified.length,records_missing_source:missingSource.length,incidents_missing_situation_or_lead:missingIncidentInfo.length},freshness,incidents:activeInc.map(x=>({id:x.id,title:x.title,municipality:x.municipality,priority:x.priority,status:x.status,location:x.location||null,lat:x.lat??null,lon:x.lon??null,lead:x.lead||null,situation:x.situation||null,updated_at:x.updated_at||null,assignments_count:(x.assignments||[]).length})),resources:resources.map(x=>({id:x.id,name:x.name,municipality:x.municipality,category:x.category,status:x.status,capacity:x.capacity||null,source:x.source||null,verified_at:x.verified_at||null,fresh:fresh(x.verified_at,days)})),mutual_aid:requests.map(x=>({id:x.id,requester:x.requester,provider:x.provider,category:x.category,description:x.description,status:x.status,requested:x.requested,committed:x.committed,unit:x.unit,source:x.source||null,updated_at:x.updated_at||null})),gaps:{unlocated_incidents:unlocated.map(x=>x.id),unassigned_incidents:unassigned.map(x=>x.id),stale_verified_resources:staleVerified.map(x=>x.id),records_missing_source:missingSource.map(x=>x.id),incidents_missing_situation_or_lead:missingIncidentInfo.map(x=>x.id),pending_without_commitment:noCommit.map(x=>x.id)}};
 return result;
}
function render(){
 const s=snapshot();latest=s;const k=$('sitKpis'),a=$('sitAlerts'),n=$('sitNeeds'),r=$('sitReport');[k,a,n,r].forEach(x=>x.replaceChildren());
 const entries=[['Incidentes activos',s.summary.active_incidents],['Prioridad P1',s.summary.p1_incidents],['Recursos verificados',s.summary.verified_resources],['Solicitudes de apoyo abiertas',s.summary.open_mutual_aid_requests],['Compromisos activos',s.summary.active_commitments],['Incidentes sin ubicación',s.summary.incidents_without_location]];
 entries.forEach(([label,value])=>{const d=node('div',undefined,'resource');d.append(node('small',label),node('b',String(value)));k.append(d);});
 const alertItems=[];
 if(s.summary.p1_incidents)alertItems.push(`Prioridad alta: ${s.summary.p1_incidents} incidente(s) P1 activos en el ámbito seleccionado.`);
 if(s.summary.incidents_without_location)alertItems.push(`${s.summary.incidents_without_location} incidente(s) activo(s) sin coordenadas.`);
 if(s.summary.incidents_without_assignment)alertItems.push(`${s.summary.incidents_without_assignment} incidente(s) activo(s) sin asignación registrada.`);
 if(s.summary.verified_resources_stale)alertItems.push(`${s.summary.verified_resources_stale} recurso(s) marcado(s) verificado(s) con verificación anterior a ${s.filter_days} días o sin fecha.`);
 if(s.summary.records_missing_source)alertItems.push(`${s.summary.records_missing_source} recurso(s) sin referencia de fuente.`);
 if(s.summary.incidents_missing_situation_or_lead)alertItems.push(`${s.summary.incidents_missing_situation_or_lead} incidente(s) sin descripción de situación o rol líder.`);
 if(!alertItems.length)alertItems.push('No se detectan brechas en las reglas básicas del tablero. Esto no certifica seguridad ni integridad del territorio.');
 a.append(node('b','Alertas y validaciones de calidad'));alertItems.forEach(x=>a.append(node('div',`• ${x}`,'resource')));
 const gapLabels=[['Incidentes sin ubicación',s.gaps.unlocated_incidents],['Incidentes sin asignación',s.gaps.unassigned_incidents],['Recursos con verificación vencida/no fechada',s.gaps.stale_verified_resources],['Registros sin fuente',s.gaps.records_missing_source],['Incidentes sin situación o líder',s.gaps.incidents_missing_situation_or_lead],['Solicitudes pendientes sin compromiso',s.gaps.pending_without_commitment]];
 n.append(node('b','Brechas que requieren revisión'));gapLabels.forEach(([label,ids])=>{const d=node('div',undefined,'resource');d.append(node('b',`${label}: ${ids.length}`),node('small',ids.length?ids.join(', '):'Ningún registro identificado'));n.append(d);});
 const lines=[`SITREP PREPPER MAP PRO 2.0`,`Generado: ${new Date(s.generated_at).toLocaleString()}`,`Ámbito: ${s.scope}`,`Ventana de frescura: ${s.filter_days} días`,`Incidentes activos: ${s.summary.active_incidents} | P1: ${s.summary.p1_incidents}`,`Recursos verificados: ${s.summary.verified_resources} | con verificación reciente: ${s.freshness.resourcesFresh}`,`Solicitudes de apoyo abiertas: ${s.summary.open_mutual_aid_requests} | pendientes: ${s.summary.pending_requests} | compromisos activos: ${s.summary.active_commitments}`,`Brechas: sin ubicación ${s.gaps.unlocated_incidents.length}; sin asignación ${s.gaps.unassigned_incidents.length}; recursos sin verificación reciente ${s.gaps.stale_verified_resources.length}; sin fuente ${s.gaps.records_missing_source.length}; incidentes sin situación/líder ${s.gaps.incidents_missing_situation_or_lead.length}.`,`Limitación: consolidación local de registros del dispositivo; no equivale a panorama oficial ni confirma disponibilidad, seguridad, despacho o recepción.`];
 r.append(node('b','Resumen de situación (SITREP)'),node('pre',lines.join('\n'),'resource'));
}
$('sitRefresh').addEventListener('click',render);
$('sitMunicipality').addEventListener('change',render);
$('sitFreshDays').addEventListener('change',render);
$('sitExport').addEventListener('click',()=>{if(!latest)render();const b=new Blob([JSON.stringify(latest,null,2)],{type:'application/json'}),u=URL.createObjectURL(b),a=document.createElement('a');a.href=u;a.download=`prepper-map-sitrep-${new Date().toISOString().slice(0,10)}.json`;a.click();setTimeout(()=>URL.revokeObjectURL(u),1200);});
$('sitCopy').addEventListener('click',async()=>{if(!latest)render();const s=latest,t=`SITREP PREPPER MAP PRO 2.0\nGenerado: ${new Date(s.generated_at).toLocaleString()}\nÁmbito: ${s.scope}\nIncidentes activos: ${s.summary.active_incidents} | P1: ${s.summary.p1_incidents}\nRecursos verificados: ${s.summary.verified_resources}\nSolicitudes abiertas: ${s.summary.open_mutual_aid_requests} | compromisos activos: ${s.summary.active_commitments}\nBrechas: ${JSON.stringify(s.gaps)}\nLimitación: datos locales; no constituyen reporte oficial ni confirman disponibilidad o seguridad.`;try{await navigator.clipboard.writeText(t);$('sitReport').append(node('small','SITREP copiado al portapapeles.'));}catch(_){$('sitReport').append(node('small','No fue posible copiar automáticamente; usa Exportar SITREP JSON.'));}});
render();
})();