/* PREPPER MAP PRO 1.8 — read-only coverage report viewer */
(()=>{'use strict';
const $=id=>document.getElementById(id);let report=null;
const el=(tag,text,cls)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n;};
function render(){
 const summary=$('zcSummary'),table=$('zcTable'),warnings=$('zcWarnings');summary.replaceChildren();table.replaceChildren();warnings.replaceChildren();
 if(!report){summary.textContent='No hay informe cargado.';return;}
 if(report.application!=='PREPPER MAP PRO'||!Array.isArray(report.zones)||!report.summary){summary.textContent='El archivo no tiene el formato de informe PREPPER MAP 1.8.';return;}
 const s=report.summary;
 summary.append(el('b',`${s.zones_analyzed} zonas analizadas · ${s.resource_points_loaded} puntos de recursos procesados`));
 summary.append(el('p',`${s.zones_without_any_registered_resource} zonas sin recursos registrados · ${s.zones_without_population_data} zonas sin dato poblacional`,'foot'));
 const tbl=document.createElement('table');tbl.style.cssText='width:100%;border-collapse:collapse;font-size:11px;text-align:left';
 const headers=['Zona','Población','Recursos registrados','Categorías','Distancia más cercana'];
 const thead=document.createElement('thead'),tr=document.createElement('tr');
 headers.forEach(h=>{const th=el('th',h);th.style.cssText='padding:6px;border-bottom:1px solid var(--line)';tr.append(th)});thead.append(tr);tbl.append(thead);
 const tbody=document.createElement('tbody');
 report.zones.forEach(z=>{
  const row=document.createElement('tr');
  const cats=Object.entries(z.resources_by_category||{}).map(([k,v])=>`${k}: ${v}`).join(' · ')||'Ninguna registrada';
  const distances=Object.entries(z.nearest_resource_distance_m_by_category||{}).map(([k,v])=>`${k}: ${Number(v).toLocaleString('es-CO')} m`).join(' · ')||'Sin datos';
  [z.zone_name,z.population===null||z.population===undefined?'Sin dato':Number(z.population).toLocaleString('es-CO'),String(z.resources_inside),cats,distances].forEach(v=>{const td=el('td',v);td.style.cssText='padding:6px;border-bottom:1px solid var(--line);vertical-align:top';row.append(td)});
  tbody.append(row);
 });tbl.append(tbody);table.append(tbl);
 (report.limitations||[]).forEach(w=>warnings.append(el('p',`• ${w}`)));
}
$('zcReportFile').addEventListener('change',async e=>{
 const f=e.target.files&&e.target.files[0];if(!f)return;
 try{if(f.size>10*1024*1024)throw new Error('El informe supera 10 MB.');const parsed=JSON.parse(await f.text());report=parsed;render();}
 catch(err){report=null;render();$('zcSummary').textContent=`No se pudo cargar el informe: ${err.message}`;}
});
$('zcClear').addEventListener('click',()=>{$('zcReportFile').value='';report=null;render();});
})();
