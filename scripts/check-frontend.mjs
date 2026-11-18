import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { execFileSync } from 'node:child_process';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const html = fs.readFileSync(path.join(root, 'frontend/index.html'), 'utf8');
const matches = [...html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g)];
if (!matches.length) throw new Error('No se encontró JavaScript inline.');
const temp = path.join(os.tmpdir(), 'prepper-map-inline-check.js');
fs.writeFileSync(temp, matches.map(x => x[1]).join('\n'));
execFileSync(process.execPath, ['--check', temp], { stdio: 'inherit' });
for (const asset of ['vendor/leaflet/leaflet.js', 'vendor/leaflet/leaflet.css', 'vendor/esri-leaflet/esri-leaflet.js']) {
  if (!html.includes(asset)) throw new Error(`Falta referencia a ${asset}`);
}
for (const id of ['map', 'routeFile', 'auditRoute', 'saveObservation', 'slopeFile', 'profileFile', 'mutualAidBox', 'maCreate', 'maExport']) {
  if (!html.includes(`id="${id}"`)) throw new Error(`Falta el control obligatorio #${id}`);
}
console.log(`OK: ${matches.length} bloque(s) JavaScript, sintaxis válida y controles GIS presentes.`);
