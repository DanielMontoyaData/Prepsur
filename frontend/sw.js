const VERSION='2.5';
self.addEventListener('install',e=>e.waitUntil(caches.open(VERSION)));
