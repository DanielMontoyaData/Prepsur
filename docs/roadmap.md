# PREPPER MAP — hoja de ruta\n\n## 1.0.0 entregado\n- Selector de cartografía raster offline desde paquetes MBTiles legales.\n- Conversor TMS a XYZ y manifiesto con procedencia/licencia.\n- Caché de teselas locales.\n\n## Pendiente de validación real\n- Conseguir MBTiles regional con permiso de almacenamiento y redistribución.\n- Pruebas físicas Android/iOS/Windows.\n- Compilar instaladores firmados.\n- Validar cobertura y vigencia de datos con cada autoridad municipal.\n\n# Roadmap

## 0.2 — incluido
- Visor PWA con capas GeoJSON locales.
- Catálogo ArcGIS por municipio/capa.
- Extractor con consulta por IDs y paginación por lotes.
- API FastAPI de lectura.
- Esquema PostGIS, índices espaciales y auditoría.
- Documentación de licencias, verificación, privacidad y operación.

## 0.4 — siguiente
- Ejecutar extracción y validar resultados reales de Envigado/Itagüí/Medellín.
- Investigar endpoints oficiales de Sabaneta, La Estrella y Caldas.
- Completar red hidrográfica y límites municipales con fuentes autorizadas.
- Importador GeoJSON → PostGIS.
- Capas de lugares con fuentes verificadas.

## 0.4
- Rutas peatonales con análisis de exposición, barreras y pendiente.
- PMTiles/MBTiles regionales con licencia de distribución comprobada.
- Descarga por municipio y fecha.
- Prueba de operación sin conectividad en iOS.

## 0.5
- Roles público, editor y propietario.
- Formularios comunitarios moderados.
- Alertas con fuente, timestamp y expiración.
- Panel de calidad y caducidad de datos.
