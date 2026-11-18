# Operación PREPPER MAP PRO 0.6

## Evaluación preliminar de rutas
Descarga y valida capas oficiales de amenaza, activa las capas locales de inundación/movimiento en masa, importa GPX/KML/GeoJSON y pulsa **Evaluar ruta importada**. El análisis muestrea aproximadamente cada 50 m y comprueba si los puntos caen dentro de polígonos activos. Exporta el informe JSON para trazabilidad.

Esto es un filtro de exposición cartográfica, no un modelo hidráulico/geotécnico. No analiza estado de superficie, pendientes, puentes, cierres, clima actual ni transitabilidad. Un resultado sin coincidencias no significa ruta segura.

## Verificación de campo
Las observaciones se guardan en `localStorage` del navegador y no se sincronizan con el servidor. Exporta manualmente el JSON. “Verificado” significa que el registrador declara haberlo verificado; no autentica al observador. No registrar direcciones privadas, datos de personas vulnerables, claves ni inventarios domésticos.

## Calidad y vigencia
El tablero informa capas locales, elementos declarados, rutas y observaciones. Marca capas sin fecha o mayores de 180 días como candidatas a revisión. La antigüedad no implica que una capa sea incorrecta; la frescura tampoco garantiza validez.

## Offline y seguridad
El service worker cambia a caché 0.6. Servicios GIS remotos, alertas y mapas base pueden no estar disponibles offline. No se cachean teselas públicas OSM. No es sistema oficial de alertas o despacho, ni genera rutas oficiales de evacuación. No sustituye SIATA, DAGRD, alcaldías ni inspección técnica.
