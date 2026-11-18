# PREPPER MAP PRO 1.6 — Cribado de afectación territorial

## Propósito
Estimar qué activos georreferenciados suministrados por el operador se encuentran dentro de un radio de análisis alrededor de un incidente, e identificar polígonos de amenaza que intersectan ese radio.

## Preparar datos
Los activos y amenazas deben ser GeoJSON FeatureCollection con geometrías válidas. Los activos deberían ser puntos y contener, cuando existan, propiedades `name`/`nombre` y `category`/`tipo`/`type`. Los polígonos de amenaza deben provenir de fuentes identificadas y vigentes para el propósito. No se incluyen activos ficticios en el proyecto.

## Ejecutar
```bash
pip install -r requirements-terrain.txt
python backend/scripts/assess_incident_impact.py \
  --lat 6.17 --lon -75.58 --radius-m 500 \
  --assets activos_salud.geojson \
  --assets puntos_abastecimiento.geojson \
  --hazard amenaza_inundacion.geojson \
  --hazard amenaza_movimientos_masa.geojson \
  --out reports/impacto-incidente.json
```
Reemplaza coordenadas y archivos por datos reales verificados. El radio es un parámetro de cribado configurable, no un límite oficial de afectación.

## Salida
El informe JSON incluye activos dentro del radio, categorías, distancia euclidiana, polígonos de amenaza que intersectan el área y sus áreas de intersección. El resultado puede orientar una verificación inicial, no determinar población afectada, daños, prioridad médica ni necesidad de evacuación.

## Salvaguardas
- No cargar datos personales de población ni domicilios privados.
- No publicar ubicaciones sensibles de infraestructura crítica.
- Diferenciar capa de amenaza de alerta vigente.
- La ausencia de activos en el resultado puede deberse a falta de datos.
- Validar coordenadas, fecha, cobertura y fuente antes de decisiones operativas.
- No utilizar el resultado como orden de evacuación ni sustituto de autoridades.
