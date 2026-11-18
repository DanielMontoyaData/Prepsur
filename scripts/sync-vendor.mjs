import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const copy = (from, to) => {
  if (!fs.existsSync(from)) throw new Error(`No se encontró dependencia: ${from}. Ejecuta npm install.`);
  fs.mkdirSync(path.dirname(to), { recursive: true });
  fs.cpSync(from, to, { recursive: true });
};
const vendor = path.join(root, 'frontend', 'vendor');
copy(path.join(root, 'node_modules/leaflet/dist/leaflet.js'), path.join(vendor, 'leaflet/leaflet.js'));
copy(path.join(root, 'node_modules/leaflet/dist/leaflet.css'), path.join(vendor, 'leaflet/leaflet.css'));
copy(path.join(root, 'node_modules/leaflet/dist/images'), path.join(vendor, 'leaflet/images'));
copy(path.join(root, 'node_modules/esri-leaflet/dist/esri-leaflet.js'), path.join(vendor, 'esri-leaflet/esri-leaflet.js'));
console.log('Dependencias cartográficas copiadas a frontend/vendor.');
