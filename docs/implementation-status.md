# Estado de implementación 0.4

## Implementado en el paquete
- Catálogo de seis fuentes GIS: Envigado, Itagüí, Sabaneta, La Estrella, Caldas y Medellín.
- Visor Leaflet con capas oficiales en vivo y capas GeoJSON locales.
- Filtro visual por municipio y botón de geolocalización bajo permiso del usuario.
- Extractor ArcGIS con reintentos, paginación y selección por municipio/fuente/capa.
- Auditoría de metadatos de servicios y capas.
- Validador GeoJSON con controles de estructura y coordenadas WGS84.
- Auditoría espacial de rutas candidatas frente a polígonos de amenaza.
- Constructor de paquete offline con datos locales disponibles.
- PWA con caché versionada para shell, recursos locales y bibliotecas CDN usadas.
- Esquema PostGIS, API FastAPI y documentación de gobernanza.

## Fuentes identificadas
Los IDs configurados se contrastaron con los metadatos públicos de los servicios ArcGIS REST. Ejecutar `python backend/scripts/check_sources.py` para repetir la auditoría desde el equipo que despliegue el proyecto.

## No se debe considerar terminado
- No hay aún geometrías oficiales descargadas dentro de este ZIP.
- No se ha desplegado una instancia PostGIS de producción.
- No hay PMTiles/MBTiles base incluidos.
- No hay rutas oficiales verificadas de Envigado/Itagüí/Sabaneta/La Estrella/Caldas.
- No hay refugios, puntos de agua potable o estaciones solares certificados.
- No hay inventario privado cargado ni cuentas de usuario implementadas.
- La geolocalización depende de permiso del usuario y contexto HTTPS/localhost.

## Hitos para operación
1. Ejecutar auditoría de fuentes.
2. Descargar capas oficiales y guardar manifiesto.
3. Validar los GeoJSON.
4. Inspeccionar atributos/leyendas de amenazas combinadas.
5. Incorporar recursos con evidencia y verificación.
6. Preparar mapa base con licencia apropiada para offline.
7. Realizar pruebas en el iPhone y simulacros de campo.
