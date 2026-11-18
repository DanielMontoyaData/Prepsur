(() => {
 'use strict';
 const $=id=>document.getElementById(id);
 let session=null, busy=false;
 const QUEUE='prepper-private-network-outbox-v1';
 const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const queue=()=>{try{return JSON.parse(localStorage.getItem(QUEUE)||'[]')}catch{return []}};
 const saveQueue=q=>localStorage.setItem(QUEUE,JSON.stringify(q.slice(-200)));
 function base(){const v=$('netApiUrl').value.trim().replace(/\/$/,'');if(!/^https:\/\//.test(v)&&!/^http:\/\/localhost(?::\d+)?$/.test(v))throw Error('La API debe usar HTTPS (HTTP solo en localhost).');return v;}
 async function req(path,{method='GET',body,token=session?.token}={}) {
  const headers={'Accept':'application/json'};if(body!==undefined)headers['Content-Type']='application/json';if(token)headers.Authorization='Bearer '+token;
  const r=await fetch(base()+path,{method,headers,body:body===undefined?undefined:JSON.stringify(body)});
  const data=await r.json().catch(()=>({}));
  if(!r.ok)throw Error(data.detail||('Error HTTP '+r.status));return data;
 }
 function setSession(result,api) {
  session={token:result.access_token,tenant:result.profile.tenant_id,profile:result.profile,api};
  $('netTenant').value=session.tenant;
  $('netProfile').textContent=`Conectado como ${session.profile.display_name} (@${session.profile.username}) · rol ${session.profile.role} · grupo ${session.tenant}.`;
  try{window.PrepperSync.configure({baseUrl:api,tenantId:session.tenant,token:session.token});}catch(e){console.warn(e);}
 }
 async function join() {
  const api=base(),code=$('netInviteCode').value.trim();
  const result=await req('/api/network/join',{method:'POST',token:null,body:{code,username:$('netUsername').value.trim(),display_name:$('netDisplayName').value.trim(),password:$('netPassword').value}});
  setSession(result,api);$('netPassword').value='';await refreshAll();flushQueue();
 }
 async function login() {
  const api=base(),result=await req('/api/network/login',{method:'POST',token:null,body:{tenant_id:$('netTenant').value.trim(),username:$('netUsername').value.trim(),password:$('netPassword').value}});
  setSession(result,api);$('netPassword').value='';await refreshAll();flushQueue();
 }
 async function createInvite() {
  const api=base(),token=$('netAdminToken').value;
  if(!token)throw Error('Introduce el token administrador.');
  const r=await req('/api/network/invites',{method:'POST',token,body:{role:'member',hours:72,max_uses:1}});
  $('netInviteResult').textContent=`Código: ${r.code} · vence: ${new Date(r.expires_at).toLocaleString()} · un solo uso. Compártelo de forma privada.`;
  $('netAdminToken').value='';
 }
 async function refreshMessages() {
  if(!session)throw Error('Inicia sesión para ver los mensajes.');
  const r=await req('/api/network/messages');
  $('netMessages').innerHTML=r.messages.length?r.messages.map(m=>`<div style="padding:6px 0;border-bottom:1px solid #304553"><b>${esc(m.display_name)}</b> <small>${esc(new Date(m.created_at).toLocaleString())}</small><div>${esc(m.body)}</div></div>`).join(''):'Todavía no hay mensajes.';
 }
 async function refreshMembers() {
  if(!session)throw Error('Inicia sesión para consultar integrantes.');
  const r=await req('/api/network/members');
  $('netMembers').innerHTML=r.members.length?r.members.map(m=>`<div style="padding:5px 0;border-bottom:1px solid #304553"><b>${esc(m.display_name)}</b> · @${esc(m.username)} · ${esc(m.role)}</div>`).join(''):'No hay integrantes.';
 }
 async function refreshObservations() {
  if(!session)throw Error('Inicia sesión para ver las observaciones.');
  const r=await req('/api/network/observations');
  if(window.PrepperMap&&window.L){if(!window.PrepperNetworkObservationLayer)window.PrepperNetworkObservationLayer=L.layerGroup().addTo(window.PrepperMap);window.PrepperNetworkObservationLayer.clearLayers();r.observations.forEach(o=>{if(o.latitude!==null&&o.latitude!==undefined&&o.longitude!==null&&o.longitude!==undefined){L.marker([o.latitude,o.longitude]).bindPopup(`<b>${esc(o.title)}</b><br>${esc(o.body)}<br><small>${esc(o.display_name)} · reporte de usuario</small>`).addTo(window.PrepperNetworkObservationLayer);}});}
  $('netObservations').innerHTML=r.observations.length?r.observations.map(o=>`<div style="padding:7px 0;border-bottom:1px solid #304553"><b>${esc(o.title)}</b> · ${esc(o.category)}<div>${esc(o.body)}</div><small>${esc(o.display_name)} · ${esc(new Date(o.created_at).toLocaleString())}${o.latitude!==null&&o.latitude!==undefined?` · ${o.latitude}, ${o.longitude}`:''}</small></div>`).join(''):'No hay observaciones compartidas.';
 }
 async function sendMessage() {
  const body=$('netMessageText').value.trim();if(!body)return;
  if(!session)throw Error('Inicia sesión para enviar mensajes.');
  if(!navigator.onLine){const q=queue();q.push({kind:'message',body,created_at:new Date().toISOString()});saveQueue(q);$('netMessageText').value='';$('netMessages').textContent=`Sin conexión. Mensaje guardado localmente (${q.length} pendientes).`;return;}
  await req('/api/network/messages',{method:'POST',body:{body}});$('netMessageText').value='';await refreshMessages();
 }
 async function shareObservation() {
  if(!session)throw Error('Inicia sesión para compartir observaciones.');
  const payload={title:$('netObsTitle').value.trim(),body:$('netObsBody').value.trim(),category:$('netObsCategory').value};
  const lat=$('netObsLat').value.trim(),lon=$('netObsLon').value.trim();
  if((lat&&!lon)||(!lat&&lon))throw Error('Debes indicar latitud y longitud juntas.');
  if(lat){payload.latitude=Number(lat);payload.longitude=Number(lon);if(!Number.isFinite(payload.latitude)||!Number.isFinite(payload.longitude))throw Error('Coordenadas inválidas.');}
  if(!payload.title||!payload.body)throw Error('Completa título y descripción.');
  if(!navigator.onLine){const q=queue();q.push({kind:'observation',payload,created_at:new Date().toISOString()});saveQueue(q);$('netObsBody').value='';$('netObservations').textContent=`Sin conexión. Observación guardada localmente (${q.length} pendientes).`;return;}
  await req('/api/network/observations',{method:'POST',body:payload});$('netObsBody').value='';await refreshObservations();
 }
 async function flushQueue() {
  if(busy||!session||!navigator.onLine)return;busy=true;
  try{let q=queue(),sent=0;while(q.length){const item=q[0];if(item.kind==='message')await req('/api/network/messages',{method:'POST',body:{body:item.body}});else if(item.kind==='observation')await req('/api/network/observations',{method:'POST',body:item.payload});q=q.slice(1);saveQueue(q);sent++;}if(sent){$('netProfile').textContent+=' · '+sent+' elementos pendientes sincronizados.';await refreshAll();}}
  catch(e){console.warn('Cola de red privada pendiente:',e.message);}
  finally{busy=false;}
 }
 async function refreshAll(){await Promise.allSettled([refreshMembers(),refreshMessages(),refreshObservations()]);}
 $('netJoin').onclick=()=>join().catch(e=>$('netProfile').textContent=e.message);
 $('netLogin').onclick=()=>login().catch(e=>$('netProfile').textContent=e.message);
 $('netCreateInvite').onclick=()=>createInvite().catch(e=>$('netInviteResult').textContent=e.message);
 $('netLogout').onclick=async()=>{try{if(session&&navigator.onLine)await req('/api/network/logout',{method:'POST'});}catch(e){console.warn('No se pudo revocar sesión remota:',e.message);}session=null;try{window.PrepperSync.clearSession();}catch{}$('netProfile').textContent='Sesión cerrada en este dispositivo. La cola local pendiente se conserva.';};
 $('netSendMessage').onclick=()=>sendMessage().catch(e=>$('netMessages').textContent=e.message);
 $('netRefreshMembers').onclick=()=>refreshMembers().catch(e=>$('netMembers').textContent=e.message);
 $('netRefreshMessages').onclick=()=>refreshMessages().catch(e=>$('netMessages').textContent=e.message);
 $('netShareObservation').onclick=()=>shareObservation().catch(e=>$('netObservations').textContent=e.message);
 $('netRefreshObservations').onclick=()=>refreshObservations().catch(e=>$('netObservations').textContent=e.message);
 window.addEventListener('online',flushQueue);
})();
