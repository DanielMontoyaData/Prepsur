# PREPPER MAP 1.1 — Operación y preparación de datos

## Estado verificado de esta entrega

- Catálogo configurado: **26 capas de 6 jurisdicciones**, basadas en fuentes GIS municipales y Medellín.
- Capas descargadas en el paquete: **0**. No se incorporaron polígonos ficticios ni coordenadas de refugios no verificados.
- Mapas base regionales incluidos: **0**. Hay conversor y descarga a caché, no un MBTiles regional con licencia comprobada.
- La compilación Windows/Android/iOS está configurada, pero no se distribuyen ejecutables nativos firmados.

## Secuencia operativa

1. `python backend/scripts/check_sources.py` para comprobar fuentes según conectividad.
2. `python backend/scripts/extract_arcgis.py --dry-run` para inspeccionar metadatos. La descarga completa puede ser pesada y está sujeta a condiciones de reutilización.
3. `python backend/scripts/extract_arcgis.py --municipality Envigado --max-features 10000` para un piloto controlado; **si se trunca, el resultado no debe usarse como cobertura completa**.
4. `python backend/scripts/validate_dataset.py` para comprobar GeoJSON descargados.
5. `python backend/scripts/quality_report.py --max-age-days 180` para actualizar `frontend/data/quality-report.json`.
6. `python backend/scripts/check_release.py` para revisar bloqueos y pendientes antes de distribuir.
7. `npm install && npm run sync:vendor` para instalar bibliotecas web locales.
8. Abrir la aplicación por servidor HTTP/HTTPS; no con `file://`. Para PWA, usar HTTPS y confirmar funcionamiento en modo avión.

## Cartografía offline

Usar un MBTiles raster adquirido con permiso de almacenamiento y redistribución. Ejecutar:

```bash
python backend/scripts/mbtiles_to_xyz.py mapa.mbtiles \
  --provider "Nombre real del proveedor" \
  --license "Licencia verificable" \
  --attribution "Atribución obligatoria"
```

El conversor crea `frontend/offline-tiles/manifest.json`, `tile-index.json` y teselas raster XYZ. En la aplicación, usar **Guardar teselas en este dispositivo**, verificar el contador y luego probar sin conexión. Si el índice supera 30.000 teselas, dividir el paquete. La descarga a Cache Storage depende de la cuota disponible y puede ser desalojada por el sistema. Una aplicación nativa que distribuya teselas dentro de sus recursos puede acceder a ellas localmente sin la precarga PWA.

## Auditoría y límites

El informe calcula SHA-256, recuento, extensión, fecha, incidencias y procedencia de cada capa descargada. Una capa consistente no implica seguridad, vigencia normativa ni que se haya cartografiado toda la amenaza. Los equipamientos POT no se clasifican automáticamente como albergues. La fuente oficial de Medellín no se extrapola a Envigado ni a otros municipios.

## Distribución

Los workflows de GitHub Actions preparan instaladores Windows NSIS y Android, pero deben ejecutarse y verificarse; Android Play y Apple App Store requieren firma, pruebas, revisión de privacidad y cumplimiento de requisitos de las tiendas. No publicar como producto de emergencia certificado.

## Novedades 1.2.0
- La bitácora del puesto de mando funciona localmente; exportar respaldos manualmente.
- El catálogo incorpora 2 capas DAGRD adicionales en Medellín: amenaza de incendios forestales (8) y tecnológica (9).
- El catálogo total pasa a 26 capas; la disponibilidad y geometría descargada debe comprobarse con `check_sources.py` y `extract_arcgis.py`.
