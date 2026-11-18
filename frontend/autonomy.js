/* PREPPER MAP PRO 1.7 — autonomy and supply calculator */
(()=>{'use strict';
const $=id=>document.getElementById(id),KEY='prepper-map-autonomy-v1';
const ids=['auScenario','auPeople','auDays','auWater','auFood','auEnergy','auWaterRate','auFoodRate','auEnergyRate','auWaterExtra','auFoodExtra','auEnergyExtra'];
let latest=null;
const num=id=>{const n=Number($(id).value);if(!Number.isFinite(n)||n<0)throw new Error(`Valor inválido: ${id}`);return n;};
const fmt=(n,d=1)=>Number(n).toLocaleString('es-CO',{maximumFractionDigits:d});
function calculate(){
 const people=num('auPeople'),days=num('auDays');
 if(people<1||people>100000||days<1||days>365)throw new Error('Personas: 1–100.000. Días: 1–365.');
 const rows=[
  {key:'water',label:'Agua',unit:'L',stock:num('auWater'),daily:people*num('auWaterRate')+num('auWaterExtra')},
  {key:'food',label:'Alimentos',unit:'kg',stock:num('auFood'),daily:people*num('auFoodRate')+num('auFoodExtra')},
  {key:'energy',label:'Energía',unit:'kWh',stock:num('auEnergy'),daily:people*num('auEnergyRate')+num('auEnergyExtra')}
 ].map(x=>({...x,required:x.daily*days,days:x.daily>0?x.stock/x.daily:null,deficit:Math.max(0,x.daily*days-x.stock),surplus:Math.max(0,x.stock-x.daily*days),coverage:x.daily>0?Math.min(100,x.stock/(x.daily*days)*100):100}));
 latest={application:'PREPPER MAP PRO',version:'1.7.0',created_at:new Date().toISOString(),scenario:$('auScenario').value,people,days_target:days,resources:rows,notes:['Estimación determinista basada en consumos ingresados por el operador.','No valida potabilidad, inocuidad, estado de equipos ni acceso físico.','No incorpora pérdidas, desperdicio, variación de demanda o reabastecimiento futuro.']};
 const host=$('auResults');host.replaceChildren();
 rows.forEach(r=>{
  const card=document.createElement('div');card.className='resource';
  const title=document.createElement('b');title.textContent=r.label;card.append(title);
  const p=document.createElement('p');p.textContent=`Reserva: ${fmt(r.stock)} ${r.unit} · Consumo diario: ${fmt(r.daily)} ${r.unit}/día`;card.append(p);
  const q=document.createElement('p');q.textContent=`Autonomía: ${r.days===null?'No calculable (consumo diario cero)':fmt(r.days,2)+' días'} · Cobertura objetivo: ${fmt(r.coverage)}%`;card.append(q);
  const z=document.createElement('p');z.textContent=r.deficit>0?`Déficit para ${days} días: ${fmt(r.deficit)} ${r.unit}`:`Objetivo cubierto. Excedente: ${fmt(r.surplus)} ${r.unit}`;card.append(z);
  const bar=document.createElement('div');bar.style.cssText='height:8px;background:var(--line);border-radius:8px;overflow:hidden';
  const fill=document.createElement('div');fill.style.cssText=`height:100%;width:${r.coverage}%;background:${r.deficit>0?'#d97706':'#16845b'}`;bar.append(fill);card.append(bar);host.append(card);
 });
 const total=rows.filter(x=>x.deficit>0).length;
 const status=document.createElement('p');status.className='foot';status.textContent=total?`${total} de 3 categorías presentan déficit para el horizonte seleccionado.`:'Las tres categorías cubren el horizonte indicado según los datos ingresados.';host.append(status);
}
function download(name,content,type){const blob=new Blob([content],{type}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1500);}
function read(){try{return JSON.parse(localStorage.getItem(KEY)||'[]')}catch(_){return []}}
function saved(){const list=read();$('auSaved').textContent=list.length?`Escenarios guardados localmente: ${list.map(x=>x.label).join(' · ')}`:'No hay escenarios guardados en este dispositivo.';}
$('auCalculate').addEventListener('click',()=>{try{calculate()}catch(e){alert(e.message)}});
$('auSave').addEventListener('click',()=>{try{calculate();const list=read();list.push({label:`${latest.scenario} · ${latest.people} personas · ${latest.days_target} días`,data:latest});localStorage.setItem(KEY,JSON.stringify(list.slice(-50)));saved();}catch(e){alert(e.message)}});
$('auExport').addEventListener('click',()=>{try{if(!latest)calculate();download('prepper-map-autonomia.json',JSON.stringify(latest,null,2),'application/json')}catch(e){alert(e.message)}});
$('auCSV').addEventListener('click',()=>{try{if(!latest)calculate();const lines=[['Recurso','Reserva','Unidad','Consumo diario','Requerido horizonte','Autonomia dias','Deficit','Cobertura %'],...latest.resources.map(x=>[x.label,x.stock,x.unit,x.daily,x.required,x.days??'',x.deficit,x.coverage])];const csv=lines.map(r=>r.map(v=>'"'+String(v).replaceAll('"','""')+'"').join(';')).join('\r\n');download('prepper-map-autonomia.csv','\ufeff'+csv,'text/csv;charset=utf-8')}catch(e){alert(e.message)}});
ids.forEach(id=>$(id).addEventListener('change',()=>{try{calculate()}catch(_){}}));
saved();
})();
