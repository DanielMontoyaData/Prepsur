# PREPPER MAP PRO 1.3 — operación del centro de mando

## Novedades
- Incidentes con coordenadas WGS84 y marcadores por prioridad en el mapa.
- Selección de incidente desde marcador.
- Bitácora manual de comunicaciones por incidente.
- Inventario territorial local con fuente, estado de verificación y marcadores.
- Respaldo e importación JSON separados.

## Capas territoriales
El catálogo contiene 26 capas configuradas para Envigado, Itagüí, Sabaneta,
La Estrella, Caldas y Medellín-sur. No significa que las 26 geometrías estén
descargadas localmente. La versión de entrega no incluye capas oficiales
descargadas ni cartografía base regional offline.

La fuente POT de Envigado publica, entre otras, inundación (ID 5), movimientos
en masa (ID 6), equipamientos urbanos (ID 2) y suelo de protección (ID 7).
Fuente: https://portalidem.metropol.gov.co/server/rest/services/POT_Envigado/MapServer

El servicio DAGRD de Medellín publica amenazas de incendios forestales (ID 8)
y amenaza tecnológica (ID 9), además de otras capas de amenaza, riesgo,
puntos de encuentro, rutas y sensores. Su ámbito es el Distrito de Medellín;
no se extrapola a Envigado ni a los otros municipios.
Fuente: https://www.medellin.gov.co/servidormapas/rest/services/ambiente_dllo_sost/VC_Gestion_Riesgo/MapServer

## Protocolo de registro
- Capturar solo incidentes de ejercicio o información que el operador esté autorizado a gestionar.
- Confirmar municipio, hora, fuente y nivel de certeza.
- Las coordenadas deben estar en latitud/longitud EPSG:4326.
- No ubicar víctimas ni domicilios privados en el mapa.
- Usar la bitácora de comunicaciones como registro, no como transmisor.
- El inventario no declara automáticamente recursos disponibles; verificar antes de asignar.
- No convertir equipamientos POT en refugios sin validación específica.

## Respaldo
Exportar periódicamente:
- Bitácora de incidentes y comunicaciones.
- Inventario de recursos.

Guardar los archivos en un repositorio autorizado. La aplicación no sincroniza
automáticamente los datos entre dispositivos.

## Validación antes de despliegue
- Instalar dependencias: `npm install`.
- Copiar bibliotecas locales: `npm run sync:vendor`.
- Ejecutar pruebas: `python -m unittest discover -s tests`.
- Abrir por HTTPS o servidor local, no `file://`.
- Probar los marcadores, importación/exportación y modo avión en cada dispositivo.
- Ejecutar `python backend/scripts/check_release.py`; la versión no está lista para
  distribución pública mientras no se integren datos GIS oficiales, mapas base y vendor.
