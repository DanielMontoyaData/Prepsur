# PREPPER MAP PRO 1.4 — Descarga y control de datos oficiales

## Objetivo

La versión 1.4 endurece la extracción de servicios ArcGIS REST y añade una auditoría reproducible del paquete local. No incorpora geometrías ficticias ni convierte una conexión disponible en una validación territorial.

## Flujo recomendado

1. Revisar metadatos y capacidades del servicio antes de extraer:
   `python backend/scripts/extract_arcgis.py --municipality Envigado --dry-run`
2. Descargar las capas catalogadas de Envigado:
   `python backend/scripts/extract_arcgis.py --municipality Envigado`
3. Auditar archivos y manifiesto:
   `python backend/scripts/validate_official_pack.py`
4. Revisar `gis/downloaded/manifest.json`, la fecha de captura, recuentos, SHA-256 y estado de cada capa.

También se puede ejecutar `npm run inspect:envigado`, `npm run download:envigado` y `npm run audit:official-pack`.

## Controles incorporados

- Paginación que respeta `exceededTransferLimit`, incluso si una página devuelve menos elementos de los solicitados.
- Descarga por lotes de ObjectIDs cuando el servicio permite enumerarlos.
- Límite defensivo de páginas para evitar ciclos infinitos.
- SHA-256 y tamaño en bytes por GeoJSON.
- Metadatos de procedencia, CRS de salida, fecha UTC, recuento y estado de completitud.
- Auditoría posterior de estructura GeoJSON, existencia del archivo, hash, recuento y truncamiento.

## Interpretación de estados

- `downloaded`: la extracción terminó sin error técnico; no implica validación de campo.
- `truncated_by_user_limit`: se aplicó el límite `--max-features`; no usar como cobertura completa.
- `failed`: la fuente no respondió o la extracción falló; revisar el error y reintentar.
- `metadata_ok`: se consultaron metadatos, pero no se descargaron geometrías.

## Precauciones

- EPSG:4326 es el CRS de intercambio; el servicio puede usar otro CRS nativo.
- Las capas POT representan cartografía de planeación, no alertas en tiempo real.
- Los polígonos de amenaza son insumos de análisis, no certificaciones prediales ni instrucciones de evacuación.
- La cartografía del DAGRD se mantiene limitada al Distrito de Medellín.
- La verificación SHA-256 confirma que el archivo no cambió respecto del manifiesto; no certifica precisión, actualidad, licencia o calidad de origen.
- Antes de redistribuir, revisar atribución y términos de reutilización de cada autoridad.

## Estado de la entrega

El entorno de construcción de esta entrega no tiene conectividad DNS hacia los servicios cartográficos, por lo que no se descargaron capas reales en esta sesión. El extractor y el validador quedan listos para ejecutarse desde un equipo con conexión. No se declara ninguna capa como descargada.
