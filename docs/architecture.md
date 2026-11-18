# Arquitectura técnica

## Componentes
1. Frontend Leaflet/PWA: visor, capas locales, búsqueda, exportación y estado de conectividad.
2. Catálogo GIS: `gis/sources/sources.json` como registro de autoridad, municipio, endpoint, capas, CRS y nota de licencia.
3. Extractor: ArcGIS REST metadata + `returnIdsOnly` + consulta por `objectIds` para evitar truncamiento silencioso.
4. PostGIS: almacenamiento espacial e índices GiST.
5. API FastAPI: catálogo, manifiesto, lugares y salud del servicio.
6. Offline: shell PWA + GeoJSON locales. PMTiles/MBTiles se dejan para un proceso de empaquetado con datos y licencia validados.

## CRS
Los servicios pueden publicar EPSG:9377, EPSG:3116 u otros CRS. El extractor solicita `outSR=4326` para intercambio GeoJSON. Conservar siempre CRS original en metadatos. No reasignar CRS: transformar coordenadas.

## Escala y semántica
No mezclar amenaza, riesgo, susceptibilidad, condición de riesgo y alerta activa. Cada fuente mantiene su terminología. La severidad no se deduce de nombres de campos sin inspeccionar la leyenda/metadatos.

## Routing
No implementar routing de evacuación con una simple ruta peatonal OSM. Requiere red topológica, pendientes, barreras, cierres, cruces de cauces, exposición y validación institucional/de campo. Las rutas calculadas deben rotularse como propuestas, nunca oficiales.
