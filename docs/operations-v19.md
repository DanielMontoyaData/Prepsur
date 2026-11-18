# Operación — Coordinación intermunicipal PRO 1.9

## Alcance
El módulo `frontend/mutual-aid.js` mantiene en el navegador un registro de solicitudes de apoyo entre municipios. Permite registrar solicitante, oferente, categoría, recurso identificado, cantidad solicitada, unidad, capacidad declarada, roles responsables, fecha requerida, fuente y observaciones. Permite actualizar estados, registrar cantidad comprometida y exportar/importar JSON y CSV.

## Flujo de estados
`solicitada → evaluada → aprobada → asignada → en_transito → recibida → cerrada`

También puede marcarse `rechazada`. Las transiciones siguen una secuencia controlada (con retroceso limitado para correcciones); `recibida` solo puede pasar a `cerrada` y los estados terminales no se reabren. El operador registra manualmente cada transición; el software no aprueba, despacha, rastrea ni confirma la recepción de recursos.

## Control de capacidad
Cuando se informa un identificador de recurso y una capacidad total, el sistema suma compromisos en estados `asignada`, `en_transito` y `recibida` para el mismo municipio oferente, identificador de recurso y unidad. Rechaza una transición o compromiso que supere la capacidad declarada. El control es local a este navegador y solo considera los registros cargados aquí. No evita doble asignación en otros dispositivos, bases de datos o instituciones.

## Datos y privacidad
- Usar roles funcionales, no nombres, teléfonos, cédulas ni datos personales.
- Incluir una referencia documental o fuente verificable cuando exista.
- La capacidad es declarada por el operador; no se certifica.
- Importar solo respaldos confiables y revisar duplicados y vigencia.
- Exportar respaldos periódicamente y guardarlos en un lugar seguro.
- Los datos permanecen en `localStorage`; no hay sincronización ni servidor multiusuario.

## Interpretación
Los totales del tablero mezclan unidades distintas y no deben sumarse como magnitudes físicas. No hay integración con CRUE, bomberos, consejos municipales, radio, despacho ni sistemas oficiales. El módulo es una bitácora de coordinación y no reemplaza procedimientos ni autorizaciones institucionales.
