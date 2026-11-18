/* PREPPER MAP 1.5 — incident command, resource assignment and field SITREP. */
(() => {
  'use strict';
  const KEY='prepper-map-incident-command-v2';
  const $=id=>document.getElementById(id);
  let incidents=[],currentId=null;
  const now=()=>new Date().toISOString();
  const makeId=()=>`PM-${now().slice(0,10).replaceAll('-','')}-${Math.random().toString(36).slice(2,7).toUpperCase()}`;
  const node=(tag,text,cls)=>{const e=document.createElement(tag);if(text!==undefined)e.textContent=text;if(cls)e.className=cls;return e;};
  const validCoord=(lat,lon)=>Number.isFinite(lat)&&Number.isFinite(lon)&&lat>=-90&&lat<=90&&lon>=-180&&lon<=180;
  const current=()=>incidents.find(x=>x.id===currentId)||null;
  function emitIncident(x,operation='update'){
    if(!x)return;const eventId=`${x.id}-${x.updated_at||now()}-${operation}`;
    window.dispatchEvent(new CustomEvent('prepper:event',{detail:{event_id:eventId,entity_type:'incident',entity_id:x.id,operation,created_at:x.updated_at||now(),source_device:'prepper-webview',schema_version:1,payload:x}}));
  }
  function persist(){
    try{localStorage.setItem(KEY,JSON.stringify({schema_version:2,updated_at:now(),incidents}));return true;}
    catch(e){$('icSummary').textContent=`No se pudo guardar: ${e.message}. Exporta el respaldo y libera espacio.`;return false;}
  }
  function load(){
    try{
      let raw=localStorage.getItem(KEY);
      if(raw){const d=JSON.parse(raw);if(d.schema_version!==2||!Array.isArray(d.incidents))throw Error('Formato de bitácora no reconocido');incidents=d.incidents.filter(x=>x&&typeof x.id==='string'&&typeof x.title==='string'&&Array.isArray(x.log)).slice(-100);}
      else{
        const old=JSON.parse(localStorage.getItem('prepper-map-incident-command-v1')||'{"schema_version":1,"incidents":[]}');
        if(old.schema_version===1&&Array.isArray(old.incidents)){incidents=old.incidents.filter(x=>x&&typeof x.id==='string'&&Array.isArray(x.log)).map(x=>({...x,lat:x.lat??null,lon:x.lon??null,communications:Array.isArray(x.communications)?x.communications:[],assignments:Array.isArray(x.assignments)?x.assignments:[]})).slice(-100);persist();}
      }
    }catch(e){$('icSummary').textContent=`No se pudo leer la bitácora. No se sobrescribieron los datos existentes: ${e.message}`;incidents=[];}
  }
  function formData(){
    const lat=$('icLat').value.trim()===''?null:Number($('icLat').value),lon=$('icLon').value.trim()===''?null:Number($('icLon').value);
    if((lat===null)!==(lon===null))throw Error('Para ubicar el incidente debes indicar latitud y longitud.');
    if(lat!==null&&!validCoord(lat,lon))throw Error('Coordenadas fuera de rango.');
    return {title:$('icTitle').value.trim(),municipality:$('icMunicipality').value,priority:$('icPriority').value,status:$('icStatus').value,location:$('icLocation').value.trim(),lead:$('icLead').value.trim(),situation:$('icSituation').value.trim(),lat,lon};
  }
  function writeForm(x){
    $('icTitle').value=x?.title||'';$('icMunicipality').value=x?.municipality||'Envigado';$('icPriority').value=x?.priority||'P2';$('icStatus').value=x?.status||'activo';$('icLocation').value=x?.location||'';$('icLead').value=x?.lead||'';$('icSituation').value=x?.situation||'';$('icLat').value=x?.lat??'';$('icLon').value=x?.lon??'';
  }
  function updateMap(){
    const layer=window.PREPPER_MAP_INCIDENT_LAYER;if(!layer||!window.L)return;
    layer.clearLayers();
    incidents.filter(x=>x.lat!==null&&x.lat!==undefined&&x.lon!==null&&x.lon!==undefined&&validCoord(Number(x.lat),Number(x.lon))).forEach(x=>{
      const color=({P1:'#ef4444',P2:'#f59e0b',P3:'#3b82f6',P4:'#22a06b'})[x.priority]||'#64748b';
      const marker=L.circleMarker([Number(x.lat),Number(x.lon)],{radius:9,color,fillColor:color,fillOpacity:.75,weight:2});
      const popup=node('div');popup.append(node('b',`${x.priority} · ${x.title}`),node('div',`${x.municipality} · ${x.status}`),node('div',x.location||'Sin referencia'),node('small',x.id));
      marker.bindPopup(popup);marker.on('click',()=>{currentId=x.id;writeForm(x);render();});
      marker.addTo(layer);
    });
  }
  function render(){
    const opts=$('icOptions');opts.replaceChildren();
    incidents.slice().reverse().forEach(x=>{const o=document.createElement('option');o.value=`${x.id} · ${x.title}`;opts.append(o);});
    const x=current();
    if(!x){$('icAssignments').replaceChildren();$('icResourceSelect').replaceChildren();$('icSummary').textContent=incidents.length?`${incidents.length} incidentes locales. Selecciona uno para abrir su ficha.`:'No hay incidentes registrados en este dispositivo.';$('icTimeline').replaceChildren();$('icCommsList').replaceChildren();updateMap();return;}
    $('icSelect').value=`${x.id} · ${x.title}`;
    $('icSummary').textContent=`${x.id} · ${x.municipality} · ${x.priority} · ${x.status.toUpperCase()} · ${x.lat!==null&&x.lat!==undefined?`Coordenadas ${x.lat}, ${x.lon}`:'Sin coordenadas'} · Actualizado ${new Date(x.updated_at).toLocaleString()}`;
    const timeline=$('icTimeline');timeline.replaceChildren();timeline.append(node('b',`Bitácora (${x.log.length})`));
    x.log.slice().reverse().slice(0,25).forEach(e=>{const d=node('div',undefined,'resource');d.append(node('b',`${new Date(e.at).toLocaleString()} · ${e.kind||'Novedad'}`),node('span',e.text));timeline.append(d);});
    const comms=$('icCommsList');comms.replaceChildren();comms.append(node('b',`Comunicaciones (${(x.communications||[]).length})`));
    (x.communications||[]).slice().reverse().slice(0,20).forEach(c=>{const d=node('div',undefined,'resource');d.append(node('b',`${new Date(c.at).toLocaleString()} · ${c.network} · ${c.ack}`),node('div',`${c.from||'Origen no indicado'} → ${c.to||'Destino no indicado'}`),node('span',c.message));comms.append(d);});
    if((x.communications||[]).length>20)comms.append(node('small','Se muestran las 20 comunicaciones más recientes.'));
    const assignments=$('icAssignments');assignments.replaceChildren();
    const resourceData=(()=>{try{return JSON.parse(localStorage.getItem('prepper-map-resource-registry-v1')||'{"resources":[]}').resources||[];}catch(_){return [];}})();
    const verified=resourceData.filter(r=>r.status==='verificado');
    const select=$('icResourceSelect'),previous=select.value;select.replaceChildren();
    const empty=document.createElement('option');empty.value='';empty.textContent=verified.length?'Selecciona un recurso':'No hay recursos verificados';select.append(empty);
    verified.forEach(r=>{const o=document.createElement('option');o.value=r.id;o.textContent=`${r.name} · ${r.municipality} · ${r.category}`;select.append(o);});
    if(verified.some(r=>r.id===previous))select.value=previous;
    const list=(x.assignments||[]).slice().reverse();
    assignments.append(node('b',`Asignaciones (${list.length})`));
    list.slice(0,30).forEach(a=>{
      const r=resourceData.find(z=>z.id===a.resource_id);
      const d=node('div',undefined,'resource');
      d.append(node('b',`${a.resource_name||r?.name||'Recurso no disponible'} · ${(a.status||'solicitado').replaceAll('_',' ')}`),
        node('div',`${a.municipality||r?.municipality||'Municipio no indicado'} · ${a.quantity||'Cantidad no indicada'}`),
        node('small',`${new Date(a.at).toLocaleString()} · ${a.note||'Sin observación'}`));
      assignments.append(d);
    });
    if(!list.length)assignments.append(node('span','No hay recursos asignados a este incidente.'));
    if(list.length>30)assignments.append(node('small','Se muestran las 30 asignaciones más recientes.'));
    updateMap();
  }
  function select(){
    const raw=$('icSelect').value.trim(),x=incidents.find(v=>v.id===raw||raw.startsWith(v.id+' ·'));
    if(!x){$('icSummary').textContent='No se encontró el incidente.';return;}
    currentId=x.id;writeForm(x);render();
  }
  $('icCreate').addEventListener('click',()=>{
    let data;try{data=formData();}catch(e){alert(e.message);return;}if(!data.title){alert('Escribe el nombre del incidente.');return;}
    let x=current();if(!x){x={id:makeId(),created_at:now(),log:[],communications:[]};incidents.push(x);currentId=x.id;x.log.push({at:now(),kind:'Apertura',text:'Registro creado en bitácora local.'});}
    else x.log.push({at:now(),kind:'Actualización',text:`Ficha actualizada. Estado ${data.status}; prioridad ${data.priority}.`});
    Object.assign(x,data,{updated_at:now()});x.communications=x.communications||[];x.assignments=x.assignments||[];x.log=x.log.slice(-500);incidents=incidents.slice(-100);
    if(persist()){emitIncident(x,x.log.length===1?'create':'update');$('icSelect').value=`${x.id} · ${x.title}`;render();}
  });
  $('icNew').addEventListener('click',()=>{currentId=null;$('icSelect').value='';$('icLogText').value='';writeForm(null);render();});
  $('icSelect').addEventListener('change',select);$('icSelect').addEventListener('keydown',e=>{if(e.key==='Enter')select();});
  $('icAddLog').addEventListener('click',()=>{
    const x=current(),text=$('icLogText').value.trim();if(!x){alert('Selecciona un incidente.');return;}if(!text){alert('Escribe la novedad.');return;}
    x.log.push({at:now(),kind:'Novedad',text});x.log=x.log.slice(-500);x.updated_at=now();if(persist()){emitIncident(x);$('icLogText').value='';render();}
  });
  $('icAddComms').addEventListener('click',()=>{
    const x=current(),network=$('icNet').value.trim(),message=$('icMessage').value.trim();
    if(!x){alert('Selecciona un incidente.');return;}if(!network||!message){alert('Indica la red/canal autorizado y el contenido del mensaje.');return;}
    x.communications=x.communications||[];x.communications.push({at:now(),network,from:$('icFrom').value.trim(),to:$('icTo').value.trim(),message,ack:$('icAck').value});
    x.communications=x.communications.slice(-500);x.updated_at=now();x.log.push({at:now(),kind:'Comunicación',text:`Registro de comunicación en ${network}; confirmación: ${$('icAck').value}.`});
    if(persist()){emitIncident(x);$('icMessage').value='';render();}
  });
  $('icShowMap').addEventListener('click',()=>{
    const x=current();if(!x){alert('Selecciona un incidente.');return;}if(!validCoord(Number(x.lat),Number(x.lon))){alert('Este incidente no tiene coordenadas válidas. Añádelas y actualiza la ficha.');return;}
    const map=window.PREPPER_MAP_MAP;if(!map){alert('El mapa todavía no está disponible.');return;}map.setView([Number(x.lat),Number(x.lon)],16);updateMap();
    const markerLayer=window.PREPPER_MAP_INCIDENT_LAYER;if(markerLayer){markerLayer.eachLayer(m=>{const ll=m.getLatLng();if(Math.abs(ll.lat-Number(x.lat))<1e-7&&Math.abs(ll.lng-Number(x.lon))<1e-7)m.openPopup();});}
  });
  function download(name,payload){const blob=new Blob([JSON.stringify(payload,null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1200);}
  $('icExport').addEventListener('click',()=>download(`prepper-map-bitacora-${now().slice(0,10)}.json`,{application:'PREPPER MAP',schema_version:2,exported_at:now(),storage:'local_only',incidents}));
  $('icImport').addEventListener('click',()=>$('icImportFile').click());
  $('icImportFile').addEventListener('change',async e=>{
    const file=e.target.files?.[0];if(!file)return;
    try{const d=JSON.parse(await file.text());if(d.application!=='PREPPER MAP'||![1,2].includes(d.schema_version)||!Array.isArray(d.incidents)||d.incidents.length>100)throw Error('Respaldo incompatible o supera 100 incidentes.');
      const ids=new Set(incidents.map(x=>x.id));d.incidents.forEach(x=>{if(x&&typeof x.id==='string'&&typeof x.title==='string'&&Array.isArray(x.log)&&!ids.has(x.id)){incidents.push({...x,lat:x.lat??null,lon:x.lon??null,communications:x.communications||[],assignments:x.assignments||[]});ids.add(x.id);}});
      incidents=incidents.slice(-100);if(persist()){currentId=incidents.at(-1)?.id||null;if(current())writeForm(current());render();}
    }catch(err){alert(`No se pudo importar: ${err.message}`);}finally{e.target.value='';}
  });
  
  $('icAssignResource').addEventListener('click',()=>{
    const x=current(),resourceId=$('icResourceSelect').value;
    if(!x){alert('Selecciona un incidente.');return;}
    if(!resourceId){alert('Selecciona un recurso verificado del inventario.');return;}
    let resources=[];try{resources=JSON.parse(localStorage.getItem('prepper-map-resource-registry-v1')||'{"resources":[]}').resources||[];}catch(_){}
    const r=resources.find(v=>v.id===resourceId&&v.status==='verificado');
    if(!r){alert('El recurso ya no está verificado o no existe. Actualiza el inventario.');render();return;}
    x.assignments=x.assignments||[];
    const status=$('icAssignmentStatus').value;
    const assignment={id:`AS-${Date.now()}-${Math.random().toString(36).slice(2,6)}`,resource_id:r.id,resource_name:r.name,municipality:r.municipality,category:r.category,status,quantity:$('icAssignmentQty').value.trim(),note:$('icAssignmentNote').value.trim(),at:now()};
    x.assignments.push(assignment);x.assignments=x.assignments.slice(-300);x.updated_at=now();
    x.log.push({at:now(),kind:'Asignación de recurso',text:`${r.name}: ${status.replaceAll('_',' ')}${assignment.quantity?' · '+assignment.quantity:''}.`});
    x.log=x.log.slice(-500);
    if(persist()){emitIncident(x);$('icAssignmentQty').value='';$('icAssignmentNote').value='';render();}
  });
  $('icCopySitrep').addEventListener('click',async()=>{
    const x=current();if(!x){alert('Selecciona un incidente.');return;}
    const assigned=(x.assignments||[]).filter(a=>!['liberado','cancelado'].includes(a.status));
    const sitrep=[
      'SITREP · PREPPER MAP',
      `ID: ${x.id}`,
      `INCIDENTE: ${x.title}`,
      `MUNICIPIO: ${x.municipality}`,
      `PRIORIDAD: ${x.priority}`,
      `ESTADO: ${x.status}`,
      `UBICACIÓN: ${x.location||'No precisada'}`,
      `COORDENADAS: ${x.lat!==null&&x.lat!==undefined?`${x.lat}, ${x.lon}`:'No registradas'}`,
      `RESPONSABLE: ${x.lead||'No asignado'}`,
      `SITUACIÓN: ${x.situation||'Sin descripción'}`,
      `RECURSOS ACTIVOS: ${assigned.length?assigned.map(a=>`${a.resource_name} (${a.status})`).join('; '):'Ninguno registrado'}`,
      `ACTUALIZADO: ${x.updated_at||now()}`,
      'FUENTE: Registro operativo local; verificar por canal institucional antes de retransmitir.'
    ].join('\n');
    try{await navigator.clipboard.writeText(sitrep);alert('SITREP copiado. Revísalo y transmite únicamente por canales autorizados.');}
    catch(_){const area=document.createElement('textarea');area.value=sitrep;document.body.append(area);area.select();try{document.execCommand('copy');alert('SITREP copiado.');}catch(e){alert('No fue posible copiar automáticamente.');}area.remove();}
  });
$('icDelete').addEventListener('click',()=>{const x=current();if(!x)return;if(!confirm(`¿Eliminar ${x.id} y su bitácora?`))return;const removed=current();incidents=incidents.filter(v=>v.id!==currentId);currentId=null;writeForm(null);$('icSelect').value='';if(persist())emitIncident({...removed,updated_at:now()},'delete');render();});
  $('icClear').addEventListener('click',()=>{if(!incidents.length||!confirm('¿Borrar todos los incidentes? Exporta primero el respaldo.'))return;incidents=[];currentId=null;writeForm(null);$('icSelect').value='';persist();render();});
  load();if(incidents.length){currentId=incidents.at(-1).id;writeForm(current());}render();
  window.PREPPER_MAP_INCIDENTS={getAll:()=>incidents.map(x=>({...x})),select:id=>{if(incidents.some(x=>x.id===id)){currentId=id;writeForm(current());render();}}};
})();
