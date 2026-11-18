# PREPPER MAP PRO 0.7 — terreno, conectividad y paquetes offline

## 1. Preparar el DEM
Obtén un DEM/DSM GeoTIFF con licencia y cobertura documentadas. Copernicus DEM GLO-30 es un DSM de superficie de 30 m, que incluye edificios y vegetación; no es un DTM de suelo desnudo. La documentación oficial indica cobertura global GLO-30 y GLO-90, con acceso/condiciones según categoría de usuario. No asumir precisión de ingeniería.

Para el análisis de pendiente, reproyecta el GeoTIFF a un CRS proyectado en metros adecuado para el área de estudio. Para el Valle de Aburrá puede utilizarse MAGNA-SIRGAS / Origen-Nacional EPSG:9377 cuando corresponda y tras verificar el CRS de entrada.

```bash
pip install -r requirements-terrain.txt
python backend/scripts/prepare_terrain.py --dem data/dem/valle_aburra_dem.tif
```

Produce `gis/terrain/slope_percent.tif`, `slope_degrees.tif`, `slope_classes.tif`, `slope_classes.geojson` y `terrain_manifest.json`. La capa GeoJSON puede cargarse desde el panel **Terreno y altimetría**.

Clases de pendiente: 0–5%, 5–15%, 15–30%, 30–45% y >45%. Son clases descriptivas para lectura territorial, no umbrales universales de seguridad ni criterios de construcción.

## 2. Perfil de elevación de ruta
Con un DEM disponible y una ruta GeoJSON en WGS84:

```bash
python backend/scripts/terrain_route_profile.py \
  --route ruta_candidata.geojson \
  --dem data/dem/valle_aburra_dem.tif \
  --interval 30 \
  --output perfil_ruta.json
```

El JSON contiene muestras, elevación, ascenso/descenso acumulado aproximado y gradiente máximo entre muestras. Cárgalo en el panel **Terreno y altimetría**. La precisión depende de resolución, vertical datum, DSM/DTM y calidad de la ruta.

## 3. Conectividad de senderos
Después de ejecutar el descargador OSM:

```bash
python backend/scripts/download_osm_trails.py
python backend/scripts/analyze_trail_network.py \
  --input gis/routes/osm_trails.geojson \
  --output gis/routes/network_metrics.json
```

Las métricas describen componentes conectados, nodos terminales y cruces geométricos aproximados. No demuestran transitabilidad, estado, permiso de acceso ni seguridad. La red OSM puede estar incompleta o desactualizada. Atribuir © OpenStreetMap contributors y respetar ODbL y políticas de uso.

## 4. Paquete offline
```bash
python backend/scripts/build_offline_pack.py --output dist/prepper-map-offline.zip
```
Incluye aplicación, documentación, rutas y derivados GeoJSON/TIF presentes. No descarga mapas base ni garantiza que servicios remotos, alertas o mapas externos funcionen sin internet. Verifica la fecha de cada conjunto antes de usarlo.

## 5. Interpretación responsable
- Pendiente no equivale a estabilidad geotécnica.
- Elevación de DSM puede representar copas de árboles y edificios.
- Perfil altimétrico no conoce escaleras, barro, derrumbes, cierres, iluminación ni condiciones meteorológicas.
- Conectividad cartográfica no equivale a paso transitable.
- No usar estos resultados para emitir instrucciones oficiales de evacuación.
- Toda ruta crítica debe inspeccionarse en campo y validarse con autoridades y organismos competentes.
