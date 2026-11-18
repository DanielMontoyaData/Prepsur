# Revisión PREPPER MAP PRO 2.5

## Verificado
- Sintaxis Python (compileall) y JS (node --check, scripts/check-frontend.mjs): OK.
- tauri.conf.json válido.

## NO verificado (el entorno no tenía internet, Rust ni Windows)
- Pruebas pytest (no se pudieron instalar fastapi/pytest).
- Compilación del .exe, APK o IPA.
- Descarga de Leaflet/Esri (se hace con `npm run sync:vendor` durante el build).

## Correcciones aplicadas
1. CORS: Tauri en Windows usa el origen `http://tauri.localhost`; no estaba permitido, la sincronización habría fallado en el .exe.
2. CSP de Tauri: no permitía conectar a la API HTTPS privada configurada por el usuario; ahora permite `https:` y `localhost:8000`.
3. Makefile: `make test` usaba unittest pero las pruebas son pytest. Añadidos `install-dev` y `api`.
4. `run_windows.bat` / `run_mac_linux.sh`: ahora también arrancan la API y avisan si falta `frontend/vendor`.
5. Eliminados `__pycache__` y `.pytest_cache` del paquete; `.gitignore` ampliado (sqlite, vendor).
6. Workflow de Windows: caché de Rust para builds más rápidos.
7. Estructura: carpeta única, sin la carpeta envolvente `_RELEASE`.

## Pendientes recomendados (no cambiados)
- Las sesiones de usuario no caducan (solo se revocan al cerrar sesión).
- No hay límite de intentos de login/registro en la API; ponlo en el proxy inverso.
- README.md es un historial de "Novedades" desordenado y habla de 1.5; conviene reescribirlo para 2.5.
- Docs v06–v25 acumuladas; se podrían consolidar.
