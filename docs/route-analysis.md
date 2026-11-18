# Auditoría de rutas candidatas

PREPPER MAP 0.4 incorpora un control geométrico preliminar con `audit_route.py`.

## Entradas
- Una ruta candidata en GeoJSON (LineString o FeatureCollection).
- Uno o varios GeoJSON de amenazas descargadas del catálogo.
- Todas las geometrías deben estar en EPSG:4326.

## Salida
- Número de entidades de amenaza revisadas.
- Número de intersecciones con la ruta.
- Atributos de cada polígono intersectado.
- Informe JSON reproducible.

## Límites
La intersección geométrica es una prueba de cribado. No modela profundidad/velocidad de inundación, estabilidad de taludes, distancia de seguridad, caída de árboles, condiciones de paso ni estado de la vía. No certifica una ruta como segura. Las rutas oficiales y órdenes de evacuación prevalecen.
