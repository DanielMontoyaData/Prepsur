# Protocolo de verificación

## Estados
- `verified`: evidencia directa reciente y suficiente.
- `potential`: existe indicio razonable, pero falta confirmar disponibilidad/condiciones.
- `pending`: dato recibido o extraído que aún no se ha comprobado.
- `unusable`: cerrado, inaccesible o inseguro según evidencia actual.

## Confianza
0–24 preliminar; 25–49 evidencia indirecta; 50–74 fuente confiable no confirmada en campo; 75–89 comprobación directa; 90–100 confirmación institucional/documental reciente. El puntaje es calidad de dato, no probabilidad de seguridad.

## Evidencia mínima por tipo
- Refugio: acto/comunicado de activación, dirección, horario, capacidad, responsable, accesibilidad y fecha de vigencia.
- Agua: responsable, tipo de suministro, potabilidad documentada, horario y condiciones de acceso.
- Carga: tipo de energía, potencia/conectores, costo, horario, acceso público y confirmación de operación.
- Salud/rescate: entidad, servicio, canal oficial, cobertura y condición de atención.
- Ruta: fuente, fecha, segmento, barreras, pendiente, cruce de cauce, amenaza superpuesta y revisión de campo.
- Comercio: existencia, horario habitual y contacto; nunca asumir inventario durante crisis.

Registrar cada cambio en `verification_log`.
