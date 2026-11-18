# Construcción offline — PREPPER MAP PRO 1.0

## Qué queda disponible
- Aplicación web y recursos locales que se hayan descargado.
- GeoJSON locales con sus atributos y metadatos.
- Último manifiesto de extracción.
- Biblioteca Leaflet/Esri Leaflet cacheada por el service worker después de una primera carga online desde `unpkg.com`.

## Qué NO queda disponible automáticamente
- Teselas base OSM: no se cachean ni se descargan masivamente.
- Servicios ArcGIS dinámicos y feeds SIATA/SIAMMO en vivo.
- Alertas nuevas una vez desconectado.
- Datos que nunca se descargaron al dispositivo.

## Crear paquete
```bash
python backend/scripts/build_offline_pack.py
```

El archivo se genera en `dist/prepper-map-offline.zip`. Incluye la aplicación, documentación y GeoJSON disponibles al momento de la creación.

## Cartografía base offline
Incorporar únicamente un PMTiles/MBTiles producido a partir de una fuente con licencia compatible. No descargar en masa `tile.openstreetmap.org`. El manifiesto de paquetes debe guardar proveedor, licencia, fecha, zooms y extensión.

## Prueba en iPhone
1. Publicar la PWA bajo HTTPS.
2. Abrirla en Safari con internet.
3. Esperar la instalación del service worker y cargar cada capa local que se necesite.
4. Añadir a pantalla de inicio si se desea.
5. Activar modo avión y probar navegación por los datos descargados.
6. Verificar que el indicador diga OFFLINE y que la fecha de la instantánea sea visible.
7. Repetir después de cada actualización de la aplicación.
