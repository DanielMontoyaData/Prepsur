/* PREPPER MAP PRO 2.1 — configurable service dependency and disruption scenarios. */
(()=>{'use strict';
const KEY='prepper-map-scenario-lab-v1', $=id=>document.getElementById(id), now=()=>new Date().toISOString();
const MUNICIPALITIES=['Envigado','Itagüí','Sabaneta','La Estrella','Caldas','Medellín'];
const SECTORS=['agua','energia','comunicaciones','movilidad','salud','alimentos','saneamiento','combustible','otro'];
const CRITICALITY=['critica','alta','media','baja'];
let nodes=[],scenarios=[],lastResult=null;
const el=(tag,text,cls)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n;};
function save(){try{localStorage.setItem(KEY,JSON.stringify({schema_version:1,updated_at:now(),nodes,scenarios}));return true;}catch(e){ $('scWarnings').textContent=`No se pudo guardar localmente: ${e.message}`;return false;}}
function load(){try{const d=JSON.parse(localStorage.getItem(KEY)||'{"schema_version":1,"nodes":[],"scenarios":[]}');if(d.schema_version!==1||!Array.isArray(d.nodes)||!Array.isArray(d.scenarios))throw Error('Formato local no reconocido');nodes=d.nodes;scenarios=d.scenarios;}catch(e){nodes=[];scenarios=[];$('scWarnings').textContent=`No se cargaron datos anteriores: ${e.message}`;}}
function id(){return `N-${Math.random().toString(36).slice(2,8).toUpperCase()}`;}
function validateGraph(candidate){
 const map=new Map(candidate.map(n=>[n.id,n])), visiting=new Set(), done=new Set();
 function visit(k){if(visiting.has(k))throw Error(`Dependencia circular detectada en ${k}.`);if(done.has(k))return;const n=map.get(k);if(!n)throw Error(`No existe el nodo ${k}.`);visiting.add(k);(n.dependencies||[]).forEach(d=>{if(!map.has(d))throw Error(`El nodo ${k} depende de un ID inexistente: ${d}.`);visit(d);});visiting.delete(k);done.add(k);}
 candidate.forEach(n=>visit(n.id));return true;
}
function renderNodes(){
 const box=$('scNodeList');box.replaceChildren();
 if(!nodes.length){box.append(el('small','No hay nodos registrados. No se han precargado instalaciones reales.'));return;}
 nodes.forEach(n=>{const d=el('div',undefined,'resource');d.append(el('b',`${n.name} · ${n.id}`),el('div',`${n.municipality} · ${n.sector} · criticidad ${n.criticality} · capacidad ${n.capacity??'no informada'} ${n.unit||''}`),el('small',`Dependencias proveedoras: ${(n.dependencies||[]).join(', ')||'ninguna'} · Fuente: ${n.source||'no indicada'}`));const b=el('button','Eliminar nodo');b.type='button';b.addEventListener('click',()=>{if(nodes.some(x=>(x.dependencies||[]).includes(n.id))){alert('No se puede eliminar: otros nodos dependen de este nodo. Edita primero esas dependencias.');return;}if(!confirm(`¿Eliminar ${n.name}?`))return;nodes=nodes.filter(x=>x.id!==n.id);save();renderNodes();});d.append(b);box.append(d);});
}
function parseOverrides(raw,scope){
 const out={};raw.split(/\r?\n/).map(x=>x.trim()).filter(Boolean).forEach(line=>{const m=line.match(/^([A-Za-z0-9_-]+)\s*=\s*(\d{1,3}(?:\.\d+)?)$/);if(!m)throw Error(`Línea inválida: ${line}. Usa ID=porcentaje.`);const key=m[1],value=Number(m[2]);if(value<0||value>100)throw Error(`El porcentaje debe estar entre 0 y 100: ${line}`);if(out[key]!==undefined)throw Error(`Afectación duplicada para ${key}.`);const n=nodes.find(x=>x.id===key);if(!n)throw Error(`No existe el nodo ${key}.`);if(scope!=='todos'&&n.municipality!==scope)throw Error(`${key} no pertenece al municipio seleccionado (${scope}).`);out[key]=value;});return out;
}
function calculate(name,scope,overrides){
 validateGraph(nodes);
 const byId=new Map(nodes.map(n=>[n.id,n])), cache={}, visiting=new Set();
 function effective(k){if(cache[k]!==undefined)return cache[k];if(visiting.has(k))throw Error(`Ciclo detectado en ${k}.`);const n=byId.get(k);if(!n)throw Error(`Nodo desconocido: ${k}`);visiting.add(k);const direct=overrides[k]===undefined?100:overrides[k];const deps=(n.dependencies||[]).map(effective);const bottleneck=deps.length?Math.min(...deps):100;const value=direct*bottleneck/100;visiting.delete(k);cache[k]=value;return value;}
 const selected=nodes.filter(n=>scope==='todos'||n.municipality===scope);
 const results=selected.map(n=>{const available=effective(n.id),cap=n.capacity===null?null:Number(n.capacity),effectiveCapacity=cap===null?null:cap*available/100;return {id:n.id,name:n.name,municipality:n.municipality,sector:n.sector,criticality:n.criticality,source:n.source||null,direct_availability:overrides[n.id]??100,effective_availability_pct:Number(available.toFixed(2)),capacity:cap,unit:n.unit||null,effective_capacity:effectiveCapacity===null?null:Number(effectiveCapacity.toFixed(4)),capacity_loss:cap===null?null:Number((cap-effectiveCapacity).toFixed(4)),dependencies:n.dependencies||[],affected:available<99.999};});
 const affected=results.filter(x=>x.affected),critical=affected.filter(x=>x.criticality==='critica');
 return {application:'PREPPER MAP PRO',version:'2.1.0',scenario_name:name,scope,generated_at:now(),assumptions:{unaffected_nodes_start_at_100_pct:true,dependency_rule:'Each dependent node is limited by the minimum effective availability of its listed provider dependencies; its direct availability is multiplied by that bottleneck.',multi_dependency:'All listed dependencies are treated as required (AND/bottleneck), not redundant alternatives.',capacity:'Effective capacity is the declared reference capacity multiplied by effective availability; no population or demand is inferred.',data_status:'User-entered hypothetical model; not a forecast or official operational picture.'},summary:{nodes_in_scope:results.length,affected_nodes:affected.length,critical_nodes_affected:critical.length,average_effective_availability_pct:results.length?Number((results.reduce((s,x)=>s+x.effective_availability_pct,0)/results.length).toFixed(2)):null},overrides,results};
}
function renderResult(result){
 const box=$('scResult');box.replaceChildren();
 const m=result.summary;
 const k=el('div',undefined,'au-grid');
 [['Nodos en ámbito',m.nodes_in_scope],['Nodos afectados',m.affected_nodes],['Críticos afectados',m.critical_nodes_affected],['Disponibilidad efectiva promedio',m.average_effective_availability_pct===null?'—':`${m.average_effective_availability_pct}%`]].forEach(([a,b])=>{const d=el('div',undefined,'resource');d.append(el('small',a),el('b',String(b)));k.append(d);});box.append(k);
 const note=el('p','Regla conservadora: cada dependencia registrada se considera necesaria; el nodo dependiente queda limitado por el proveedor con menor disponibilidad. No representa redundancia real ni valida la topología física.','foot');box.append(note);
 const table=document.createElement('table');const thead=document.createElement('thead'),tr=document.createElement('tr');['Nodo','Municipio','Sector','Criticidad','Directa %','Efectiva %','Capacidad efectiva','Dependencias'].forEach(x=>tr.append(el('th',x)));thead.append(tr);table.append(thead);
 const tbody=document.createElement('tbody');result.results.forEach(x=>{const row=document.createElement('tr');[`${x.name} (${x.id})`,x.municipality,x.sector,x.criticality,String(x.direct_availability),String(x.effective_availability_pct),x.effective_capacity===null?'No informada':`${x.effective_capacity} ${x.unit||''}`,x.dependencies.join(', ')||'—'].forEach(v=>row.append(el('td',v)));tbody.append(row);});table.append(tbody);box.append(table);
 if(!result.results.length)box.append(el('small','No hay nodos en el ámbito seleccionado.'));
 const b=el('button','Guardar escenario y resultado');b.type='button';b.addEventListener('click',()=>{scenarios.push({id:`SC-${Date.now()}`,name:result.scenario_name,scope:result.scope,overrides:result.overrides,generated_at:result.generated_at,result});scenarios=scenarios.slice(-100);if(save())$('scWarnings').textContent=`Escenario guardado localmente. Historial disponible: ${scenarios.length}.`;});box.append(b);
}
$('scNodeAdd').addEventListener('click',()=>{
 const name=$('scNodeName').value.trim(),source=$('scNodeSource').value.trim(),capRaw=$('scNodeCapacity').value.trim(),capacity=capRaw===''?null:Number(capRaw),unit=$('scNodeUnit').value.trim();
 if(!name){alert('Escribe el nombre del servicio o activo.');return;}if(!source){alert('Indica una fuente o referencia verificable.');return;}if(capacity!==null&&(!Number.isFinite(capacity)||capacity<0)){alert('Capacidad inválida.');return;}if(capacity!==null&&!unit){alert('Indica la unidad de capacidad.');return;}
 const dependencies=$('scNodeDeps').value.split(',').map(x=>x.trim()).filter(Boolean),item={id:id(),name,municipality:$('scNodeMunicipality').value,sector:$('scNodeSector').value,criticality:$('scNodeCriticality').value,capacity,unit:unit||null,dependencies,source,created_at:now()};
 try{validateGraph([...nodes,item]);}catch(e){alert(e.message);return;}
 nodes.push(item);if(save()){['scNodeName','scNodeCapacity','scNodeUnit','scNodeDeps','scNodeSource'].forEach(k=>$(k).value='');renderNodes();$('scWarnings').textContent=`Nodo ${item.id} registrado. Anota su ID para referenciarlo en dependencias y escenarios.`;}
});
$('scRun').addEventListener('click',()=>{try{const name=$('scName').value.trim()||`Escenario ${new Date().toLocaleString()}`,scope=$('scMunicipality').value,overrides=parseOverrides($('scOverrides').value,scope);lastResult=calculate(name,scope,overrides);renderResult(lastResult);$('scWarnings').textContent=`Cálculo completado: ${lastResult.summary.affected_nodes} nodos afectados de ${lastResult.summary.nodes_in_scope}. No es pronóstico ni alerta oficial.`;}catch(e){alert(`No se pudo calcular: ${e.message}`);}});
$('scClear').addEventListener('click',()=>{$('scOverrides').value='';$('scResult').replaceChildren();lastResult=null;});
$('scExport').addEventListener('click',()=>{const data={application:'PREPPER MAP PRO',kind:'scenario_lab',schema_version:1,exported_at:now(),nodes,scenarios,last_result:lastResult};const b=new Blob([JSON.stringify(data,null,2)],{type:'application/json'}),u=URL.createObjectURL(b),a=document.createElement('a');a.href=u;a.download=`prepper-map-escenarios-${now().slice(0,10)}.json`;a.click();setTimeout(()=>URL.revokeObjectURL(u),1200);});
$('scCSV').addEventListener('click',()=>{if(!lastResult){alert('Primero ejecuta un escenario.');return;}const cols=['id','name','municipality','sector','criticality','direct_availability','effective_availability_pct','capacity','unit','effective_capacity','capacity_loss','dependencies'];const q=v=>'"'+String(Array.isArray(v)?v.join('|'):v??'').replace(/"/g,'""')+'"';const csv=[cols.join(','),...lastResult.results.map(x=>cols.map(k=>q(x[k])).join(','))].join('\r\n');const b=new Blob([csv],{type:'text/csv;charset=utf-8'}),u=URL.createObjectURL(b),a=document.createElement('a');a.href=u;a.download='prepper-map-escenario.csv';a.click();setTimeout(()=>URL.revokeObjectURL(u),1200);});
load();renderNodes();
})();