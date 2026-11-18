# PREPPER MAP PRO 1.8 — Cobertura y brechas territoriales

## Objetivo
Comparar polígonos de zonas con puntos de recursos georreferenciados, contar recursos dentro de cada zona, identificar categorías registradas y calcular distancia euclidiana desde un punto representativo de la zona al recurso más cercano de cada categoría.

## Datos requeridos
- `zones.geojson`: FeatureCollection de polígonos. Puede incluir `name` y `population` como propiedades.
- `resources.geojson`: FeatureCollection de puntos. Debe incluir `name` y `category`.
- CRS de entrada predeterminado EPSG:4326. Cambiar `--source-crs` si los archivos tienen otro CRS.

No incluyas datos personales ni domicilios privados. Usa ubicaciones públicas o datos agregados con autorización.

## Ejemplo
```bash
pip install -r requirements-terrain.txt
python backend/scripts/assess_zone_coverage.py \
  --zones zones.geojson \
  --resources verified-resources.geojson \
  --population-field population \
  --category-field category \
  --name-field name \
  --rate water=4 \
  --out reports/zone-coverage.json
```
Las tasas son unidades de recurso por persona y día, interpretadas por el operador. Ejemplo `water=4` significa 4 unidades (litros si los datos usan litros) por persona/día. No es una recomendación universal.

## Ver el informe
Abre PREPPER MAP, sección “Cobertura y brechas territoriales”, selecciona el JSON de salida. El visor muestra totales y tabla por zona. El archivo se procesa localmente en el navegador; el límite de carga es 10 MB.

## Interpretación y límites
- `resources_inside` es un conteo de puntos incluidos en el polígono, no un inventario de capacidad.
- La distancia se mide desde un punto representativo al punto de recurso más cercano, en línea recta; no es distancia vial ni tiempo de respuesta.
- Las zonas sin puntos pueden deberse a datos incompletos.
- Población ausente permanece como `null`; no se imputan ni extrapolan cifras.
- Requerimientos solo se calculan si existe población y se suministran tasas.
- No genera puntuación automática de vulnerabilidad ni recomienda negar o priorizar asistencia.
- Validar cobertura, fecha, fuente, operación y accesibilidad de cada registro antes de usar en decisiones.
