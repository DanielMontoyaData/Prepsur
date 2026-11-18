# Operación — Inteligencia operativa territorial PRO 2.0

## Qué hace
El tablero `frontend/situation-board.js` lee los registros locales de incidentes, recursos y coordinación intermunicipal. Consolida indicadores por ámbito municipal y permite exportar un SITREP JSON o copiar un resumen textual.

## Indicadores y brechas
- Incidentes activos y P1.
- Recursos marcados `verificado`, sin convertir esa marca en disponibilidad actual.
- Solicitudes de apoyo abiertas y compromisos en estados asignada, en tránsito o recibida.
- Incidentes sin coordenadas o asignación registrada.
- Recursos sin fuente o con verificación más antigua que la ventana seleccionada.
- Incidentes sin situación o rol líder documentado.
- Solicitudes pendientes sin compromiso.

## Frescura y calidad
La frescura se calcula con `updated_at` en incidentes y `verified_at` en recursos. Un registro sin fecha se considera no reciente. La ventana es configurable entre 1 y 365 días. La ausencia de brechas solo significa que las reglas automáticas no detectaron esos problemas; no certifica exactitud.

## Límites
- Solo lectura: no modifica los módulos de origen.
- Solo datos disponibles en el `localStorage` de este navegador.
- No sincroniza equipos ni instituciones.
- No confirma despacho, recepción física, disponibilidad, capacidad real ni seguridad de rutas.
- Los recursos y solicitudes no se suman en unidades heterogéneas.
- El SITREP es un borrador operativo local; debe revisarse y validarse antes de difundirlo como informe institucional.
