# Operación PREPPER MAP PRO 1.5

## Asignación de recursos
1. Registra primero el recurso en el inventario.
2. Aporta una fuente y confirma existencia, ubicación y disponibilidad antes de marcarlo verificado.
3. Abre el incidente y selecciona el recurso verificado.
4. Registra estado, cantidad/capacidad y observación.
5. Actualiza el estado a medida que recibas confirmación real.
6. Exporta la bitácora con frecuencia y conserva respaldos fuera del dispositivo.

Estados: `solicitado`, `asignado`, `en_camino`, `en_sitio`, `liberado`, `cancelado`. Un estado registrado es una anotación del operador, no una señal automática de despacho ni telemetría.

## SITREP
El botón Copiar SITREP construye un mensaje con identificador, municipio, prioridad, estado, ubicación, responsable, situación y recursos activos. Revisa exactitud, sensibilidad y destinatarios antes de retransmitir. Usa únicamente redes y canales autorizados. La aplicación no transmite por radio.

## Análisis GIS de exposición de rutas
Instala dependencias: `pip install -r requirements-terrain.txt`.
Ejemplo:
```bash
python backend/scripts/analyze_route_exposure.py --routes ruta.gpx.geojson --hazard gis/downloaded/envigado_5_riesgos_de_inundacion.geojson --hazard gis/downloaded/envigado_6_riesgos_movimientos_en_masa.geojson --out reports/envigado-route-screening.json
```
El ejemplo requiere que los archivos indicados existan realmente. El analizador transforma las geometrías al CRS métrico configurado (por defecto EPSG:9377), calcula longitud de ruta coincidente con polígonos y genera:
- informe JSON con longitudes y porcentajes de intersección por capa;
- GeoJSON con segmentos de coincidencia para inspección cartográfica.

No confundir el porcentaje de coincidencia con probabilidad de accidente o nivel de riesgo individual. El resultado no incorpora condiciones en tiempo real, cierres, clima, caudales, obstáculos ni inspección de campo. La ausencia de intersección no significa seguridad. No utilizar para ordenar evacuaciones ni reemplazar rutas oficiales.

## Respaldo
La bitácora exportada mantiene incidentes, comunicaciones y asignaciones. La información se guarda localmente en el dispositivo; exporta respaldos cifrados o guárdalos en un repositorio controlado según las políticas de la entidad.
