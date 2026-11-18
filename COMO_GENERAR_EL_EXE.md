# Cómo obtener el .exe (instalador de Windows)

El .exe se compila con Tauri 2 (necesita Windows, Rust y Node). La forma más simple, sin instalar nada:

## Opción A — GitHub Actions (recomendada)
1. Crea un repositorio **privado** en GitHub y sube esta carpeta (el `.gitignore` ya excluye secretos y datos).
2. Ve a **Actions → "Build Windows installer" → Run workflow**.
3. Al terminar (~10-15 min), descarga el artefacto **prepper-map-windows-installer**: contiene `PREPPER MAP_2.5.0_x64-setup.exe`.

## Opción B — En tu PC con Windows
1. Instala Node 22+, Rust (https://rustup.rs) y las "Build Tools de Visual Studio" (C++).
2. En esta carpeta:
   ```
   npm install
   npm run icons:generate
   npm run build:windows
   ```
3. El instalador queda en `src-tauri\target\release\bundle\nsis\`.

## Antes de usar la red privada con amigos
- El servidor API (`backend/`) corre aparte (no va dentro del .exe). Despliégalo detrás de HTTPS.
- Copia `.env.example` a `.env` y define `PREPPER_TOKENS` con un token largo y aleatorio.
- En la app, configura la URL HTTPS de tu API.
