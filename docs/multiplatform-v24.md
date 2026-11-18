# PREPPER MAP PRO 2.4 — Multiplataforma

## Plataformas objetivo

| Plataforma | Modalidad | Salida prevista | Requisitos de compilación |
|---|---|---|---|
| Windows 10/11 | Tauri nativo | Instalador NSIS `.exe` | Windows + Rust + WebView2 |
| macOS | Tauri nativo | `.dmg` | macOS + Xcode Command Line Tools |
| Linux | Tauri nativo | `.deb` y `.AppImage` | Linux + WebKitGTK 4.1 y dependencias Tauri |
| Android | Tauri nativo | `.apk` / `.aab` | Android SDK, NDK, JDK 21 |
| iPhone/iPad | Tauri nativo | `.ipa` | macOS + Xcode + firma Apple |
| Navegador | PWA | Instalable desde navegador compatible | Hosting HTTPS |
| Android/iOS sin tienda | PWA | Acceso instalable desde navegador | Hosting HTTPS; límites del navegador |

## Comandos locales

```bash
npm install
npm run prepare:app

# Windows
npm run build:windows

# macOS
npm run build:macos

# Linux
npm run build:linux

# Android
npm run android:init
npm run build:android
npm run build:android:aab

# iOS (requiere macOS y Xcode)
npm run ios:init
npm run build:ios
```

Para la PWA, servir la carpeta `frontend/` mediante HTTPS. En Android se puede instalar desde el menú del navegador compatible. En iOS/iPadOS se agrega a la pantalla de inicio desde Safari. La PWA comparte la interfaz y los datos locales del navegador; no tiene todos los permisos ni integraciones de una aplicación nativa.

## Automatización CI
- Windows: `.github/workflows/build-windows.yml`
- macOS: `.github/workflows/build-macos.yml`
- Linux: `.github/workflows/build-linux.yml`
- Android: `.github/workflows/build-android.yml`
- iOS: `.github/workflows/build-ios.yml`

La compilación iOS automatizada requiere secretos de firma Apple en GitHub Actions. No se incluyen certificados ni perfiles de aprovisionamiento en el repositorio.

## Qué significa realmente multiplataforma
Se mantiene un solo frontend y una sola base de código, con empaquetado distinto por sistema operativo. Los datos locales no se comparten automáticamente entre dispositivos. Para compartir eventos se usa la API privada híbrida de PREPPER MAP 2.3/2.4. La sincronización debe probarse con dispositivos reales y con conectividad intermitente.

## Límites de esta entrega
Esta versión incorpora configuración y flujos de construcción multiplataforma. No incluye binarios compilados ni firmados. No se han probado instalaciones reales en Windows, macOS, Linux, Android o iOS en este entorno. La disponibilidad de funciones offline depende de que los mapas y capas se descarguen y empaqueten previamente.
