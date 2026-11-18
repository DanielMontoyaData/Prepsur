/* Explicit, opt-in event synchronization. Credentials remain in memory only. */
(() => {
 'use strict';
 const DB='prepper-sync-outbox-v1', STORE='events'; let db=null, session=null, autoPush=false, pushing=false;
 const open=()=>new Promise((ok,no)=>{const r=indexedDB.open(DB,1);r.onupgradeneeded=()=>{if(!r.result.objectStoreNames.contains(STORE))r.result.createObjectStore(STORE,{keyPath:'event_id'});};r.onsuccess=()=>{db=r.result;ok(db)};r.onerror=()=>no(r.error)});
 const tx=(mode='readonly')=>db.transaction(STORE,mode).objectStore(STORE);
 const all=()=>new Promise((ok,no)=>{const r=tx().getAll();r.onsuccess=()=>ok(r.result||[]);r.onerror=()=>no(r.error)});
 const put=e=>new Promise((ok,no)=>{const r=tx('readwrite').put(e);r.onsuccess=()=>ok();r.onerror=()=>no(r.error)});
 const del=id=>new Promise((ok,no)=>{const r=tx('readwrite').delete(id);r.onsuccess=()=>ok();r.onerror=()=>no(r.error)});
 const valid=e=>{if(!e||typeof e!=='object'||!e.event_id||!e.entity_type||!e.entity_id||!e.operation||!e.created_at||!e.payload||typeof e.payload!=='object')throw Error('Evento incompleto. Requiere event_id, entity_type, entity_id, operation, created_at y payload.');return e};
 async function enqueue(e){await open();valid(e);await put({...e,schema_version:e.schema_version||1});const n=(await all()).length;if(autoPush&&navigator.onLine&&session)push().catch(err=>console.warn('PREPPER sync pendiente:',err));return n;}
 async function configure({baseUrl,tenantId,token}){if(!/^https:\/\//.test(baseUrl)&&!/^http:\/\/localhost(?::\d+)?$/.test(baseUrl))throw Error('Usa HTTPS; HTTP solo se admite en localhost.');if(!tenantId||!token)throw Error('Falta tenant o token.');session={baseUrl:baseUrl.replace(/\/$/,''),tenantId,token};}
 async function push(){if(pushing) return {accepted:0,duplicates:0,busy:true};if(!navigator.onLine)throw Error('Sin conexión. Los eventos permanecen en la cola local.');if(!session)throw Error('Configura la sesión antes de sincronizar.');pushing=true;try{await open();const events=await all();if(!events.length)return {accepted:0,duplicates:0};let total={accepted:0,duplicates:0};for(let i=0;i<events.length;i+=100){const batch=events.slice(i,i+100);const r=await fetch(session.baseUrl+'/api/sync/push',{method:'POST',headers:{'Content-Type':'application/json','Authorization':'Bearer '+session.token},body:JSON.stringify({tenant_id:session.tenantId,events:batch})});if(!r.ok)throw Error('Sincronización rechazada: HTTP '+r.status);const data=await r.json();for(const item of data.results||[])await del(item.event_id);total.accepted+=data.accepted||0;total.duplicates+=data.duplicates||0;}return total;}finally{pushing=false;}}
 async function pull({since=null,limit=500}={}){if(!session)throw Error('Configura la sesión antes de sincronizar.');const u=new URL(session.baseUrl+'/api/sync/pull');u.searchParams.set('tenant_id',session.tenantId);u.searchParams.set('limit',String(Math.min(1000,Math.max(1,limit))));if(since)u.searchParams.set('since',since);const r=await fetch(u,{headers:{Authorization:'Bearer '+session.token}});if(!r.ok)throw Error('Descarga de eventos rechazada: HTTP '+r.status);return r.json();}
 async function count(){await open();return (await all()).length;}
 window.PrepperSync={enqueue,configure,push,pull,count,enableAutoPush(value){autoPush=!!value;return autoPush;},isAutoPushEnabled(){return autoPush;},hasSession(){return !!session;},clearSession(){session=null;autoPush=false;},pending:all};
 window.addEventListener('prepper:event',e=>{enqueue(e.detail).catch(err=>console.error('PREPPER outbox:',err));});
 window.addEventListener('online',()=>{if(autoPush&&session)push().catch(e=>console.warn('PREPPER reconexión:',e));});
 document.addEventListener('visibilitychange',()=>{if(!document.hidden&&autoPush&&session&&navigator.onLine)push().catch(e=>console.warn('PREPPER reanudación:',e));});
 open().catch(e=>console.warn('PREPPER outbox no disponible:',e));
})();
