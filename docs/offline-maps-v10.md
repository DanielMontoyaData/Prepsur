# Cartografía base offline — PREPPER MAP 1.0

## Qué aporta
La aplicación reconoce paquetes raster XYZ locales en `frontend/offline-tiles/`
y permite alternar entre esa cartografía y OpenStreetMap online. El service worker
incluye el manifiesto y las teselas locales en su estrategia de caché.

## Preparar desde MBTiles
El conversor no descarga mapas; transforma un archivo MBTiles raster ya obtenido
legalmente. Requiere Python estándar (usa SQLite incluido).

```bash
python backend/scripts/mbtiles_to_xyz.py valle_aburra.mbtiles \\
  --output frontend/offline-tiles \\
  --provider "Proveedor de cartografía" \\
  --license "Licencia y versión" \\
  --attribution "Atribución exigida por el proveedor"
```

Formatos raster admitidos: PNG, JPG/JPEG y WebP. Los MBTiles vectoriales PBF no
son compatibles con este conversor. Se convierte el esquema TMS de MBTiles a XYZ.
El manifiesto registra proveedor, licencia, atribución, fecha, zooms, extensión
y número de teselas.

## Validación antes de distribuir
- Confirmar por escrito que la licencia permite almacenamiento offline y
  redistribución dentro de la app.
- Verificar la atribución visible en el mapa.
- Confirmar que bounds/zoom cubren el área necesaria.
- Probar modo avión en Android/iOS/Windows.
- No interpretar cobertura cartográfica como garantía de seguridad.
- El paquete puede quedar desactualizado; no contiene alertas en vivo.

## Límites
No se incluye un MBTiles regional en este repositorio: no se ha descargado ni
validado un proveedor/licencia para el área. La función queda lista para recibir
un paquete legal. No se recomienda descargar teselas masivas del servidor
estándar de OpenStreetMap.
