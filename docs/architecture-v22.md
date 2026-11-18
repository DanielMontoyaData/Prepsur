# PREPPER MAP PRO 2.2 — Consolidación y sincronización segura

## Qué incorpora
- API versionada 2.2 con endpoints de estado, catálogo GIS, manifiesto, capas y lugares.
- Almacén SQLite de eventos append-only con idempotencia por `event_id`, hash SHA-256 del payload, tenant, dispositivo, actor y bitácora de recepción.
- Sincronización explícita push/pull; no se transmite automáticamente información operativa.
- Control de acceso Bearer por rol y tenant. La API queda deshabilitada si no se configuran secretos. No se incluyen credenciales de fábrica.
- Cliente web con outbox IndexedDB, reintentos manuales y token solo en memoria de sesión.
- Auditor del catálogo GIS con modo local y remoto; descarga opcional por capas tras verificar metadatos.
- Contrato JSON del evento, guía de despliegue y controles de publicación.

## Modelo de sincronización
Los módulos existentes siguen siendo la fuente local de sus registros. Un productor debe emitir `window.dispatchEvent(new CustomEvent('prepper:event',{detail:event}))` para encolar un evento. La cola conserva el evento si no hay red. El envío se hace mediante `PrepperSync.configure()` y `PrepperSync.push()` desde una sesión autorizada. Los eventos descargados se entregan al integrador de cada módulo; el cliente no los aplica automáticamente para evitar sobrescrituras silenciosas.

## Credenciales y aislamiento
Configurar `PREPPER_TOKENS` como JSON de token aleatorio largo a claims: `{"TOKEN_ALEATORIO":{"role":"admin","tenant_id":"organizacion-1","actor":"operador-01"}}`. Crear tokens distintos por usuario/dispositivo y rotarlos fuera del repositorio. El tenant de la solicitud debe coincidir con el tenant de la credencial. Usar HTTPS, secretos del gestor de despliegue y CORS explícito. No publicar SQLite ni el puerto de base de datos directamente.

## Límites y asuntos no resueltos
- La sincronización transporta eventos, pero no resuelve conflictos ni materializa automáticamente cambios en las tablas locales de los módulos. Requiere adaptadores por entidad, política de conflictos y pruebas multiusuario.
- SQLite es apropiado para piloto/local; para operación multiinstancia debe migrarse a PostgreSQL/PostGIS con migraciones, backups, alta disponibilidad y monitoreo.
- Los eventos pueden contener información operativa: desplegar solo con política de clasificación, retención, consentimiento institucional y evaluación de impacto de privacidad.
- No se incluye identidad corporativa, MFA, recuperación de cuenta ni gestión central de usuarios.
- No hay cartografía oficial precargada por esta versión; el auditor identifica estado y la extracción requiere ejecución explícita.
- No se incluye transmisión de radio, despacho, alerta pública ni integración SIATA/SIATA-like en vivo.

## Despliegue de piloto
1. Copiar `.env.example` a `.env`; generar contraseñas y tokens aleatorios y no compartir el archivo.
2. Configurar `POSTGRES_PASSWORD`, `PREPPER_TOKENS` (JSON de claims con rol y tenant) y `CORS_ORIGINS` para el origen exacto de la aplicación.
3. Ejecutar `docker compose -f deploy/docker-compose.yml up -d --build`.
4. La API se publica solo en `127.0.0.1:8000` por defecto; poner un proxy TLS delante para acceso remoto y cambiar el bind solo después de endurecer firewall y proxy.
5. El servicio PostGIS queda provisionado, pero la API 2.2 todavía usa SQLite para la bandeja de eventos. No asumir que los datos ya están migrados a PostGIS.
