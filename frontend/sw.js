const VERSION='2.5';
const CACHE=`prepper-map-pro-${VERSION}-shell`;
const CORE=['./','./index.html','./privacy.html','./ops-center.js','./resource-registry.js','./sync-client.js','./sync-panel.js','./network-panel.js','./autonomy.js','./zone-coverage.js','./mutual-aid.js','./situation-board.js','./scenario-lab.js','./manifest.webmanifest','./live_layers.json','./data/places.geojson','./data/manifest.json','./data/quality-report.json','./icons/prepper-map-icon.png','./icons/icon-192.png','./icons/icon-512.png','./offline-tiles/manifest.json','./offline-tiles/tile-index.json','./vendor/leaflet/leaflet.js','./vendor/leaflet/leaflet.css','./vendor/esri-leaflet/esri-leaflet.js'];
self.addEventListener('install',event=>event.waitUntil((async()=>{const cache=await caches.open(CACHE);await Promise.all(CORE.map(async path=>{try{await cache.add(path)}catch(error){}}));await self.skipWaiting()})()));
self.addEventListener('activate',event=>event.waitUntil((async()=>{const keys=await caches.keys();await Promise.all(keys.filter(key=>key.startsWith('prepper-map-pro-')&&key!==CACHE).map(key=>caches.delete(key)));await self.clients.claim()})()));
self.addEventListener('fetch',event=>{
 const req=event.request;if(req.method!=='GET')return;const url=new URL(req.url);if(url.origin!==self.location.origin)return;
 if(url.pathname.includes('/offline-tiles/')&&/\.(png|jpg|webp)$/.test(url.pathname)){event.respondWith((async()=>{const c=await caches.open('prepper-map-pro-2.5-offline-tiles');const hit=await c.match(req);if(hit)return hit;try{return await fetch(req)}catch{return new Response('',{status:503})}})());return;}
 // Navegación: red primero y shell local como respaldo. Archivos de datos: red primero y caché después.
 event.respondWith((async()=>{const cache=await caches.open(CACHE);const cached=await cache.match(req);
  try{const response=await fetch(req);if(response.ok&&(req.mode==='navigate'||url.pathname.includes('/data/')||url.pathname.includes('/offline-tiles/')||/\.(json|geojson|js|css|webmanifest)$/.test(url.pathname)))await cache.put(req,response.clone());return response;}
  catch(error){if(cached)return cached;if(req.mode==='navigate')return (await cache.match('./index.html'))||new Response('Aplicación no disponible sin conexión. Abre PREPPER MAP una vez conectado para preparar el modo offline.',{status:503,headers:{'Content-Type':'text/plain; charset=utf-8'}});return new Response('Sin conexión: recurso no descargado.',{status:503,headers:{'Content-Type':'text/plain; charset=utf-8'}});}
 })());
});
