# PREPPER MAP PRO 2.3 — Estado de entrega

## Enfoque
Uso privado propio y de un grupo pequeño de amigos. Arquitectura híbrida: funcionamiento local/offline y sincronización voluntaria cuando hay internet.

## Verificado en este paquete
- 67 pruebas Python aprobadas.
- `node --check` aprobado para sync-client.js, sync-panel.js y sw.js.
- Cliente de cola local IndexedDB.
- Indicador online/offline.
- Envío automático opcional tras conexión, solo con sesión HTTPS configurada y autorización explícita.
- Descarga remota manual a JSON para revisión; no hay aplicación automática de eventos.
- Token de sesión no persistido por la aplicación.

## No verificado / pendiente
- El chequeo integral `scripts/check-frontend.mjs` no pudo ejecutarse porque el entorno rechazó crear `/tmp/prepper-map-inline-check.js` (EACCES). No se reporta como aprobado.
- No se ejecutaron pruebas multi-dispositivo reales.
- No se desplegó API remota ni se generaron credenciales.
- No se compilaron APK/EXE/IPA.
- No se incluyeron mapas base offline ni capas GIS oficiales nuevas.
- Los módulos deben emitir eventos `prepper:event` para que sus cambios concretos entren en la cola; la integración completa por entidad sigue pendiente.

## Recomendación de uso
Primero probar en red local con datos ficticios, luego configurar servidor privado HTTPS. No compartir tokens en chats ni guardar información sensible en registros. La aplicación es una herramienta de preparación y coordinación entre conocidos, no un sistema certificado de despacho o alerta.
