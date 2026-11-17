## Novedades 1.8
- Análisis de cobertura y brechas por zona: conteo de recursos, categorías y distancia al recurso más cercano.
- Requerimientos diarios estimados con población agregada disponible y tasas configuradas.
- Visor local de informes JSON.
- Ver `docs/operations-v18.md`.

## Novedades 1.7
- Calculadora de autonomía de agua, alimentos y energía para escenarios de hogar, refugio, comunidad y puesto de operaciones.
- Consumo por persona y cargas adicionales configurables; autonomía, cobertura y déficit.
- Guardado local y exportación JSON/CSV; calculadora CLI equivalente.
- Ver `docs/operations-v17.md`.

# PREPPER MAP PRO 1.5 — Atlas GIS de resiliencia civil y aplicación multiplataforma

Plataforma independiente para preparación civil y resiliencia territorial en Envigado, Itagüí, Sabaneta, La Estrella, Caldas y sur de Medellín.

## Novedades 1.6\n- Cribado GIS de activos e intersecciones de amenazas alrededor de un incidente, con radio configurable y reporte JSON.\n- Validación de datos de entrada y límites metodológicos documentados.\n- Ver `docs/operations-v16.md`.\n\n## Novedades 1.5
- Asignación de recursos verificados a incidentes, con estados y trazabilidad en la bitácora.
- Generador de SITREP estructurado para revisión y copia manual por canales autorizados.
- Analizador GIS métrico de intersección de rutas con polígonos de amenaza; produce informe JSON y GeoJSON de segmentos coincidentes.
- 40 pruebas automatizadas superadas en esta entrega.
- Ver `docs/operations-v15.md`.

## Novedades 1.4
- Extractor ArcGIS REST reforzado contra truncamientos de paginación.
- Manifiesto con SHA-256, bytes, fecha de captura y estado de completitud.
- Validador reproducible de capas oficiales y comandos de descarga para Envigado.
- Ver `docs/official-data-v14.md` y `docs/implementation-status-v14.md`.

## Novedades 1.3
- Incidentes georreferenciados sobre el mapa y selección desde sus marcadores.
- Bitácora de comunicaciones por incidente (registro manual, no transmisión).
- Inventario local de recursos con fuente, ubicación, estado y respaldo JSON.
- Ver `docs/command-and-resources-v13.md` y `docs/operations-v13.md`.

## Novedades 1.2
- Puesto de mando local: registro de incidentes, prioridades, estados, bitácora cronológica y respaldo/importación JSON.
- Catálogo ampliado a 26 capas con dos amenazas adicionales de Medellín: incendios forestales y amenaza tecnológica (DAGRD IDs 8 y 9).
- Bitácora almacenada localmente; no despacha ni transmite órdenes.
- Ver `docs/incident-command-v12.md`.

## Novedades 1.1
- Auditoría GIS con SHA-256, extensión, antigüedad, procedencia y estado de cada capa.
- Descarga/caché de teselas offline y comprobación previa de publicación.
- Ver `docs/operations-v11.md`.

## Novedades 0.8
- Base multiplataforma Tauri 2 para Windows, Android e iOS.
- Instalador Windows NSIS `.exe` configurado y flujos de compilación Windows/Android en GitHub Actions.
- Librerías Leaflet/Esri-Leaflet preparadas para empaquetado local sin CDN.
- Mejoras de interfaz móvil, iconos PWA, política de privacidad y borrado de observaciones locales.
- Ver `docs/multiplatform-v08.md`.

## Novedades 0.7
- Procesamiento DEM GeoTIFF para pendientes y clases de terreno.
- Perfil de elevación de rutas, ascenso/descenso y gradiente aproximado.
- Métricas topológicas de red OSM.
- Visualización en el panel web de GeoJSON de pendientes y perfil JSON.
- Paquete offline ahora incorpora rutas y productos de terreno locales si existen.
- Ver `docs/terrain-and-connectivity-v07.md`. Dependencias adicionales: `requirements-terrain.txt`.

## Novedades 0.6
- Centro de evaluación territorial con indicadores de calidad y vigencia.
- Evaluación preliminar de rutas importadas frente a polígonos de amenaza locales activos, con exportación JSON.
- Bitácora local de observaciones de campo, sin sincronización, exportable manualmente.
- Ver `docs/operations-v06.md` para metodología y límites.

## Novedades 0.5
- Módulo de senderos y plataformas GPS: Wikiloc, komoot, Mapy.com, AllTrails y OpenStreetMap.
- Importación local de GPX, KML y GeoJSON en el navegador; exportación de los tracks importados a GeoJSON.
- Catálogo de proveedores con límites de integración explícitos: sin scraping ni APIs ficticias.
- Descargador de senderos OSM mediante Overpass, con atributos de superficie/acceso cuando estén mapeados y atribución ODbL.
- Carga opcional de `frontend/data/routes/osm_trails.geojson` en el mapa.
- Herramientas para auditar rutas candidatas contra capas de amenaza descargadas.

## Novedades 0.4
- Auditoría automatizada de metadatos de capas ArcGIS (`check_sources.py`).
- Extractor ArcGIS más robusto: paginación por objectIds, reintentos, límite por capa, preservación de metadatos y resumen reproducible.
- Validador GeoJSON ampliado: estructura, coordenadas WGS84, geometrías vacías, IDs duplicados y coherencia con manifiesto.
- Auditoría de rutas candidatas frente a polígonos de amenaza (`audit_route.py`). Requiere Shapely; detecta intersecciones, no calcula por sí mismo rutas seguras.
- Constructor de paquete offline con los datos locales existentes (`build_offline_pack.py`).
- PWA con caché versionada y fallback explícito; el modo offline no inventa alertas ni actualiza datos sin conexión.
- Catálogo de fuentes revisado con IDs de capas contrastados contra los servicios públicos disponibles.
- Pruebas automatizadas ampliadas y documentación de límites operativos.

## Cobertura
- Envigado: POT, inundación (5), movimiento en masa (6), equipamientos (2), suelo de protección (7).
- Itagüí: POT, movimiento en masa (7), inundación (8), equipamientos (9).
- Sabaneta: POT, riesgos combinados (5), equipamientos (8), suelo de protección (7).
- La Estrella: POT, riesgos combinados (6), equipamientos (7), suelo de protección (4, 5).
- Caldas: POT, riesgos combinados (2), equipamientos (1), suelo de protección (3).
- Medellín: DAGRD, amenazas de avenidas torrenciales, inundación, movimiento en masa, incendios forestales y tecnológicas; puntos de encuentro, rutas y sensores. La cobertura se limita al Distrito de Medellín.

## Inicio rápido
Requiere Python 3.11+.
```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python -m http.server 8080 --directory frontend
```
Abrir http://localhost:8080.

## Senderos y rutas GPS
El visor ofrece enlaces a proveedores y procesa archivos GPS localmente:
- Wikiloc: no ofrece API pública; abrir rutas compartidas y cargar GPX/KML exportados con permisos.
- komoot: sin API pública general; admite intercambio mediante GPX en sus funciones oficiales.
- Mapy.com y AllTrails: acceso como portales externos, sin scraping.
- OpenStreetMap: datos de senderos descargables con Overpass y licencia ODbL.

Descargar senderos OSM para el área regional aproximada:
```bash
python backend/scripts/download_osm_trails.py
```
Cambiar extensión geográfica con `--bbox south,west,north,east`. El conjunto se guarda en `gis/routes/` y `frontend/data/routes/`. Respetar el uso de Overpass y no ejecutar descargas repetitivas de gran tamaño.

Los caminos OSM son candidatos cartográficos, no rutas oficiales ni verificadas en campo. La disponibilidad de `surface`, `sac_scale`, `access`, `smoothness` e `incline` depende de lo que haya mapeado la comunidad.

## Auditoría de fuentes
```bash
python backend/scripts/check_sources.py
```
Genera `gis/audit/source_audit.json`. La comprobación requiere internet. Un servicio disponible no implica que todos sus datos estén actualizados o que sean aptos para decisiones de evacuación.

## Extracción GIS
Primero inspecciona:
```bash
python backend/scripts/extract_arcgis.py --dry-run
```
Después descarga:
```bash
python backend/scripts/extract_arcgis.py
```
Opciones:
```bash
python backend/scripts/extract_arcgis.py --municipality Envigado --max-features 50000
python backend/scripts/extract_arcgis.py --source envigado_pot --layer 5
```
Los archivos se guardan en `gis/downloaded/` y `frontend/data/`. La extracción requiere internet y puede tardar según el tamaño de cada capa.

## Validación de datos
```bash
python backend/scripts/validate_dataset.py
```

## Auditoría de una ruta candidata
Proporciona una ruta GeoJSON LineString y capas de amenaza descargadas:
```bash
python backend/scripts/audit_route.py \
  --route path/to/route.geojson \
  --hazards gis/downloaded/envigado_5_flood_risk.geojson \
  --hazards gis/downloaded/envigado_6_landslide_risk.geojson
```
Instala `shapely` (incluido en requirements). El informe clasifica intersecciones espaciales con las geometrías descargadas. No sustituye un análisis hidrológico/geotécnico ni una autorización oficial.

## Paquete offline
```bash
python backend/scripts/build_offline_pack.py
```
Crea un ZIP con la aplicación, metadatos y GeoJSON locales existentes. No incluye teselas base ni alertas en vivo salvo que el usuario incorpore cartografía con licencia adecuada. Para iPhone, instala la PWA desde Safari mientras tengas conexión; el comportamiento offline debe probarse en el dispositivo.

## PostGIS / API
```bash
docker compose -f deploy/docker-compose.yml up -d
uvicorn backend.app.main:app --reload --port 8000
```
Aplica `schema/schema.sql` a la base. Mantén los datos privados fuera del directorio público.

## Seguridad y límites
- Las rutas candidatas no son rutas oficiales.
- Los puntos de encuentro de Medellín no se extrapolan a otros municipios.
- Un equipamiento POT no equivale a refugio habilitado.
- Un punto comercial no es abastecimiento garantizado durante un colapso.
- No se publican ubicaciones de armas, inventarios sensibles ni objetivos de saqueo.
- Los datos offline son una instantánea con fecha; no representan el estado actual.
- Las alertas oficiales y las instrucciones de organismos de socorro prevalecen.


## Aplicaciones nativas
PREPPER MAP incluye un proyecto Tauri 2 para Windows, Android e iOS. Consulta `docs/multiplatform-v08.md`. Ejecuta `npm install`, `npm run sync:vendor` y `npm run check` antes de compilar o desplegar el frontend estático. Los instaladores requieren el entorno de cada plataforma; iOS requiere macOS/Xcode y firma Apple.


## Versión 1.4 — Datos oficiales auditables

- Inspección de metadatos ArcGIS: `npm run inspect:envigado`
- Descarga de capas catalogadas de Envigado: `npm run download:envigado` (requiere conexión)
- Auditoría de integridad: `npm run audit:official-pack`
- Guía: `docs/official-data-v14.md` y estado: `docs/implementation-status-v14.md`.

Las descargas se guardan en `gis/downloaded/` y `frontend/data/`. La ausencia de una capa en el manifiesto significa que no está disponible localmente; el catálogo de fuentes no equivale a datos descargados.


## Coordinación intermunicipal PRO 1.9
El módulo lateral permite registrar solicitudes de apoyo entre municipios, compromisos, estados y bitácora; incluye control local de capacidad declarada y exportación JSON/CSV. Consulta `docs/operations-v19.md` y `docs/implementation-status-v19.md`. No existe sincronización multiusuario, integración institucional ni despacho automático.


## Inteligencia operativa territorial PRO 2.0
Tablero de solo lectura que consolida incidentes, recursos y solicitudes intermunicipales del almacenamiento local. Incluye filtro municipal, análisis de frescura y brechas, y exportación SITREP. Consulta `docs/operations-v20.md`.


## Laboratorio de escenarios PRO 2.1
Permite modelar dependencias de servicios y afectaciones hipotéticas, calcular propagación conservadora y exportar resultados. No incluye infraestructura real precargada. Consulta `docs/operations-v21.md`.

## Versión 2.2 — consolidación
Consulta `docs/architecture-v22.md` y `docs/release-readiness-v22.md`. Para auditar el catálogo sin conexión: `python backend/scripts/audit_gis_catalog.py`. Para comprobar servicios ArcGIS: `python backend/scripts/audit_gis_catalog.py --remote`. Para descargar capas oficiales tras comprobar metadatos: `python backend/scripts/audit_gis_catalog.py --remote --download` (puede tardar y producir errores parciales; revisa `gis/audits/catalog-audit-latest.json` y `gis/downloaded/manifest.json`).

La sincronización API permanece deshabilitada hasta configurar `PREPPER_TOKENS` con tokens aleatorios y claims `role` + `tenant_id`; usa HTTPS en despliegue. Los eventos recibidos no se aplican automáticamente.


## Versión 2.3 — Red privada híbrida
Consulta `docs/hybrid-private-network-v23.md` y `docs/release-readiness-v23.md`.
\n\n## PREPPER MAP PRO 2.4 — Multiplataforma\nLa misma base de código se prepara para Windows, macOS, Linux, Android, iPhone/iPad y PWA. Consulta `docs/multiplatform-v24.md` para requisitos y comandos.\n

## PREPPER MAP PRO 2.5 — Red privada de amigos
Perfiles, invitaciones, mensajería y observaciones compartidas por grupo. Ver `docs/private-friends-network-v25.md` para el despliegue y los límites de seguridad.
