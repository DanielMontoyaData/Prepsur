# Senderos, rutas y plataformas GPS — 0.5

## Proveedores
- Wikiloc: enlace de búsqueda y uso de tracks que el usuario exporte con autorización. No API pública; no scraping.
- komoot: enlaces compartidos e importación/exportación GPS individual. No API pública general.
- Mapy.com / AllTrails: referencias externas, sin extracción automatizada.
- OpenStreetMap: caminos, senderos y relaciones `route=hiking` por Overpass.

## Flujo de trabajo
1. Buscar la ruta en el proveedor externo.
2. Verificar fecha, autor, actividad, dificultad, permisos, acceso y avisos del proveedor.
3. Si está permitido, exportar GPX/KML y cargarlo en PREPPER MAP.
4. Contrastar la geometría con amenazas oficiales descargadas.
5. Revisar cruces, pendientes, puentes, quebradas y cierres en campo.
6. Registrar responsable, fecha, fuente y estado de verificación.

## Descarga de OSM
```bash
python backend/scripts/download_osm_trails.py
python backend/scripts/download_osm_trails.py --bbox 6.00,-75.80,6.30,-75.40
```
El bounding box predeterminado es una aproximación regional amplia, no límites administrativos oficiales. El script descarga caminos etiquetados como `path`, `footway`, `track`, `steps`, `bridleway` y relaciones `route=hiking`.

Atribución: © OpenStreetMap contributors. Datos sujetos a ODbL. Para redistribución, cumplir las obligaciones de atribución y licencia aplicables.

## Campos útiles
`highway`, `surface`, `tracktype`, `smoothness`, `sac_scale`, `incline`, `access`, `foot`, `name`, `ref`, `network`, `osmc:symbol`.

Los valores ausentes no se infieren. `sac_scale` es clasificación de dificultad de senderismo si está mapeada; no es una valoración de seguridad ni aptitud para evacuación.

## Uso en emergencias
El sistema debe distinguir:
- ruta recreativa publicada;
- camino OSM cartografiado;
- ruta propuesta por análisis;
- ruta revisada en campo;
- ruta oficialmente definida por autoridad.

Ninguna de las primeras tres categorías debe presentarse como ruta segura o ruta oficial de evacuación.
