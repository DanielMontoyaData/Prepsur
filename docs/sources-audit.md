# Auditoría de fuentes GIS — PREPPER MAP PRO 0.4

## Fuentes ArcGIS consultadas
Los servicios siguientes publican metadatos REST. La lista de IDs se debe revalidar con `check_sources.py` antes de cada extracción.

| Municipio | Servicio | IDs configurados | Observación |
|---|---|---|---|
| Envigado | POT_Envigado/MapServer | 2, 5, 6, 7 | Equipamientos, inundación, movimiento en masa, protección |
| Itagüí | POT_Itagui/MapServer | 7, 8, 9 | Movimiento en masa, inundación, equipamientos |
| Sabaneta | POT_Sabaneta/MapServer | 5, 7, 8 | Riesgos combinados, protección, equipamientos |
| La Estrella | POT_La_Estrella/MapServer | 4, 5, 6, 7 | Suelo de protección, riesgos combinados, equipamientos |
| Caldas | POT_Caldas/MapServer | 1, 2, 3 | Equipamientos, riesgos combinados, protección |
| Medellín | VC_Gestion_Riesgo/MapServer | 0, 1, 2, 10, 11, 12, 13 | Servicio distrital DAGRD; no extrapolar sus puntos/rutas a otros municipios |

## Metadatos observados en servicios públicos
- Envigado publica capas 0–11 y declara referencia espacial 9377; el servicio identifica copyright de Alcaldía de Envigado, Planeación.
- Itagüí publica capas 0–9 y declara referencia espacial 9377.
- Sabaneta publica capa `Riesgos` en ID 5; no desagregar sin analizar atributos y leyenda.
- La Estrella publica `Riesgos` en ID 6.
- Caldas publica `Riesgos` en ID 2.
- Medellín DAGRD publica amenazas, riesgos, alarmas, puntos de encuentro, rutas y sensores. El servicio es del Distrito de Medellín.

## Enlaces directos
- https://portalidem.metropol.gov.co/server/rest/services/POT_Envigado/MapServer
- https://portalidem.metropol.gov.co/server/rest/services/POT_Itagui/MapServer
- https://portalidem.metropol.gov.co/server/rest/services/POT_Sabaneta/MapServer
- https://portalidem.metropol.gov.co/server/rest/services/POT_La_Estrella/MapServer
- https://portalidem.metropol.gov.co/server/rest/services/POT_Caldas/MapServer
- https://www.medellin.gov.co/servidormapas/rest/services/ambiente_dllo_sost/VC_Gestion_Riesgo/MapServer

## Advertencias
1. EPSG:9377 es el CRS de origen reportado por los servicios POT consultados. El extractor solicita geometría en EPSG:4326 para GeoJSON; conserva el CRS original en metadatos.
2. Los mapas POT son instrumentos de ordenamiento/amenaza y no equivalen a alertas en tiempo real.
3. Las capas `mixed_hazard` permanecen combinadas.
4. La existencia de una capa de puntos de encuentro o rutas de evacuación en Medellín no habilita su uso como recurso oficial de Envigado, Itagüí, Sabaneta, La Estrella o Caldas.
5. La consulta automatizada de metadatos no certifica vigencia normativa, exactitud de escala ni seguridad de una ruta.
