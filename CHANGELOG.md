# Changelog

## 2.1.0
- Laboratorio local de escenarios de interrupción y dependencias entre servicios.
- Inventario configurable de nodos, capacidades de referencia, fuentes y dependencias.
- Propagación conservadora por cuello de botella; rechazo de ciclos y dependencias inexistentes.
- Cálculo de capacidad efectiva, exportación JSON/CSV y motor CLI reproducible.
- No se precargan infraestructuras reales ni se presentan escenarios como pronósticos.

## 2.0.0
- Tablero de inteligencia operativa territorial de solo lectura.
- Consolidación local de incidentes, recursos verificados y solicitudes intermunicipales.
- Filtro municipal y ventana de frescura de datos.
- Alertas de calidad y brechas: ubicación, asignación, fuente, verificación y campos operativos incompletos.
- Generación y exportación de SITREP JSON; copia de resumen textual.
- Versiones frontend/Tauri/Cargo alineadas.

## 1.9.0
- Módulo de coordinación intermunicipal con registro de solicitudes y ofrecimientos.
- Flujo de estados desde solicitada hasta recibida/cerrada o rechazada.
- Bitácora de cambios y roles funcionales.
- Registro de cantidades solicitadas y comprometidas.
- Control de capacidad local para evitar sobrecompromisos del mismo recurso identificado y unidad.
- Importación JSON validada y exportación JSON/CSV.
- Tablero de actividad municipal y documentación operativa.
- Persistencia local; sin sincronización institucional ni despacho automático.

## 1.8.0
- Análisis GIS de cobertura de recursos por zona con polígonos y puntos.
- Conteo de recursos por categoría dentro de cada polígono.
- Distancia euclidiana al recurso más cercano por categoría.
- Estimación de demanda a partir de población agregada y tasas aportadas por el operador.
- Campo poblacional ausente se conserva como null; no se inventan cifras.
- Visor frontend para cargar y revisar informes JSON.
- Pruebas para conteo, demanda, población ausente y validación de población.

# Changelog

## 1.7.0
- Calculadora de autonomía de agua, alimentos y energía para hogares, refugios, comunidades y puestos de operaciones.
- Consumos por persona y consumos adicionales diarios configurables.
- Cálculo de autonomía, requerimiento para horizonte, cobertura, déficit y excedente.
- Guardado local de escenarios y exportación JSON/CSV.
- CLI Python equivalente y pruebas unitarias.
- Advertencias sobre límites de los indicadores y calidad de reservas.

# Changelog

## 1.6.0
- Nuevo cribado GIS de afectación territorial: activos dentro de un radio configurable e intersección del área con polígonos de amenaza.
- Reporte JSON con distancias, categorías, áreas de coincidencia y limitaciones explícitas.
- Validación de coordenadas, radio y estructura GeoJSON.
- Pruebas de activos cercanos/lejanos, intersección de amenaza, radio inválido y GeoJSON inválido.

# Changelog

## 1.5.0
- Centro de operaciones: asignación de recursos verificados a incidentes con estados solicitado, asignado, en camino, en sitio, liberado y cancelado.
- Registro cronológico automático de cada cambio de asignación; se conserva localmente y viaja en el respaldo JSON.
- Generador de SITREP estructurado para copiar y revisar antes de retransmitir por canales autorizados.
- Analizador GIS de exposición de rutas a polígonos de amenaza, con medición en CRS métrico, reporte JSON y segmentos de coincidencia GeoJSON.
- El análisis diferencia ausencia de intersección de seguridad y registra las limitaciones de las fuentes.
- Actualización de versión y pruebas de regresión.

# Changelog

## 1.4.0
- Extracción ArcGIS REST reforzada para respetar `exceededTransferLimit`, incluso con páginas cortas o vacías.
- Metadatos de descarga ampliados: SHA-256, bytes, fecha UTC y estado de completitud.
- Nuevo validador de paquete oficial: estructura GeoJSON, existencia, hash, recuentos, CRS y truncamiento.
- Comandos npm para inspección, descarga y auditoría de capas de Envigado.
- Documentación de interpretación, limitaciones y estado real de datos.

## 1.3.0
- Georreferenciación de incidentes en mapa con marcadores diferenciados por prioridad.
- Registro de comunicaciones manuales asociadas a incidentes, con confirmación.
- Inventario local de recursos por municipio, categoría, fuente y estado de verificación.
- Exportación e importación JSON separada de inventario y bitácora.
- Migración automática de la bitácora 1.2 al esquema 1.3.
- Ampliación de pruebas y documentación operativa.

# Changelog

## 1.2.0
- Added a local incident-command log with incident records, priorities, status, chronology, backup and restore.
- Expanded Medellín DAGRD catalog with forest-fire and technological-hazard layers (IDs 8 and 9), retaining district-only scope.
- Added local-only operational data handling and validation tests.

## 1.2.0 — Calidad territorial y preparación offline
- Inventario auditable de 24 capas de seis jurisdicciones, sin declarar descargados datos que no existen.
- Auditoría GIS con fechas, SHA-256, extensiones, recuentos, licencias y señales de incompletitud.
- Conversión MBTiles a XYZ con índice de teselas y descarga offline iniciada por el usuario.
- Cache Storage para teselas instaladas, controles de progreso, detención y comprobación.
- Preflight de lanzamiento y guía operativa reproducible; pruebas automatizadas adicionales.
- No incluye cartografía regional real ni ejecutables compilados.

# Changelog

## 1.0.0
- Added offline raster basemap support using locally supplied MBTiles converted to XYZ.
- Added strict provider, license and attribution metadata requirements.
- Added local basemap selector and service-worker caching for offline tile packages.
- Added conversion documentation and tests. No regional map tiles are bundled.

# PREPPER MAP PRO 0.9

## 0.9.0
- Biblioteca offline personal persistente con IndexedDB para importar, visualizar, administrar y exportar capas GeoJSON.
- Validación de estructura y geometrías GeoJSON y límite de tamaño por número de elementos.
- Service worker reforzado con fallback de navegación y caché de recursos locales/datos.
- Se aclara que el almacenamiento offline de capas no incluye teselas cartográficas base ni servicios en vivo.

# PREPPER MAP PRO 0.8

- Proyecto multiplataforma Tauri 2: Windows, Android e iOS.
- Instalador Windows NSIS EXE configurado; workflows para compilar Windows y Android.
- Librerías Leaflet y Esri-Leaflet pasan a dependencias locales npm; eliminada dependencia CDN para el motor cartográfico.
- Icono, metadatos, manifest y service worker versionados 0.8.
- Mejoras de ergonomía móvil: safe areas, controles táctiles y foco accesible.
- Prueba estructural de interfaz y guía de compilación/firma.

# PREPPER MAP PRO 0.7

- Flujo opcional de procesamiento de DEM GeoTIFF: pendiente en porcentaje/grados, clases raster y polígonos GeoJSON.
- Perfil altimétrico de rutas con elevación, ascenso/descenso y gradiente aproximado.
- Métricas topológicas de red de senderos OSM (componentes, nodos terminales y cruces).
- Panel web para visualizar clases de pendiente y perfil de elevación importados.
- Paquetes offline ampliados para incluir rutas y derivados de terreno locales disponibles.
- Dependencias geoespaciales opcionales aisladas en `requirements-terrain.txt`.

# PREPPER MAP PRO 0.6

- Centro de evaluación territorial con indicadores de capas, elementos, rutas y observaciones.
- Evaluación preliminar de rutas importadas frente a polígonos de amenaza locales activos, con muestreo aproximado cada 50 m y exportación JSON.
- Bitácora local de observaciones de campo, almacenada en navegador y exportable manualmente.
- Indicador de vigencia de capas: sin fecha o mayores de 180 días quedan marcadas para revisión.
- Caché PWA versionada 0.6 y documentación operativa.

# Changelog

## 0.4.0
- Añadida auditoría automatizada de fuentes ArcGIS REST.
- Fortalecido el extractor con selección de fuente/capa, reintentos y paginación.
- Añadida validación de coordenadas, geometrías y manifiesto.
- Añadida auditoría de intersección de rutas candidatas con amenazas.
- Añadido constructor de paquete offline basado en datos locales disponibles.
- Actualizado service worker y documentación de límites offline.
- Añadidas pruebas de integridad del catálogo.

## 0.3.0
- Ampliación de fuentes a seis municipios.
- Catálogo de capas POT y DAGRD.
- Visor Leaflet y extracción GeoJSON.

## 0.5.0
- Integración externa de Wikiloc, komoot, Mapy.com y AllTrails mediante enlaces y flujos GPX legales.
- Importador local de GPX, KML y GeoJSON en el visor.
- Descargador Overpass de caminos y senderos OpenStreetMap.
- Carga de senderos OSM con metadatos ODbL y estado no verificado.
- Documentación de trazabilidad y evaluación de rutas.

## 2.2.0 — Consolidación y sincronización segura
- API 2.2 y almacén append-only de eventos con idempotencia, hash de payload y auditoría.
- Autorización Bearer con roles y aislamiento obligatorio por tenant; sync deshabilitado sin secretos.
- Outbox IndexedDB y panel de sincronización explícita; token solo en memoria.
- Auditor de catálogo ArcGIS con comprobación remota opcional y extracción controlada por capa.
- Contrato JSON, arquitectura, guía de credenciales y checklist de publicación.
- Se mantienen los límites: eventos pull no se aplican automáticamente; faltan adaptadores/conflict resolution, SSO/MFA y despliegue PostGIS.
\n## 2.3.0 — Red privada híbrida\n- Panel de sincronización orientado a grupo privado.\n- Indicador online/offline.\n- Envío automático opcional al recuperar conectividad, solo con sesión configurada.\n- La descarga remota continúa bajo revisión manual; no se aplican eventos automáticamente.\n- Se documentan privacidad, límites y despliegue para grupo pequeño.\n\n## 2.4.0 — Multiplataforma ampliada\n- Versiones de paquete, Tauri y Rust alineadas en 2.4.0.\n- PWA actualizada con caché de shell 2.4.\n- Flujos CI para macOS, Linux e iOS; se conservan Windows y Android.\n- Guía de instalación y compilación por plataforma.\n
## 2.5.0 — Red privada de amigos
- Registro e inicio de sesión mediante invitaciones privadas.
- Perfiles e integrantes por grupo privado.
- Sesiones independientes por dispositivo y revocación al cerrar sesión.
- Mensajería grupal y observaciones compartidas.
- Marcadores de observaciones georreferenciadas en el mapa.
- Cola local para mensajes y observaciones sin conexión, con envío al reconectar.
- 70 pruebas automatizadas aprobadas.
