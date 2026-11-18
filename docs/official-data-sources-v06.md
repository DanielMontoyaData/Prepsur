# Fuentes geoespaciales para ampliar PREPPER MAP

Fuentes recomendadas para futuras integraciones; la presencia en este catálogo no significa que sus capas ya estén descargadas ni integradas en la aplicación.

| Fuente | Uso recomendado | Precaución |
|---|---|---|
| SIATA / SIAMMO — https://siata.gov.co/geotecnia/siammo.html | Consulta de alertas y contexto de movimientos en masa en el Valle de Aburrá | Es un sistema de visualización y monitoreo; confirmar alertas y protocolos en el canal oficial. |
| IDEAM Geoportal — https://www.ideam.gov.co/geoportal-ambiental-institucional | Información hidrometeorológica y ambiental oficial, metadatos y geoservicios | Verificar fecha, escala, cobertura y licencia de cada capa antes de usarla. |
| Colombia en Mapas — https://www.colombiaenmapas.gov.co/inicio/plataformas.html | Descubrir plataformas geográficas oficiales, incluido SGC | Diferenciar cartografía nacional de estudios detallados municipales. |
| Copernicus DEM — https://dataspace.copernicus.eu/explore-data/data-collections/copernicus-contributing-missions/collections-description/COP-DEM | Elevación y análisis topográfico preliminar | GLO-30 es un modelo de superficie de 30 m; no equivale a un DTM de precisión predial ni sirve por sí solo para certificar pendientes de senderos. |
| OpenStreetMap — https://www.openstreetmap.org/ | Red de caminos, senderos y elementos mapeados | Respetar ODbL, atribución y políticas de uso; no depender de la API de edición para descargas masivas. |

## Orden técnico recomendado
1. Consolidar y documentar las capas municipales POT/amenaza que ya están catalogadas.
2. Incorporar series temporales oficiales de lluvia/alertas mediante mecanismos autorizados, sin scraping.
3. Integrar un DEM con metadatos y generar perfiles de elevación y pendiente solo cuando se descargue y valide el raster de cobertura completa.
4. Incorporar observaciones de campo con trazabilidad, responsable, fecha, evidencia y revisión editorial antes de publicar.
5. Mantener por separado los datos oficiales, los datos abiertos de terceros y las observaciones comunitarias.

## Referencias técnicas
- Copernicus describe GLO-30 como un DSM global de 30 m; incluye superficie, vegetación y edificios: https://dataspace.copernicus.eu/explore-data/data-collections/copernicus-contributing-missions/collections-description/COP-DEM
- IDEAM ofrece geoportal, metadatos, descargas y geoservicios oficiales: https://www.ideam.gov.co/geoportal-ambiental-institucional
- SIAMMO presenta información del sistema de alertas por movimientos en masa del AMVA: https://siata.gov.co/geotecnia/siammo.html
- La política de OSM exige atribución y recomienda alternativas para usuarios de grandes volúmenes: https://openstreetmap.github.io/owg-website/policies/api/


## Elevación: advertencia metodológica
Copernicus DEM GLO-30 es un modelo digital de superficie (DSM), no un modelo de terreno desnudo. Puede representar vegetación y edificios. Para pendientes y perfiles de rutas se debe registrar resolución, CRS, fecha/versión, datum vertical y tipo de modelo. No usarlo como único insumo para estabilidad de laderas o decisiones de evacuación.
