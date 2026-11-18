# Puesto de mando georreferenciado y recursos — PREPPER MAP 1.3

## Incidentes
Cada incidente puede guardar municipio, prioridad, estado, referencia general,
coordinador, situación, latitud/longitud y bitácora. Si se añaden coordenadas
WGS84 válidas, el incidente aparece en el mapa. El marcador abre su ficha y
permite seleccionarlo. No geocodifica automáticamente direcciones.

## Comunicaciones
Cada incidente admite registros de red/canal autorizado, indicativo origen,
destino/grupo, mensaje y confirmación. Es una bitácora manual: no transmite
radio, no controla equipos, no asigna frecuencias ni sustituye el procedimiento
de comunicaciones de la institución. Registrar solo identificadores y mensajes
no sensibles; no almacenar datos médicos, nombres de víctimas o claves.

## Inventario territorial
Registro de recursos por categoría y municipio, con capacidad, ubicación general,
fuente, observaciones y estado: por verificar, verificado o inactivo. Para marcar
un recurso como verificado, el operador confirma que comprobó existencia,
ubicación y disponibilidad. La confirmación queda fechada; no es una certificación
institucional. Los marcadores del inventario solo aparecen cuando el estado es
verificado y hay coordenadas válidas.

## Persistencia y respaldo
- Incidentes y comunicaciones: localStorage del navegador/dispositivo.
- Recursos: almacén local independiente.
- Exportar respaldos JSON periódicamente y guardarlos en ubicación controlada.
- Importar agrega IDs nuevos; no reemplaza registros con el mismo ID.
- Límite de 100 incidentes, 500 eventos por incidente y 500 recursos.

## Reglas operativas
1. Separar hechos confirmados, reportes no confirmados e hipótesis.
2. Registrar fuente y hora en la bitácora.
3. No declarar un recurso disponible por el solo hecho de existir en un directorio.
4. No tratar un equipamiento POT como refugio sin validación específica.
5. No interpretar capas de amenaza como alertas en tiempo real.
6. Utilizar canales institucionales y frecuencias legalmente autorizados.
