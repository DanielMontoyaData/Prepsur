# PREPPER MAP PRO 2.5 — Red privada de amigos

## Funciones incorporadas
- Invitaciones de un uso, con vencimiento configurable (1–720 horas).
- Registro de usuario con nombre visible, usuario y contraseña.
- Contraseñas derivadas mediante PBKDF2-HMAC-SHA256 (240.000 iteraciones) y salt aleatorio.
- Sesiones por dispositivo: cada inicio de sesión emite un token distinto; cerrar sesión revoca ese token.
- Perfiles e integrantes del mismo grupo (tenant).
- Mensajería grupal persistente en servidor.
- Observaciones compartidas con categoría y coordenadas opcionales.
- Marcadores de observaciones compartidas en el mapa cuando contienen coordenadas.
- Cola local de mensajes/observaciones cuando no hay conexión; envío al recuperar internet y tras iniciar sesión.

## Flujo inicial
1. El administrador despliega la API privada y configura un token largo propio en `PREPPER_TOKENS`, con rol `admin` y `tenant_id` para el grupo.
2. Cada usuario abre la app y configura la URL HTTPS de la API.
3. El administrador introduce su token en “Invitar a un amigo” y genera una invitación de un uso, válida por 72 horas.
4. Comparte el código por un canal privado. No lo publiques.
5. El amigo introduce el código, un usuario, nombre visible y contraseña de al menos 10 caracteres.
6. El servidor crea el perfil y devuelve un token de sesión para ese dispositivo.
7. Los demás dispositivos pueden iniciar sesión con el mismo usuario y contraseña; cada uno recibe su propia sesión. La contraseña no se comparte en chats.
8. Los mensajes y observaciones se comparten dentro del grupo. La cola local se transmite al recuperar conexión.

## Endpoints
- `POST /api/network/invites` — administrador/operador crea invitación.
- `POST /api/network/join` — registro con código.
- `POST /api/network/login` — inicio de sesión.
- `POST /api/network/logout` — revoca la sesión actual.
- `GET /api/network/me` — perfil de sesión.
- `GET /api/network/members` — integrantes del grupo.
- `GET|POST /api/network/messages` — mensajería grupal.
- `GET|POST /api/network/observations` — observaciones compartidas.
- Las rutas `/api/sync/*` continúan disponibles para sincronización de eventos.

## Despliegue seguro para amigos
- No exponer el puerto 8000 directamente a internet. Publicar mediante proxy inverso HTTPS.
- Configurar `CORS_ORIGINS` con el origen exacto del frontend.
- Activar límites de frecuencia para login, registro e invitaciones en el proxy.
- Mantener backups cifrados de `data/sync.sqlite3` y probar restauración.
- Rotar el token administrador si se pierde o se comparte por error.
- Usar contraseñas únicas. El sistema no incluye recuperación automática de contraseña ni MFA.
- El token de sesión vive en memoria en la aplicación; al recargar, volver a iniciar sesión.
- La cola offline se conserva en `localStorage` del navegador y no está cifrada por la app. No guardar datos privados delicados.
- Los mensajes y observaciones del grupo se almacenan en el servidor. No son cifrado de extremo a extremo.
- Las coordenadas son aportadas por usuarios y no constituyen validación oficial.

## Límites
- Mensajería es de actualización manual, no chat instantáneo en tiempo real.
- No hay llamadas, push notifications, adjuntos ni cifrado E2E.
- Las observaciones se comparten en el mapa solo si tienen latitud/longitud.
- La app no despacha recursos ni transmite por radio.
- La plataforma sigue siendo de preparación y coordinación privada; no sustituye canales oficiales de emergencia.
